# app/services/drift_engine.py
"""
Drift engine: compares a resource's current configuration with its approved
baseline and reports every difference.

Detects:
- modified values  (baseline says X, resource now says Y)
- removed values   (baseline has a control, resource no longer has it)
- added values     (resource has a setting that is not in the baseline)

Nested configs are compared key by key using dotted paths.
Lists are compared as whole values (order-sensitive) for now.
"""

from typing import Any

from app.schemas import ChangeType, Finding, FindingType, Resource, Severity
from app.services.normalize import MISSING, flatten, normalize_value

# Default severity for drift on paths that no security rule covers.
# Paths covered by a rule are reported by the rule engine instead, with the
# rule's own severity (see scan_service.py).
DRIFT_SEVERITY: dict[ChangeType, Severity] = {
    ChangeType.MODIFIED: Severity.MEDIUM,
    ChangeType.REMOVED: Severity.MEDIUM,
    ChangeType.ADDED: Severity.LOW,
}


def diff_configs(baseline: dict, current: dict) -> list[dict[str, Any]]:
    """
    Return raw differences between two (possibly nested) config dicts.

    Each item: {"path", "change", "expected", "actual"}
    """
    if not isinstance(baseline, dict):
        raise ValueError("Baseline configuration must be a dictionary.")
    if not isinstance(current, dict):
        raise ValueError("Current configuration must be a dictionary.")

    flat_baseline = {k: normalize_value(v) for k, v in flatten(baseline).items()}
    flat_current = {k: normalize_value(v) for k, v in flatten(current).items()}

    changes: list[dict[str, Any]] = []
    for path in sorted(flat_baseline.keys() | flat_current.keys()):
        expected = flat_baseline.get(path, MISSING)
        actual = flat_current.get(path, MISSING)

        if expected is MISSING:
            changes.append({"path": path, "change": ChangeType.ADDED,
                            "expected": None, "actual": actual})
        elif actual is MISSING:
            changes.append({"path": path, "change": ChangeType.REMOVED,
                            "expected": expected, "actual": None})
        elif expected != actual:
            changes.append({"path": path, "change": ChangeType.MODIFIED,
                            "expected": expected, "actual": actual})

    return changes


def detect_drift(resource: Resource, baseline: dict,
                 ignore_paths: set[str] | None = None) -> list[Finding]:
    """
    Compare one resource against its baseline and return drift findings.

    ignore_paths: dotted paths to skip, typically the paths already evaluated
    by the rule engine, so the same problem is not reported twice.
    """
    ignore_paths = ignore_paths or set()
    findings: list[Finding] = []

    for change in diff_configs(baseline, resource.config):
        if change["path"] in ignore_paths:
            continue

        change_type: ChangeType = change["change"]
        if change_type is ChangeType.REMOVED:
            finding_type = FindingType.MISSING_CONTROL
            title = f"Baseline control '{change['path']}' is missing"
        elif change_type is ChangeType.ADDED:
            finding_type = FindingType.DRIFT
            title = f"Setting '{change['path']}' is not in the approved baseline"
        else:
            finding_type = FindingType.DRIFT
            title = f"'{change['path']}' differs from the approved baseline"

        findings.append(Finding(
            finding_type=finding_type,
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            path=change["path"],
            expected=change["expected"],
            actual=change["actual"],
            severity=DRIFT_SEVERITY[change_type],
            title=title,
            change=change_type,
            remediation="Restore the approved value, or review and approve "
                        "this change as the new baseline.",
        ))

    return findings
