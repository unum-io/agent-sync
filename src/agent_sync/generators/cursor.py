"""Cursor generators."""

from __future__ import annotations

import json
from pathlib import Path

from agent_sync.generators._helpers import SyncContext, globs_to_list


def generate_cursor(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    description = item.get("description", name)
    globs = item.get("globs")
    always_apply = item.get("always_apply", False)

    fm_lines = ["---", f"description: {json.dumps(description)}"]
    if always_apply:
        fm_lines.append("alwaysApply: true")
    if globs:
        fm_lines.append(f"globs: {globs_to_list(globs)}")
    fm_lines.append("---")

    content = "\n".join(fm_lines) + "\n" + ctx.header(source) + "\n" + body
    rule_name = name if name != "general" else "general-instructions"
    return [(ctx.repo_root / ".cursor" / "rules" / f"{rule_name}.mdc", content)]


def generate_cursor_command(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    content = ctx.header(source) + body
    return [(ctx.repo_root / ".cursor" / "commands" / f"{name}.md", content)]
