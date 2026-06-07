"""Tests for tweak metadata validation."""

from __future__ import annotations

from wintuner.app.core.tweak_model import RiskLevel, Tweak, TweakResult, TweakState
from wintuner.app.core.tweak_registry import get_all_tweaks, load_all_tweaks


def _noop_detect() -> TweakState:
    return TweakState(enabled=None)


def _noop_apply() -> TweakResult:
    return TweakResult(True, "ok")


def test_tweak_validation_passes_minimal() -> None:
    tweak = Tweak(
        id="test_tweak",
        title="Test",
        category="Test",
        description="Desc",
        risk_level=RiskLevel.LOW,
        requires_admin=False,
        reversible=True,
        affected_area="Test",
        notes="",
        why_use="Because",
        undo_instructions="Undo it",
        detect_fn=_noop_detect,
        apply_fn=_noop_apply,
        undo_fn=lambda v: TweakResult(True, "undone"),
    )
    assert tweak.validate() == []


def test_tweak_validation_missing_fields() -> None:
    tweak = Tweak(
        id="",
        title="",
        category="",
        description="",
        risk_level=RiskLevel.LOW,
        requires_admin=False,
        reversible=True,
        affected_area="",
        notes="",
        why_use="",
        undo_instructions="",
        apply_fn=_noop_apply,
    )
    errors = tweak.validate()
    assert "Missing id" in errors
    assert "Missing apply_fn" not in errors
    assert "Missing detect_fn" in errors


def test_loaded_tweaks_have_valid_metadata() -> None:
    load_all_tweaks()
    tweaks = get_all_tweaks()
    assert len(tweaks) >= 5
    for tweak in tweaks:
        errors = tweak.validate()
        assert errors == [], f"{tweak.id}: {errors}"
