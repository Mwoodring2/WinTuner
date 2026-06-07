"""WinTuner dashboard page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from wintuner.app.core.change_log import ChangeLog
from wintuner.app.core.system_info import SystemSummary, get_system_summary


class StatCard(QFrame):
    """Small info card for dashboard metrics."""

    def __init__(self, title: str, value: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("class", "card")
        self.setStyleSheet(
            "StatCard { background-color: #2d2d2d; border: 1px solid #3c3c3c; "
            "border-radius: 6px; padding: 8px; }"
        )
        layout = QVBoxLayout(self)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #888; font-size: 11px;")
        self._value_lbl = QLabel(value)
        self._value_lbl.setStyleSheet("color: #fff; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_lbl)
        layout.addWidget(self._value_lbl)

    def set_value(self, value: str) -> None:
        self._value_lbl.setText(value)


class DashboardPage(QWidget):
    """System summary and recent changes."""

    def __init__(self, change_log: ChangeLog, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._change_log = change_log
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Dashboard")
        title.setProperty("class", "title")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        self._admin_warning = QLabel()
        self._admin_warning.setWordWrap(True)
        self._admin_warning.setStyleSheet(
            "color: #cca700; background: #3a3a00; border: 1px solid #665500; "
            "border-radius: 4px; padding: 10px;"
        )
        layout.addWidget(self._admin_warning)

        grid = QGridLayout()
        grid.setSpacing(10)
        self._cards: dict[str, StatCard] = {}
        card_defs = [
            ("windows", "Windows"),
            ("disk", "Disk Free"),
            ("startup", "Startup Apps"),
            ("restore", "Restore Points"),
            ("admin", "Admin Status"),
            ("ram", "RAM"),
        ]
        for i, (key, label) in enumerate(card_defs):
            card = StatCard(label, "—")
            self._cards[key] = card
            grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(grid)

        recent_title = QLabel("Recent Changes by WinTuner")
        recent_title.setStyleSheet("font-weight: bold; margin-top: 8px;")
        layout.addWidget(recent_title)

        self._recent_lbl = QLabel("No changes yet.")
        self._recent_lbl.setWordWrap(True)
        self._recent_lbl.setStyleSheet("color: #aaa;")
        layout.addWidget(self._recent_lbl)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()

    def refresh(self) -> None:
        summary = get_system_summary()
        self._update_summary(summary)
        self._update_recent()

    def _update_summary(self, s: SystemSummary) -> None:
        if s.is_admin:
            self._admin_warning.hide()
        else:
            self._admin_warning.setText(
                "⚠ Running without administrator rights. Some tools and tweaks will be "
                "limited. Restart WinTuner as administrator for full access."
            )
            self._admin_warning.show()

        self._cards["windows"].set_value(f"{s.edition}\nBuild {s.build_number}")
        self._cards["disk"].set_value(f"{s.disk_free_gb} GB free / {s.disk_total_gb} GB")
        self._cards["startup"].set_value(str(s.startup_app_count))
        if s.restore_point_available is None:
            restore_txt = "Unknown"
        elif s.restore_point_available:
            restore_txt = "Available"
        else:
            restore_txt = "Not detected"
        self._cards["restore"].set_value(restore_txt)
        self._cards["admin"].set_value("Yes" if s.is_admin else "No")
        self._cards["ram"].set_value(f"{s.ram_gb} GB")

    def _update_recent(self) -> None:
        recent = self._change_log.get_recent(5)
        if not recent:
            self._recent_lbl.setText("No changes yet.")
            return
        lines = []
        for r in recent:
            status = "✓" if r.success else "✗"
            ts = r.timestamp[:19].replace("T", " ")
            lines.append(f"{status} {ts} — {r.tweak_title}")
        self._recent_lbl.setText("\n".join(lines))

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.refresh()
