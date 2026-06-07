"""Single source of truth for WinTuner versioning."""

APP_NAME = "WinTuner"
APP_VERSION = "0.1.3-alpha"
APP_STAGE = "alpha"


def display_version() -> str:
    """Return user-facing version string."""
    return APP_VERSION
