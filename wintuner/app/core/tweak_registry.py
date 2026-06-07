"""Central registry of all available tweaks."""

from __future__ import annotations

import logging

from wintuner.app.core.tweak_model import Tweak

logger = logging.getLogger(__name__)

_registry: dict[str, Tweak] = {}


def register_tweak(tweak: Tweak) -> None:
    """Add a tweak to the global registry."""
    errors = tweak.validate()
    if errors:
        logger.warning("Registering tweak %s with issues: %s", tweak.id, errors)
    _registry[tweak.id] = tweak


def get_tweak(tweak_id: str) -> Tweak | None:
    """Look up a tweak by id."""
    return _registry.get(tweak_id)


def get_all_tweaks() -> list[Tweak]:
    """Return all registered tweaks sorted by category then title."""
    return sorted(_registry.values(), key=lambda t: (t.category, t.title))


def get_tweaks_by_category(category: str) -> list[Tweak]:
    """Return tweaks in a given category."""
    return [t for t in _registry.values() if t.category == category]


def get_categories() -> list[str]:
    """Return sorted unique categories."""
    return sorted({t.category for t in _registry.values()})


def search_tweaks(query: str) -> list[Tweak]:
    """Filter tweaks by title, description, or category."""
    if not query.strip():
        return get_all_tweaks()
    q = query.lower()
    return [
        t
        for t in _registry.values()
        if q in t.title.lower()
        or q in t.description.lower()
        or q in t.category.lower()
        or any(q in tag.lower() for tag in t.tags)
    ]


def load_all_tweaks() -> None:
    """Import and register all tweak modules."""
    from wintuner.app.tweaks import explorer_tweaks, performance_tweaks, privacy_tweaks, storage_tweaks

    explorer_tweaks.register()
    privacy_tweaks.register()
    storage_tweaks.register()
    performance_tweaks.register()
    logger.info("Loaded %d tweaks.", len(_registry))
