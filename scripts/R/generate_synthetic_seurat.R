#!/usr/bin/env Rscript
# =============================================================================
# Generate Synthetic scRNA-seq Data as Seurat Object
# Project: Tissue fluidity in wound healing (Sarate Lab)
# =============================================================================
# Usage: Rscript scripts/R/generate_synthetic_seurat.R
# Output: data/synthetic/synthetic_seurat.rds
# =============================================================================

suppressPackageStartupMessages({
  library(Matrix)
})

set.seed(42)
cat("=== Generating Synthetic scRNA-seq Seurat-Compatible Data ===\n")

# --- Configuration ---
n_cells <- 8000
n_genes <- 2000

conditions <- c("control", "wound_3d", "wound_7d", "wound_14d")
n_per_cond <- 2000

cell_types <- c("Basal_Keratinocyte", "Diff_Keratinocyte", "Fibroblast",
                 "Myofibroblast", "Macrophage", "Neutrophil", "T_Cell",
                 "Endothelial", "Hair_Follicle_SC", "Melanocyte")

# Proportions per condition (rows = cell types, cols = conditions)
prop_matrix <- matrix(c(
  0.25, 0.10, 0.20, 0.22,  # Basal Krt
  0.20, 0.05, 0.10, 0.18,  # Diff Krt
  0.20, 0.15, 0.20, 0.20,  # Fibroblast
  0.02, 0.08, 0.15, 0.05,  # Myofibroblast
  0.08, 0.25, 0.12, 0.10,  # Macrophage
  0.02, 0.15, 0.03, 0.02,  # Neutrophil
  0.05, 0.08, 0.06, 0.05,  # T Cell
  0.08, 0.06, 0.08, 0.08,  # Endothelial
  0.06, 0.03, 0.03, 0.05,  # HFSC
  0.04, 0.05, 0.03, 0.05   # Melanocyte
), nrow = 10, ncol = 4, byrow = TRUE)

# Marker genes
markers <- list(
  Basal_Keratinocyte = c("Krt14", "Krt5", "Tp63", "Itga6"),
  Diff_Keratinocyte  = c("Krt10", "Krt1", "Ivl", "Lor"),
  Fibroblast         = c("Col1a1", "Col3a1", "Dcn", "Pdgfra"),
  Myofibroblast      = c("Acta2", "Tagln", "Cnn1", "Postn"),
  Macrophage         = c("Cd68", "Adgre1", "Csf1r", "Mrc1"),
  Neutrophil         = c("S100a8", "S100a9", "Ly6g", "Cxcr2"),
  T_Cell             = c("Cd3d", "Cd3e", "Cd4", "Cd8a"),
  Endothelial        = c("Pecam1", "Cdh5", "Kdr", "Vwf"),
  Hair_Follicle_SC   = c("Sox9", "Lgr5", "Cd34", "Lhx2"),
  Melanocyte         = c("Dct", "Tyrp1", "Pmel", "Mitf")
)

fluidity_genes <- c("Vim", "Cdh1", "Cdh2", "Fn1", "Mmp2", "Mmp9", "Mmp14",
                     "Tgfb1", "Acta2", "Snai1", "Snai2", "Twist1", "Zeb1",
                     "Yap1", "Piezo1", "Rac1", "RhoA", "Cdc42", "Itgb1",
                     "Wnt5a", "Vegfa", "Fgf2", "Pdgfa", "Lox", "Timp1")

# --- Build gene names ---
all_markers <- unique(unlist(markers))
special_genes <- unique(c(all_markers, fluidity_genes))
n_random <- n_genes - length(special_genes)
random_genes <- paste0("Gene_", sprintf("%04d", seq_len(n_random)))
gene_names <- c(special_genes, random_genes)[1:n_genes]

# --- Assign cells ---
all_ct <- character(0)
all_cond <- character(0)
all_sample <- character(0)

for (j in seq_along(conditions)) {
  cond <- conditions[j]
  props <- prop_matrix[, j]
  props <- props / sum(props)
  
  ct_assign <- sample(cell_types, n_per_cond, replace = TRUE, prob = props)
  half <- n_per_cond %/% 2
  samp <- c(rep(paste0(cond, "_rep1"), half), rep(paste0(cond, "_rep2"), n_per_cond - half))
  
  all_ct <- c(all_ct, ct_assign)
  all_cond <- c(all_cond, rep(cond, n_per_cond))
  all_sample <- c(all_sample, samp)
}

total_cells <- length(all_ct)
cat(sprintf("Total cells: %d, Total genes: %d\n", total_cells, length(gene_names)))

# --- Generate counts (negative binomial) ---
cat("Generating base expression...\n")
mu_vals <- rexp(n_genes, rate = 2)
counts_mat <- matrix(0L, nrow = n_genes, ncol = total_cells)

for (g in seq_len(n_genes)) {
  r <- max(1, round(1 / runif(1, 0.1, 2)))
  p <- r / (r + mu_vals[g])
  p <- min(0.99, max(0.01, p))
  counts_mat[g, ] <- rnbinom(total_cells, size = r, prob = p)
}

# --- Add marker signals ---
cat("Adding cell-type marker signatures...\n")
gene_idx <- setNames(seq_along(gene_names), gene_names)

for (ct in names(markers)) {
  cell_mask <- which(all_ct == ct)
  for (gene in markers[[ct]]) {
    if (gene %in% names(gene_idx)) {
      gi <- gene_idx[gene]
      counts_mat[gi, cell_mask] <- counts_mat[gi, cell_mask] + rpois(length(cell_mask), lambda = 15) + 10
    }
  }
}

# --- Add tissue fluidity signals ---
cat("Adding tissue fluidity gene signatures...\n")
fluidity_boost <- list(
  control = 1.0, wound_3d = 2.5, wound_7d = 3.0, wound_14d = 1.5
)
responsive_ct <- c("Fibroblast" = 2.0, "Myofibroblast" = 2.5, 
                    "Basal_Keratinocyte" = 1.5, "Endothelial" = 1.2)

for (gene in fluidity_genes) {
  if (gene %in% names(gene_idx)) {
    gi <- gene_idx[gene]
    for (i in seq_len(total_cells)) {
      ct_f <- ifelse(all_ct[i] %in% names(responsive_ct), responsive_ct[all_ct[i]], 0.5)
      cond_f <- fluidity_boost[[all_cond[i]]]
      counts_mat[gi, i] <- counts_mat[gi, i] + rpois(1, lambda = 3 * cond_f * ct_f)
    }
  }
}

# --- Add dropout ---
cat("Adding dropout (zero-inflation)...\n")
dropout_mask <- matrix(rbinom(n_genes * total_cells, 1, 0.7), nrow = n_genes)
counts_mat <- counts_mat * dropout_mask
counts_mat[counts_mat < 0] <- 0

# --- Create sparse matrix ---
rownames(counts_mat) <- gene_names
barcodes <- paste0("CELL_", sprintf("%06d", seq_len(total_cells)))
colnames(counts_mat) <- barcodes
sparse_counts <- Matrix(counts_mat, sparse = TRUE)

# --- Create metadata ---
metadata <- data.frame(
  barcode = barcodes,
  cell_type = all_ct,
  condition = all_cond,
  sample = all_sample,
  organism = "Mus musculus",
  tissue = "skin",
  wound_phase = ifelse(all_cond == "control", "homeostasis",
                ifelse(all_cond == "wound_3d", "inflammatory",
                ifelse(all_cond == "wound_7d", "proliferative", "remodeling"))),
  nCount_RNA = colSums(counts_mat),
  nFeature_RNA = colSums(counts_mat > 0),
  percent_mt = round(runif(total_cells, 1, 12), 2),
  row.names = barcodes,
  stringsAsFactors = FALSE
)

# --- Save outputs ---
output_dir <- file.path("data", "synthetic")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

saveRDS(list(counts = sparse_counts, metadata = metadata, gene_names = gene_names),
        file.path(output_dir, "synthetic_seurat_data.rds"))
cat(sprintf("Saved: %s\n", file.path(output_dir, "synthetic_seurat_data.rds")))

write.csv(metadata, file.path(output_dir, "synthetic_metadata_R.csv"), row.names = FALSE)
cat(sprintf("Saved: %s\n", file.path(output_dir, "synthetic_metadata_R.csv")))

# Summary
cat("\n=== Summary ===\n")
cat(sprintf("Cells: %d | Genes: %d\n", total_cells, n_genes))
cat(sprintf("Conditions: %s\n", paste(conditions, collapse = ", ")))
cat(sprintf("Cell types: %d\n", length(cell_types)))
cat(sprintf("Sparsity: %.1f%%\n", 100 * sum(counts_mat == 0) / length(counts_mat)))
cat(sprintf("Mean counts/cell: %.0f\n", mean(colSums(counts_mat))))
cat(sprintf("Mean genes/cell: %.0f\n", mean(colSums(counts_mat > 0))))
cat("DONE.\n")
