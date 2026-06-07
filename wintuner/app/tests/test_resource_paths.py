"""Tests for bundled resource path resolution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from wintuner.app.core.resource_paths import get_data_file, is_frozen, resource_path


def test_get_data_file_exists_in_dev_mode() -> None:
    path = get_data_file("god_mode_tools.json")
    assert path.exists()
    assert path.name == "god_mode_tools.json"


def test_get_data_file_profiles_exists() -> None:
    path = get_data_file("profiles.json")
    assert path.exists()


def test_is_frozen_false_in_dev() -> None:
    assert is_frozen() is False


def test_resource_path_uses_meipass_when_frozen(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    data_dir = bundle / "data"
    data_dir.mkdir(parents=True)
    json_file = data_dir / "god_mode_tools.json"
    json_file.write_text("{}", encoding="utf-8")

    with patch("wintuner.app.core.resource_paths.get_bundle_root", return_value=bundle):
        with patch("wintuner.app.core.resource_paths.is_frozen", return_value=True):
            resolved = resource_path(Path("data") / "god_mode_tools.json")
    assert resolved == json_file


def test_resource_path_falls_back_to_app_root_when_not_in_bundle() -> None:
    resolved = resource_path("data/profiles.json")
    assert resolved.exists()
    assert "profiles.json" in resolved.name
