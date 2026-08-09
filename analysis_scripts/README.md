# Analysis scripts

- `verify_public_source_data.py` is the portable public reconciliation entry
  point and uses only the released Source Data workbook.
- `count_recompute.c` and `count_recompute.awk` implement independent count
  reconciliation.
- `design_recompute.R` implements independent design-matrix reconciliation.
- `build_final_story_only_submission.py` and
  `build_source_data_workbook.mjs` are the exact archived manuscript/source-data
  build scripts. They retain the original project-relative evidence paths and
  require the non-redistributed source objects described in the manuscript.

The archived builders are provenance-bearing research code; the public
verification entry point is the supported path for released aggregate data.

