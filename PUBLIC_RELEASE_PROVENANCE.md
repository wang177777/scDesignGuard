# Public release provenance

## Evaluated identity

- Software version: `0.1.0`
- Schema version: `1.0.0`
- Python API version: `1.0`
- Evaluated source commit: `6d7d87b45c64c7f6f62ba818eb69b33c147d66e5`
- Evaluated source tree: `f2be0de9ac1c0d6cb55274d209254cab5b0f3f68`
- Evaluated wheel SHA-256:
  `59b74e2e60315094fb5e9d70224eb7724d8839d75e2e3f8457042f2df0ec9986`
- Evaluated OCI archive SHA-256:
  `ad675089b934e6d96c1bfd83b9deb4fc6c9ac8dbda345ce9e08a9d7d9b21c85d`

`LEGACY_V0_1_0_EVALUATOR_IDENTITY_MANIFEST.csv` and `.json` preserve the exact
v0.1.0 identity receipt. `PUBLIC_RELEASE_CHECKSUMS.sha256` covers the current
public tree.

## Post-evaluation public packaging

The following changes are packaging or documentation only:

- a public README, license, citation metadata and community files;
- a portable `pyproject.toml` README path and project URLs;
- a corrected public fixture path in the test harness;
- a corrected OCI build-context path;
- publication artifacts and a public numerical-reconciliation script;
- continuous-integration configuration.

Evaluator modules in `src/scdesignguard_nm03/`, the JSON Schema, the
reason-code registry, the exact evaluated wheel and the frozen scientific
results remain unchanged.

## v0.1.1 reproducibility packaging

Release v0.1.1 adds archive-relative PROCEED, BLOCK, NON_EVALUABLE and ABSTAIN
fixtures, checksum-bound golden outputs, a 17-method test suite, clean-wheel
fixture checks and current manuscript artifacts. The reviewer archive and its
SHA-256 sidecar are attached to the GitHub release.

## Excluded from public release

Internal Git history, named human-review files, private authorization records,
credentials, machine-local paths, controlled data and third-party raw objects
remain in their governed source locations. This implements the project privacy
and licensing policy; scientific denominators and results remain as reported.
