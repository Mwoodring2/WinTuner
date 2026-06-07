"""Unified search across God Mode tools and tweak metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from wintuner.app.core.launcher import LaunchTool, load_tools
from wintuner.app.core.tweak_model import Tweak
from wintuner.app.core.tweak_registry import get_all_tweaks


class ResultType(str, Enum):
    """Kind of unified search result."""

    TOOL = "tool"
    TWEAK = "tweak"


@dataclass(frozen=True)
class SearchResult:
    """A single unified search hit for tools or tweaks."""

    id: str
    title: str
    result_type: ResultType
    category: str
    description: str
    risk_level: str | None = None
    requires_admin: bool = False
    reversible: bool | None = None
    command: str | None = None
    command_type: str | None = None
    tool_args: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)

    @property
    def dedupe_key(self) -> tuple[str, str]:
        """Unique key for deduplication."""
        return (self.result_type.value, self.id)

    def validate(self) -> list[str]:
        """Return validation errors for required fields."""
        errors: list[str] = []
        if not self.id:
            errors.append("Missing id")
        if not self.title:
            errors.append("Missing title")
        if self.result_type not in ResultType:
            errors.append(f"Invalid result_type: {self.result_type}")
        if not self.category:
            errors.append("Missing category")
        if not self.description:
            errors.append("Missing description")
        if self.result_type == ResultType.TOOL and not self.command:
            errors.append("Tool missing command")
        if self.result_type == ResultType.TWEAK and self.risk_level is None:
            errors.append("Tweak missing risk_level")
        return errors


def _tool_to_result(tool: LaunchTool) -> SearchResult:
    return SearchResult(
        id=tool.id,
        title=tool.name,
        result_type=ResultType.TOOL,
        category=tool.category,
        description=tool.description,
        requires_admin=tool.requires_admin,
        command=tool.command,
        command_type=tool.command_type,
        tool_args=list(tool.args),
    )


def _tweak_to_result(tweak: Tweak) -> SearchResult:
    keywords = list(tweak.tags) + [tweak.id, tweak.affected_area]
    return SearchResult(
        id=tweak.id,
        title=tweak.title,
        result_type=ResultType.TWEAK,
        category=tweak.category,
        description=tweak.description,
        risk_level=tweak.risk_level.value,
        requires_admin=tweak.requires_admin,
        reversible=tweak.reversible,
        keywords=keywords,
    )


def _matches(query: str, *fields: str) -> bool:
    q = query.lower()
    return any(q in (field or "").lower() for field in fields if field)


def _tool_matches(tool: LaunchTool, query: str) -> bool:
    return _matches(query, tool.id, tool.name, tool.description, tool.category)


def _tweak_matches(tweak: Tweak, query: str) -> bool:
    tag_text = " ".join(tweak.tags)
    return _matches(
        query,
        tweak.id,
        tweak.title,
        tweak.description,
        tweak.category,
        tweak.why_use,
        tweak.affected_area,
        tag_text,
    )


def search_all(query: str) -> list[SearchResult]:
    """Search God Mode tools and tweaks. Empty query returns no results."""
    stripped = query.strip()
    if not stripped:
        return []

    seen: set[tuple[str, str]] = set()
    results: list[SearchResult] = []

    for tool in load_tools():
        if _tool_matches(tool, stripped):
            result = _tool_to_result(tool)
            if result.dedupe_key not in seen:
                seen.add(result.dedupe_key)
                results.append(result)

    for tweak in get_all_tweaks():
        if _tweak_matches(tweak, stripped):
            result = _tweak_to_result(tweak)
            if result.dedupe_key not in seen:
                seen.add(result.dedupe_key)
                results.append(result)

    return sorted(results, key=lambda r: (r.result_type.value, r.category.lower(), r.title.lower()))
