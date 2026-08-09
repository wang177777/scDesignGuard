"""Deterministic Design Contract Compiler."""

import copy
import hashlib
import json
import posixpath
import re
from pathlib import PurePosixPath
from typing import Any, Dict, Iterable, List

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_TOP = {
    "schema_version", "task_id", "identity", "governance", "design",
    "count_source", "evidence", "robustness", "uncertainty", "claims",
}
ALLOWED_TOP = REQUIRED_TOP | {"sources"}


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _safe_relative_path(value: str) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        return False
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        return False
    return posixpath.normpath(value) == value


def validate_contract(contract: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return deterministic structural validation errors; never modifies input."""
    errors: List[Dict[str, str]] = []
    if not isinstance(contract, dict):
        return [{"path": "$", "code": "TYPE", "message": "contract must be an object"}]
    for key in sorted(REQUIRED_TOP - set(contract)):
        errors.append({"path": "$", "code": "REQUIRED", "message": f"missing {key}"})
    for key in sorted(set(contract) - ALLOWED_TOP):
        errors.append({"path": f"$.{key}", "code": "ADDITIONAL_PROPERTY", "message": "field is not allowed by schema 1.0.0"})
    if contract.get("schema_version") != "1.0.0":
        errors.append({"path": "$.schema_version", "code": "CONST", "message": "must equal 1.0.0"})
    if not isinstance(contract.get("task_id"), str) or not contract.get("task_id"):
        errors.append({"path": "$.task_id", "code": "TYPE", "message": "nonempty string required"})
    identity = contract.get("identity", {})
    if not isinstance(identity, dict):
        errors.append({"path": "$.identity", "code": "TYPE", "message": "object required"})
    else:
        expected_identity = {"binding_status", "dataset_id", "version", "sha256"}
        for key in sorted(expected_identity - set(identity)):
            errors.append({"path": f"$.identity.{key}", "code": "REQUIRED", "message": "field is required"})
        for key in sorted(set(identity) - expected_identity):
            errors.append({"path": f"$.identity.{key}", "code": "ADDITIONAL_PROPERTY", "message": "field is not allowed"})
        if identity.get("binding_status") not in ("EXACT", "UNBOUND"):
            errors.append({"path": "$.identity.binding_status", "code": "ENUM", "message": "EXACT or UNBOUND required"})
        for key in ("dataset_id", "version", "sha256"):
            if not isinstance(identity.get(key), str):
                errors.append({"path": f"$.identity.{key}", "code": "TYPE", "message": "string required"})
        if identity.get("binding_status") == "EXACT":
            for key in ("dataset_id", "version"):
                if not identity.get(key):
                    errors.append({"path": f"$.identity.{key}", "code": "MIN_LENGTH", "message": "nonempty string required for EXACT binding"})
            if not SHA256_RE.fullmatch(identity.get("sha256", "")):
                errors.append({"path": "$.identity.sha256", "code": "PATTERN", "message": "lowercase SHA-256 required for EXACT binding"})
    design = contract.get("design", {})
    if isinstance(design, dict):
        matrix = design.get("matrix")
        contrast = design.get("contrast")
        if not isinstance(matrix, list) or not matrix or not all(isinstance(row, list) and row for row in matrix):
            errors.append({"path": "$.design.matrix", "code": "SHAPE", "message": "nonempty rectangular numeric matrix required"})
        else:
            width = len(matrix[0])
            if any(len(row) != width for row in matrix):
                errors.append({"path": "$.design.matrix", "code": "SHAPE", "message": "matrix must be rectangular"})
            if any(not isinstance(x, (int, float)) or isinstance(x, bool) for row in matrix for x in row):
                errors.append({"path": "$.design.matrix", "code": "TYPE", "message": "matrix must be numeric"})
            if not isinstance(contrast, list) or len(contrast) != width or any(not isinstance(x, (int, float)) or isinstance(x, bool) for x in (contrast or [])):
                errors.append({"path": "$.design.contrast", "code": "SHAPE", "message": "numeric contrast must match matrix columns"})
    else:
        errors.append({"path": "$.design", "code": "TYPE", "message": "object required"})

    object_specs = {
        "governance": ({"license_status", "role_leakage"}, {"license_status", "role_leakage"}),
        "design": ({"biological_unit", "repeated_samples_as_donors", "donor_condition_conflict", "complete_confounding", "matrix", "contrast"}, {"biological_unit", "repeated_samples_as_donors", "donor_condition_conflict", "complete_confounding", "matrix", "contrast"}),
        "count_source": ({"valid", "integer", "nonnegative", "raw_library_sum_positive"}, {"valid", "integer", "nonnegative", "raw_library_sum_positive"}),
        "evidence": ({"target_support_sufficient", "independence_sufficient", "reference_present", "model_estimable"}, {"target_support_sufficient", "independence_sufficient", "reference_present", "model_estimable"}),
        "robustness": ({"lodo_stable", "direction_stable", "filtering_stable", "annotation_stable", "confounding_stable"}, {"lodo_stable", "direction_stable", "filtering_stable", "annotation_stable", "confounding_stable"}),
        "uncertainty": ({"clustered_uncertainty_resolved", "coverage_pass"}, {"clustered_uncertainty_resolved", "coverage_pass"}),
    }
    bool_fields = {
        "governance": {"role_leakage"},
        "design": {"repeated_samples_as_donors", "donor_condition_conflict", "complete_confounding"},
        "count_source": {"valid", "integer", "nonnegative", "raw_library_sum_positive"},
        "evidence": {"target_support_sufficient", "independence_sufficient", "reference_present", "model_estimable"},
        "robustness": {"lodo_stable", "direction_stable", "filtering_stable", "annotation_stable", "confounding_stable"},
        "uncertainty": {"clustered_uncertainty_resolved", "coverage_pass"},
    }
    for section, (required, allowed) in object_specs.items():
        obj = contract.get(section)
        if not isinstance(obj, dict):
            if section != "design":
                errors.append({"path": f"$.{section}", "code": "TYPE", "message": "object required"})
            continue
        for key in sorted(required - set(obj)):
            errors.append({"path": f"$.{section}.{key}", "code": "REQUIRED", "message": "field is required"})
        for key in sorted(set(obj) - allowed):
            errors.append({"path": f"$.{section}.{key}", "code": "ADDITIONAL_PROPERTY", "message": "field is not allowed"})
        for key in sorted(bool_fields[section] & set(obj)):
            if not isinstance(obj[key], bool):
                errors.append({"path": f"$.{section}.{key}", "code": "TYPE", "message": "boolean required"})
    governance = contract.get("governance", {})
    if isinstance(governance, dict) and governance.get("license_status") not in ("RESOLVED", "UNRESOLVED"):
        errors.append({"path": "$.governance.license_status", "code": "ENUM", "message": "RESOLVED or UNRESOLVED required"})
    if isinstance(design, dict) and (not isinstance(design.get("biological_unit"), str) or not design.get("biological_unit")):
        errors.append({"path": "$.design.biological_unit", "code": "TYPE", "message": "nonempty string required"})
    claims = contract.get("claims")
    if not isinstance(claims, list):
        errors.append({"path": "$.claims", "code": "TYPE", "message": "array required"})
    else:
        for i, claim in enumerate(claims):
            if not isinstance(claim, dict) or set(claim) != {"claim_id", "mapped_to_passed_gate"}:
                errors.append({"path": f"$.claims[{i}]", "code": "SHAPE", "message": "exact claim_id and mapped_to_passed_gate fields required"})
                continue
            if not isinstance(claim["claim_id"], str) or not claim["claim_id"]:
                errors.append({"path": f"$.claims[{i}].claim_id", "code": "TYPE", "message": "nonempty string required"})
            if not isinstance(claim["mapped_to_passed_gate"], bool):
                errors.append({"path": f"$.claims[{i}].mapped_to_passed_gate", "code": "TYPE", "message": "boolean required"})
    sources = contract.get("sources", [])
    if not isinstance(sources, list):
        errors.append({"path": "$.sources", "code": "TYPE", "message": "array required"})
    else:
        for i, source in enumerate(sources):
            if not isinstance(source, dict) or set(source) != {"relative_path", "sha256"}:
                errors.append({"path": f"$.sources[{i}]", "code": "SHAPE", "message": "exact relative_path and sha256 fields required"})
                continue
            if not _safe_relative_path(source.get("relative_path", "")):
                errors.append({"path": f"$.sources[{i}].relative_path", "code": "PATH_UNSAFE", "message": "canonical relative POSIX path required"})
            if not SHA256_RE.fullmatch(source.get("sha256", "")):
                errors.append({"path": f"$.sources[{i}].sha256", "code": "PATTERN", "message": "lowercase SHA-256 required"})
    return errors


def compile_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Compile an input contract to a deterministic, hash-bound representation."""
    errors = validate_contract(contract)
    if errors:
        raise ValueError(json.dumps({"schema_errors": errors}, sort_keys=True))
    normalized = copy.deepcopy(contract)
    normalized.setdefault("sources", [])
    normalized["sources"] = sorted(normalized["sources"], key=lambda x: x["relative_path"])
    source_sha = hashlib.sha256(_canonical_bytes(contract)).hexdigest()
    normalized_sha = hashlib.sha256(_canonical_bytes(normalized)).hexdigest()
    return {
        "compiler": "scdesignguard-nm03",
        "compiler_version": "0.1.0",
        "api_version": "1.0",
        "schema_version": "1.0.0",
        "source_contract_sha256": source_sha,
        "compiled_contract_sha256": normalized_sha,
        "contract": normalized,
    }


def canonical_json(value: Any) -> str:
    return _canonical_bytes(value).decode("utf-8")
