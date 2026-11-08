import pytest

from app.utils.parser import parse_config


def test_json():
    assert parse_config(b'{"public": false}', "a.json") == {"public": False}


def test_json_with_windows_bom():
    assert parse_config('﻿{"a": 1}'.encode("utf-8"), "a.json") == {"a": 1}


def test_yaml():
    assert parse_config(b"public: false\nencryption:\n  enabled: true\n", "a.yml") == {
        "public": False, "encryption": {"enabled": True}}


@pytest.mark.parametrize("content,name", [
    (b'{"a": 1}', "a.txt"),          # wrong extension
    (b"", "a.json"),                 # empty
    (b"   ", "a.json"),              # whitespace only
    (b"{bad json", "a.json"),        # invalid JSON
    (b"[1, 2]", "a.json"),           # not an object
    (b"a: [unclosed", "a.yaml"),     # invalid YAML
    (b"\xff\xfe\x00", "a.json"),     # not UTF-8
    (b"!!python/object/apply:os.system ['echo hi']", "a.yaml"),  # unsafe YAML tag
])
def test_rejected(content, name):
    with pytest.raises(ValueError):
        parse_config(content, name)


def test_too_large(monkeypatch):
    monkeypatch.setattr("app.utils.parser.MAX_UPLOAD_BYTES", 10)
    with pytest.raises(ValueError, match="too large"):
        parse_config(b'{"a": "0123456789"}', "a.json")
