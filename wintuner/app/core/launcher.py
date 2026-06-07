"""Safe Windows tool launcher for God Mode page."""

from __future__ import annotations

import json
import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from wintuner.app.core.app_logging import log_launcher_result
from wintuner.app.core.resource_paths import get_data_file

logger = logging.getLogger(__name__)

_TOOLS_FILE = get_data_file("god_mode_tools.json")

ALLOWED_COMMAND_TYPES = frozenset({"exe", "control", "ms-settings", "shell", "rundll32"})

ALLOWLISTED_RUNDLL32_ARGS = frozenset(
    {
        "sysdm.cpl,EditEnvironmentVariables",
    }
)


class CommandType(str, Enum):
    """Supported launcher command types."""

    EXE = "exe"
    CONTROL = "control"
    MS_SETTINGS = "ms-settings"
    SHELL = "shell"
    RUNDLL32 = "rundll32"


@dataclass
class LaunchTool:
    """A launchable Windows tool entry."""

    id: str
    name: str
    description: str
    command: str
    args: list[str]
    category: str
    command_type: str
    requires_admin: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LaunchTool:
        """Create a LaunchTool from a JSON dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            command=data["command"],
            args=data.get("args", []),
            category=data.get("category", "General"),
            command_type=data.get("command_type", _infer_command_type(data)),
            requires_admin=data.get("requires_admin", False),
        )

    def validate(self) -> list[str]:
        """Return a list of validation errors, empty if valid."""
        errors: list[str] = []
        if not self.id:
            errors.append("Missing id")
        if not self.name:
            errors.append("Missing name")
        if not self.command:
            errors.append("Missing command")
        if self.command_type not in ALLOWED_COMMAND_TYPES:
            errors.append(f"Unsupported command_type: {self.command_type}")
        type_errors = validate_command_for_type(self.command_type, self.command, self.args)
        errors.extend(type_errors)
        return errors


def _infer_command_type(data: dict[str, Any]) -> str:
    """Infer command type from legacy JSON entries missing command_type."""
    command = data.get("command", "")
    if command.startswith("ms-settings:"):
        return CommandType.MS_SETTINGS.value
    if command.lower() == "control.exe":
        return CommandType.CONTROL.value
    if command.lower() == "rundll32.exe":
        return CommandType.RUNDLL32.value
    if command.endswith(":") or command.lower().endswith(".cpl"):
        return CommandType.SHELL.value
    return CommandType.EXE.value


def validate_command_for_type(command_type: str, command: str, args: list[str]) -> list[str]:
    """Validate command and args match the declared type."""
    errors: list[str] = []
    if command_type == CommandType.MS_SETTINGS.value:
        if not command.startswith("ms-settings:"):
            errors.append("ms-settings command must start with ms-settings:")
    elif command_type == CommandType.CONTROL.value:
        if Path(command).name.lower() != "control.exe":
            errors.append("control type requires control.exe")
        if not args:
            errors.append("control type requires at least one argument")
    elif command_type == CommandType.SHELL.value:
        if not command:
            errors.append("shell type requires a command URI or path")
    elif command_type == CommandType.EXE.value:
        if not command:
            errors.append("exe type requires a command")
    elif command_type == CommandType.RUNDLL32.value:
        if Path(command).name.lower() != "rundll32.exe":
            errors.append("rundll32 type requires rundll32.exe")
        if not args:
            errors.append("rundll32 type requires allowlisted arguments")
        elif args[0] not in ALLOWLISTED_RUNDLL32_ARGS:
            errors.append(f"rundll32 argument not allowlisted: {args[0]}")
    return errors


def load_tools(path: Path | None = None) -> list[LaunchTool]:
    """Load God Mode tools from JSON."""
    filepath = path or _TOOLS_FILE
    if not filepath.exists():
        logger.error("God mode tools file not found: %s", filepath)
        return []
    with open(filepath, encoding="utf-8") as fh:
        raw = json.load(fh)
    tools = [LaunchTool.from_dict(item) for item in raw.get("tools", [])]
    for tool in tools:
        errs = tool.validate()
        if errs:
            logger.warning("Tool %s validation issues: %s", tool.id, errs)
    return tools


def launch_tool(tool: LaunchTool) -> tuple[bool, str]:
    """Launch a Windows tool safely. Returns (success, message)."""
    validation_errors = tool.validate()
    if validation_errors:
        msg = f"Cannot launch {tool.name}: {'; '.join(validation_errors)}"
        logger.error(msg)
        log_launcher_result(tool.id, False, msg)
        return False, msg

    try:
        cmd_type = tool.command_type
        if cmd_type == CommandType.MS_SETTINGS.value:
            os.startfile(tool.command)
        elif cmd_type == CommandType.SHELL.value:
            target = tool.command
            if tool.args:
                target = f"{tool.command} {' '.join(tool.args)}"
            os.startfile(target)
        elif cmd_type == CommandType.CONTROL.value:
            subprocess.Popen(
                [tool.command, *tool.args],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        elif cmd_type == CommandType.RUNDLL32.value:
            subprocess.Popen(
                [tool.command, *tool.args],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        else:
            subprocess.Popen(
                [tool.command, *tool.args],
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        msg = f"Opened {tool.name}."
        log_launcher_result(tool.id, True, msg)
        return True, msg
    except FileNotFoundError:
        msg = (
            f"Could not find '{tool.command}'. "
            "This tool may not be available on your system."
        )
        logger.error(msg)
        log_launcher_result(tool.id, False, msg)
        return False, msg
    except OSError as exc:
        msg = f"Failed to open {tool.name}: {exc}"
        logger.error(msg)
        log_launcher_result(tool.id, False, msg)
        return False, msg


def search_tools(tools: list[LaunchTool], query: str) -> list[LaunchTool]:
    """Filter tools by name, description, or category."""
    if not query.strip():
        return tools
    q = query.lower()
    return [
        t
        for t in tools
        if q in t.name.lower() or q in t.description.lower() or q in t.category.lower()
    ]
