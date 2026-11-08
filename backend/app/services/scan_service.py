# app/services/scan_service.py
"""
One entry point for a full scan: payload -> resources -> findings -> risk.

Call run_scan() from upload.py instead of calling the drift, rule and risk
engines separately.

Accepted payload shapes:

1. A flat single-resource config (what you upload today):
     {"public": true, "encrypted": false, ...}

2. Multiple resources:
     {"resources": [
         {"resource_id": "bucket-logs", "resource_type": "s3_bucket",
          "config": {"public": false, "encrypted": true}},
         ...
     ]}
   "id" / "type" are accepted as short forms of resource_id / resource_type.
"""

from typing import Any

from app.core.baseline import get_baseline
from app.schemas import SEVERITY_RANK, Finding, Resource, ScanResult
from app.services.drift_engine import detect_drift
from app.services.risk_engine import calculate_risk_score
from app.services.rule_engine import evaluate_resource, get_rules, rule_paths_for


def extract_resources(payload: Any, default_id: str = "uploaded-config") -> list[Resource]:
    if not isinstance(payload, dict):
        raise ValueError("Configuration must be a JSON object.")

    if "resources" not in payload:
        return [Resource(resource_id=default_id, resource_type="generic", config=payload)]

    items = payload["resources"]
    if not isinstance(items, list) or not items:
        raise ValueError("'resources' must be a non-empty list.")

    resources: list[Resource] = []
    seen: set[str] = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"resources[{i}] must be an object.")
        config = item.get("config")
        if not isinstance(config, dict):
            raise ValueError(f"resources[{i}].config must be an object.")
        resource_id = str(item.get("resource_id") or item.get("id") or f"resource-{i}")
        if resource_id in seen:
            raise ValueError(f"Duplicate resource id '{resource_id}'.")
        seen.add(resource_id)
        resources.append(Resource(
            resource_id=resource_id,
            resource_type=str(item.get("resource_type") or item.get("type") or "generic"),
            config=config,
        ))
    return resources


def run_scan(payload: Any) -> ScanResult:
    resources = extract_resources(payload)
    rules = get_rules()
    findings: list[Finding] = []

    for resource in resources:
        # 1. Security rules (own severity, remediation, frameworks).
        findings.extend(evaluate_resource(resource, rules))

        # 2. Baseline drift, skipping paths the rules already judged,
        #    so one problem is not reported twice.
        covered = rule_paths_for(resource.resource_type, rules)
        findings.extend(detect_drift(resource, get_baseline(resource.resource_type),
                                     ignore_paths=covered))

    # Worst first, then stable by resource and path.
    findings.sort(key=lambda f: (-SEVERITY_RANK[f.severity], f.resource_id, f.path))

    return ScanResult(
        resources_scanned=len(resources),
        findings=findings,
        risk=calculate_risk_score(findings),
    )
