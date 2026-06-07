"""Resolve bundled data file paths for dev and PyInstaller packaged runs."""

from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
    """Return True when running from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def get_bundle_root() -> Path | None:
    """Return PyInstaller extraction root (sys._MEIPASS), or None when running from source."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return None


def resource_path(relative: str) -> Path:
    """Resolve a path relative to the app package or PyInstaller bundle root."""
    rel = Path(relative)
    bundle = get_bundle_root()
    if bundle is not None:
        candidate = bundle / rel
        if candidate.exists():
            return candidate
    # Development: paths relative to wintuner/app/
    app_root = Path(__file__).resolve().parents[1]
    return app_root / rel


def get_data_file(name: str) -> Path:
    """Return path to a JSON data file bundled under wintuner/app/data/."""
    return resource_path(Path("data") / name)
