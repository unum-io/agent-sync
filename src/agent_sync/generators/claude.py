"""Claude generators."""

from __future__ import annotations

import json
from pathlib import Path

from agent_sync.generators._helpers import SyncContext, globs_to_paths


def generate_claude(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    globs = item.get("globs")
    always_apply = item.get("always_apply", False)

    if name == "general":
        content = f"# {ctx.project_name}\n\n" + ctx.header(source) + body
        return [(ctx.repo_root / "CLAUDE.md", content)]

    upper_name = name.upper().replace("-", "_")
    if always_apply and not globs:
        paths_block = "paths:\n  - '**'"
    elif globs:
        paths_block = globs_to_paths(globs)
    else:
        paths_block = "paths:\n  - '**'"

    content = f"---\n{paths_block}\n---\n" + ctx.header(source) + "\n" + body
    return [(ctx.repo_root / ".claude" / "rules" / f"{upper_name}.md", content)]


def generate_claude_command(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    description = item.get("description", name)

    fm_lines = [
        "---",
        f"name: {json.dumps(name)}",
        f"description: {json.dumps(description)}",
        "---",
    ]
    content = "\n".join(fm_lines) + "\n" + ctx.header(source) + "\n" + body
    return [(ctx.repo_root / ".claude" / "skills" / name / "SKILL.md", content)]
