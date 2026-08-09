"""Exact-arithmetic validity verifier and terminal-state engine."""

from fractions import Fraction
from typing import Any, Dict, Iterable, List, Sequence

from .catalog import CLAIM_LIMITS, REASONS, STATE_PRECEDENCE
from .compiler import canonical_json, validate_contract
import hashlib


def _rank(matrix: Sequence[Sequence[float]]) -> int:
    rows = [[Fraction(str(value)) for value in row] for row in matrix]
    if not rows:
        return 0
    width = len(rows[0])
    rank = 0
    for col in range(width):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][col] != 0), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][col]
        rows[rank] = [value / divisor for value in rows[rank]]
        for r in range(len(rows)):
            if r != rank and rows[r][col] != 0:
                factor = rows[r][col]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def contrast_is_estimable(matrix: Sequence[Sequence[float]], contrast: Sequence[float]) -> bool:
    """A contrast is estimable iff it lies in the row space of the design matrix."""
    return _rank(matrix) == _rank(list(matrix) + [list(contrast)])


def _add(reasons: List[str], condition: bool, code: str) -> None:
    if condition:
        reasons.append(code)


def evaluate_contract(contract: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate one validated design contract without executing scientific analysis."""
    schema_errors = validate_contract(contract)
    if schema_errors:
        raise ValueError({"schema_errors": schema_errors})
    reasons: List[str] = []
    identity = contract["identity"]
    governance = contract["governance"]
    design = contract["design"]
    count = contract["count_source"]
    evidence = contract["evidence"]
    robust = contract["robustness"]
    uncertainty = contract["uncertainty"]
    claims = contract["claims"]
    design_rank = _rank(design["matrix"])
    augmented_rank = _rank(list(design["matrix"]) + [list(design["contrast"])])

    _add(reasons, identity.get("binding_status") != "EXACT" or not all(identity.get(k) for k in ("dataset_id", "version", "sha256")), "GOV.IDENTITY.UNBOUND")
    _add(reasons, governance.get("license_status") != "RESOLVED", "GOV.LICENSE.UNRESOLVED")
    _add(reasons, bool(governance.get("role_leakage")), "GOV.ROLE.LEAKAGE")
    _add(reasons, any(not row.get("mapped_to_passed_gate", False) for row in claims), "GOV.CLAIM.UNMAPPED")
    _add(reasons, design.get("biological_unit") != "donor" or bool(design.get("repeated_samples_as_donors")), "DESIGN.DONOR.INVALID")
    _add(reasons, bool(design.get("donor_condition_conflict")), "DESIGN.CONDITION.CONFLICT")
    _add(reasons, bool(design.get("complete_confounding")), "DESIGN.CONFOUNDING.COMPLETE")
    _add(reasons, not (count.get("valid") and count.get("integer") and count.get("nonnegative") and count.get("raw_library_sum_positive")), "COUNT.SOURCE.INVALID")
    _add(reasons, not evidence.get("target_support_sufficient", False), "EVIDENCE.TARGET_SUPPORT.INSUFFICIENT")
    _add(reasons, design_rank != augmented_rank, "EVIDENCE.ESTIMABILITY.INSUFFICIENT")
    _add(reasons, not evidence.get("independence_sufficient", False), "EVIDENCE.INDEPENDENCE.INSUFFICIENT")
    _add(reasons, not evidence.get("reference_present", False), "EVIDENCE.REFERENCE.MISSING")
    _add(reasons, not evidence.get("model_estimable", False), "EVIDENCE.MODEL.NONESTIMABLE")
    _add(reasons, not robust.get("lodo_stable", False), "ROBUSTNESS.LODO.FRAGILE")
    _add(reasons, not robust.get("direction_stable", False), "ROBUSTNESS.DIRECTION.UNSTABLE")
    _add(reasons, not robust.get("filtering_stable", False), "ROBUSTNESS.FILTERING.FRAGILE")
    _add(reasons, not robust.get("annotation_stable", False), "ROBUSTNESS.ANNOTATION.SENSITIVE")
    _add(reasons, not robust.get("confounding_stable", False), "ROBUSTNESS.CONFOUNDING.SENSITIVE")
    _add(reasons, not uncertainty.get("clustered_uncertainty_resolved", False), "UNCERTAINTY.CLUSTERING.UNRESOLVED")
    _add(reasons, not uncertainty.get("coverage_pass", False), "UNCERTAINTY.COVERAGE.BELOW_THRESHOLD")
    if not reasons:
        reasons.append("OUTPUT.SAFE_TO_PROCEED")
    reasons = sorted(set(reasons), key=lambda code: (STATE_PRECEDENCE[REASONS[code][0]], code))
    state = REASONS[reasons[0]][0]
    return {
        "task_id": contract["task_id"],
        "contract_sha256": hashlib.sha256(canonical_json(contract).encode("utf-8")).hexdigest(),
        "terminal_state": state,
        "state_precedence": STATE_PRECEDENCE[state],
        "reason_codes": reasons,
        "reason_ledger": [
            {"reason_code": code, "terminal_state": REASONS[code][0], "definition": REASONS[code][1]}
            for code in reasons
        ],
        "estimability_proof": {
            "method": "EXACT_RATIONAL_ROW_SPACE_RANK",
            "design_rank": design_rank,
            "augmented_with_contrast_rank": augmented_rank,
            "contrast_dimension": len(design["contrast"]),
            "estimable": design_rank == augmented_rank,
            "floating_tolerance_used": False,
        },
        "claim_limit": CLAIM_LIMITS[state],
        "biological_truth_certified": False,
        "scientific_analysis_executed": False,
        "separate_authorization_required": True,
        "abstention_calibration": {
            "policy_id": "NM00_V1_1_1_PRECEDENCE_CALIBRATION",
            "score": {"BLOCK": 1.0, "NON_EVALUABLE": 0.75, "ABSTAIN": 0.5, "PROCEED": 0.0}[state],
            "probability_interpretation": "NONE_POLICY_SCORE_ONLY",
        },
    }
