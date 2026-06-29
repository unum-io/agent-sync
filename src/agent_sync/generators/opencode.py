"""OpenCode generators."""

from __future__ import annotations

import json
from pathlib import Path

from agent_sync.generators._helpers import SyncContext, globs_to_list


def generate_opencode(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    description = item.get("description", name)
    globs = item.get("globs")
    always_apply = item.get("always_apply", False)

    if name == "general":
        content = f"# {ctx.project_name}\n\n" + ctx.header(source) + body
        return [(ctx.repo_root / "AGENTS.md", content)]

    if always_apply and not globs:
        globs = "**/*"

    fm_lines = [
        "---",
        f"name: {json.dumps(description)}",
        f"alwaysApply: {'true' if always_apply else 'false'}",
    ]
    if globs:
        fm_lines.append(f"globs: {globs_to_list(globs)}")
    fm_lines.append("---")

    content = "\n".join(fm_lines) + "\n" + ctx.header(source) + "\n" + body
    return [(ctx.repo_root / ".opencode" / "rules" / f"{name}.md", content)]
