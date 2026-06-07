"""System information gathering for the WinTuner dashboard."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any

from wintuner.app.core.admin import is_admin

logger = logging.getLogger(__name__)


@dataclass
class SystemSummary:
    """Snapshot of key system facts shown on the dashboard."""

    windows_version: str = "Unknown"
    build_number: str = "Unknown"
    edition: str = "Unknown"
    disk_free_gb: float = 0.0
    disk_total_gb: float = 0.0
    disk_drive: str = "C:"
    startup_app_count: int = 0
    restore_point_available: bool | None = None
    is_admin: bool = False
    machine_name: str = "Unknown"
    processor: str = "Unknown"
    ram_gb: float = 0.0


def _run_wmic(args: list[str]) -> str:
    """Run a WMIC query and return stripped stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            ["wmic", *args],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError) as exc:
        logger.debug("WMIC query failed (%s): %s", args, exc)
    return ""


def _get_windows_info() -> dict[str, str]:
    """Collect Windows version details via platform and WMIC."""
    info: dict[str, str] = {
        "version": platform.version(),
        "edition": "Windows",
        "build": platform.release(),
    }
    caption = _run_wmic(["os", "get", "Caption", "/value"])
    build = _run_wmic(["os", "get", "BuildNumber", "/value"])
    for line in caption.splitlines():
        if line.startswith("Caption="):
            info["edition"] = line.split("=", 1)[1].strip()
    for line in build.splitlines():
        if line.startswith("BuildNumber="):
            info["build"] = line.split("=", 1)[1].strip()
    return info


def _get_disk_space(drive: str = "C:\\") -> tuple[float, float]:
    """Return (free_gb, total_gb) for the given drive."""
    try:
        usage = shutil.disk_usage(drive)
        return round(usage.free / (1024**3), 1), round(usage.total / (1024**3), 1)
    except OSError as exc:
        logger.warning("Could not read disk usage for %s: %s", drive, exc)
        return 0.0, 0.0


def _count_startup_apps() -> int:
    """Estimate startup app count from common registry Run keys."""
    count = 0
    try:
        import winreg

        paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]
        for hive, subkey in paths:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    count += winreg.QueryInfoKey(key)[1]
            except OSError:
                pass
    except ImportError:
        logger.debug("winreg not available for startup count.")
    return count


def _check_restore_points() -> bool | None:
    """Return True if system restore appears enabled, None if undetectable."""
    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-ComputerRestorePoint -ErrorAction SilentlyContinue | Measure-Object).Count -ge 0",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if result.returncode == 0:
            return True
    except (subprocess.SubprocessError, FileNotFoundError, OSError) as exc:
        logger.debug("Restore point check failed: %s", exc)
    return None


def _get_ram_gb() -> float:
    """Return total physical RAM in GB."""
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return round(stat.ullTotalPhys / (1024**3), 1)
    except (AttributeError, OSError) as exc:
        logger.debug("RAM detection failed: %s", exc)
    return 0.0


def get_system_summary() -> SystemSummary:
    """Build a SystemSummary for the dashboard."""
    win_info = _get_windows_info()
    free_gb, total_gb = _get_disk_space()
    return SystemSummary(
        windows_version=win_info.get("version", "Unknown"),
        build_number=win_info.get("build", "Unknown"),
        edition=win_info.get("edition", "Unknown"),
        disk_free_gb=free_gb,
        disk_total_gb=total_gb,
        startup_app_count=_count_startup_apps(),
        restore_point_available=_check_restore_points(),
        is_admin=is_admin(),
        machine_name=platform.node(),
        processor=platform.processor() or "Unknown",
        ram_gb=_get_ram_gb(),
    )
