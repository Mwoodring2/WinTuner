"""Tests for admin detection (non-destructive)."""

from __future__ import annotations

import sys

from wintuner.app.core.admin import admin_required_message, is_admin


def test_is_admin_returns_bool() -> None:
    result = is_admin()
    assert isinstance(result, bool)


def test_admin_message_contains_action() -> None:
    msg = admin_required_message("Test Action")
    assert "Test Action" in msg
    assert "administrator" in msg.lower()


def test_is_admin_false_on_non_windows(monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    # is_admin checks sys.platform internally at call time
    import wintuner.app.core.admin as admin_mod

    monkeypatch.setattr(admin_mod.sys, "platform", "linux")
    assert admin_mod.is_admin() is False
