# scDesignGuard

scDesignGuard is a stage-aware framework for deciding whether source identity,
donor design, target support and model estimability authorize a proposed
single-cell analysis. Its deterministic evaluator validates a completed design
contract and returns `PROCEED`, `ABSTAIN`, `BLOCK` or `NON_EVALUABLE` with
machine-readable reason codes. Contract construction and downstream inference
are handled by the surrounding workflow.

This public repository contains the evaluated NM03 v0.1.0 software and the
v0.1.1 reproducibility packaging: schema, 21-code reason registry, four
terminal-state fixtures with golden outputs, 17 test methods, software bill of
materials, bounded recomputation helpers and the project-generated manuscript,
Source Data and figures.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
scdesignguard validate-schema tests/fixtures/valid.json
scdesignguard compile tests/fixtures/valid.json --output reports/compiled.json
scdesignguard verify reports/compiled.json
python -m unittest discover -s tests -v
```

See [INSTALLATION.md](INSTALLATION.md), [API_REFERENCE.md](API_REFERENCE.md)
and [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the complete workflow.
`ci/github-actions-tests.yml` is a ready-to-enable GitHub Actions workflow
template; the same commands were executed locally before release.

## Repository contents

- `src/scdesignguard_nm03/`: deterministic compiler, evaluator, blocker,
  repair suggestions, privacy filter and report renderer.
- `artifacts/`: evaluated wheel, JSON Schema and SBOM. The exact OCI archive
  is attached to the GitHub release because it is a binary release artifact.
- `tests/`: four terminal-state fixtures, golden outputs and 17
  unit/integration test methods.
- `analysis_scripts/`: aggregate Source Data verification and selected count
  and design recomputation helpers.
- `paper/`: final manuscript artifacts, Source Data and publication figures.
- `LEGACY_V0_1_0_EVALUATOR_IDENTITY_MANIFEST.*`: historical hashes linking
  the evaluated software to source commit
  `6d7d87b45c64c7f6f62ba818eb69b33c147d66e5` and tree
  `f2be0de9ac1c0d6cb55274d209254cab5b0f3f68`.

## Data availability and redistribution boundary

Official accession or collection identifiers and project-generated aggregate
Source Data are provided in `paper/source_data/`. Third-party expression
objects, repository payloads, participant-level metadata and human-review
records remain with their official repositories or governed project stores.
Frozen membership, denominators and results are recorded in the released
Source Data.

## Reproducibility

The exact evaluated wheel is included and hash-bound. Release v0.1.1 adds
archive-relative fixtures, golden outputs, reproducibility receipts and current
publication artifacts while retaining evaluator logic, schema, reason codes,
wheel and OCI identity. See `PUBLIC_RELEASE_PROVENANCE.md`,
`PUBLIC_RELEASE_CHECKSUMS.sha256` and the
[v0.1.1 release](https://github.com/wang177777/scDesignGuard/releases/tag/v0.1.1).

## License and citation

Code is released under the [BSD 3-Clause License](LICENSE). Project-generated
manuscript figures and Source Data are released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) unless a file states
otherwise. Cite this repository using [CITATION.cff](CITATION.cff).
