# app/services/normalize.py
"""
Helpers shared by the drift engine and the rule engine.

- flatten():         turns nested dicts into {"a.b.c": value}
- get_path():        reads a dotted path from a nested dict
- normalize_value(): makes "true", "Yes", "enabled", 1 etc. compare equal to True
"""

from typing import Any

# Sentinel meaning "this key does not exist" (different from a value of None).
MISSING = object()

_TRUE_STRINGS = {"true", "yes", "on", "enabled", "enable", "1"}
_FALSE_STRINGS = {"false", "no", "off", "disabled", "disable", "0"}


def normalize_value(value: Any) -> Any:
    """Normalize common string spellings of booleans and trim strings."""
    if isinstance(value, str):
        stripped = value.strip()
        lowered = stripped.lower()
        if lowered in _TRUE_STRINGS:
            return True
        if lowered in _FALSE_STRINGS:
            return False
        return stripped
    if isinstance(value, list):
        return [normalize_value(v) for v in value]
    if isinstance(value, dict):
        return {k: normalize_value(v) for k, v in value.items()}
    return value


def flatten(obj: dict, prefix: str = "") -> dict[str, Any]:
    """
    Flatten a nested dict into dotted paths.

    {"encryption": {"enabled": False}} -> {"encryption.enabled": False}

    Empty dicts are kept as leaf values so "the whole block was emptied" is
    still visible as a change. Lists are kept as leaf values.
    """
    out: dict[str, Any] = {}
    for key, value in obj.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict) and value:
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def get_path(obj: dict, path: str) -> Any:
    """Return the value at a dotted path, or MISSING if any part is absent."""
    current: Any = obj
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return MISSING
        current = current[part]
    return current
