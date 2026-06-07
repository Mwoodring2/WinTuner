"""Unified search results page for God Mode tools and tweaks."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.admin import admin_required_message, is_admin
from wintuner.app.core.change_log import ChangeLog
from wintuner.app.core.launcher import LaunchTool, launch_tool
from wintuner.app.core.search_service import ResultType, SearchResult, search_all
from wintuner.app.core.tweak_registry import get_tweak
from wintuner.app.ui.dialogs import show_error, show_info
from wintuner.app.ui.tweak_actions import show_tweak_detail_dialog


class SearchResultsPage(QWidget):
    """Display unified search results with safe launch/detail actions."""

    def __init__(self, change_log: ChangeLog, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._change_log = change_log
        self._query = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("Search")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        self._summary = QLabel("Start typing in the search bar to find tools and tweaks.")
        self._summary.setWordWrap(True)
        self._summary.setStyleSheet("color: #aaa;")
        layout.addWidget(self._summary)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._results_container = QWidget()
        self._results_layout = QVBoxLayout(self._results_container)
        self._results_layout.setSpacing(8)
        self._results_layout.addStretch()
        scroll.setWidget(self._results_container)
        layout.addWidget(scroll, stretch=1)

    def run_search(self, query: str) -> None:
        """Execute search and rebuild result cards."""
        self._query = query.strip()
        self._clear_results()

        if not self._query:
            self._summary.setText("Start typing in the search bar to find tools and tweaks.")
            return

        results = search_all(self._query)
        if not results:
            self._summary.setText(f'No results for "{self._query}". Try another term.')
            return

        tool_count = sum(1 for r in results if r.result_type == ResultType.TOOL)
        tweak_count = sum(1 for r in results if r.result_type == ResultType.TWEAK)
        self._summary.setText(
            f'{len(results)} result(s) for "{self._query}" '
            f"({tool_count} tool(s), {tweak_count} tweak(s))"
        )

        for result in results:
            self._results_layout.insertWidget(
                self._results_layout.count() - 1,
                self._build_result_card(result),
            )

    def _clear_results(self) -> None:
        while self._results_layout.count() > 1:
            item = self._results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _build_result_card(self, result: SearchResult) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: #2d2d2d; border: 1px solid #3c3c3c; "
            "border-radius: 6px; padding: 8px; }"
        )
        row = QHBoxLayout(card)

        info = QVBoxLayout()
        type_label = "Tool" if result.result_type == ResultType.TOOL else "Tweak"
        header = QLabel(f"<b>{result.title}</b>  <span style='color:#4ec9b0;'>{type_label}</span>")
        info.addWidget(header)
        info.addWidget(QLabel(f"<span style='color:#888;'>Category:</span> {result.category}"))
        desc = QLabel(result.description)
        desc.setWordWrap(True)
        info.addWidget(desc)

        badges: list[str] = []
        if result.requires_admin:
            badges.append("Needs Admin")
        if result.result_type == ResultType.TWEAK:
            badges.append(f"Risk: {result.risk_level}")
            if result.reversible:
                badges.append("Reversible")
            else:
                badges.append("Not Reversible")
        if badges:
            info.addWidget(QLabel(" · ".join(badges)))

        row.addLayout(info, stretch=1)

        if result.result_type == ResultType.TOOL:
            btn = QPushButton("Launch")
            btn.clicked.connect(lambda checked=False, r=result: self._launch_tool(r))
        else:
            btn = QPushButton("View Details")
            btn.clicked.connect(lambda checked=False, r=result: self._view_tweak(r))
        row.addWidget(btn, alignment=Qt.AlignmentFlag.AlignTop)

        return card

    def _launch_tool(self, result: SearchResult) -> None:
        if result.requires_admin and not is_admin():
            show_error(self, "Admin Required", admin_required_message(result.title))
            return
        tool = LaunchTool(
            id=result.id,
            name=result.title,
            description=result.description,
            command=result.command or "",
            args=list(result.tool_args),
            category=result.category,
            command_type=result.command_type or "exe",
            requires_admin=result.requires_admin,
        )
        ok, msg = launch_tool(tool)
        if ok:
            show_info(self, "Launched", msg)
        else:
            show_error(self, "Launch Failed", msg)

    def _view_tweak(self, result: SearchResult) -> None:
        tweak = get_tweak(result.id)
        if tweak is None:
            show_error(self, "Not Found", f"Tweak '{result.id}' is not available.")
            return
        show_tweak_detail_dialog(self, self._change_log, tweak)
