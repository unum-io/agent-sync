"""Load optional .ai/config.yaml with sensible defaults."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from agent_sync.parser import parse_yaml

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


def _parse_watcher_ignore(text: str) -> list[str] | None:
    """Extract watcher_ignore list from config text."""
    in_block = False
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("watcher_ignore:"):
            val = stripped.split(":", 1)[1].strip()
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1]
                return [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
            in_block = True
            continue
        if in_block:
            if stripped.startswith("- "):
                items.append(stripped[2:].strip().strip("'\""))
            elif stripped and not stripped.startswith("#"):
                break
    return items if items else None


def load_config(repo_root: Path, source_dir: str = ".ai") -> SyncConfig:
    """Load config from ``{source_dir}/config.yaml`` or return defaults."""
    config_path = repo_root / source_dir / "config.yaml"
    project_name = repo_root.name

    if not config_path.exists():
        return SyncConfig(project_name=project_name, source_dir=source_dir)

    text = config_path.read_text()
    raw = parse_yaml(text)

    frameworks = ALL_FRAMEWORKS
    if "frameworks" in raw and isinstance(raw["frameworks"], list):
        frameworks = frozenset(str(f) for f in raw["frameworks"])

    opencode_ignore = _parse_watcher_ignore(text) or list(DEFAULT_OPENCODE_WATCHER_IGNORE)

    return SyncConfig(
        project_name=str(raw.get("project_name", project_name)),
        source_dir=str(raw.get("source_dir", source_dir)),
        frameworks=frameworks,
        opencode_watcher_ignore=opencode_ignore,
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
