"""Main sync orchestration."""

from __future__ import annotations

import sys
from pathlib import Path

from agent_sync.config import SyncConfig, format_opencode_json, load_config
from agent_sync.generators import (
    COMMAND_GENERATORS,
    INSTRUCTION_GENERATORS,
    SCRIPT_DEST_FRAMEWORKS,
)
from agent_sync.generators._helpers import SyncContext
from agent_sync.parser import load_toml, reject_legacy_yaml

KILO_JSON_CONTENT = """{
  "$schema": "https://app.kilo.ai/config.json",
  "instructions": [
    ".kilo/rules/*.md"
  ]
}
"""


def sync(
    repo_root: Path,
    *,
    source_dir: str | None = None,
    dry_run: bool = False,
    check: bool = False,
    config: SyncConfig | None = None,
) -> list[Path] | int:
    """
    Read manifest.toml and generate all framework files.

    Returns list of written paths, or if check=True, exit code (0 = in sync, 1 = out of sync).
    """
    cfg = config or load_config(repo_root, source_dir or ".ai")
    ai_dir = repo_root / cfg.source_dir
    reject_legacy_yaml(ai_dir)
    manifest_path = ai_dir / "manifest.toml"

    if not manifest_path.exists():
        print(f"ERROR: {manifest_path} not found", file=sys.stderr)
        sys.exit(1)

    manifest = load_toml(manifest_path)
    ctx = SyncContext(
        repo_root=repo_root,
        source_prefix=cfg.source_dir,
        project_name=cfg.project_name,
    )
    written: list[Path] = []
    out_of_sync = False

    instruction_gens = _enabled_generators(INSTRUCTION_GENERATORS, cfg.frameworks)
    command_gens = _enabled_command_generators(cfg.frameworks)

    for item in manifest.get("instructions", []):
        written, out_of_sync = _process_item(
            item,
            ai_dir,
            repo_root,
            ctx,
            instruction_gens,
            written,
            out_of_sync,
            dry_run,
            check,
        )

    for item in manifest.get("commands", []):
        written, out_of_sync = _process_item(
            item,
            ai_dir,
            repo_root,
            ctx,
            command_gens,
            written,
            out_of_sync,
            dry_run,
            check,
        )

    if cfg.write_opencode_json and "opencode" in cfg.frameworks:
        opencode_path = repo_root / "opencode.json"
        opencode_content = format_opencode_json(cfg.opencode_watcher_ignore)
        out_of_sync = _check_or_write(
            opencode_path, opencode_content, out_of_sync, dry_run, check
        )
        written.append(opencode_path)

    if cfg.write_kilo_json and "kilo" in cfg.frameworks:
        kilo_path = repo_root / "kilo.json"
        out_of_sync = _check_or_write(kilo_path, KILO_JSON_CONTENT, out_of_sync, dry_run, check)
        written.append(kilo_path)

    if check:
        return 1 if out_of_sync else 0
    return written


def _enabled_generators(registry: dict, frameworks: frozenset[str]) -> list:
    return [fn for key, fn in registry.items() if key in frameworks]


def _enabled_command_generators(frameworks: frozenset[str]) -> list:
    gens = []
    if "copilot" in frameworks:
        gens.append(COMMAND_GENERATORS["copilot"])
        gens.append(COMMAND_GENERATORS["copilot_prompt"])
    if "cursor" in frameworks:
        gens.append(COMMAND_GENERATORS["cursor"])
    if "claude" in frameworks:
        gens.append(COMMAND_GENERATORS["claude"])
    if "gemini" in frameworks:
        gens.append(COMMAND_GENERATORS["gemini"])
        gens.append(COMMAND_GENERATORS["gemini_workflow"])
    if "kilo" in frameworks:
        gens.append(COMMAND_GENERATORS["kilo"])
    return gens


def _process_item(
    item: dict,
    ai_dir: Path,
    repo_root: Path,
    ctx: SyncContext,
    generators: list,
    written: list[Path],
    out_of_sync: bool,
    dry_run: bool,
    check: bool,
) -> tuple[list[Path], bool]:
    source_path = ai_dir / item["file"]
    if not source_path.exists():
        print(f"  WARN: Source file {source_path} not found, skipping", file=sys.stderr)
        return written, out_of_sync

    body = source_path.read_text()
    src_scripts = source_path.parent / "scripts"
    has_scripts = src_scripts.is_dir()
    rel_source_dir = source_path.parent.relative_to(repo_root).as_posix()

    for gen_fn in generators:
        for path, content in gen_fn(item, body, ctx):
            if has_scripts:
                dest_skill_dir = _script_dest(gen_fn.__name__, item["name"])
                if dest_skill_dir:
                    content = content.replace(
                        rel_source_dir + "/scripts",
                        dest_skill_dir + "/scripts",
                    )

            out_of_sync = _check_or_write(path, content, out_of_sync, dry_run, check)
            written.append(path)

            is_subfolder = path.parent.name in (item["name"], item["name"].replace("-", "_"))
            if is_subfolder and has_scripts:
                files, oos = _sync_dir(src_scripts, path.parent / "scripts", dry_run, check)
                if oos:
                    out_of_sync = True
                written.extend(files)

    return written, out_of_sync


def _script_dest(gen_name: str, item_name: str) -> str | None:
    for fw in SCRIPT_DEST_FRAMEWORKS:
        if fw in gen_name:
            if fw == "gemini":
                return f".gemini/skills/{item_name.replace('-', '_')}"
            return f".{fw}/skills/{item_name}" if fw != "copilot" else f".github/skills/{item_name}"
    return None


def _check_or_write(
    path: Path, content: str, out_of_sync: bool, dry_run: bool, check: bool
) -> bool:
    if check:
        if not path.exists() or path.read_text() != content:
            return True
        return out_of_sync
    _write_file(path, content, dry_run)
    return out_of_sync


def _write_file(path: Path, content: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  [DRY-RUN] Would write: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() == content:
        print(f"  [UNCHANGED] {path}")
        return

    path.write_text(content)
    print(f"  [WROTE] {path}")


def _sync_dir(src: Path, dest: Path, dry_run: bool, check: bool) -> tuple[list[Path], bool]:
    written_files: list[Path] = []
    out_of_sync = False

    if not src.is_dir():
        return written_files, out_of_sync

    for item in src.rglob("*"):
        if not item.is_file():
            continue
        rel_path = item.relative_to(src)
        target_path = dest / rel_path
        content_bytes = item.read_bytes()

        if check:
            if not target_path.exists() or target_path.read_bytes() != content_bytes:
                out_of_sync = True
        else:
            if dry_run:
                print(f"  [DRY-RUN] Would write (bytes): {target_path}")
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if target_path.exists() and target_path.read_bytes() == content_bytes:
                    print(f"  [UNCHANGED] {target_path}")
                else:
                    target_path.write_bytes(content_bytes)
                    print(f"  [WROTE] {target_path}")
        written_files.append(target_path)

    return written_files, out_of_sync
