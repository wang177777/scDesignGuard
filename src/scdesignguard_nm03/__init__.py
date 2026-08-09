"""scDesignGuard NM03 software-freeze candidate public API."""

from .compiler import compile_contract, validate_contract
from .engine import evaluate_contract
from .blocker import AnalysisBlockedError, require_proceed
from .repair import propose_repairs
from .privacy import public_release_view

__all__ = [
    "AnalysisBlockedError",
    "compile_contract",
    "evaluate_contract",
    "propose_repairs",
    "public_release_view",
    "require_proceed",
    "validate_contract",
]

__version__ = "0.1.0"
SCHEMA_VERSION = "1.0.0"
API_VERSION = "1.0"

