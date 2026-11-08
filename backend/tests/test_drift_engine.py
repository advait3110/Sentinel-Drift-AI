from app.schemas import ChangeType, FindingType, Resource, Severity
from app.services.drift_engine import detect_drift, diff_configs


def test_no_drift_when_identical():
    cfg = {"public": False, "encryption": {"enabled": True}}
    assert diff_configs(cfg, dict(cfg)) == []


def test_modified_nested_value():
    changes = diff_configs({"encryption": {"enabled": True}},
                           {"encryption": {"enabled": False}})
    assert changes == [{"path": "encryption.enabled", "change": ChangeType.MODIFIED,
                        "expected": True, "actual": False}]


def test_added_and_removed():
    changes = diff_configs({"a": 1, "b": 2}, {"a": 1, "c": 3})
    by_path = {c["path"]: c["change"] for c in changes}
    assert by_path == {"b": ChangeType.REMOVED, "c": ChangeType.ADDED}


def test_string_booleans_are_not_drift():
    assert diff_configs({"public": False}, {"public": "false"}) == []
    assert diff_configs({"public": False}, {"public": "Disabled"}) == []


def test_detect_drift_respects_ignore_paths():
    r = Resource(resource_id="r1", config={"public": True, "extra": 1})
    findings = detect_drift(r, {"public": False}, ignore_paths={"public"})
    assert [f.path for f in findings] == ["extra"]
    assert findings[0].severity is Severity.LOW


def test_removed_control_is_missing_control_finding():
    r = Resource(resource_id="r1", config={})
    [f] = detect_drift(r, {"tls_version": "1.2"})
    assert f.finding_type is FindingType.MISSING_CONTROL
    assert f.change is ChangeType.REMOVED
