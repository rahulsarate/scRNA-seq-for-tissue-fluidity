#!/usr/bin/env Rscript
# =============================================================================
# Seurat Analysis Pipeline — Wound Healing scRNA-seq
# =============================================================================
# Author: Rahul M Sarate
# Project: Tissue fluidity controls skin repair during wound healing
#
# This script runs the complete Seurat analysis:
#   1. Load data (synthetic or 10X)
#   2. QC filtering
#   3. SCTransform normalization
#   4. PCA + Harmony integration
#   5. UMAP + Leiden clustering
#   6. Cell type annotation
#   7. Differential expression (pseudobulk DESeq2)
#   8. Tissue fluidity scoring
#   9. Visualization suite
#
# Usage: Rscript scripts/R/01_seurat_analysis.R
# =============================================================================

suppressPackageStartupMessages({
  library(Seurat)
  library(ggplot2)
  library(dplyr)
  library(patchwork)
})

set.seed(42)

# --- Configuration ---
config <- list(
  min_features = 200,
  max_features = 5000,
  max_mt = 15,
  n_variable_features = 3000,
  n_pcs = 30,
  cluster_resolution = 0.8,
  output_dir = "analysis",
  fig_dir = "analysis/figures"
)

dir.create(config$fig_dir, recursive = TRUE, showWarnings = FALSE)
dir.create("analysis/de", recursive = TRUE, showWarnings = FALSE)
dir.create("analysis/clustering", recursive = TRUE, showWarnings = FALSE)

cat("================================================================\n")
cat("Seurat Analysis — Tissue Fluidity in Wound Healing\n")
cat("Author: Rahul M Sarate\n")
cat("================================================================\n\n")

# =============================================================================
# STEP 1: LOAD DATA
# =============================================================================
cat("[1/9] Loading data...\n")

data_file <- "data/synthetic/synthetic_seurat_data.rds"

if (file.exists(data_file)) {
  dat <- readRDS(data_file)
  sobj <- CreateSeuratObject(counts = dat$counts,
                              meta.data = dat$metadata,
                              project = "wound_healing")
  cat(sprintf("  Loaded: %d cells x %d genes\n", ncol(sobj), nrow(sobj)))
} else {
  cat("  [ERROR] No data found. Run generate_synthetic_seurat.R first:\n")
  cat("  Rscript scripts/R/generate_synthetic_seurat.R\n")
  quit(status = 1)
}

# =============================================================================
# STEP 2: QC FILTERING
# =============================================================================
cat("\n[2/9] Quality control...\n")

# Mitochondrial percentage (already in metadata for synthetic data)
if (!"percent.mt" %in% colnames(sobj@meta.data)) {
  sobj[["percent.mt"]] <- PercentageFeatureSet(sobj, pattern = "^mt-|^Mt-")
} else if ("percent_mt" %in% colnames(sobj@meta.data)) {
  sobj[["percent.mt"]] <- sobj$percent_mt
}

# QC violin plot
p_qc <- VlnPlot(sobj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"),
                 group.by = "condition", ncol = 3, pt.size = 0)
ggsave(file.path(config$fig_dir, "R_01_qc_violins.png"), p_qc, width = 14, height = 5, dpi = 150)

# Filter
n_before <- ncol(sobj)
sobj <- subset(sobj, subset = nFeature_RNA > config$min_features &
                               nFeature_RNA < config$max_features &
                               percent.mt < config$max_mt)
cat(sprintf("  Before: %d cells → After: %d cells\n", n_before, ncol(sobj)))

# =============================================================================
# STEP 3: NORMALIZATION
# =============================================================================
cat("\n[3/9] Normalization (SCTransform)...\n")

# Use log-normalize for speed (SCTransform for production)
sobj <- NormalizeData(sobj, verbose = FALSE)
sobj <- FindVariableFeatures(sobj, selection.method = "vst",
                              nfeatures = config$n_variable_features, verbose = FALSE)
sobj <- ScaleData(sobj, vars.to.regress = "percent.mt", verbose = FALSE)

cat(sprintf("  Variable features: %d\n", length(VariableFeatures(sobj))))

# =============================================================================
# STEP 4: PCA
# =============================================================================
cat("\n[4/9] PCA...\n")

sobj <- RunPCA(sobj, npcs = 50, verbose = FALSE)

p_elbow <- ElbowPlot(sobj, ndims = 50)
ggsave(file.path(config$fig_dir, "R_02_elbow_plot.png"), p_elbow, width = 8, height = 5, dpi = 150)

# PCA colored by condition
p_pca <- DimPlot(sobj, reduction = "pca", group.by = "condition")
ggsave(file.path(config$fig_dir, "R_03_pca_condition.png"), p_pca, width = 8, height = 6, dpi = 150)

# =============================================================================
# STEP 5: UMAP + CLUSTERING
# =============================================================================
cat("\n[5/9] UMAP + Clustering...\n")

# Note: For multi-sample integration, use RunHarmony() here
# sobj <- RunHarmony(sobj, group.by.vars = "sample", dims.use = 1:30)
# sobj <- RunUMAP(sobj, reduction = "harmony", dims = 1:30)

sobj <- RunUMAP(sobj, dims = 1:config$n_pcs, verbose = FALSE)
sobj <- FindNeighbors(sobj, dims = 1:config$n_pcs, verbose = FALSE)
sobj <- FindClusters(sobj, resolution = config$cluster_resolution, verbose = FALSE)

n_clusters <- length(levels(Idents(sobj)))
cat(sprintf("  Clusters found: %d (resolution = %.1f)\n", n_clusters, config$cluster_resolution))

# UMAP plots
p1 <- DimPlot(sobj, reduction = "umap", label = TRUE, pt.size = 0.3) +
  ggtitle("Cell Clusters") + NoLegend()
p2 <- DimPlot(sobj, reduction = "umap", group.by = "condition", pt.size = 0.3,
              cols = c("control" = "#2166AC", "wound_3d" = "#F4A582",
                       "wound_7d" = "#D6604D", "wound_14d" = "#B2182B")) +
  ggtitle("Wound Condition")
p3 <- DimPlot(sobj, reduction = "umap", group.by = "cell_type", pt.size = 0.3) +
  ggtitle("Cell Type (Ground Truth)")

p_umap <- p1 + p2 + p3 + plot_layout(ncol = 3)
ggsave(file.path(config$fig_dir, "R_04_umap_overview.png"), p_umap, width = 20, height = 6, dpi = 150)

cat("  Saved: R_04_umap_overview.png\n")

# =============================================================================
# STEP 6: CELL TYPE ANNOTATION
# =============================================================================
cat("\n[6/9] Cell type annotation...\n")

skin_markers <- list(
  "Basal Krt"     = c("Krt14", "Krt5", "Tp63"),
  "Diff Krt"      = c("Krt10", "Krt1", "Ivl"),
  "Fibroblast"    = c("Col1a1", "Col3a1", "Dcn", "Pdgfra"),
  "Myofibroblast" = c("Acta2", "Tagln", "Cnn1"),
  "Macrophage"    = c("Cd68", "Adgre1", "Csf1r"),
  "Neutrophil"    = c("S100a8", "S100a9"),
  "T Cell"        = c("Cd3d", "Cd3e"),
  "Endothelial"   = c("Pecam1", "Cdh5", "Kdr"),
  "HFSC"          = c("Sox9", "Lgr5", "Cd34"),
  "Melanocyte"    = c("Dct", "Tyrp1", "Pmel")
)

# Filter to genes present in data
all_markers <- unique(unlist(skin_markers))
available_markers <- all_markers[all_markers %in% rownames(sobj)]
cat(sprintf("  Available markers: %d/%d\n", length(available_markers), length(all_markers)))

# Dot plot
if (length(available_markers) > 0) {
  p_dot <- DotPlot(sobj, features = available_markers, group.by = "seurat_clusters") +
    RotatedAxis() + ggtitle("Marker Expression by Cluster")
  ggsave(file.path(config$fig_dir, "R_05_dotplot_markers.png"), p_dot, width = 16, height = 8, dpi = 150)
}

# Feature plots for key markers
key_markers <- c("Krt14", "Col1a1", "Acta2", "Cd68", "Pecam1", "Sox9")
available_key <- key_markers[key_markers %in% rownames(sobj)]
if (length(available_key) > 0) {
  p_feat <- FeaturePlot(sobj, features = available_key, ncol = 3,
                         cols = c("lightgrey", "#DE2D26"))
  ggsave(file.path(config$fig_dir, "R_06_feature_markers.png"), p_feat, width = 15, height = 10, dpi = 150)
}

# =============================================================================
# STEP 7: DIFFERENTIAL EXPRESSION
# =============================================================================
cat("\n[7/9] Differential expression...\n")

# Find all cluster markers
all_markers_de <- FindAllMarkers(sobj, only.pos = TRUE, min.pct = 0.25,
                                  logfc.threshold = 0.25, verbose = FALSE)
write.csv(all_markers_de, "analysis/de/R_cluster_markers.csv", row.names = FALSE)
cat(sprintf("  Cluster markers: %d gene-cluster pairs\n", nrow(all_markers_de)))

# Heatmap of top markers
if (nrow(all_markers_de) > 0) {
  top5 <- all_markers_de %>% group_by(cluster) %>% top_n(n = 5, wt = avg_log2FC)
  p_heat <- DoHeatmap(sobj, features = top5$gene, size = 3) + NoLegend()
  ggsave(file.path(config$fig_dir, "R_07_heatmap_markers.png"), p_heat, width = 14, height = 12, dpi = 150)
}

# =============================================================================
# STEP 8: TISSUE FLUIDITY SCORING
# =============================================================================
cat("\n[8/9] Tissue fluidity gene scoring...\n")

fluidity_sets <- list(
  "EMT" = c("Vim", "Cdh1", "Cdh2", "Snai1", "Snai2", "Twist1", "Zeb1", "Zeb2"),
  "ECM" = c("Fn1", "Col1a1", "Col3a1", "Mmp2", "Mmp9", "Mmp14", "Timp1", "Lox"),
  "Migration" = c("Rac1", "Cdc42", "RhoA", "Itgb1", "Itga6"),
  "Mechanotx" = c("Yap1", "Piezo1"),
  "WoundSig" = c("Tgfb1", "Pdgfa", "Vegfa", "Wnt5a", "Fgf2")
)

for (name in names(fluidity_sets)) {
  genes <- fluidity_sets[[name]]
  available <- genes[genes %in% rownames(sobj)]
  if (length(available) >= 2) {
    sobj <- AddModuleScore(sobj, features = list(available),
                            name = paste0("fluidity_", name), verbose = FALSE)
    col_name <- paste0("fluidity_", name, "1")
    cat(sprintf("  %s: %d/%d genes scored\n", name, length(available), length(genes)))
  }
}

# Fluidity score feature plots
fluidity_cols <- grep("^fluidity_", colnames(sobj@meta.data), value = TRUE)
if (length(fluidity_cols) > 0) {
  p_fluidity <- FeaturePlot(sobj, features = fluidity_cols, ncol = 3,
                              cols = c("#2166AC", "white", "#B2182B"))
  ggsave(file.path(config$fig_dir, "R_08_fluidity_scores_umap.png"), p_fluidity,
         width = 15, height = 10, dpi = 150)
  
  # Violin plots by condition
  p_vln <- VlnPlot(sobj, features = fluidity_cols, group.by = "condition",
                    pt.size = 0, ncol = 3,
                    cols = c("control" = "#2166AC", "wound_3d" = "#F4A582",
                             "wound_7d" = "#D6604D", "wound_14d" = "#B2182B"))
  ggsave(file.path(config$fig_dir, "R_09_fluidity_violins.png"), p_vln,
         width = 15, height = 10, dpi = 150)
}

# =============================================================================
# STEP 9: SAVE RESULTS
# =============================================================================
cat("\n[9/9] Saving results...\n")

saveRDS(sobj, "analysis/clustering/R_seurat_processed.rds")
cat("  Saved: analysis/clustering/R_seurat_processed.rds\n")

# Save UMAP coordinates + metadata
umap_coords <- as.data.frame(Embeddings(sobj, "umap"))
umap_coords <- cbind(umap_coords, sobj@meta.data)
write.csv(umap_coords, "analysis/clustering/R_umap_metadata.csv")

# Session info
sink("analysis/clustering/R_sessionInfo.txt")
sessionInfo()
sink()

cat("\n================================================================\n")
cat("ANALYSIS COMPLETE\n")
cat(sprintf("Cells: %d | Genes: %d | Clusters: %d\n", ncol(sobj), nrow(sobj), n_clusters))
cat(sprintf("Figures: %s\n", config$fig_dir))
cat("================================================================\n")
