"""God Mode tool launcher page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.admin import admin_required_message, is_admin
from wintuner.app.core.launcher import LaunchTool, load_tools, launch_tool, search_tools
from wintuner.app.ui.dialogs import show_error, show_info


class GodModePage(QWidget):
    """Searchable launcher for Windows tools."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tools = load_tools()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("God Mode Launcher")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        subtitle = QLabel("Quick access to useful Windows tools and settings.")
        subtitle.setStyleSheet("color: #aaa;")
        layout.addWidget(subtitle)

        self._search = QLineEdit()
        self._search.setObjectName("searchBar")
        self._search.setPlaceholderText("Search tools…")
        self._search.textChanged.connect(self._rebuild)
        layout.addWidget(self._search)

        self._grid_container = QWidget()
        self._grid = QGridLayout(self._grid_container)
        self._grid.setSpacing(8)
        layout.addWidget(self._grid_container)
        layout.addStretch()

        self._rebuild()

    def _rebuild(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        query = self._search.text()
        tools = search_tools(self._tools, query)
        col_count = 3
        for i, tool in enumerate(tools):
            btn = QPushButton(tool.name)
            btn.setToolTip(f"{tool.description}\nCategory: {tool.category}")
            btn.clicked.connect(lambda checked=False, t=tool: self._launch(t))
            self._grid.addWidget(btn, i // col_count, i % col_count)

        if not tools:
            lbl = QLabel("No tools match your search.")
            lbl.setStyleSheet("color: #888;")
            self._grid.addWidget(lbl, 0, 0)

    def _launch(self, tool: LaunchTool) -> None:
        if tool.requires_admin and not is_admin():
            show_error(self, "Admin Required", admin_required_message(tool.name))
            return
        ok, msg = launch_tool(tool)
        if ok:
            show_info(self, "Launched", msg)
        else:
            show_error(self, "Launch Failed", msg)

    def set_search_query(self, query: str) -> None:
        self._search.setText(query)
        self._rebuild()
