"""Tweak data model and registry value helpers."""

from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


class RiskLevel(enum.Enum):
    """Risk classification for a tweak."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class TweakState:
    """Detected current state of a tweak."""

    enabled: bool | None
    raw_value: Any = None
    description: str = ""


@dataclass
class TweakResult:
    """Outcome of applying or undoing a tweak."""

    success: bool
    message: str
    previous_value: Any = None
    new_value: Any = None


@dataclass
class Tweak:
    """A reversible Windows tweak with full metadata."""

    id: str
    title: str
    category: str
    description: str
    risk_level: RiskLevel
    requires_admin: bool
    reversible: bool
    affected_area: str
    notes: str
    why_use: str
    undo_instructions: str
    tags: list[str] = field(default_factory=list)
    requires_restart: bool = False
    requires_sign_out: bool = False
    changes_registry: bool = False
    opens_settings: bool = False
    detect_fn: Callable[[], TweakState] | None = field(default=None, repr=False)
    apply_fn: Callable[[], TweakResult] | None = field(default=None, repr=False)
    undo_fn: Callable[[Any], TweakResult] | None = field(default=None, repr=False)

    def validate(self) -> list[str]:
        """Return validation errors for required metadata fields."""
        errors: list[str] = []
        if not self.id:
            errors.append("Missing id")
        if not self.title:
            errors.append("Missing title")
        if not self.category:
            errors.append("Missing category")
        if not self.description:
            errors.append("Missing description")
        if not self.affected_area:
            errors.append("Missing affected_area")
        if not self.why_use:
            errors.append("Missing why_use")
        if not self.undo_instructions:
            errors.append("Missing undo_instructions")
        if self.risk_level not in RiskLevel:
            errors.append(f"Invalid risk_level: {self.risk_level}")
        if self.apply_fn is None:
            errors.append("Missing apply_fn")
        if self.detect_fn is None:
            errors.append("Missing detect_fn")
        if self.reversible:
            if self.undo_fn is None and not self.opens_settings:
                errors.append("Reversible tweak missing undo_fn")
        else:
            if not self.undo_instructions.strip():
                errors.append("Non-reversible tweak must document undo unavailable reason")
            if self.undo_fn is not None:
                errors.append("Non-reversible tweak should not define undo_fn")
        if self.requires_restart and "restart" not in self.undo_instructions.lower():
            errors.append("requires_restart tweak should mention restart in undo_instructions")
        if self.requires_sign_out and "sign out" not in self.undo_instructions.lower():
            errors.append("requires_sign_out tweak should mention sign out in undo_instructions")
        return errors

    def detect(self) -> TweakState:
        """Detect current tweak state."""
        if self.detect_fn is None:
            return TweakState(enabled=None, description="Detection not available.")
        try:
            return self.detect_fn()
        except OSError as exc:
            logger.error("Detect failed for %s: %s", self.id, exc)
            return TweakState(enabled=None, description=str(exc))

    def apply(self) -> TweakResult:
        """Apply the tweak."""
        if self.apply_fn is None:
            return TweakResult(False, "Apply function not defined.")
        try:
            result = self.apply_fn()
            from wintuner.app.core.app_logging import log_tweak_apply

            log_tweak_apply(self.id, result.success, result.message)
            return result
        except OSError as exc:
            logger.error("Apply failed for %s: %s", self.id, exc)
            from wintuner.app.core.app_logging import log_tweak_apply

            log_tweak_apply(self.id, False, str(exc))
            return TweakResult(False, str(exc))

    def undo(self, previous_value: Any) -> TweakResult:
        """Undo the tweak using the stored previous value."""
        if self.undo_fn is None:
            return TweakResult(False, "Undo not supported for this tweak.")
        try:
            result = self.undo_fn(previous_value)
            from wintuner.app.core.app_logging import log_tweak_undo

            log_tweak_undo(self.id, result.success, result.message)
            return result
        except OSError as exc:
            logger.error("Undo failed for %s: %s", self.id, exc)
            from wintuner.app.core.app_logging import log_tweak_undo

            log_tweak_undo(self.id, False, str(exc))
            return TweakResult(False, str(exc))


def read_registry_dword(hive: Any, subkey: str, value_name: str) -> int | None:
    """Read a DWORD registry value, returning None if missing."""
    import winreg

    try:
        with winreg.OpenKey(hive, subkey) as key:
            val, _ = winreg.QueryValueEx(key, value_name)
            return int(val)
    except OSError:
        return None


def write_registry_dword(hive: Any, subkey: str, value_name: str, value: int) -> None:
    """Write a DWORD registry value, creating the key if needed."""
    import winreg

    with winreg.CreateKey(hive, subkey) as key:
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)


def delete_registry_value(hive: Any, subkey: str, value_name: str) -> None:
    """Delete a registry value if it exists."""
    import winreg

    try:
        with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, value_name)
    except OSError:
        pass
