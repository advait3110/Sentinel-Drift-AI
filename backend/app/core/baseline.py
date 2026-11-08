# app/core/baseline.py
"""
Approved security baselines, per resource type.

Temporary in-code store. Next step: move baselines into the database
(per organization, versioned, with an approval record) and keep this file
only as the default used when an org has not approved its own baseline yet.
"""

from copy import deepcopy

DEFAULT_BASELINES: dict[str, dict] = {
    # Used for any resource type without a specific baseline,
    # including flat single-resource uploads.
    "generic": {
        "public": False,
        "encrypted": True,
        "root_access": False,
    },
    # Examples for when uploads include resource types:
    "s3_bucket": {
        "public": False,
        "encrypted": True,
        "versioning": True,
        "logging_enabled": True,
        "https_only": True,
    },
    "iam_user": {
        "mfa_enabled": True,
        "iam_admin": False,
    },
}


def get_baseline(resource_type: str) -> dict:
    """Return a copy of the baseline for this resource type (never the original)."""
    return deepcopy(DEFAULT_BASELINES.get(resource_type, DEFAULT_BASELINES["generic"]))


# Backward compatibility for code that still imports BASELINE.
BASELINE = get_baseline("generic")
