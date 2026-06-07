"""Tests for optimizer profile parsing."""

from __future__ import annotations

from wintuner.app.core.profiles import load_profiles
from wintuner.app.core.tweak_registry import get_tweak, load_all_tweaks


def test_load_profiles() -> None:
    profiles = load_profiles()
    assert len(profiles) == 5
    ids = {p.id for p in profiles}
    assert "balanced_cleanup" in ids
    assert "gaming_performance" in ids


def test_profile_actions_reference_valid_tweaks() -> None:
    load_all_tweaks()
    for profile in load_profiles():
        assert profile.name
        assert len(profile.actions) >= 1
        for action in profile.actions:
            tweak = get_tweak(action.tweak_id)
            assert tweak is not None, f"{profile.id}: missing tweak {action.tweak_id}"
