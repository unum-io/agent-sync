"""Kilo generators."""

from __future__ import annotations

import json
from pathlib import Path

from agent_sync.generators._helpers import SyncContext


def generate_kilo_instructions(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    content = ctx.header(source) + body
    return [(ctx.repo_root / ".kilo" / "rules" / f"{name}.md", content)]


def generate_kilo_command(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    description = item.get("description", name)
    argument_hint = item.get("argument-hint", "")

    fm_lines = ["---", f"description: {json.dumps(description)}"]
    if argument_hint:
        fm_lines.append(f"argument-hint: {json.dumps(argument_hint)}")
    fm_lines.append("---")

    content = "\n".join(fm_lines) + "\n" + ctx.header(source) + "\n" + body
    return [(ctx.repo_root / ".kilo" / "command" / f"{name}.md", content)]
