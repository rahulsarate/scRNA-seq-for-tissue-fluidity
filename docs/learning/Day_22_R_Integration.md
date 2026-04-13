# Day 22: R Integration & DESeq2 Deep Dive

> **Goal**: Understand the R side of the project — Seurat, DESeq2, clusterProfiler — and why we use both languages.

---

## Why Both Python AND R?

```
Python (Scanpy):                    R (Seurat/DESeq2):
+ Fast, scalable                    + Gold-standard stats (DESeq2)
+ AnnData ecosystem                 + Bioconductor packages
+ Dashboard (FastAPI)               + Publication-quality plots (ggplot2)
+ RNA velocity (scVelo)             + Pathway analysis (clusterProfiler)
- DE stats less mature              - Slower on large data
- Fewer enrichment tools            - No web framework

Our strategy: Python for pipeline + dashboard, R for DE + enrichment
```

---

## R Coding Conventions (Our Project)

```r
# Variables: snake_case
wound_sobj <- readRDS("data/counts/wound_seurat.rds")
min_genes <- config$qc$min_genes

# Seurat objects: PascalCase variable names
WoundData <- CreateSeuratObject(counts = raw_counts)

# Assignment: <- (not =)
x <- 42  # Correct
x = 42   # Avoid (valid but unconventional)

# Pipe: |> or %>%
wound_sobj |>
  NormalizeData() |>
  FindVariableFeatures() |>
  ScaleData()
```

---

## Seurat v5 Pipeline (R Version)

Our R pipeline mirrors the Python one:

```r
# scripts/R/01_seurat_analysis.R

library(Seurat)
library(yaml)

# Load config (same file as Python!)
config <- yaml::read_yaml("configs/analysis_config.yaml")

# Step 1: Create Seurat object
wound_sobj <- CreateSeuratObject(
  counts = raw_counts,
  min.cells = config$qc$min_cells_per_gene,
  min.features = config$qc$min_genes
)

# Step 2: QC
wound_sobj[["percent.mt"]] <- PercentageFeatureSet(wound_sobj, pattern = "^mt-")
wound_sobj <- subset(wound_sobj,
  nFeature_RNA > config$qc$min_genes &
  nFeature_RNA < config$qc$max_genes &
  percent.mt < config$qc$max_percent_mt
)

# Step 3: Normalize
wound_sobj <- NormalizeData(wound_sobj) |>
  FindVariableFeatures(nfeatures = 2000) |>
  ScaleData()

# Step 4: PCA + UMAP
wound_sobj <- RunPCA(wound_sobj, npcs = config$clustering$n_pcs) |>
  FindNeighbors(dims = 1:config$clustering$n_pcs) |>
  FindClusters(resolution = config$clustering$resolution) |>
  RunUMAP(dims = 1:config$clustering$n_pcs)

# Save
saveRDS(wound_sobj, "data/counts/wound_seurat.rds")
```

---

## DESeq2: The Gold Standard for scRNA-seq DE

### Why Pseudobulk DESeq2?

```
Cell-level DE (e.g., Wilcoxon):
  - Treats each cell as independent
  - Inflated p-values (cells from same sample aren't independent)
  - High false positive rate

Pseudobulk DESeq2:
  - Aggregate cells per sample first
  - Treats samples (not cells) as replicates
  - Proper statistical model
  - Gold standard per benchmarks
```

### Pseudobulk: From Cells to Samples

```
Before (cell-level):                After (pseudobulk):
Cell_1 (sample_1, fibroblast)      sample_1_fibroblast: sum of 500 cells
Cell_2 (sample_1, fibroblast)      sample_2_fibroblast: sum of 480 cells
...                                sample_3_fibroblast: sum of 510 cells
Cell_500 (sample_1, fibroblast)    sample_4_fibroblast: sum of 520 cells
Cell_501 (sample_2, fibroblast)
...
```

### DESeq2 Workflow

```r
library(DESeq2)

# 1. Create pseudobulk counts
# Sum raw counts per sample × cell_type
pseudo_counts <- aggregate_counts(adata, group_by = c("sample", "cell_type"))

# 2. Create DESeq2 object
dds <- DESeqDataSetFromMatrix(
  countData = pseudo_counts,
  colData = sample_metadata,
  design = ~ condition    # Compare conditions
)

# 3. Run DESeq2
dds <- DESeq(dds)

# 4. Extract results with shrinkage
res <- lfcShrink(dds,
  coef = "condition_wound_7d_vs_control",
  type = "ashr"                              # Our configured shrinkage
)

# 5. Filter significant genes
sig_genes <- res[which(res$padj < 0.05 & abs(res$log2FoldChange) > 1.0), ]
```

### What DESeq2 Does Internally

```
Step 1: Size factor normalization
  → Accounts for sequencing depth differences

Step 2: Dispersion estimation
  → Models biological variability per gene

Step 3: Negative binomial GLM
  → Fits a model: counts ~ condition

Step 4: Wald test
  → Tests if condition coefficient ≠ 0

Step 5: BH correction
  → Adjusts p-values for multiple testing
```

### Log2 Fold Change Shrinkage (ashr)

```
Without shrinkage:                   With ashr shrinkage:
  Low-expression genes get           All genes get reliable
  extreme fold changes               fold change estimates
  (noisy, unreliable)                (conservative, trustworthy)

  Gene X: 2 counts vs 0 counts      Gene X: shrunk toward 0
  → log2FC = infinity!               → log2FC = modest value
```

---

## clusterProfiler: Pathway Enrichment in R

```r
library(clusterProfiler)
library(org.Mm.eg.db)    # Mouse annotation database

# Convert gene symbols to Entrez IDs
gene_ids <- bitr(sig_genes$gene,
  fromType = "SYMBOL",
  toType = "ENTREZID",
  OrgDb = org.Mm.eg.db
)

# GO enrichment
go_results <- enrichGO(
  gene = gene_ids$ENTREZID,
  OrgDb = org.Mm.eg.db,
  ont = "BP",           # Biological Process
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05
)

# KEGG enrichment
kegg_results <- enrichKEGG(
  gene = gene_ids$ENTREZID,
  organism = "mmu",      # Mouse
  pvalueCutoff = 0.05
)
```

---

## Python ↔ R Data Exchange

```
Python (AnnData .h5ad)  ←→  R (Seurat .rds)

Option 1: Shared file formats
  Python writes CSV → R reads CSV
  analysis/de/wound_7d_vs_control.csv

Option 2: Convert objects
  anndata2ri (Python package)
  SeuratDisk (R package)

Option 3: Shared config
  Both read configs/analysis_config.yaml
  Same parameters, same results
```

---

## Interview Q&A

### Q: "Why do you use both Python and R?"

> "Each language has strengths. Python handles our pipeline (Scanpy is fast and scalable), dashboard (FastAPI), and data management. R provides gold-standard statistics (DESeq2 for pseudobulk DE), the Bioconductor ecosystem (clusterProfiler for pathway analysis), and ggplot2 for publication figures. Both read the same config file, so parameters stay consistent."

### Q: "Why pseudobulk DESeq2 instead of Wilcoxon?"

> "Cell-level tests like Wilcoxon treat each cell as an independent sample, but cells from the same mouse aren't independent — they share biological and technical variation. This inflates significance, producing many false positives. Pseudobulk aggregates cells per sample first, then uses DESeq2's negative binomial model on sample-level counts. Benchmarking studies consistently show pseudobulk DESeq2 has the best type-1 error control for scRNA-seq."

### Q: "What is ashr shrinkage?"

> "It's a method to stabilize log2 fold change estimates. Genes with very low expression can show extreme fold changes (2 counts vs 0 = infinity). Ashr shrinks unreliable estimates toward zero while preserving strong, well-supported effects. We configure this in analysis_config.yaml as `shrinkage: ashr`."

---

## Self-Check Questions

1. **Why both Python and R?** → Python for pipeline + dashboard, R for DE + enrichment statistics
2. **What is pseudobulk?** → Summing cell counts per sample to create sample-level replicates
3. **Why pseudobulk over cell-level DE?** → Cells from same sample aren't independent; pseudobulk gives proper statistics
4. **What statistical model does DESeq2 use?** → Negative binomial generalized linear model
5. **What does ashr shrinkage do?** → Stabilizes fold changes for low-expression genes
6. **What R assignment operator?** → `<-` (not `=`)
7. **What is clusterProfiler?** → R package for GO, KEGG, GSEA enrichment analysis
8. **How do Python and R share parameters?** → Both read the same `analysis_config.yaml`
9. **Seurat naming convention?** → PascalCase for objects, pipe-based workflow
10. **What does BH correction do?** → Benjamini-Hochberg: adjusts p-values for multiple testing

---

**Next**: [Day 23 — Batch Effects & Integration](Day_23_Batch_Effects.md)
