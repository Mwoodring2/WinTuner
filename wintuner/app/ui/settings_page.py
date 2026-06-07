"""Settings and About pages."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from wintuner.app.core.app_logging import get_log_path
from wintuner.app.core.change_log import ChangeLog
from wintuner.app.core.restore_point import open_system_protection, open_system_restore
from wintuner.app.core.version import APP_NAME, APP_STAGE, display_version
from wintuner.app.ui.dialogs import show_info


class SettingsPage(QWidget):
    """App settings and restore point helpers."""

    def __init__(self, change_log: ChangeLog, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._change_log = change_log
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        layout.addWidget(QLabel(f"Version: {display_version()} ({APP_STAGE})"))
        layout.addWidget(QLabel(f"Change log:\n{change_log.path}"))
        layout.addWidget(QLabel(f"Application log:\n{get_log_path()}"))

        prot_btn = QPushButton("Open System Protection (Create Restore Point)")
        prot_btn.clicked.connect(self._open_protection)
        layout.addWidget(prot_btn)

        restore_btn = QPushButton("Open System Restore")
        restore_btn.clicked.connect(self._open_restore)
        layout.addWidget(restore_btn)

        layout.addStretch()

    def _open_protection(self) -> None:
        ok, msg = open_system_protection()
        show_info(self, "System Protection", msg)

    def _open_restore(self) -> None:
        ok, msg = open_system_restore()
        show_info(self, "System Restore", msg)


class AboutPage(QWidget):
    """About WinTuner."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"About {APP_NAME}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        layout.addWidget(title)

        body = QLabel(
            f"<b>{APP_NAME} {display_version()}</b> ({APP_STAGE})<br><br>"
            "A local-first Windows utility for safely finding settings, "
            "launching tools, and applying reversible tweaks.<br><br>"
            "<b>What we do:</b> Launch Windows tools, apply documented reversible tweaks, "
            "clean user temp files with preview, and log every change.<br><br>"
            "<b>What we do NOT do:</b> Registry cleaners, fake speed boosts, "
            "disable Defender/Firewall/UAC/Windows Update, kill services, "
            "debloat scripts, cloud sync, telemetry, or ads.<br><br>"
            "All changes are logged locally. No account required."
        )
        body.setWordWrap(True)
        body.setOpenExternalLinks(True)
        layout.addWidget(body)
        layout.addStretch()
