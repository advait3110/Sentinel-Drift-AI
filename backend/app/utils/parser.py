# app/utils/parser.py
"""Turn an uploaded file into a config dict. Accepts JSON and YAML."""

import json

import yaml

from app.core.config import MAX_UPLOAD_BYTES

ALLOWED_EXTENSIONS = (".json", ".yaml", ".yml")


def parse_config(content: bytes, filename: str) -> dict:
    name = (filename or "").lower()
    if not name.endswith(ALLOWED_EXTENSIONS):
        raise ValueError("Only .json, .yaml or .yml files are supported.")

    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError(f"File is too large. Maximum size is {MAX_UPLOAD_BYTES // 1000} KB.")

    try:
        text = content.decode("utf-8-sig")  # also strips a Windows BOM
    except UnicodeDecodeError:
        raise ValueError("File must be UTF-8 encoded text.") from None

    if not text.strip():
        raise ValueError("File is empty.")

    try:
        if name.endswith(".json"):
            data = json.loads(text)
        else:
            data = yaml.safe_load(text)  # safe_load never executes YAML tags
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno}).") from None
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {exc}") from None

    if not isinstance(data, dict):
        raise ValueError("The file must contain a JSON/YAML object at the top level, not a list or value.")

    return data
