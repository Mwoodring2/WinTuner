"""Tests for unified search service."""

from __future__ import annotations

from wintuner.app.core.search_service import ResultType, search_all
from wintuner.app.core.tweak_registry import load_all_tweaks


def test_empty_query_returns_no_results() -> None:
    load_all_tweaks()
    assert search_all("") == []
    assert search_all("   ") == []


def test_finds_god_mode_tool_task_manager() -> None:
    load_all_tweaks()
    results = search_all("task")
    ids = {r.id for r in results if r.result_type == ResultType.TOOL}
    assert "task_manager" in ids


def test_finds_device_manager() -> None:
    load_all_tweaks()
    results = search_all("device")
    assert any(r.id == "device_manager" for r in results)


def test_finds_file_extensions_tweak() -> None:
    load_all_tweaks()
    results = search_all("file extensions")
    tweak_ids = {r.id for r in results if r.result_type == ResultType.TWEAK}
    assert "explorer_show_extensions" in tweak_ids


def test_finds_temp_cleanup_tweak() -> None:
    load_all_tweaks()
    results = search_all("temp")
    tweak_ids = {r.id for r in results if r.result_type == ResultType.TWEAK}
    assert "storage_clear_user_temp" in tweak_ids


def test_case_insensitive_search() -> None:
    load_all_tweaks()
    lower = search_all("task manager")
    upper = search_all("TASK MANAGER")
    assert {r.dedupe_key for r in lower} == {r.dedupe_key for r in upper}


def test_no_duplicate_results() -> None:
    load_all_tweaks()
    results = search_all("settings")
    keys = [r.dedupe_key for r in results]
    assert len(keys) == len(set(keys))


def test_search_result_shape_for_tool() -> None:
    load_all_tweaks()
    results = search_all("task manager")
    tool = next(r for r in results if r.id == "task_manager")
    assert tool.title
    assert tool.result_type == ResultType.TOOL
    assert tool.category
    assert tool.description
    assert tool.command
    assert tool.command_type
    assert tool.validate() == []


def test_search_result_shape_for_tweak() -> None:
    load_all_tweaks()
    results = search_all("explorer_show_extensions")
    tweak = next(r for r in results if r.id == "explorer_show_extensions")
    assert tweak.result_type == ResultType.TWEAK
    assert tweak.risk_level is not None
    assert tweak.reversible is not None
    assert tweak.validate() == []


def test_search_does_not_launch_tools(monkeypatch) -> None:
    load_all_tweaks()
    called = {"launch": False}

    def fake_launch(_tool):
        called["launch"] = True
        return True, "no"

    monkeypatch.setattr("wintuner.app.core.launcher.launch_tool", fake_launch)
    search_all("task")
    assert called["launch"] is False


def test_search_does_not_apply_tweaks(monkeypatch) -> None:
    load_all_tweaks()
    called = {"apply": False}

    from wintuner.app.core.tweak_registry import get_all_tweaks as original_fn

    original = original_fn()

    class SpyTweak:
        def __init__(self, tweak):
            self._tweak = tweak

        def __getattr__(self, name):
            return getattr(self._tweak, name)

        def apply(self):
            called["apply"] = True
            return self._tweak.apply()

    monkeypatch.setattr(
        "wintuner.app.core.search_service.get_all_tweaks",
        lambda: [SpyTweak(t) for t in original],
    )
    search_all("extensions")
    assert called["apply"] is False
