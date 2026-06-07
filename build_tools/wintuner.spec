# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for WinTuner onedir Windows build."""

import sys
from pathlib import Path

block_cipher = None

PROJECT_ROOT = Path(SPECPATH).resolve().parent
APP_ROOT = PROJECT_ROOT / "wintuner" / "app"

datas = [
    (str(APP_ROOT / "data" / "god_mode_tools.json"), "data"),
    (str(APP_ROOT / "data" / "profiles.json"), "data"),
]

hiddenimports = [
    "wintuner.app.core.admin",
    "wintuner.app.core.app_logging",
    "wintuner.app.core.change_log",
    "wintuner.app.core.launcher",
    "wintuner.app.core.profiles",
    "wintuner.app.core.resource_paths",
    "wintuner.app.core.restore_point",
    "wintuner.app.core.search_service",
    "wintuner.app.core.system_info",
    "wintuner.app.core.temp_cleanup",
    "wintuner.app.core.tweak_model",
    "wintuner.app.core.tweak_registry",
    "wintuner.app.core.version",
    "wintuner.app.tweaks.explorer_tweaks",
    "wintuner.app.tweaks.performance_tweaks",
    "wintuner.app.tweaks.privacy_tweaks",
    "wintuner.app.tweaks.storage_tweaks",
    "wintuner.app.ui.dashboard_page",
    "wintuner.app.ui.dialogs",
    "wintuner.app.ui.god_mode_page",
    "wintuner.app.ui.main_window",
    "wintuner.app.ui.optimizer_page",
    "wintuner.app.ui.search_results_page",
    "wintuner.app.ui.settings_page",
    "wintuner.app.ui.tweak_actions",
    "wintuner.app.ui.style",
    "wintuner.app.ui.tweaks_page",
    "wintuner.app.ui.undo_page",
]

a = Analysis(
    [str(APP_ROOT / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="WinTuner",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Future: add uac_admin manifest here for optional elevated default launch.
    # v0.1.1 intentionally runs as invoker — no forced elevation.
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="WinTuner",
)
