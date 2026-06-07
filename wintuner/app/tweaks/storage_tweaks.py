"""Storage-related tweaks and actions."""

from __future__ import annotations

import logging
import os
import subprocess

from wintuner.app.core.tweak_model import RiskLevel, Tweak, TweakResult, TweakState
from wintuner.app.core.tweak_registry import register_tweak
from wintuner.app.core.temp_cleanup import execute_cleanup, preview_cleanup

logger = logging.getLogger(__name__)


def _detect_temp_cleanup() -> TweakState:
    preview = preview_cleanup()
    return TweakState(
        enabled=None,
        raw_value=preview.total_bytes,
        description=f"{preview.file_count} items, {preview.total_mb} MB in user temp folders",
    )


def _apply_temp_cleanup() -> TweakResult:
    preview = preview_cleanup(force_refresh=True)
    if preview.file_count == 0:
        return TweakResult(True, "No temp files found to clean.", previous_value=0, new_value=0)
    result = execute_cleanup(preview)
    msg = (
        f"Deleted {result.deleted_count} items, freed "
        f"{round(result.freed_bytes / (1024 * 1024), 2)} MB."
    )
    if result.skipped_locked or result.skipped_unsafe:
        skipped = result.skipped_count
        msg += f" Skipped {skipped} locked or unsafe items."
    return TweakResult(
        True,
        msg,
        previous_value=preview.total_bytes,
        new_value=result.freed_bytes,
    )




def _apply_empty_recycle_bin() -> TweakResult:
    try:
        from ctypes import windll, wintypes

        result = windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000001 | 0x00000002)
        if result == 0:
            return TweakResult(True, "Recycle Bin emptied.", previous_value="full", new_value="empty")
        return TweakResult(False, f"Recycle Bin empty returned code {result}.")
    except OSError as exc:
        return TweakResult(False, str(exc))


def _detect_recycle_bin() -> TweakState:
    return TweakState(enabled=None, description="Use Apply to empty the Recycle Bin")




def _apply_open_storage_sense() -> TweakResult:
    try:
        os.startfile("ms-settings:storagesense")
        return TweakResult(True, "Opened Storage Sense settings.", previous_value=None, new_value=None)
    except OSError as exc:
        return TweakResult(False, str(exc))


def _detect_open_storage_sense() -> TweakState:
    return TweakState(enabled=None, description="Opens Windows Storage Sense settings")


def _undo_open_storage_sense(_prev: object) -> TweakResult:
    return TweakResult(True, "No change to undo (launcher only).")


def register() -> None:
    """Register storage tweaks."""
    register_tweak(
        Tweak(
            id="storage_clear_user_temp",
            title="Clear User Temp Files",
            category="Storage",
            description="Remove files from your user TEMP folder (safe locations only).",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=False,
            affected_area="User temp directories",
            notes="Skips locked files. Preview shown before apply in Optimizer.",
            why_use="Free disk space from leftover installer and app temp files.",
            undo_instructions="Not reversible — deleted temp files cannot be recovered.",
            tags=["Safe"],
            detect_fn=_detect_temp_cleanup,
            apply_fn=_apply_temp_cleanup,
        )
    )
    register_tweak(
        Tweak(
            id="storage_empty_recycle_bin",
            title="Empty Recycle Bin",
            category="Storage",
            description="Permanently remove all items currently in the Recycle Bin.",
            risk_level=RiskLevel.MEDIUM,
            requires_admin=False,
            reversible=False,
            affected_area="Recycle Bin",
            notes="Requires confirmation before applying.",
            why_use="Recover disk space from deleted files.",
            undo_instructions="Not reversible — use file recovery tools if needed.",
            tags=["Needs confirmation"],
            detect_fn=_detect_recycle_bin,
            apply_fn=_apply_empty_recycle_bin,
        )
    )
    register_tweak(
        Tweak(
            id="storage_open_storage_sense",
            title="Open Storage Sense Settings",
            category="Storage",
            description="Launch Windows Storage Sense to configure automatic cleanup.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="Windows Settings launcher",
            notes="Opens Settings only — does not change anything.",
            why_use="Configure automatic temp file cleanup by Windows.",
            undo_instructions="No change to undo.",
            tags=["Opens Windows Settings", "Safe"],
            opens_settings=True,
            detect_fn=_detect_open_storage_sense,
            apply_fn=_apply_open_storage_sense,
            undo_fn=_undo_open_storage_sense,
        )
    )
