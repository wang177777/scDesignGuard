# Analysis scripts

- `verify_public_source_data.py` reconciles the released aggregate Source Data
  workbook.
- `count_recompute.c` and `count_recompute.awk` recompute selected count
  summaries from prepared inputs.
- `design_recompute.R` recomputes selected design-matrix summaries from
  prepared inputs.

These helpers cover the released aggregate checks. The contract evaluator is
under `src/`, and its executable fixtures and golden outputs are under
`tests/`.
