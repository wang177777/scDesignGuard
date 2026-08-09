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

`ARCHIVAL_EVALUATOR_IDENTITY_MANIFEST.csv` and `.json` preserve the exact
identity receipt. `PUBLIC_RELEASE_CHECKSUMS.sha256` covers this public tree.

## Post-evaluation public packaging

The following changes are packaging or documentation only:

- a public README, license, citation metadata and community files;
- a portable `pyproject.toml` README path and project URLs;
- a corrected public fixture path in the test harness;
- a corrected OCI build-context path;
- publication artifacts and a public numerical-reconciliation script;
- continuous-integration configuration.

These changes do not alter evaluator modules in `src/scdesignguard_nm03/`, the
JSON Schema, the reason-code registry, the exact evaluated wheel or the frozen
scientific results.

## Excluded from public release

The public repository intentionally excludes internal Git history, named
human-review/signature files, private authorization records, credentials,
machine-local paths, controlled data and third-party raw objects whose
redistribution rights are unresolved. This exclusion is a privacy and
licensing boundary, not a change to scientific denominators or results.

