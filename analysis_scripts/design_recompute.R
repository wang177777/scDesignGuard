#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3) stop("usage: script RECORD_ID DONOR_LEDGER OUTPUT")
record_id <- args[[1]]
ledger <- read.csv(args[[2]], stringsAsFactors = FALSE, check.names = FALSE)
ledger <- ledger[ledger$qualifies_minimum_20 == "True" | ledger$qualifies_minimum_20 == TRUE, ]
ledger$donor <- factor(ledger$donor)
ledger$condition <- factor(ledger$condition)
X <- model.matrix(~ donor + condition, data = ledger)
rank <- qr(X)$rank
condition_cols <- grep("^condition", colnames(X))
estimable <- nlevels(ledger$condition) == 2 && rank == ncol(X) && length(condition_cols) == 1
out <- data.frame(
  record_id = record_id,
  n_pseudobulk_rows = nrow(ledger),
  n_donors = nlevels(ledger$donor),
  design_columns = ncol(X),
  design_rank = rank,
  condition_effect_estimable = estimable,
  residual_df = nrow(ledger) - rank,
  stringsAsFactors = FALSE
)
write.table(out, args[[3]], sep = "\t", quote = FALSE, row.names = FALSE)
