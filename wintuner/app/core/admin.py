"""Administrator privilege detection for WinTuner."""

from __future__ import annotations

import ctypes
import logging
import sys

logger = logging.getLogger(__name__)


def is_admin() -> bool:
    """Return True if the current process has administrator privileges."""
    if sys.platform != "win32":
        logger.warning("Admin check skipped: not running on Windows.")
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError) as exc:
        logger.error("Failed to check admin status: %s", exc)
        return False


def admin_required_message(action: str) -> str:
    """Return a user-friendly message explaining admin is needed."""
    return (
        f'"{action}" requires administrator privileges.\n\n'
        "Close WinTuner, right-click run.bat (or the app shortcut) and choose "
        '"Run as administrator", then try again.'
    )
