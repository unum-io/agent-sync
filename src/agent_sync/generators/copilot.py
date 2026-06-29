"""Copilot generators."""

from __future__ import annotations

import json
from pathlib import Path

from agent_sync.generators._helpers import SyncContext, globs_to_apply_to


def generate_copilot(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    files = []
    name = item["name"]
    source = item["file"]

    if name == "general":
        content = f"---\napplyTo: '**'\n---\n" + ctx.header(source) + body
        files.append((ctx.repo_root / ".github" / "copilot-instructions.md", content))
    else:
        globs = item.get("globs", "**")
        always_apply = item.get("always_apply", False)
        if always_apply and not globs:
            globs = "**"
        apply_to = globs_to_apply_to(globs) if globs else "'**'"
        upper_name = name.upper().replace("-", "_")
        content = f"---\napplyTo: {apply_to}\n---\n" + ctx.header(source) + body
        files.append(
            (ctx.repo_root / ".github" / "instructions" / f"{upper_name}.instructions.md", content)
        )

    return files


def generate_copilot_skill(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    description = item.get("description", name)
    argument_hint = item.get("argument-hint", "")

    fm_lines = ["---", f"name: {json.dumps(name)}", f"description: {json.dumps(description)}"]
    if argument_hint:
        fm_lines.append(f"argument-hint: {json.dumps(argument_hint)}")
    fm_lines.append("---")

    content = "\n".join(fm_lines) + "\n" + ctx.header(source) + "\n" + body
    return [(ctx.repo_root / ".github" / "skills" / name / "SKILL.md", content)]


def generate_copilot_prompt(item: dict, body: str, ctx: SyncContext) -> list[tuple[Path, str]]:
    name = item["name"]
    source = item["file"]
    description = item.get("description", name)

    content = (
        f"---\nmode: 'agent'\ndescription: {json.dumps(description)}\n---\n"
        + ctx.header(source)
        + "\n"
        + body
    )
    return [(ctx.repo_root / ".github" / "prompts" / f"{name}.prompt.md", content)]
