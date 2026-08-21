
# Data dictionary

Rows are observations; columns are variables. Absolute experimental values are retained in `01_PHM2010`, `02_NASA`, and `03_MENDELEY_CROSS_MACHINE`. `04_cross_dataset`, `07_figure_ready`, and `08_table_ready` contain explicitly derived projections.

`aggregation_level` distinguishes run-point, task-point, across-seed mean, and across-task mean. `uncertainty_type` distinguishes moving-block bootstrap 95% CI, across-seed standard deviation, across-task standard deviation, and point estimates. Missing values are `NA` or empty and are never estimated.

`status` is restricted to AUTHORITATIVE, CANONICAL_COPY, DERIVED, AUDIT_SUPPORTING, SUPERSEDED, EXCLUDED, and UNRESOLVED.
