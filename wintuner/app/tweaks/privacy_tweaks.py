"""Privacy-related tweaks (lite, non-destructive)."""

from __future__ import annotations

import winreg

from wintuner.app.core.tweak_model import (
    RiskLevel,
    Tweak,
    TweakResult,
    TweakState,
    delete_registry_value,
    read_registry_dword,
    write_registry_dword,
)
from wintuner.app.core.tweak_registry import register_tweak

_CONTENT_DELIVERY = r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
_PRIVACY = r"Software\Microsoft\Windows\CurrentVersion\Privacy"
_EXPLORER_ADVANCED = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"


def _detect_tips() -> TweakState:
    val = read_registry_dword(winreg.HKEY_CURRENT_USER, _CONTENT_DELIVERY, "SubscribedContent-338389Enabled")
    enabled = val == 0 if val is not None else None
    if val is None:
        return TweakState(enabled=None, raw_value=None, description="Default")
    return TweakState(enabled=enabled, raw_value=val, description="Disabled" if enabled else "Enabled")


def _apply_disable_tips() -> TweakResult:
    prev = read_registry_dword(
        winreg.HKEY_CURRENT_USER, _CONTENT_DELIVERY, "SubscribedContent-338389Enabled"
    )
    write_registry_dword(
        winreg.HKEY_CURRENT_USER, _CONTENT_DELIVERY, "SubscribedContent-338389Enabled", 0
    )
    write_registry_dword(
        winreg.HKEY_CURRENT_USER, _CONTENT_DELIVERY, "SubscribedContent-310093Enabled", 0
    )
    return TweakResult(True, "Windows tips and suggestions disabled.", previous_value=prev, new_value=0)


def _undo_disable_tips(prev: object) -> TweakResult:
    if prev is None:
        delete_registry_value(
            winreg.HKEY_CURRENT_USER, _CONTENT_DELIVERY, "SubscribedContent-338389Enabled"
        )
    else:
        write_registry_dword(
            winreg.HKEY_CURRENT_USER, _CONTENT_DELIVERY, "SubscribedContent-338389Enabled", int(prev)
        )
    return TweakResult(True, "Windows tips setting restored.", previous_value=0, new_value=prev)


def _detect_suggestions() -> TweakState:
    val = read_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "ShowSyncProviderNotifications")
    if val is None:
        return TweakState(enabled=None, raw_value=None)
    enabled = val == 0
    return TweakState(enabled=enabled, raw_value=val)


def _apply_disable_suggestions() -> TweakResult:
    prev = read_registry_dword(
        winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "ShowSyncProviderNotifications"
    )
    write_registry_dword(
        winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "ShowSyncProviderNotifications", 0
    )
    return TweakResult(
        True, "Sync provider notifications disabled.", previous_value=prev, new_value=0
    )


def _undo_disable_suggestions(prev: object) -> TweakResult:
    if prev is None:
        delete_registry_value(
            winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "ShowSyncProviderNotifications"
        )
    else:
        write_registry_dword(
            winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "ShowSyncProviderNotifications", int(prev)
        )
    return TweakResult(True, "Sync provider notifications restored.", previous_value=0, new_value=prev)


def register() -> None:
    """Register privacy tweaks."""
    register_tweak(
        Tweak(
            id="privacy_disable_tips",
            title="Disable Windows Tips & Suggestions",
            category="Privacy Lite",
            description="Reduce tips, tricks, and suggestion pop-ups from Windows.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="Windows notifications and content delivery",
            notes="Uses documented ContentDeliveryManager keys.",
            why_use="Fewer distractions while working.",
            undo_instructions="WinTuner Undo Center restores previous registry values.",
            tags=["Safe", "Changes Registry"],
            changes_registry=True,
            detect_fn=_detect_tips,
            apply_fn=_apply_disable_tips,
            undo_fn=_undo_disable_tips,
        )
    )
    register_tweak(
        Tweak(
            id="privacy_disable_sync_notifications",
            title="Disable Sync Provider Notifications",
            category="Privacy Lite",
            description="Stop File Explorer notifications about cloud sync providers.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="File Explorer notifications",
            notes="Does not disable cloud sync itself.",
            why_use="Cleaner File Explorer without OneDrive-style prompts.",
            undo_instructions="WinTuner Undo Center restores the previous value.",
            tags=["Safe", "Changes Registry"],
            changes_registry=True,
            detect_fn=_detect_suggestions,
            apply_fn=_apply_disable_suggestions,
            undo_fn=_undo_disable_suggestions,
        )
    )
