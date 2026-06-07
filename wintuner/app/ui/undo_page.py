"""Undo Center page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.admin import admin_required_message, is_admin
from wintuner.app.core.change_log import ChangeLog, ChangeRecord
from wintuner.app.core.tweak_registry import get_tweak
from wintuner.app.ui.dialogs import confirm_dialog, show_error, show_info


class UndoPage(QWidget):
    """View and undo changes made by WinTuner."""

    def __init__(self, change_log: ChangeLog, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._change_log = change_log
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Undo Center")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        note = QLabel("Revert changes made by WinTuner. Only reversible tweaks appear here.")
        note.setStyleSheet("color: #aaa;")
        layout.addWidget(note)

        self._list = QListWidget()
        layout.addWidget(self._list, stretch=1)

        btn_row = QHBoxLayout()
        undo_btn = QPushButton("Undo Selected")
        undo_btn.clicked.connect(self._undo_selected)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.clicked.connect(self.refresh)
        btn_row.addWidget(undo_btn)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def refresh(self) -> None:
        self._list.clear()
        for record in self._change_log.get_undoable():
            ts = record.timestamp[:19].replace("T", " ")
            item = QListWidgetItem(f"{ts} — {record.tweak_title}")
            item.setData(Qt.ItemDataRole.UserRole, record.record_id)
            self._list.addItem(item)
        if self._list.count() == 0:
            item = QListWidgetItem("No undoable changes.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self._list.addItem(item)

    def _undo_selected(self) -> None:
        item = self._list.currentItem()
        if item is None or not item.data(Qt.ItemDataRole.UserRole):
            show_error(self, "No Selection", "Select a change to undo.")
            return
        record_id = item.data(Qt.ItemDataRole.UserRole)
        record = self._change_log.find_by_id(record_id)
        if record is None:
            show_error(self, "Not Found", "Change record not found.")
            return
        self._undo_record(record)

    def _undo_record(self, record: ChangeRecord) -> None:
        tweak = get_tweak(record.tweak_id)
        if tweak is None:
            show_error(self, "Error", f"Tweak '{record.tweak_id}' no longer available.")
            return
        if tweak.requires_admin and not is_admin():
            show_error(self, "Admin Required", admin_required_message(tweak.title))
            return
        if not confirm_dialog(
            self,
            "Confirm Undo",
            f"Undo '{record.tweak_title}'?\n\nThis will restore the previous value.",
        ):
            return
        result = tweak.undo(record.previous_value)
        undo_record = ChangeRecord.create(
            tweak_id=record.tweak_id,
            tweak_title=f"UNDO: {record.tweak_title}",
            previous_value=record.new_value,
            new_value=record.previous_value,
            success=result.success,
            error_message="" if result.success else result.message,
            undo_available=False,
        )
        self._change_log.add(undo_record)
        if result.success:
            self._change_log.mark_undone(record.record_id)
            show_info(self, "Undone", result.message)
            self.refresh()
        else:
            show_error(self, "Undo Failed", result.message)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.refresh()
