"""Application logging to a local file under ~/.wintuner/logs."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from wintuner.app.core.version import APP_NAME, APP_VERSION

_LOG_DIR = Path.home() / ".wintuner" / "logs"
_LOG_FILE = _LOG_DIR / "wintuner.log"
_MAX_BYTES = 512_000
_BACKUP_COUNT = 3

_configured = False


def get_log_path() -> Path:
    """Return the path to the application log file."""
    return _LOG_FILE


def setup_app_logging() -> Path:
    """Configure rotating file logging and return the log file path."""
    global _configured
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    if not _configured:
        root.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            _LOG_FILE,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        root.addHandler(handler)
        _configured = True

    logging.getLogger(__name__).info("%s %s starting", APP_NAME, APP_VERSION)
    return _LOG_FILE


def log_admin_status(is_admin: bool) -> None:
    """Log whether the process is elevated."""
    logging.getLogger(__name__).info(
        "Admin status: %s", "elevated" if is_admin else "standard user"
    )


def log_launcher_result(tool_id: str, success: bool, message: str) -> None:
    """Log a God Mode launcher attempt."""
    level = logging.INFO if success else logging.WARNING
    logging.getLogger("wintuner.launcher").log(
        level, "Launcher %s: success=%s msg=%s", tool_id, success, message
    )


def log_tweak_apply(tweak_id: str, success: bool, message: str) -> None:
    """Log a tweak apply attempt."""
    level = logging.INFO if success else logging.WARNING
    logging.getLogger("wintuner.tweak").log(
        level, "Apply %s: success=%s msg=%s", tweak_id, success, message
    )


def log_tweak_undo(tweak_id: str, success: bool, message: str) -> None:
    """Log a tweak undo attempt."""
    level = logging.INFO if success else logging.WARNING
    logging.getLogger("wintuner.tweak").log(
        level, "Undo %s: success=%s msg=%s", tweak_id, success, message
    )


def log_cleanup_preview(item_count: int, total_bytes: int, skipped: int) -> None:
    """Log temp cleanup dry-run summary (counts only, no file paths)."""
    logging.getLogger("wintuner.cleanup").info(
        "Cleanup preview: items=%d bytes=%d skipped=%d",
        item_count,
        total_bytes,
        skipped,
    )


def log_cleanup_result(deleted: int, freed_bytes: int, skipped: int) -> None:
    """Log temp cleanup execution summary."""
    logging.getLogger("wintuner.cleanup").info(
        "Cleanup result: deleted=%d freed_bytes=%d skipped=%d",
        deleted,
        freed_bytes,
        skipped,
    )
