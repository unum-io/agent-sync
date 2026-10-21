"""Tests for config loading."""

from pathlib import Path

from agent_sync.config import DEFAULT_OPENCODE_WATCHER_IGNORE, format_opencode_json, load_config


def test_defaults_without_config(tmp_path: Path):
    cfg = load_config(tmp_path)
    assert cfg.project_name == tmp_path.name
    assert cfg.opencode_watcher_ignore == list(DEFAULT_OPENCODE_WATCHER_IGNORE)


def test_loads_project_name(tmp_path: Path):
    ai = tmp_path / ".ai"
    ai.mkdir()
    (ai / "config.toml").write_text('project_name = "MyApp"\n')
    cfg = load_config(tmp_path)
    assert cfg.project_name == "MyApp"


def test_watcher_ignore_override(tmp_path: Path):
    ai = tmp_path / ".ai"
    ai.mkdir()
    (ai / "config.toml").write_text(
        '[opencode]\nwatcher_ignore = ["bazel-*", "node_modules/**"]\n'
    )
    cfg = load_config(tmp_path)
    assert cfg.opencode_watcher_ignore == ["bazel-*", "node_modules/**"]


def test_frameworks_subset(tmp_path: Path):
    ai = tmp_path / ".ai"
    ai.mkdir()
    (ai / "config.toml").write_text('frameworks = ["claude", "cursor"]\n')
    cfg = load_config(tmp_path)
    assert cfg.frameworks == frozenset({"claude", "cursor"})


def test_format_opencode_json():
    content = format_opencode_json(["node_modules/**", "dist/**"])
    assert '"node_modules/**"' in content
    assert ".opencode/rules/*.md" in content
