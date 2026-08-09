# Reproducibility

## 1. Verify the public tree

```bash
shasum -a 256 -c PUBLIC_RELEASE_CHECKSUMS.sha256
```

## 2. Reproduce evaluator tests

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
python -m unittest discover -s tests -v
```

## 3. Verify frozen numerical claims

The project-generated Source Data workbook is
`paper/source_data/scDesignGuard_Nature_Methods_SOURCE_DATA.xlsx`. Run:

```bash
python analysis_scripts/verify_public_source_data.py \
  paper/source_data/scDesignGuard_Nature_Methods_SOURCE_DATA.xlsx
```

The script reports the overlap-excluded 15-family benchmark denominators and
Wilson intervals, four held-out end-to-end outcomes, nine known-invalid
challenges and key beta-cell application totals. It does not access expression
matrices or refit biological models.

## 4. Third-party inputs

Raw expression and repository objects are not redistributed. Accessions,
collection identifiers, request receipts and aggregate outputs are provided in
the manuscript and Source Data. Download exact source objects from the cited
official repositories and comply with source terms. No result-dependent family
replacement or threshold relaxation is permitted.

## 5. Analysis environments

- Core evaluator: Python 3.9+; evaluated in Python 3.12.12.
- Independent count recomputation: ISO C source in `analysis_scripts/`.
- Independent design-matrix recomputation: R script in `analysis_scripts/`.
- Figure/manuscript build: Python source retained in `analysis_scripts/`.
- Source Data build: Node.js source retained in `analysis_scripts/`.

The accompanying SBOM and archival identity manifest record exact evaluated
software identity. The OCI archive attached to release `v0.1.0` provides the
evaluated container bytes.

