"""Load TOML source files (manifest.toml, config.toml)."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path


def load_toml(path: Path) -> dict:
    """Parse a TOML file, exiting with a readable error if it is malformed."""
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        print(f"ERROR: {path}: {e}", file=sys.stderr)
        sys.exit(1)


def reject_legacy_yaml(ai_dir: Path) -> None:
    """Exit with a migration hint if old YAML source files are still present."""
    legacy = [p for p in (ai_dir / "manifest.yaml", ai_dir / "config.yaml") if p.exists()]
    if legacy:
        names = ", ".join(str(p) for p in legacy)
        print(
            f"ERROR: found {names}. agent-sync now reads TOML; "
            "convert to manifest.toml / config.toml (see README).",
            file=sys.stderr,
        )
        sys.exit(1)
