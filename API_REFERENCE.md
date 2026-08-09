# NM03 v0.1.0 bounded API reference

Frozen versions: software `0.1.0`, schema `1.0.0`, Python API `1.0`.

## Python API

- `compile_contract(value)`: validates and canonicalizes a prospective design contract.
- `validate_contract(value)`: returns schema/contract errors without scientific analysis.
- `evaluate_contract(contract)`: returns one of `PROCEED`, `ABSTAIN`, `BLOCK`,
  or `NON_EVALUABLE` plus exact reason codes.
- `require_proceed(result, authorization=None)`: fail-closed blocker; a
  `PROCEED` state alone is not authorization.
- `propose_repairs(result)`: returns non-mutating repair suggestions.
- `public_release_view(value)`: returns an allowlisted copy and redaction ledger.

Terminal precedence is `BLOCK > NON_EVALUABLE > ABSTAIN > PROCEED`. The 21
frozen reasons are enumerated in `REASON_CODE_MANIFEST.csv`.

## CLI

```text
scdesignguard compile INPUT [--output PATH]
scdesignguard verify INPUT [--output PATH]
scdesignguard repair INPUT [--output PATH]
scdesignguard filter-public INPUT [--output PATH]
scdesignguard validate-schema INPUT [--output PATH]
scdesignguard report INPUT --output PATH
```

Output paths must be safe relative POSIX paths. The CLI returns `2` for bounded
input, JSON or path errors. It does not run differential expression, modelling,
performance evaluation or any other scientific analysis.

## Interpretation boundary

`PROCEED` means only that none of the implemented higher-precedence reasons was
triggered for the supplied contract. It does not establish biological truth,
general validity, performance, causality or permission to begin a subsequent scientific analysis.
