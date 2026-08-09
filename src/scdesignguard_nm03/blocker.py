"""Fail-closed invalid-analysis blocker."""

from typing import Any, Dict


class AnalysisBlockedError(RuntimeError):
    """Raised when a governed action is attempted outside PROCEED."""


def require_proceed(result: Dict[str, Any], authorization: Dict[str, Any] = None) -> None:
    """Require PROCEED plus an explicit, exact task-bound authorization."""
    if result.get("terminal_state") != "PROCEED":
        codes = ",".join(result.get("reason_codes", []))
        raise AnalysisBlockedError(f"terminal_state={result.get('terminal_state')}; reasons={codes}")
    if not authorization or authorization.get("authorized") is not True:
        raise AnalysisBlockedError("PROCEED does not itself authorize scientific execution")
    if authorization.get("task_id") != result.get("task_id"):
        raise AnalysisBlockedError("authorization task_id mismatch")
    if authorization.get("contract_sha256") != result.get("contract_sha256"):
        raise AnalysisBlockedError("authorization contract_sha256 mismatch")
    if authorization.get("scope") != "SCIENTIFIC_EXECUTION":
        raise AnalysisBlockedError("authorization scope mismatch")
    if not authorization.get("authorization_id"):
        raise AnalysisBlockedError("authorization_id required")
