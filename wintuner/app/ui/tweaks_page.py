"""Tweaks library browser page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.admin import admin_required_message, is_admin
from wintuner.app.core.change_log import ChangeLog, ChangeRecord
from wintuner.app.core.restore_point import open_system_protection
from wintuner.app.core.temp_cleanup import preview_cleanup
from wintuner.app.core.tweak_model import RiskLevel, Tweak
from wintuner.app.core.tweak_registry import get_all_tweaks, search_tweaks
from wintuner.app.ui.dialogs import (
    confirm_dialog,
    confirm_tweak_dialog,
    restore_point_prompt,
    ScrollDialog,
    show_error,
    show_info,
)


class TweaksPage(QWidget):
    """Browse and apply individual tweaks."""

    def __init__(self, change_log: ChangeLog, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._change_log = change_log
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Tweaks Library")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        self._search = QLineEdit()
        self._search.setObjectName("searchBar")
        self._search.setPlaceholderText("Search tweaks…")
        self._search.textChanged.connect(self._refresh_list)
        layout.addWidget(self._search)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._show_detail)
        layout.addWidget(self._list, stretch=1)

        btn_row = QHBoxLayout()
        detail_btn = QPushButton("View Details")
        detail_btn.clicked.connect(self._show_detail_from_btn)
        apply_btn = QPushButton("Apply Selected")
        apply_btn.clicked.connect(self._apply_selected)
        btn_row.addWidget(detail_btn)
        btn_row.addWidget(apply_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._refresh_list()

    def _refresh_list(self) -> None:
        self._list.clear()
        query = self._search.text()
        tweaks = search_tweaks(query) if query else get_all_tweaks()
        for tweak in tweaks:
            state = tweak.detect()
            status = ""
            if state.enabled is True:
                status = " [ON]"
            elif state.enabled is False:
                status = " [OFF]"
            badges = f"({tweak.risk_level.value})"
            if tweak.requires_admin:
                badges += " Admin"
            if tweak.reversible:
                badges += " Rev"
            item = QListWidgetItem(f"{tweak.title}{status}  {badges}  — {tweak.category}")
            item.setData(Qt.ItemDataRole.UserRole, tweak.id)
            self._list.addItem(item)

    def _selected_tweak(self) -> Tweak | None:
        item = self._list.currentItem()
        if item is None:
            return None
        from wintuner.app.core.tweak_registry import get_tweak

        return get_tweak(item.data(Qt.ItemDataRole.UserRole))

    def _show_detail_from_btn(self) -> None:
        tweak = self._selected_tweak()
        if tweak:
            self._show_detail_for(tweak)

    def _show_detail(self, item: QListWidgetItem) -> None:
        from wintuner.app.core.tweak_registry import get_tweak

        tweak = get_tweak(item.data(Qt.ItemDataRole.UserRole))
        if tweak:
            self._show_detail_for(tweak)

    def _show_detail_for(self, tweak: Tweak) -> None:
        state = tweak.detect()
        dlg = ScrollDialog(tweak.title, self)
        sl = dlg.scroll_layout()
        sl.addWidget(QLabel(f"<b>Category:</b> {tweak.category}"))
        sl.addWidget(QLabel(tweak.description))
        sl.addWidget(QLabel(f"<b>Why:</b> {tweak.why_use}"))
        sl.addWidget(QLabel(f"<b>Risk:</b> {tweak.risk_level.value.capitalize()}"))
        sl.addWidget(QLabel(f"<b>Current state:</b> {state.description or state.enabled}"))
        sl.addWidget(QLabel(f"<b>Undo:</b> {tweak.undo_instructions}"))
        sl.addWidget(QLabel(f"<b>Notes:</b> {tweak.notes}"))
        sl.addStretch()
        close_btn = dlg.add_button(QDialogButtonBox.ButtonRole.RejectRole, "Close")
        close_btn.clicked.connect(dlg.accept)
        dlg.exec()

    def _apply_selected(self) -> None:
        tweak = self._selected_tweak()
        if tweak is None:
            show_error(self, "No Selection", "Select a tweak from the list first.")
            return
        if self._do_apply(tweak):
            show_info(self, "Applied", f"{tweak.title} applied successfully.")
            self._refresh_list()

    def _do_apply(self, tweak: Tweak) -> bool:
        if tweak.requires_admin and not is_admin():
            show_error(self, "Admin Required", admin_required_message(tweak.title))
            return False
        if tweak.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH):
            if not restore_point_prompt(self, open_system_protection):
                return False
        if tweak.id == "storage_clear_user_temp":
            preview = preview_cleanup()
            if not confirm_dialog(
                self,
                "Confirm Temp Cleanup",
                f"Delete {preview.file_count} items ({preview.total_mb} MB)?",
            ):
                return False
        elif tweak.id == "storage_empty_recycle_bin":
            if not confirm_dialog(self, "Confirm", "Empty the Recycle Bin permanently?"):
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
            show_error(self, "Failed", result.message)
        return result.success

    def set_search_query(self, query: str) -> None:
        self._search.setText(query)
        self._refresh_list()
