# app/services/risk_engine.py
"""
Risk engine: turns findings into an explainable 0-100 score and risk level.

- Every severity has a fixed deduction (info deducts nothing).
- The worst finding caps the risk level: one critical finding can never be
  rated better than "High Risk", one high finding never better than "Moderate".
- The result includes counts and plain-language reasons, so the score can be
  explained to an auditor without reading code.
"""

from app.schemas import SEVERITY_RANK, Finding, RiskSummary, Severity

SEVERITY_WEIGHTS: dict[Severity, int] = {
    Severity.CRITICAL: 40,
    Severity.HIGH: 20,
    Severity.MEDIUM: 8,
    Severity.LOW: 3,
    Severity.INFO: 0,
}

# Best-to-worst order of levels.
RISK_LEVELS = ["Excellent", "Good", "Moderate", "High Risk", "Critical"]

# The best level allowed when a finding of this severity exists.
LEVEL_CAP: dict[Severity, str] = {
    Severity.CRITICAL: "High Risk",
    Severity.HIGH: "Moderate",
    Severity.MEDIUM: "Good",
}


def level_from_score(score: int) -> str:
    """
    90-100 -> Excellent
    75-89  -> Good
    50-74  -> Moderate
    25-49  -> High Risk
    0-24   -> Critical
    """
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 50:
        return "Moderate"
    if score >= 25:
        return "High Risk"
    return "Critical"


def get_risk_level(score: int, findings: list[Finding]) -> str:
    """Score-based level, made worse if the worst finding demands it."""
    level = level_from_score(score)
    if not findings:
        return level

    worst = max((f.severity for f in findings), key=lambda s: SEVERITY_RANK[s])
    cap = LEVEL_CAP.get(worst)
    if cap and RISK_LEVELS.index(level) < RISK_LEVELS.index(cap):
        return cap
    return level


def calculate_risk_score(findings: list[Finding]) -> RiskSummary:
    if not isinstance(findings, list):
        raise ValueError("Findings must be provided as a list.")

    counts = {s.value: 0 for s in Severity}
    for finding in findings:
        if not isinstance(finding, Finding):
            raise TypeError(f"Expected Finding, got {type(finding).__name__}.")
        counts[finding.severity.value] += 1

    deduction = sum(SEVERITY_WEIGHTS[Severity(sev)] * n for sev, n in counts.items())
    score = max(100 - deduction, 0)
    level = get_risk_level(score, findings)

    explanation: list[str] = []
    for sev in Severity:
        n = counts[sev.value]
        if n and SEVERITY_WEIGHTS[sev]:
            explanation.append(
                f"{n} {sev.value} finding(s) x {SEVERITY_WEIGHTS[sev]} = "
                f"-{n * SEVERITY_WEIGHTS[sev]} points"
            )
    if deduction > 100:
        explanation.append(f"Total deductions ({deduction}) exceed 100; score floored at 0.")
    if level != level_from_score(score):
        explanation.append(
            f"Risk level raised to '{level}' because at least one "
            f"{max((f.severity for f in findings), key=lambda s: SEVERITY_RANK[s]).value} "
            f"finding exists."
        )
    if not explanation:
        explanation.append("No findings that reduce the score.")

    return RiskSummary(
        risk_score=score,
        risk_level=level,
        findings_count=len(findings),
        severity_counts=counts,
        explanation=explanation,
    )
