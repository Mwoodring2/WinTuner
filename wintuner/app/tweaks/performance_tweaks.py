"""Performance and power related tweaks."""

from __future__ import annotations

import logging
import os
import subprocess

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

logger = logging.getLogger(__name__)

_PERSONALIZE = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"


def _detect_transparency() -> TweakState:
    val = read_registry_dword(winreg.HKEY_CURRENT_USER, _PERSONALIZE, "EnableTransparency")
    if val is None:
        return TweakState(enabled=None, raw_value=None)
    enabled = val == 0
    return TweakState(
        enabled=enabled,
        raw_value=val,
        description="Transparency off" if enabled else "Transparency on",
    )


def _apply_disable_transparency() -> TweakResult:
    prev = read_registry_dword(winreg.HKEY_CURRENT_USER, _PERSONALIZE, "EnableTransparency")
    write_registry_dword(winreg.HKEY_CURRENT_USER, _PERSONALIZE, "EnableTransparency", 0)
    return TweakResult(
        True,
        "Transparency effects disabled.",
        previous_value=prev,
        new_value=0,
    )


def _undo_disable_transparency(prev: object) -> TweakResult:
    if prev is None:
        delete_registry_value(winreg.HKEY_CURRENT_USER, _PERSONALIZE, "EnableTransparency")
    else:
        write_registry_dword(
            winreg.HKEY_CURRENT_USER, _PERSONALIZE, "EnableTransparency", int(prev)
        )
    return TweakResult(True, "Transparency setting restored.", previous_value=0, new_value=prev)


def _apply_open_startup_apps() -> TweakResult:
    try:
        os.startfile("ms-settings:startupapps")
        return TweakResult(True, "Opened Startup Apps settings.", previous_value=None, new_value=None)
    except OSError as exc:
        return TweakResult(False, str(exc))


def _detect_startup_apps() -> TweakState:
    return TweakState(enabled=None, description="Opens Windows Startup Apps settings")


def _undo_startup_apps(_prev: object) -> TweakResult:
    return TweakResult(True, "No change to undo (launcher only).")


def _apply_open_background_apps() -> TweakResult:
    try:
        os.startfile("ms-settings:privacy-backgroundapps")
        return TweakResult(
            True, "Opened Background Apps settings.", previous_value=None, new_value=None
        )
    except OSError as exc:
        return TweakResult(False, str(exc))


def _detect_background_apps() -> TweakState:
    return TweakState(enabled=None, description="Opens Background Apps privacy settings")


def _undo_background_apps(_prev: object) -> TweakResult:
    return TweakResult(True, "No change to undo (launcher only).")


def _apply_open_power_options() -> TweakResult:
    try:
        subprocess.Popen(["powercfg.cpl"], shell=False)
        return TweakResult(True, "Opened Power Options.", previous_value=None, new_value=None)
    except OSError as exc:
        return TweakResult(False, str(exc))


def _detect_power_options() -> TweakState:
    return TweakState(enabled=None, description="Opens Power Options control panel")


def _undo_power_options(_prev: object) -> TweakResult:
    return TweakResult(True, "No change to undo (launcher only).")


def register() -> None:
    """Register performance tweaks."""
    register_tweak(
        Tweak(
            id="performance_disable_transparency",
            title="Disable Transparency Effects",
            category="Performance",
            description="Turn off window and taskbar transparency for a small GPU/CPU savings.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="Windows visual effects",
            notes="Uses the official Personalize registry setting.",
            why_use="Slightly reduce GPU work on low-end hardware.",
            undo_instructions="WinTuner Undo Center, or Settings → Personalization → Colors.",
            tags=["Safe", "Changes Registry"],
            changes_registry=True,
            detect_fn=_detect_transparency,
            apply_fn=_apply_disable_transparency,
            undo_fn=_undo_disable_transparency,
        )
    )
    register_tweak(
        Tweak(
            id="startup_open_settings",
            title="Open Startup Apps Settings",
            category="Startup",
            description="Launch Windows Startup Apps so you can disable unwanted launchers.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="Windows Settings launcher",
            notes="Does not disable any apps directly — you choose in Settings.",
            why_use="Reduce boot time by turning off unnecessary startup apps.",
            undo_instructions="No change to undo.",
            tags=["Opens Windows Settings", "Safe"],
            opens_settings=True,
            detect_fn=_detect_startup_apps,
            apply_fn=_apply_open_startup_apps,
            undo_fn=_undo_startup_apps,
        )
    )
    register_tweak(
        Tweak(
            id="background_open_settings",
            title="Open Background Apps Settings",
            category="Background Apps",
            description="Launch Background Apps privacy settings to limit app background activity.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="Windows Settings launcher",
            notes="Opens Settings only.",
            why_use="Save battery and bandwidth by limiting background apps.",
            undo_instructions="No change to undo.",
            tags=["Opens Windows Settings", "Safe"],
            opens_settings=True,
            detect_fn=_detect_background_apps,
            apply_fn=_apply_open_background_apps,
            undo_fn=_undo_background_apps,
        )
    )
    register_tweak(
        Tweak(
            id="power_open_options",
            title="Open Power Options",
            category="Power",
            description="Launch Power Options so you can switch power plans manually.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="Control Panel launcher",
            notes="Does not force a power plan change.",
            why_use="Switch to High performance or Balanced as needed.",
            undo_instructions="No change to undo.",
            tags=["Opens Windows Settings", "Safe"],
            opens_settings=True,
            detect_fn=_detect_power_options,
            apply_fn=_apply_open_power_options,
            undo_fn=_undo_power_options,
        )
    )
