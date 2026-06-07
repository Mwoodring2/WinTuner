"""Explorer-related tweaks."""

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

_EXPLORER_ADVANCED = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
_EXPLORER_POLICY = (
    r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
)


def _detect_show_extensions() -> TweakState:
    val = read_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "HideFileExt")
    if val is None:
        return TweakState(enabled=None, raw_value=None, description="Default (hidden)")
    enabled = val == 0
    return TweakState(enabled=enabled, raw_value=val, description="Shown" if enabled else "Hidden")


def _apply_show_extensions() -> TweakResult:
    prev = read_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "HideFileExt")
    write_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "HideFileExt", 0)
    return TweakResult(True, "File extensions are now visible.", previous_value=prev, new_value=0)


def _undo_show_extensions(prev: object) -> TweakResult:
    if prev is None:
        delete_registry_value(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "HideFileExt")
    else:
        write_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "HideFileExt", int(prev))
    return TweakResult(True, "File extension visibility restored.", previous_value=0, new_value=prev)


def _detect_show_hidden() -> TweakState:
    val = read_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "Hidden")
    if val is None:
        return TweakState(enabled=None, raw_value=None)
    enabled = val == 1
    return TweakState(enabled=enabled, raw_value=val)


def _apply_show_hidden() -> TweakResult:
    prev = read_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "Hidden")
    write_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "Hidden", 1)
    write_registry_dword(
        winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "ShowSuperHidden", 0
    )
    return TweakResult(True, "Hidden files are now visible.", previous_value=prev, new_value=1)


def _undo_show_hidden(prev: object) -> TweakResult:
    if prev is None:
        delete_registry_value(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "Hidden")
    else:
        write_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "Hidden", int(prev))
    return TweakResult(True, "Hidden file visibility restored.", previous_value=1, new_value=prev)


def _detect_launch_to_this_pc() -> TweakState:
    val = read_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "LaunchTo")
    enabled = val == 1
    return TweakState(
        enabled=enabled,
        raw_value=val,
        description="This PC" if enabled else "Quick access (default)",
    )


def _apply_launch_to_this_pc() -> TweakResult:
    prev = read_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "LaunchTo")
    write_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "LaunchTo", 1)
    return TweakResult(
        True,
        "File Explorer will open to This PC.",
        previous_value=prev,
        new_value=1,
    )


def _undo_launch_to_this_pc(prev: object) -> TweakResult:
    if prev is None:
        delete_registry_value(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "LaunchTo")
    else:
        write_registry_dword(winreg.HKEY_CURRENT_USER, _EXPLORER_ADVANCED, "LaunchTo", int(prev))
    return TweakResult(True, "File Explorer launch location restored.", previous_value=1, new_value=prev)


def _detect_compact_menu() -> TweakState:
    val = read_registry_dword(
        winreg.HKEY_CURRENT_USER,
        r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32",
        "",
    )
    # Classic menu is enabled when the key exists with empty default value
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32",
        ) as key:
            val_str, _ = winreg.QueryValueEx(key, "")
            enabled = val_str == ""
    except OSError:
        enabled = False
        val_str = None
    return TweakState(enabled=enabled, raw_value=val_str, description="Classic" if enabled else "Modern")


def _apply_compact_menu() -> TweakResult:
    subkey = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
    prev_exists = _detect_compact_menu().enabled
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
    return TweakResult(
        True,
        "Classic compact right-click menu enabled. Sign out and back in to see the change.",
        previous_value=prev_exists,
        new_value=True,
    )


def _undo_compact_menu(prev: object) -> TweakResult:
    subkey = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
    try:
        winreg.DeleteKey(
            winreg.HKEY_CURRENT_USER,
            subkey + r"\InprocServer32",
        )
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, subkey)
    except OSError as exc:
        return TweakResult(False, f"Could not remove classic menu key: {exc}")
    return TweakResult(
        True,
        "Modern right-click menu restored. Sign out and back in to see the change.",
        previous_value=True,
        new_value=False,
    )


def register() -> None:
    """Register all Explorer tweaks."""
    register_tweak(
        Tweak(
            id="explorer_show_extensions",
            title="Show File Extensions",
            category="Explorer",
            description="Display file extensions like .txt and .pdf in File Explorer.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="File Explorer appearance",
            notes="Changes a single HKCU registry value.",
            why_use="Helps identify file types and avoid opening the wrong file.",
            undo_instructions="WinTuner Undo Center, or Folder Options → View → uncheck 'Hide extensions'.",
            tags=["Safe", "Changes Registry"],
            changes_registry=True,
            detect_fn=_detect_show_extensions,
            apply_fn=_apply_show_extensions,
            undo_fn=_undo_show_extensions,
        )
    )
    register_tweak(
        Tweak(
            id="explorer_show_hidden",
            title="Show Hidden Files",
            category="Explorer",
            description="Reveal hidden files and folders in File Explorer.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="File Explorer visibility",
            notes="Does not enable protected operating system files.",
            why_use="Access config files or troubleshoot missing items.",
            undo_instructions="WinTuner Undo Center, or Folder Options → View → select 'Don't show hidden files'.",
            tags=["Safe", "Changes Registry"],
            changes_registry=True,
            detect_fn=_detect_show_hidden,
            apply_fn=_apply_show_hidden,
            undo_fn=_undo_show_hidden,
        )
    )
    register_tweak(
        Tweak(
            id="explorer_launch_this_pc",
            title="Open File Explorer to This PC",
            category="Explorer",
            description="Set File Explorer to open on This PC instead of Quick access.",
            risk_level=RiskLevel.LOW,
            requires_admin=False,
            reversible=True,
            affected_area="File Explorer default page",
            notes="Requires restarting Explorer or opening a new window.",
            why_use="Prefer the traditional drives and folders view.",
            undo_instructions="WinTuner Undo Center, or Explorer Options → General → Open File Explorer to Quick access.",
            tags=["Safe", "Changes Registry"],
            changes_registry=True,
            detect_fn=_detect_launch_to_this_pc,
            apply_fn=_apply_launch_to_this_pc,
            undo_fn=_undo_launch_to_this_pc,
        )
    )
    register_tweak(
        Tweak(
            id="explorer_classic_context_menu",
            title="Enable Classic Right-Click Menu",
            category="Explorer",
            description="Restore the compact Windows 10-style right-click menu on Windows 11.",
            risk_level=RiskLevel.MEDIUM,
            requires_admin=False,
            reversible=True,
            affected_area="File Explorer context menu",
            notes="Requires sign out/in. Some modern menu items will be hidden.",
            why_use="Prefer the shorter, faster classic menu.",
            undo_instructions="WinTuner Undo Center removes the registry key. Sign out and back in.",
            tags=["Changes Registry", "Requires Sign Out"],
            changes_registry=True,
            requires_sign_out=True,
            detect_fn=_detect_compact_menu,
            apply_fn=_apply_compact_menu,
            undo_fn=_undo_compact_menu,
        )
    )
