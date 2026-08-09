# scDesignGuard

scDesignGuard is a fail-closed, stage-aware framework for deciding whether a
single-cell analysis is scientifically authorized by its source identity,
donor design, target support and model estimability. The software returns one
of four terminal states (`PROCEED`, `ABSTAIN`, `BLOCK` or `NON_EVALUABLE`)
together with machine-readable reason codes. A `PROCEED` state does not itself
authorize downstream scientific execution.

This public repository contains the evaluated scDesignGuard NM03 v0.1.0
software, schema, 21-code reason registry, synthetic test fixture, unit tests,
software bill of materials, analysis scripts and the project-generated Source
Data and figure outputs used for the accompanying manuscript.

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
- `tests/`: synthetic fixture and 13 fail-closed/unit/integration tests.
- `analysis_scripts/`: source-data, figure and independent recomputation code.
- `paper/`: final manuscript artifacts, Source Data and publication figures.
- `ARCHIVAL_EVALUATOR_IDENTITY_MANIFEST.*`: hashes linking the evaluated
  software to source commit `6d7d87b45c64c7f6f62ba818eb69b33c147d66e5`
  and tree `f2be0de9ac1c0d6cb55274d209254cab5b0f3f68`.

## Data availability and redistribution boundary

Third-party expression objects, repository payloads, participant-level
metadata and human-review/signature records are not redistributed here.
Official accession or collection identifiers and project-generated aggregate
Source Data are provided in `paper/source_data/`. Obtain third-party inputs
from the official repositories cited in the manuscript and comply with their
terms. The absence of a third-party object from this repository is not a
scientific exclusion and does not change any frozen denominator or result.

## Reproducibility boundary

The exact evaluated wheel is included and hash-bound. Public-release
documentation and packaging metadata were added after evaluation; these do
not modify evaluator logic, the schema, reason codes, frozen endpoints or
scientific results. See `PUBLIC_RELEASE_PROVENANCE.md` and
`PUBLIC_RELEASE_CHECKSUMS.sha256`.

## AI-assisted development disclosure

OpenAI Codex was used under author supervision for code-development support,
workflow automation, testing, documentation, figure assembly and language
editing. All scientific decisions, code, outputs and text used in the study
were reviewed and verified by the authors, who take full responsibility.

## License and citation

Code is released under the [BSD 3-Clause License](LICENSE). Project-generated
manuscript figures and Source Data are released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) unless a file states
otherwise. Cite this repository using [CITATION.cff](CITATION.cff).
