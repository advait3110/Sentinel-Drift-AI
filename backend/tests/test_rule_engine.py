import pytest

from app.schemas import FindingType, Resource, Severity
from app.services.rule_engine import Rule, evaluate_resource, load_rules


def rule(**overrides) -> Rule:
    data = {"id": "T-1", "title": "Encryption off", "path": "encrypted",
            "operator": "equals", "value": True, "severity": "high", "on_missing": "fail"}
    data.update(overrides)
    return Rule.model_validate(data)


def res(config, rtype="generic") -> Resource:
    return Resource(resource_id="r1", resource_type=rtype, config=config)


def test_shipped_rules_load():
    rules = load_rules()
    assert len(rules) == 10
    assert len({r.id for r in rules}) == 10


def test_pass_produces_no_finding():
    assert evaluate_resource(res({"encrypted": True}), [rule()]) == []


def test_fail_produces_misconfiguration():
    [f] = evaluate_resource(res({"encrypted": False}), [rule()])
    assert f.finding_type is FindingType.MISCONFIGURATION
    assert f.severity is Severity.HIGH


def test_missing_control_fails_not_passes():
    # The original bug: a missing key was silently treated as compliant.
    [f] = evaluate_resource(res({}), [rule()])
    assert f.finding_type is FindingType.MISSING_CONTROL
    assert f.severity is Severity.HIGH


def test_null_value_counts_as_missing():
    [f] = evaluate_resource(res({"encrypted": None}), [rule()])
    assert f.finding_type is FindingType.MISSING_CONTROL


def test_on_missing_info_and_skip():
    [f] = evaluate_resource(res({}), [rule(on_missing="info")])
    assert f.severity is Severity.INFO
    assert evaluate_resource(res({}), [rule(on_missing="skip")]) == []


def test_string_boolean_normalized():
    assert evaluate_resource(res({"encrypted": "true"}), [rule()]) == []


def test_nested_path():
    r = rule(path="encryption.enabled")
    assert evaluate_resource(res({"encryption": {"enabled": True}}), [r]) == []
    assert len(evaluate_resource(res({"encryption": {"enabled": False}}), [r])) == 1


def test_resource_type_filter():
    r = rule(resource_types=["s3_bucket"])
    assert evaluate_resource(res({"encrypted": False}, "iam_user"), [r]) == []
    assert len(evaluate_resource(res({"encrypted": False}, "s3_bucket"), [r])) == 1


def test_numeric_operators():
    r = rule(path="min_tls", operator="gte", value=1.2)
    assert evaluate_resource(res({"min_tls": 1.3}), [r]) == []
    assert len(evaluate_resource(res({"min_tls": 1.0}), [r])) == 1
    assert len(evaluate_resource(res({"min_tls": "abc"}), [r])) == 1


def test_bad_rule_rejected():
    with pytest.raises(ValueError):
        rule(operator="in", value="not-a-list")
    with pytest.raises(ValueError):
        rule(severity="severe")
