"""Tweaks library browser page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.change_log import ChangeLog
from wintuner.app.core.tweak_registry import get_all_tweaks, get_tweak, search_tweaks
from wintuner.app.ui.dialogs import show_error, show_info
from wintuner.app.ui.tweak_actions import apply_tweak_with_confirmations, show_tweak_detail_dialog


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

    def _selected_tweak(self):
        item = self._list.currentItem()
        if item is None:
            return None
        return get_tweak(item.data(Qt.ItemDataRole.UserRole))

    def _show_detail_from_btn(self) -> None:
        tweak = self._selected_tweak()
        if tweak:
            show_tweak_detail_dialog(self, self._change_log, tweak)

    def _show_detail(self, item: QListWidgetItem) -> None:
        tweak = get_tweak(item.data(Qt.ItemDataRole.UserRole))
        if tweak:
            show_tweak_detail_dialog(self, self._change_log, tweak)

    def _apply_selected(self) -> None:
        tweak = self._selected_tweak()
        if tweak is None:
            show_error(self, "No Selection", "Select a tweak from the list first.")
            return
        if apply_tweak_with_confirmations(self, self._change_log, tweak):
            show_info(self, "Applied", f"{tweak.title} applied successfully.")
            self._refresh_list()

    def set_search_query(self, query: str) -> None:
        self._search.setText(query)
        self._refresh_list()
