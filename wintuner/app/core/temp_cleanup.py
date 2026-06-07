"""Safe temporary file cleanup with dry-run preview."""

from __future__ import annotations

import logging
import os
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from wintuner.app.core.app_logging import log_cleanup_preview, log_cleanup_result

logger = logging.getLogger(__name__)

_PREVIEW_CACHE_TTL_SECONDS = 45.0

_preview_cache: CleanupPreview | None = None
_preview_cache_time: float = 0.0


@dataclass
class CleanupItem:
    """A file or folder candidate for cleanup."""

    path: Path
    size_bytes: int
    is_dir: bool


@dataclass
class CleanupPreview:
    """Dry-run preview of a temp cleanup operation."""

    items: list[CleanupItem] = field(default_factory=list)
    total_bytes: int = 0
    skipped_locked: list[str] = field(default_factory=list)
    skipped_unsafe: list[str] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return len(self.items)

    @property
    def total_mb(self) -> float:
        return round(self.total_bytes / (1024 * 1024), 2)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_locked) + len(self.skipped_unsafe)


@dataclass
class CleanupResult:
    """Result of executing temp cleanup."""

    deleted_count: int = 0
    freed_bytes: int = 0
    skipped_locked: list[str] = field(default_factory=list)
    skipped_unsafe: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_locked) + len(self.skipped_unsafe)


def get_user_temp_dir() -> Path | None:
    """Return the resolved current-user TEMP directory, or None if unavailable."""
    temp_env = os.environ.get("TEMP") or os.environ.get("TMP")
    if not temp_env:
        fallback = Path.home() / "AppData" / "Local" / "Temp"
        if fallback.exists():
            return fallback.resolve()
        return None
    temp_path = Path(temp_env)
    if not temp_path.exists():
        return None
    return temp_path.resolve()


def is_safe_temp_path(entry: Path, temp_root: Path) -> bool:
    """Return True if entry resolves inside temp_root and is not a symlink escape."""
    try:
        if entry.is_symlink():
            logger.debug("Skipping symlink: %s", entry.name)
            return False
        resolved = entry.resolve()
        temp_resolved = temp_root.resolve()
        return resolved.is_relative_to(temp_resolved)
    except OSError as exc:
        logger.debug("Path safety check failed for %s: %s", entry, exc)
        return False


def _safe_size(path: Path) -> int:
    """Return file/folder size in bytes, 0 if inaccessible."""
    try:
        if path.is_file():
            return path.stat().st_size
        total = 0
        for root, _, files in os.walk(path):
            for fname in files:
                fp = Path(root) / fname
                try:
                    total += fp.stat().st_size
                except OSError:
                    pass
        return total
    except OSError:
        return 0


def invalidate_preview_cache() -> None:
    """Clear cached temp preview (e.g. after confirmed cleanup)."""
    global _preview_cache, _preview_cache_time
    _preview_cache = None
    _preview_cache_time = 0.0


def _scan_temp_preview() -> CleanupPreview:
    """Scan TEMP and build a preview. Never deletes."""
    preview = CleanupPreview()
    temp_root = get_user_temp_dir()
    if temp_root is None:
        logger.warning("User TEMP directory not found.")
        return preview

    try:
        for entry in temp_root.iterdir():
            if not is_safe_temp_path(entry, temp_root):
                preview.skipped_unsafe.append(entry.name)
                continue
            try:
                size = _safe_size(entry)
                preview.items.append(
                    CleanupItem(path=entry, size_bytes=size, is_dir=entry.is_dir())
                )
                preview.total_bytes += size
            except PermissionError:
                preview.skipped_locked.append(entry.name)
            except OSError as exc:
                logger.debug("Skipped %s: %s", entry.name, exc)
                preview.skipped_locked.append(entry.name)
    except PermissionError:
        preview.skipped_locked.append(str(temp_root))
    except OSError as exc:
        logger.warning("Cannot scan temp dir: %s", exc)
    return preview


def preview_cleanup(*, log_result: bool = False, force_refresh: bool = False) -> CleanupPreview:
    """Return a dry-run preview of user TEMP contents. Never deletes."""
    global _preview_cache, _preview_cache_time

    now = time.monotonic()
    if (
        not force_refresh
        and _preview_cache is not None
        and (now - _preview_cache_time) < _PREVIEW_CACHE_TTL_SECONDS
    ):
        preview = _preview_cache
    else:
        preview = _scan_temp_preview()
        _preview_cache = preview
        _preview_cache_time = now

    if log_result:
        log_cleanup_preview(preview.file_count, preview.total_bytes, preview.skipped_count)
    return preview


def execute_cleanup(preview: CleanupPreview | None = None) -> CleanupResult:
    """Delete temp items from a validated preview. Never runs without explicit preview."""
    if preview is None:
        preview = preview_cleanup(force_refresh=True)

    temp_root = get_user_temp_dir()
    result = CleanupResult(
        skipped_locked=list(preview.skipped_locked),
        skipped_unsafe=list(preview.skipped_unsafe),
    )

    for item in preview.items:
        if temp_root is None or not is_safe_temp_path(item.path, temp_root):
            result.skipped_unsafe.append(item.path.name)
            continue
        try:
            if item.is_dir:
                shutil.rmtree(item.path, ignore_errors=False)
            else:
                item.path.unlink()
            result.deleted_count += 1
            result.freed_bytes += item.size_bytes
        except PermissionError:
            result.skipped_locked.append(item.path.name)
        except OSError as exc:
            result.errors.append(f"{item.path.name}: {exc}")
            logger.warning("Cleanup error for %s: %s", item.path.name, exc)

    invalidate_preview_cache()
    log_cleanup_result(result.deleted_count, result.freed_bytes, result.skipped_count)
    return result
