"""Shared tweak detail and apply flows for Tweaks and Search pages."""

from __future__ import annotations

from PySide6.QtWidgets import QDialogButtonBox, QLabel, QWidget

from wintuner.app.core.admin import admin_required_message, is_admin
from wintuner.app.core.change_log import ChangeLog, ChangeRecord
from wintuner.app.core.restore_point import open_system_protection
from wintuner.app.core.temp_cleanup import preview_cleanup
from wintuner.app.core.tweak_model import RiskLevel, Tweak
from wintuner.app.ui.dialogs import (
    ScrollDialog,
    confirm_dialog,
    confirm_tweak_dialog,
    restore_point_prompt,
    show_error,
)


def show_tweak_detail_dialog(parent: QWidget, change_log: ChangeLog, tweak: Tweak) -> None:
    """Show scrollable tweak details with optional Apply (never auto-applies)."""
    state = tweak.detect()
    dlg = ScrollDialog(tweak.title, parent)
    sl = dlg.scroll_layout()
    for text in (
        f"<b>Category:</b> {tweak.category}",
        tweak.description,
        f"<b>Why:</b> {tweak.why_use}",
        f"<b>Risk:</b> {tweak.risk_level.value.capitalize()}",
        f"<b>Current state:</b> {state.description or state.enabled}",
        f"<b>Undo:</b> {tweak.undo_instructions}",
        f"<b>Notes:</b> {tweak.notes}",
    ):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        sl.addWidget(lbl)
    sl.addStretch()

    def on_apply() -> None:
        dlg.accept()
        apply_tweak_with_confirmations(parent, change_log, tweak)

    apply_btn = dlg.add_button(QDialogButtonBox.ButtonRole.AcceptRole, "Apply")
    apply_btn.clicked.connect(on_apply)
    close_btn = dlg.add_button(QDialogButtonBox.ButtonRole.RejectRole, "Close")
    close_btn.clicked.connect(dlg.accept)
    dlg.exec()


def apply_tweak_with_confirmations(
    parent: QWidget,
    change_log: ChangeLog,
    tweak: Tweak,
) -> bool:
    """Apply a tweak using the standard confirmation and logging flow."""
    if tweak.requires_admin and not is_admin():
        show_error(parent, "Admin Required", admin_required_message(tweak.title))
        return False
    if tweak.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH):
        if not restore_point_prompt(parent, open_system_protection):
            return False
    if tweak.id == "storage_clear_user_temp":
        preview = preview_cleanup(force_refresh=True)
        if not confirm_dialog(
            parent,
            "Confirm Temp Cleanup",
            f"Delete {preview.file_count} items ({preview.total_mb} MB)?",
        ):
            return False
    elif tweak.id == "storage_empty_recycle_bin":
        if not confirm_dialog(parent, "Confirm", "Empty the Recycle Bin permanently?"):
            return False
    elif not tweak.opens_settings:
        if not confirm_tweak_dialog(parent, tweak):
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
    change_log.add(record)
    if not result.success:
        show_error(parent, "Failed", result.message)
    return result.success
