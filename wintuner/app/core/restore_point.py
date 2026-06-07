"""System Restore / restore-point helper – opens settings, no fake creation."""

from __future__ import annotations

import logging
import subprocess

logger = logging.getLogger(__name__)


def open_system_protection() -> tuple[bool, str]:
    """Open Windows System Protection settings for manual restore point creation."""
    try:
        subprocess.Popen(
            ["SystemPropertiesProtection.exe"],
            shell=False,
        )
        return True, (
            "Opened System Protection settings.\n\n"
            "Select your system drive, click Create, and follow the prompts "
            "to make a restore point before applying medium or high risk changes."
        )
    except OSError as exc:
        msg = f"Could not open System Protection: {exc}"
        logger.error(msg)
        return False, msg


def open_system_restore() -> tuple[bool, str]:
    """Open the System Restore wizard."""
    try:
        subprocess.Popen(["rstrui.exe"], shell=False)
        return True, "Opened System Restore."
    except OSError as exc:
        msg = f"Could not open System Restore: {exc}"
        logger.error(msg)
        return False, msg
