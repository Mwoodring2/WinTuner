"""Tests for God Mode launcher."""

from __future__ import annotations

from unittest.mock import patch

from wintuner.app.core.launcher import (
    ALLOWLISTED_RUNDLL32_ARGS,
    LaunchTool,
    launch_tool,
    load_tools,
    search_tools,
    validate_command_for_type,
)


def test_launch_tool_validation() -> None:
    tool = LaunchTool(
        id="test",
        name="Test Tool",
        description="A test",
        command="notepad.exe",
        args=[],
        category="Test",
        command_type="exe",
    )
    assert tool.validate() == []


def test_launch_tool_validation_missing_command() -> None:
    tool = LaunchTool(
        id="test",
        name="Test",
        description="",
        command="",
        args=[],
        category="Test",
        command_type="exe",
    )
    assert "Missing command" in tool.validate()


def test_invalid_command_type_rejected() -> None:
    tool = LaunchTool(
        id="bad",
        name="Bad",
        description="",
        command="cmd.exe",
        args=["/c", "del"],
        category="Test",
        command_type="powershell",
    )
    assert any("Unsupported command_type" in e for e in tool.validate())


def test_rundll32_not_allowlisted() -> None:
    tool = LaunchTool(
        id="bad",
        name="Bad Rundll",
        description="",
        command="rundll32.exe",
        args=["shell32.dll,ShellExec_RunDLL"],
        category="Test",
        command_type="rundll32",
    )
    errors = tool.validate()
    assert any("not allowlisted" in e for e in errors)


def test_rundll32_allowlisted_validates() -> None:
    arg = next(iter(ALLOWLISTED_RUNDLL32_ARGS))
    tool = LaunchTool(
        id="env",
        name="Env",
        description="",
        command="rundll32.exe",
        args=[arg],
        category="Test",
        command_type="rundll32",
    )
    assert tool.validate() == []


def test_launch_tool_rejects_invalid_before_spawn() -> None:
    tool = LaunchTool(
        id="bad",
        name="Bad",
        description="",
        command="rundll32.exe",
        args=["evil.dll,DoBadThing"],
        category="Test",
        command_type="rundll32",
    )
    with patch("wintuner.app.core.launcher.subprocess.Popen") as mock_popen:
        ok, msg = launch_tool(tool)
    assert ok is False
    assert "allowlisted" in msg.lower() or "cannot launch" in msg.lower()
    mock_popen.assert_not_called()


def test_ms_settings_requires_prefix() -> None:
    errors = validate_command_for_type("ms-settings", "bad-uri", [])
    assert any("ms-settings:" in e for e in errors)


def test_load_tools_from_json() -> None:
    tools = load_tools()
    assert len(tools) >= 20
    ids = {t.id for t in tools}
    assert "task_manager" in ids
    assert "device_manager" in ids


def test_search_tools() -> None:
    tools = load_tools()
    results = search_tools(tools, "disk")
    assert len(results) >= 1
    assert all("disk" in t.name.lower() or "disk" in t.description.lower() for t in results)


def test_all_tools_have_required_fields() -> None:
    for tool in load_tools():
        assert tool.validate() == [], f"{tool.id} invalid: {tool.validate()}"
