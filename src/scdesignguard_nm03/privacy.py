"""Public/private artifact separation and path-safety filter."""

import copy
import posixpath
import re
from pathlib import PurePosixPath
from typing import Any, Dict, List, Tuple

PRIVATE_TOKENS = re.compile(r"(^|_)(patient|participant|donor|sample|barcode|email|name|mrn|dob|private|controlled|secret|token|credential)(_|$)", re.I)
PUBLIC_ALLOWLIST = {
    "compiler", "compiler_version", "api_version", "schema_version",
    "source_contract_sha256", "compiled_contract_sha256", "contract_sha256",
    "task_id", "terminal_state", "state_precedence", "reason_codes",
    "reason_ledger", "reason_code", "definition", "claim_limit",
    "biological_truth_certified", "scientific_analysis_executed",
    "separate_authorization_required", "abstention_calibration", "policy_id",
    "score", "probability_interpretation", "status", "valid", "errors",
    "path", "code", "message", "estimability_proof", "method", "design_rank",
    "augmented_with_contrast_rank", "contrast_dimension", "estimable",
    "floating_tolerance_used",
}


def public_release_view(value: Any) -> Dict[str, Any]:
    """Return a redacted deep copy plus an auditable redaction ledger."""
    redactions: List[str] = []

    def visit(obj: Any, path: str) -> Any:
        if isinstance(obj, dict):
            out = {}
            for key in sorted(obj):
                child = f"{path}.{key}"
                if PRIVATE_TOKENS.search(str(key)) or key not in PUBLIC_ALLOWLIST:
                    redactions.append(child)
                    continue
                out[key] = visit(obj[key], child)
            return out
        if isinstance(obj, list):
            return [visit(item, f"{path}[{i}]") for i, item in enumerate(obj)]
        return copy.deepcopy(obj)

    return {
        "artifact": visit(value, "$"),
        "redacted_paths": redactions,
        "filter_version": "1.0.0",
        "private_values_copied": False,
    }


def is_safe_output_path(path: str) -> bool:
    if not path or "\x00" in path or "\\" in path:
        return False
    pure = PurePosixPath(path)
    return (not pure.is_absolute() and all(part not in ("", ".", "..") for part in pure.parts)
            and posixpath.normpath(path) == path)
