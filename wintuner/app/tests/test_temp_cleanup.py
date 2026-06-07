"""Tests for temp cleanup dry-run and path safety."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from wintuner.app.core.temp_cleanup import (
    CleanupPreview,
    execute_cleanup,
    get_user_temp_dir,
    is_safe_temp_path,
    preview_cleanup,
)


def test_preview_cleanup_returns_preview() -> None:
    preview = preview_cleanup()
    assert isinstance(preview, CleanupPreview)
    assert preview.total_bytes >= 0
    assert preview.file_count == len(preview.items)


def test_preview_total_mb() -> None:
    preview = CleanupPreview(items=[], total_bytes=1024 * 1024)
    assert preview.total_mb == 1.0


def test_preview_never_deletes_files(tmp_path: Path) -> None:
    from wintuner.app.core import temp_cleanup as tc

    tc.invalidate_preview_cache()
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    test_file = temp_dir / "wintuner_preview_test.txt"
    test_file.write_text("keep me", encoding="utf-8")

    with patch.object(tc, "get_user_temp_dir", return_value=temp_dir):
        preview = tc.preview_cleanup(force_refresh=True)

    assert test_file.exists()
    assert preview.file_count >= 1
    tc.invalidate_preview_cache()


def test_execute_cleanup_only_deletes_after_explicit_preview(tmp_path: Path) -> None:
    from wintuner.app.core import temp_cleanup as tc

    tc.invalidate_preview_cache()
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    victim = temp_dir / "delete_me.txt"
    victim.write_text("gone", encoding="utf-8")

    with patch.object(tc, "get_user_temp_dir", return_value=temp_dir):
        preview = tc.preview_cleanup(force_refresh=True)
        assert preview.file_count >= 1
        result = tc.execute_cleanup(preview)

    assert result.deleted_count >= 1
    assert not victim.exists()
    tc.invalidate_preview_cache()


def test_is_safe_temp_path_rejects_outside_root(tmp_path: Path) -> None:
    temp_root = tmp_path / "temp"
    temp_root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("x", encoding="utf-8")
    assert is_safe_temp_path(outside, temp_root) is False


def test_is_safe_temp_path_accepts_inside_root(tmp_path: Path) -> None:
    temp_root = tmp_path / "temp"
    temp_root.mkdir()
    inside = temp_root / "inside.txt"
    inside.write_text("x", encoding="utf-8")
    assert is_safe_temp_path(inside, temp_root) is True


def test_execute_cleanup_skips_unsafe_paths(tmp_path: Path) -> None:
    temp_root = tmp_path / "temp"
    temp_root.mkdir()
    safe = temp_root / "safe.txt"
    safe.write_text("ok", encoding="utf-8")

    preview = CleanupPreview(
        items=[],
        skipped_unsafe=["bad_symlink"],
    )
    with patch("wintuner.app.core.temp_cleanup.get_user_temp_dir", return_value=temp_root):
        result = execute_cleanup(preview)

    assert safe.exists()
    assert result.skipped_count >= 1


def test_get_user_temp_dir_returns_path() -> None:
    temp = get_user_temp_dir()
    if os.environ.get("TEMP") or os.environ.get("TMP"):
        assert temp is not None
        assert temp.exists()


def test_preview_cache_avoids_rescan_within_ttl(tmp_path: Path) -> None:
    from wintuner.app.core import temp_cleanup as tc

    tc.invalidate_preview_cache()
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "a.txt").write_text("a", encoding="utf-8")

    with patch.object(tc, "get_user_temp_dir", return_value=temp_dir):
        with patch.object(tc, "_scan_temp_preview", wraps=tc._scan_temp_preview) as mock_scan:
            first = tc.preview_cleanup()
            second = tc.preview_cleanup()
            assert first.file_count == second.file_count
            assert mock_scan.call_count == 1

    tc.invalidate_preview_cache()


def test_preview_force_refresh_bypasses_cache(tmp_path: Path) -> None:
    from wintuner.app.core import temp_cleanup as tc

    tc.invalidate_preview_cache()
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()

    with patch.object(tc, "get_user_temp_dir", return_value=temp_dir):
        with patch.object(tc, "_scan_temp_preview", wraps=tc._scan_temp_preview) as mock_scan:
            tc.preview_cleanup()
            tc.preview_cleanup(force_refresh=True)
            assert mock_scan.call_count == 2

    tc.invalidate_preview_cache()


def test_execute_cleanup_invalidates_cache(tmp_path: Path) -> None:
    from wintuner.app.core import temp_cleanup as tc

    tc.invalidate_preview_cache()
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    victim = temp_dir / "gone.txt"
    victim.write_text("x", encoding="utf-8")

    with patch.object(tc, "get_user_temp_dir", return_value=temp_dir):
        preview = tc.preview_cleanup()
        tc.execute_cleanup(preview)
        assert tc._preview_cache is None

    tc.invalidate_preview_cache()
