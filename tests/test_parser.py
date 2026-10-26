"""Tests for TOML loading."""

from pathlib import Path

import pytest

from agent_sync.parser import load_toml, reject_legacy_yaml


def test_load_manifest_instructions(tmp_path: Path):
    path = tmp_path / "manifest.toml"
    path.write_text(
        """
[[instructions]]
name = "general"
file = "instructions/general.md"
description = "Core directives: \\"quoted\\", with, commas"  # trailing comment
always_apply = true

[[instructions]]
name = "python"
file = "instructions/python.md"
globs = ["**/*.py", "**/*.pyi"]
"""
    )
    data = load_toml(path)
    assert len(data["instructions"]) == 2
    first, second = data["instructions"]
    assert first["description"] == 'Core directives: "quoted", with, commas'
    assert first["always_apply"] is True
    assert second["globs"] == ["**/*.py", "**/*.pyi"]
    assert "globs" not in data


def test_quoted_values_keep_string_type(tmp_path: Path):
    path = tmp_path / "config.toml"
    path.write_text('frameworks = ["true", "a, b"]\n')
    assert load_toml(path)["frameworks"] == ["true", "a, b"]


def test_malformed_toml_exits(tmp_path: Path, capsys):
    path = tmp_path / "config.toml"
    path.write_text('project_name = "unterminated\n')
    with pytest.raises(SystemExit):
        load_toml(path)
    assert "config.toml" in capsys.readouterr().err


def test_rejects_legacy_yaml(tmp_path: Path, capsys):
    (tmp_path / "manifest.yaml").write_text("instructions:\n")
    with pytest.raises(SystemExit):
        reject_legacy_yaml(tmp_path)
    assert "manifest.yaml" in capsys.readouterr().err
