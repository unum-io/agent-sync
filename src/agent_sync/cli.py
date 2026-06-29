"""CLI entry point for agent-sync."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from importlib import resources
from pathlib import Path

from agent_sync.sync import sync


def _default_repo_root() -> Path:
    return Path.cwd()


def _install_hooks(repo_root: Path) -> int:
    hooks_dir = repo_root / ".git" / "hooks"
    if not hooks_dir.is_dir():
        print("ERROR: .git/hooks not found. Run from a git repository.", file=sys.stderr)
        return 1

    hook_src = resources.files("agent_sync") / "hooks" / "post-merge"
    hook_dest = hooks_dir / "post-merge"

    shutil.copy2(hook_src, hook_dest)
    hook_dest.chmod(hook_dest.stat().st_mode | 0o111)
    print(f"Installed post-merge hook at {hook_dest}")
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Sync AI agent instructions from .ai/ to all framework configs",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: current working directory)",
    )
    parser.add_argument(
        "--source-dir",
        default=".ai",
        help="Source directory relative to repo root (default: .ai)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if files are out of sync (exit 1 if diff found)",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("install-hooks", help="Install git post-merge hook")

    args = parser.parse_args(argv)
    repo_root = (args.repo_root or _default_repo_root()).resolve()

    if args.command == "install-hooks":
        sys.exit(_install_hooks(repo_root))

    if args.check:
        result = sync(
            repo_root,
            source_dir=args.source_dir,
            check=True,
        )
        if result == 1:
            print("ALERT: AI agent instructions are OUT OF SYNC.")
        else:
            print("AI agent instructions are up to date.")
        sys.exit(result)

    ai_dir = repo_root / args.source_dir
    print(f"Syncing from {ai_dir / 'manifest.yaml'} ...")
    print(f"Repo root: {repo_root}")
    if args.dry_run:
        print("DRY-RUN MODE — no files will be written\n")
    print()

    written = sync(repo_root, source_dir=args.source_dir, dry_run=args.dry_run)
    print(f"\n{'Would generate' if args.dry_run else 'Generated'} {len(written)} files.")


if __name__ == "__main__":
    main()
