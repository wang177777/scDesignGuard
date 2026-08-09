"""Counterfactual repair oracle; proposals never mutate a contract."""

from typing import Any, Dict, List

REPAIRS = {
    "GOV.IDENTITY.UNBOUND": "Bind exact immutable dataset/version/hash in a new prospective contract.",
    "GOV.LICENSE.UNRESOLVED": "Obtain and bind authoritative license/data-use evidence.",
    "GOV.ROLE.LEAKAGE": "Close the tainted task; establish a new prospectively blinded task.",
    "GOV.CLAIM.UNMAPPED": "Remove the claim or prospectively map it to an endpoint and Gate.",
    "DESIGN.DONOR.INVALID": "Use donor as the biological unit and aggregate repeated samples within donor-condition.",
    "DESIGN.CONDITION.CONFLICT": "Resolve from exact provenance or close the task; do not infer.",
    "DESIGN.CONFOUNDING.COMPLETE": "Define a new estimable task or close the current task.",
    "COUNT.SOURCE.INVALID": "Bind a valid raw-count source prospectively; never manufacture counts.",
    "EVIDENCE.TARGET_SUPPORT.INSUFFICIENT": "Report NON_EVALUABLE; a future task needs new prospective governance.",
    "EVIDENCE.ESTIMABILITY.INSUFFICIENT": "Amend the future task design before outcome access.",
    "EVIDENCE.INDEPENDENCE.INSUFFICIENT": "Obtain exact independence evidence or retain NON_EVALUABLE.",
    "EVIDENCE.REFERENCE.MISSING": "Obtain the required reference under a new authorized task.",
    "EVIDENCE.MODEL.NONESTIMABLE": "Specify an estimable future model; do not tune the current task.",
    "ROBUSTNESS.LODO.FRAGILE": "Withhold the conclusion and report LODO fragility.",
    "ROBUSTNESS.DIRECTION.UNSTABLE": "Withhold direction and report instability.",
    "ROBUSTNESS.FILTERING.FRAGILE": "Withhold conclusion and report filtering sensitivity.",
    "ROBUSTNESS.ANNOTATION.SENSITIVE": "Withhold conclusion and report annotation sensitivity.",
    "ROBUSTNESS.CONFOUNDING.SENSITIVE": "Withhold conclusion and report confounding sensitivity.",
    "UNCERTAINTY.CLUSTERING.UNRESOLVED": "Withhold conclusion until clustered uncertainty is prospectively resolved.",
    "UNCERTAINTY.COVERAGE.BELOW_THRESHOLD": "Withhold conclusion and report coverage failure.",
    "OUTPUT.SAFE_TO_PROCEED": "No repair proposed; separate authorization remains required.",
}


def propose_repairs(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "task_id": result.get("task_id"),
        "oracle_mode": "COUNTERFACTUAL_ONLY_NO_AUTOMATIC_MUTATION",
        "automatic_repair_performed": False,
        "proposals": [
            {"reason_code": code, "proposal": REPAIRS[code], "creates_new_task_when_semantics_change": True}
            for code in result.get("reason_codes", [])
        ],
    }

