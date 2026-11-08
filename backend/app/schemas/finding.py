# app/schemas/finding.py
"""
Typed data shapes shared by every engine in the scan pipeline.

Every engine (drift, rules, risk) produces or consumes these models, so the
API, database layer and AI layer all see one consistent structure.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# Higher number = worse. Used for sorting and "worst finding" logic.
SEVERITY_RANK: dict[Severity, int] = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
    Severity.INFO: 0,
}


class FindingType(str, Enum):
    DRIFT = "drift"                        # differs from the approved baseline
    MISCONFIGURATION = "misconfiguration"  # violates a security rule
    MISSING_CONTROL = "missing_control"    # control could not be observed


class ChangeType(str, Enum):
    ADDED = "added"        # present now, not in baseline
    REMOVED = "removed"    # in baseline, missing now
    MODIFIED = "modified"  # present in both, value differs


class Resource(BaseModel):
    """One configurable thing: a bucket, a user, a security group, a VM..."""

    resource_id: str
    resource_type: str = "generic"
    config: dict[str, Any]


class Finding(BaseModel):
    finding_type: FindingType
    resource_id: str
    resource_type: str
    path: str                              # dotted path, e.g. "encryption.enabled"
    expected: Any = None
    actual: Any = None
    severity: Severity
    title: str
    rule_id: str | None = None
    change: ChangeType | None = None       # only set for drift findings
    remediation: str | None = None
    frameworks: list[str] = Field(default_factory=list)


class RiskSummary(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    findings_count: int
    severity_counts: dict[str, int]
    explanation: list[str]                 # human-readable reasons for the score


class ScanResult(BaseModel):
    scanned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resources_scanned: int
    findings: list[Finding]
    risk: RiskSummary
