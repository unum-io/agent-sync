"""Load optional .ai/config.toml with sensible defaults."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from agent_sync.parser import load_toml, reject_legacy_yaml

ALL_FRAMEWORKS = frozenset(
    {
        "copilot",
        "cursor",
        "claude",
        "gemini",
        "antigravity",
        "continue",
        "opencode",
        "kilo",
    }
)

DEFAULT_OPENCODE_WATCHER_IGNORE = [
    "node_modules/**",
    "dist/**",
    ".venv/**",
    "__pycache__/**",
    "*.pyc",
    ".git/**",
]


@dataclass
class SyncConfig:
    project_name: str
    source_dir: str = ".ai"
    frameworks: frozenset[str] = field(default_factory=lambda: ALL_FRAMEWORKS)
    opencode_watcher_ignore: list[str] = field(default_factory=lambda: list(DEFAULT_OPENCODE_WATCHER_IGNORE))
    write_opencode_json: bool = True
    write_kilo_json: bool = True


def load_config(repo_root: Path, source_dir: str = ".ai") -> SyncConfig:
    """Load config from ``{source_dir}/config.toml`` or return defaults."""
    reject_legacy_yaml(repo_root / source_dir)
    config_path = repo_root / source_dir / "config.toml"
    project_name = repo_root.name

    if not config_path.exists():
        return SyncConfig(project_name=project_name, source_dir=source_dir)

    raw = load_toml(config_path)

    frameworks = ALL_FRAMEWORKS
    if isinstance(raw.get("frameworks"), list):
        frameworks = frozenset(str(f) for f in raw["frameworks"])

    opencode_ignore = raw.get("opencode", {}).get("watcher_ignore")
    if not isinstance(opencode_ignore, list) or not opencode_ignore:
        opencode_ignore = list(DEFAULT_OPENCODE_WATCHER_IGNORE)

    return SyncConfig(
        project_name=str(raw.get("project_name", project_name)),
        source_dir=str(raw.get("source_dir", source_dir)),
        frameworks=frameworks,
        opencode_watcher_ignore=[str(p) for p in opencode_ignore],
        write_opencode_json=raw.get("write_opencode_json", True) is not False,
        write_kilo_json=raw.get("write_kilo_json", True) is not False,
    )


def format_opencode_json(watcher_ignore: list[str]) -> str:
    """Build opencode.json content."""
    ignore_json = ",\n".join(f"      {json.dumps(p)}" for p in watcher_ignore)
    return f"""{{
  "$schema": "https://opencode.ai/config.json",
  "watcher": {{
    "ignore": [
{ignore_json}
    ]
  }},
  "instructions": [
    ".opencode/rules/*.md"
  ]
}}
"""
