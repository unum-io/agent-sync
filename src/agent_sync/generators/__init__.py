"""Framework generator registry."""

from __future__ import annotations

from typing import Callable

from agent_sync.generators.antigravity import generate_antigravity_rule
from agent_sync.generators.claude import generate_claude, generate_claude_command
from agent_sync.generators.continue_dev import generate_continue
from agent_sync.generators.copilot import (
    generate_copilot,
    generate_copilot_prompt,
    generate_copilot_skill,
)
from agent_sync.generators.cursor import generate_cursor, generate_cursor_command
from agent_sync.generators.gemini import generate_gemini, generate_gemini_workflow
from agent_sync.generators.kilo import generate_kilo_command, generate_kilo_instructions
from agent_sync.generators.opencode import generate_opencode

GeneratorFn = Callable[..., list]

INSTRUCTION_GENERATORS: dict[str, GeneratorFn] = {
    "copilot": generate_copilot,
    "cursor": generate_cursor,
    "claude": generate_claude,
    "gemini": generate_gemini,
    "antigravity": generate_antigravity_rule,
    "continue": generate_continue,
    "opencode": generate_opencode,
    "kilo": generate_kilo_instructions,
}

COMMAND_GENERATORS: dict[str, GeneratorFn] = {
    "copilot": generate_copilot_skill,
    "copilot_prompt": generate_copilot_prompt,
    "cursor": generate_cursor_command,
    "claude": generate_claude_command,
    "gemini": generate_gemini,
    "gemini_workflow": generate_gemini_workflow,
    "kilo": generate_kilo_command,
}

# Map generator function names to copilot/claude/gemini for script path rewriting
SCRIPT_DEST_FRAMEWORKS = frozenset({"copilot", "claude", "gemini"})
