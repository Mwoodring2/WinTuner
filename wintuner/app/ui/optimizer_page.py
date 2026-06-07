"""Safe optimizer profiles page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.admin import admin_required_message, is_admin
from wintuner.app.core.change_log import ChangeLog, ChangeRecord
from wintuner.app.core.profiles import Profile, load_profiles
from wintuner.app.core.restore_point import open_system_protection
from wintuner.app.core.temp_cleanup import preview_cleanup
from wintuner.app.core.tweak_model import RiskLevel, Tweak
from wintuner.app.core.tweak_registry import get_tweak
from wintuner.app.ui.dialogs import (
    confirm_dialog,
    confirm_tweak_dialog,
    restore_point_prompt,
    show_error,
    show_info,
    show_warning,
)


class OptimizerPage(QWidget):
    """Preset profiles with selectable actions."""

    def __init__(self, change_log: ChangeLog, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._change_log = change_log
        self._profiles = load_profiles()
        self._checkboxes: dict[str, QCheckBox] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Safe Optimizer Profiles")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        note = QLabel(
            "Profiles are checklists — nothing runs until you click Apply Selected. "
            "No security features are disabled."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #aaa;")
        layout.addWidget(note)

        row = QHBoxLayout()
        row.addWidget(QLabel("Profile:"))
        self._profile_combo = QComboBox()
        for p in self._profiles:
            self._profile_combo.addItem(p.name, p.id)
        self._profile_combo.currentIndexChanged.connect(self._load_profile)
        row.addWidget(self._profile_combo, stretch=1)
        layout.addLayout(row)

        self._desc_lbl = QLabel()
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setStyleSheet("color: #ccc; font-style: italic;")
        layout.addWidget(self._desc_lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._actions_widget = QWidget()
        self._actions_layout = QVBoxLayout(self._actions_widget)
        scroll.setWidget(self._actions_widget)
        layout.addWidget(scroll, stretch=1)

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply Selected")
        apply_btn.clicked.connect(self._apply_selected)
        preview_btn = QPushButton("Preview Temp Cleanup")
        preview_btn.setProperty("class", "secondary")
        preview_btn.clicked.connect(self._preview_temp)
        btn_row.addWidget(apply_btn)
        btn_row.addWidget(preview_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        if self._profiles:
            self._load_profile(0)

    def _current_profile(self) -> Profile | None:
        idx = self._profile_combo.currentIndex()
        if idx < 0 or idx >= len(self._profiles):
            return None
        return self._profiles[idx]

    def _load_profile(self, _index: int) -> None:
        while self._actions_layout.count():
            item = self._actions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._checkboxes.clear()

        profile = self._current_profile()
        if profile is None:
            return
        self._desc_lbl.setText(profile.description)
        for action in profile.actions:
            tweak = get_tweak(action.tweak_id)
            cb = QCheckBox(action.label)
            cb.setChecked(action.default_selected)
            if tweak is None:
                cb.setEnabled(False)
                cb.setToolTip("Tweak not found")
            else:
                cb.setToolTip(tweak.description)
            self._checkboxes[action.tweak_id] = cb
            self._actions_layout.addWidget(cb)
        self._actions_layout.addStretch()

    def _preview_temp(self) -> None:
        preview = preview_cleanup(log_result=True, force_refresh=True)
        show_info(
            self,
            "Temp Cleanup Preview",
            f"Found {preview.file_count} items totaling {preview.total_mb} MB "
            f"in your user TEMP folder.\n\n"
            f"Skipped: {preview.skipped_count} (locked or unsafe paths)",
        )

    def _apply_selected(self) -> None:
        selected_ids = [tid for tid, cb in self._checkboxes.items() if cb.isChecked()]
        if not selected_ids:
            show_warning(self, "Nothing Selected", "Select at least one action to apply.")
            return

        if not confirm_dialog(
            self,
            "Apply Profile Actions",
            f"Apply {len(selected_ids)} selected action(s)?\n\n"
            "Each action will show its own confirmation where required.",
        ):
            return

        results: list[str] = []
        for tweak_id in selected_ids:
            tweak = get_tweak(tweak_id)
            if tweak is None:
                results.append(f"✗ {tweak_id}: not found")
                continue
            ok = self._apply_tweak(tweak)
            results.append(f"{'✓' if ok else '✗'} {tweak.title}")

        show_info(self, "Profile Apply Complete", "\n".join(results))

    def _apply_tweak(self, tweak: Tweak) -> bool:
        if tweak.requires_admin and not is_admin():
            show_error(self, "Admin Required", admin_required_message(tweak.title))
            return False

        if tweak.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH):
            if not restore_point_prompt(self, open_system_protection):
                return False

        if tweak.id == "storage_clear_user_temp":
            preview = preview_cleanup(force_refresh=True)
            if not confirm_dialog(
                self,
                "Confirm Temp Cleanup",
                f"Delete {preview.file_count} items ({preview.total_mb} MB)?\n"
                "Locked files will be skipped.",
            ):
                return False
        elif tweak.id == "storage_empty_recycle_bin":
            if not confirm_dialog(
                self,
                "Confirm Empty Recycle Bin",
                "Permanently delete all items in the Recycle Bin?",
            ):
                return False
        elif not tweak.opens_settings:
            if not confirm_tweak_dialog(self, tweak):
                return False

        state = tweak.detect()
        result = tweak.apply()
        record = ChangeRecord.create(
            tweak_id=tweak.id,
            tweak_title=tweak.title,
            previous_value=result.previous_value if result.previous_value is not None else state.raw_value,
            new_value=result.new_value,
            success=result.success,
            error_message="" if result.success else result.message,
            undo_available=tweak.reversible and tweak.undo_fn is not None,
        )
        self._change_log.add(record)
        if not result.success:
            show_error(self, "Apply Failed", result.message)
        return result.success
