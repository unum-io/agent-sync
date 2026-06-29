"""Minimal YAML parser (stdlib only) for manifest.yaml and config.yaml."""

from __future__ import annotations


def parse_yaml(text: str) -> dict:
    """
    Parse a restricted YAML subset used by manifest.yaml and config.yaml.

    Supports:
    - Top-level scalar keys (``key: value``)
    - Top-level keys mapping to lists of dicts (manifest items)
    - Top-level keys mapping to lists of scalars (``frameworks``)
    - One level of nested mapping (``opencode: watcher_ignore: [...]``)
    """
    result: dict = {}
    current_top_key: str | None = None
    current_list: list | None = None
    current_item: dict | None = None
    nested_key: str | None = None
    nested_list: list | None = None

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip())

        # Top-level key (no indent)
        if indent == 0 and stripped.endswith(":") and not stripped.startswith("- "):
            key = stripped[:-1].strip()
            current_top_key = key
            current_list = []
            current_item = None
            nested_key = None
            nested_list = None
            result[key] = current_list
            continue

        # Top-level scalar: key: value
        if indent == 0 and ":" in stripped:
            k, v = stripped.split(":", 1)
            result[k.strip()] = yaml_scalar(v.strip())
            current_top_key = None
            current_list = None
            current_item = None
            continue

        # Nested mapping key under a top-level dict value (indent 2)
        if indent == 2 and stripped.endswith(":") and not stripped.startswith("- "):
            nested_key = stripped[:-1].strip()
            nested_list = []
            if current_top_key and isinstance(result.get(current_top_key), dict):
                result[current_top_key][nested_key] = nested_list
            elif current_top_key:
                result[current_top_key] = {nested_key: nested_list}
            continue

        # List item at indent 2 under nested key
        if indent == 2 and stripped.startswith("- ") and nested_list is not None:
            val = stripped[2:].strip()
            if ":" in val and nested_key is None:
                pass
            else:
                nested_list.append(yaml_scalar(val.split(":", 1)[0].strip() if nested_key else val))
            continue

        # List item start (manifest style)
        if stripped.startswith("- "):
            if current_list is None:
                # Scalar list at top level without preceding key setup
                continue
            # Scalar list item (frameworks)
            if current_item is None and indent <= 2:
                val = stripped[2:].strip()
                if ":" not in val:
                    current_list.append(yaml_scalar(val))
                    continue
            current_item = {}
            if isinstance(current_list, list):
                current_list.append(current_item)
            kv = stripped[2:].strip()
            if ":" in kv:
                k, v = kv.split(":", 1)
                current_item[k.strip()] = yaml_scalar(v.strip())
            continue

        # Continuation key inside a list item
        if current_item is not None and ":" in stripped:
            k, v = stripped.split(":", 1)
            current_item[k.strip()] = yaml_scalar(v.strip())
            continue

        # Inline list: frameworks: [a, b, c]
        if indent == 0 or (indent == 2 and "[" in stripped):
            pass

    # Post-process inline lists like frameworks: [copilot, cursor]
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped and "[" in stripped:
            k, v = stripped.split(":", 1)
            k = k.strip()
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                inner = v[1:-1]
                items = [yaml_scalar(x.strip().strip("'\"")) for x in inner.split(",") if x.strip()]
                result[k] = items

    return result


def yaml_scalar(val: str):
    """Convert a YAML scalar string to a Python value."""
    if val == "" or val == "~" or val == "null":
        return None
    if val in ("true", "True", "yes"):
        return True
    if val in ("false", "False", "no"):
        return False
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        return val[1:-1]
    return val
