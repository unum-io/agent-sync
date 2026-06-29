# Contributing to agent-sync

## Development setup

```bash
git clone https://github.com/unum-io/agent-sync.git
cd agent-sync
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Adding a new framework

1. Add `generate_<framework>()` in `src/agent_sync/generators/<framework>.py`
2. Register it in `src/agent_sync/generators/__init__.py`
3. Add the framework name to `ALL_FRAMEWORKS` in `src/agent_sync/config.py`
4. Add a golden test in `tests/test_generators.py`
5. Update the README framework table

Generators should return `list[tuple[Path, str]]` of `(output_path, content)`.

## Release

1. Bump version in `src/agent_sync/__init__.py` and `pyproject.toml`
2. Tag `vX.Y.Z` and push — CI publishes to PyPI via trusted publishing
