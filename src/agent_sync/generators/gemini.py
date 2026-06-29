"""Gemini generators."""

from __future__ import annotations

import json
from pathlib import Path

from agent_sync.generators._helpers import SyncContext


def generate_gemini(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    description = item.get("description", name)

    if name == "general":
        content = ctx.header(source) + body
        return [(ctx.repo_root / ".gemini" / "rules" / "general.md", content)]

    fm_lines = [
        "---",
        f"name: {json.dumps(name)}",
        f"description: {json.dumps(description)}",
        "---",
    ]
    content = "\n".join(fm_lines) + "\n" + ctx.header(source) + "\n" + body
    skill_name = name.replace("-", "_")
    return [(ctx.repo_root / ".gemini" / "skills" / skill_name / "SKILL.md", content)]


def generate_gemini_workflow(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    description = item.get("description", name)

    fm_lines = ["---", f"description: {json.dumps(description)}", "---"]
    content = "\n".join(fm_lines) + "\n" + ctx.header(source) + "\n" + body
    workflow_name = name.replace("-", "_")
    return [(ctx.repo_root / ".agents" / "workflows" / f"{workflow_name}.md", content)]
