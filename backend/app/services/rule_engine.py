# app/services/rule_engine.py
"""
Rule engine: evaluates resources against security rules loaded from YAML.

Rules live in app/rules/*.yaml. A control that cannot be observed is NOT
treated as passing: each rule's `on_missing` setting decides what happens.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator

from app.schemas import Finding, FindingType, Resource, Severity
from app.services.normalize import MISSING, get_path, normalize_value

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"

Operator = Literal["equals", "not_equals", "in", "not_in", "gte", "lte", "exists"]
OnMissing = Literal["fail", "skip", "info"]


class Rule(BaseModel):
    id: str
    title: str
    resource_types: list[str] = Field(default_factory=lambda: ["*"])
    path: str
    operator: Operator = "equals"
    value: Any = None
    severity: Severity
    on_missing: OnMissing = "fail"
    remediation: str | None = None
    frameworks: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_value(self) -> "Rule":
        if self.operator in ("in", "not_in") and not isinstance(self.value, list):
            raise ValueError(f"Rule {self.id}: operator '{self.operator}' needs a list value.")
        if self.operator in ("gte", "lte") and not isinstance(self.value, (int, float)):
            raise ValueError(f"Rule {self.id}: operator '{self.operator}' needs a numeric value.")
        return self

    def applies_to(self, resource_type: str) -> bool:
        return "*" in self.resource_types or resource_type in self.resource_types

    @property
    def expected_description(self) -> Any:
        """What the finding should show as 'expected'."""
        if self.operator == "exists":
            return "<present>"
        if self.operator == "not_equals":
            return f"not {self.value!r}"
        if self.operator == "not_in":
            return f"not in {self.value!r}"
        if self.operator == "gte":
            return f">= {self.value}"
        if self.operator == "lte":
            return f"<= {self.value}"
        return self.value


def load_rules(rules_dir: Path = RULES_DIR) -> list[Rule]:
    """Load and validate every rule file. Fails loudly on bad or duplicate rules."""
    rules: list[Rule] = []
    seen_ids: set[str] = set()

    files = sorted([*rules_dir.glob("*.yaml"), *rules_dir.glob("*.yml")])
    for file in files:
        raw = yaml.safe_load(file.read_text(encoding="utf-8")) or []
        if not isinstance(raw, list):
            raise ValueError(f"{file.name}: rule file must contain a list of rules.")
        for item in raw:
            rule = Rule.model_validate(item)
            if rule.id in seen_ids:
                raise ValueError(f"Duplicate rule id '{rule.id}' in {file.name}.")
            seen_ids.add(rule.id)
            rules.append(rule)

    return rules


@lru_cache(maxsize=1)
def get_rules() -> tuple[Rule, ...]:
    """Cached rule set for the running app. Call get_rules.cache_clear() to reload."""
    return tuple(load_rules())


def _passes(rule: Rule, actual: Any) -> bool:
    expected = normalize_value(rule.value)
    if rule.operator == "exists":
        return True  # reaching here means the value exists
    if rule.operator == "equals":
        return actual == expected
    if rule.operator == "not_equals":
        return actual != expected
    if rule.operator == "in":
        return actual in expected
    if rule.operator == "not_in":
        return actual not in expected
    if rule.operator in ("gte", "lte"):
        if isinstance(actual, bool) or not isinstance(actual, (int, float)):
            return False  # non-numeric value can't satisfy a numeric rule
        return actual >= expected if rule.operator == "gte" else actual <= expected
    raise ValueError(f"Unknown operator '{rule.operator}' in rule {rule.id}.")


def evaluate_resource(resource: Resource,
                      rules: list[Rule] | tuple[Rule, ...] | None = None) -> list[Finding]:
    """Evaluate one resource against all applicable rules."""
    rules = get_rules() if rules is None else rules
    findings: list[Finding] = []

    for rule in rules:
        if not rule.applies_to(resource.resource_type):
            continue

        raw_value = get_path(resource.config, rule.path)

        if raw_value is MISSING or raw_value is None:
            if rule.on_missing == "skip":
                continue
            findings.append(Finding(
                finding_type=FindingType.MISSING_CONTROL,
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                path=rule.path,
                expected=rule.expected_description,
                actual=None,
                severity=rule.severity if rule.on_missing == "fail" else Severity.INFO,
                title=f"Control could not be verified: {rule.title}",
                rule_id=rule.id,
                remediation=rule.remediation,
                frameworks=rule.frameworks,
            ))
            continue

        actual = normalize_value(raw_value)
        if not _passes(rule, actual):
            findings.append(Finding(
                finding_type=FindingType.MISCONFIGURATION,
                resource_id=resource.resource_id,
                resource_type=resource.resource_type,
                path=rule.path,
                expected=rule.expected_description,
                actual=actual,
                severity=rule.severity,
                title=rule.title,
                rule_id=rule.id,
                remediation=rule.remediation,
                frameworks=rule.frameworks,
            ))

    return findings


def rule_paths_for(resource_type: str,
                   rules: list[Rule] | tuple[Rule, ...] | None = None) -> set[str]:
    """Paths the rule engine already evaluates for this resource type."""
    rules = get_rules() if rules is None else rules
    return {r.path for r in rules if r.applies_to(resource_type)}
