"""Main application window with sidebar navigation."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.version import APP_NAME, display_version
from wintuner.app.core.admin import is_admin
from wintuner.app.core.change_log import ChangeLog
from wintuner.app.ui.dashboard_page import DashboardPage
from wintuner.app.ui.god_mode_page import GodModePage
from wintuner.app.ui.optimizer_page import OptimizerPage
from wintuner.app.ui.search_results_page import SearchResultsPage
from wintuner.app.ui.settings_page import AboutPage, SettingsPage
from wintuner.app.ui.tweaks_page import TweaksPage
from wintuner.app.ui.undo_page import UndoPage


class MainWindow(QMainWindow):
    """WinTuner main window."""

    NAV_ITEMS = [
        ("dashboard", "Dashboard"),
        ("search", "Search"),
        ("godmode", "God Mode"),
        ("optimizer", "Optimizer"),
        ("tweaks", "Tweaks"),
        ("undo", "Undo Center"),
        ("settings", "Settings"),
        ("about", "About"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {display_version()}")
        self.setMinimumSize(960, 640)
        self.resize(1100, 720)

        self._change_log = ChangeLog()
        self._nav_buttons: dict[str, QPushButton] = {}

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content_widget = QWidget()
        content_widget.setLayout(content)
        root.addWidget(content_widget, stretch=1)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(16, 10, 16, 6)
        self._global_search = QLineEdit()
        self._global_search.setObjectName("searchBar")
        self._global_search.setPlaceholderText("Search tools and tweaks…")
        self._global_search.returnPressed.connect(self._on_global_search)
        self._global_search.textChanged.connect(self._on_search_text_changed)
        top_bar.addWidget(self._global_search)
        content.addLayout(top_bar)

        self._stack = QStackedWidget()
        self._pages: dict[str, QWidget] = {}
        self._dashboard = DashboardPage(self._change_log)
        self._search = SearchResultsPage(self._change_log)
        self._godmode = GodModePage()
        self._optimizer = OptimizerPage(self._change_log)
        self._tweaks = TweaksPage(self._change_log)
        self._undo = UndoPage(self._change_log)
        self._settings = SettingsPage(self._change_log)
        self._about = AboutPage()

        page_map = {
            "dashboard": self._dashboard,
            "search": self._search,
            "godmode": self._godmode,
            "optimizer": self._optimizer,
            "tweaks": self._tweaks,
            "undo": self._undo,
            "settings": self._settings,
            "about": self._about,
        }
        for key, page in page_map.items():
            self._pages[key] = page
            self._stack.addWidget(page)
        content.addWidget(self._stack, stretch=1)

        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._update_status()

        self._navigate("dashboard")

    def _build_sidebar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("sidebar")
        frame.setFixedWidth(200)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(4)

        logo = QLabel(APP_NAME)
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff; padding: 8px;")
        layout.addWidget(logo)

        for key, label in self.NAV_ITEMS:
            btn = QPushButton(label)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked=False, k=key: self._navigate(k))
            self._nav_buttons[key] = btn
            layout.addWidget(btn)
        layout.addStretch()
        return frame

    def _navigate(self, key: str) -> None:
        page = self._pages.get(key)
        if page is None:
            return
        self._stack.setCurrentWidget(page)
        for k, btn in self._nav_buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._update_status()

    def _on_global_search(self) -> None:
        query = self._global_search.text().strip()
        if not query:
            return
        self._navigate("search")
        self._search.run_search(query)

    def _on_search_text_changed(self, text: str) -> None:
        if not text.strip():
            if self._stack.currentWidget() is self._search:
                self._search.run_search("")
            return
        if len(text.strip()) >= 2:
            self._navigate("search")
            self._search.run_search(text)

    def _update_status(self) -> None:
        admin_txt = "Administrator" if is_admin() else "Standard user"
        self._status.showMessage(
            f"{APP_NAME} {display_version()}  |  {admin_txt}  |  Local-only, no telemetry"
        )
