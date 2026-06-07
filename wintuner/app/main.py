"""WinTuner application entry point."""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from wintuner.app.core.admin import is_admin
from wintuner.app.core.app_logging import log_admin_status, setup_app_logging
from wintuner.app.core.tweak_registry import load_all_tweaks
from wintuner.app.core.version import APP_NAME, APP_VERSION
from wintuner.app.ui.main_window import MainWindow
from wintuner.app.ui.style import DARK_STYLE

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    """Configure console and file logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log_path = setup_app_logging()
    logger.info("Log file: %s", log_path)
    log_admin_status(is_admin())


def main() -> int:
    setup_logging()
    logger.info("Starting %s %s", APP_NAME, APP_VERSION)
    load_all_tweaks()

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(DARK_STYLE)

    window = MainWindow()
    window.show()
    logger.info("Main window shown")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
