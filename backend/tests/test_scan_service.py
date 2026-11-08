import pytest

from app.schemas import FindingType, Severity
from app.services.scan_service import extract_resources, run_scan

SECURE_FLAT = {
    "public": False, "encrypted": True, "root_access": False, "mfa_enabled": True,
    "logging_enabled": True, "backup_enabled": True, "versioning": True,
    "https_only": True, "security_group_open": False, "iam_admin": False,
}


def test_secure_config_scores_100():
    result = run_scan(SECURE_FLAT)
    assert result.findings == []
    assert result.risk.risk_score == 100


def test_public_bucket_reported_once_not_twice():
    # "public" is both in the baseline and a rule; it must appear once.
    result = run_scan({**SECURE_FLAT, "public": True})
    public = [x for x in result.findings if x.path == "public"]
    assert len(public) == 1
    assert public[0].rule_id == "SD-001"
    assert public[0].severity is Severity.CRITICAL


def test_deleting_a_control_does_not_hide_it():
    cfg = dict(SECURE_FLAT)
    del cfg["mfa_enabled"]
    result = run_scan(cfg)
    [mfa] = [x for x in result.findings if x.path == "mfa_enabled"]
    assert mfa.finding_type is FindingType.MISSING_CONTROL
    assert result.risk.risk_score < 100


def test_unknown_extra_setting_is_drift():
    result = run_scan({**SECURE_FLAT, "debug_mode": True})
    [d] = [x for x in result.findings if x.path == "debug_mode"]
    assert d.finding_type is FindingType.DRIFT


def test_multi_resource_payload_sorted_worst_first():
    payload = {"resources": [
        {"id": "user-1", "type": "iam_user", "config": {"mfa_enabled": True}},
        {"id": "bucket-1", "type": "s3_bucket", "config": {"public": True}},
    ]}
    result = run_scan(payload)
    assert result.resources_scanned == 2
    assert result.findings[0].severity is Severity.CRITICAL
    assert {x.resource_id for x in result.findings} == {"user-1", "bucket-1"}


def test_bad_payloads_rejected():
    for bad in ([], {"resources": []}, {"resources": [{"id": "a", "config": 1}]},
                {"resources": [{"id": "a", "config": {}}, {"id": "a", "config": {}}]}):
        with pytest.raises(ValueError):
            extract_resources(bad)


def test_result_is_json_serializable():
    data = run_scan({**SECURE_FLAT, "public": True}).model_dump(mode="json")
    assert data["findings"][0]["severity"] == "critical"


def test_rules_only_apply_to_relevant_resource_types():
    # An IAM user must not be flagged for bucket controls like encryption.
    result = run_scan({"resources": [
        {"id": "bot", "type": "iam_user", "config": {"mfa_enabled": True, "iam_admin": False}},
    ]})
    assert result.findings == []
    assert result.risk.risk_score == 100
