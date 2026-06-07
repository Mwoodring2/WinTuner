"""Profile loading for the Optimizer page."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from wintuner.app.core.resource_paths import get_data_file

logger = logging.getLogger(__name__)

_PROFILES_FILE = get_data_file("profiles.json")


@dataclass
class ProfileAction:
    """A single action within an optimizer profile."""

    tweak_id: str
    label: str
    default_selected: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProfileAction:
        return cls(
            tweak_id=data["tweak_id"],
            label=data.get("label", data["tweak_id"]),
            default_selected=data.get("default_selected", True),
        )


@dataclass
class Profile:
    """An optimizer preset profile."""

    id: str
    name: str
    description: str
    icon: str
    actions: list[ProfileAction] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Profile:
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            icon=data.get("icon", "default"),
            actions=[ProfileAction.from_dict(a) for a in data.get("actions", [])],
        )


def load_profiles(path: Path | None = None) -> list[Profile]:
    """Load optimizer profiles from JSON."""
    filepath = path or _PROFILES_FILE
    if not filepath.exists():
        logger.error("Profiles file not found: %s", filepath)
        return []
    with open(filepath, encoding="utf-8") as fh:
        raw = json.load(fh)
    return [Profile.from_dict(p) for p in raw.get("profiles", [])]
