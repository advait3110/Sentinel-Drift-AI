from app.schemas import Finding, FindingType, Severity
from app.services.risk_engine import calculate_risk_score


def f(sev: Severity) -> Finding:
    return Finding(finding_type=FindingType.MISCONFIGURATION, resource_id="r",
                   resource_type="generic", path="p", severity=sev, title="t")


def test_no_findings_is_excellent():
    r = calculate_risk_score([])
    assert (r.risk_score, r.risk_level) == (100, "Excellent")


def test_single_critical_is_never_moderate():
    r = calculate_risk_score([f(Severity.CRITICAL)])
    assert r.risk_score == 60
    assert r.risk_level == "High Risk"


def test_single_high_capped_at_moderate():
    r = calculate_risk_score([f(Severity.HIGH)])
    assert r.risk_score == 80
    assert r.risk_level == "Moderate"


def test_info_does_not_deduct():
    r = calculate_risk_score([f(Severity.INFO)] * 5)
    assert r.risk_score == 100


def test_floor_at_zero_and_counts_kept():
    r = calculate_risk_score([f(Severity.CRITICAL)] * 5)
    assert r.risk_score == 0
    assert r.risk_level == "Critical"
    assert r.severity_counts["critical"] == 5
    assert any("floored" in line for line in r.explanation)
