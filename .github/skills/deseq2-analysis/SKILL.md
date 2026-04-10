---
name: deseq2-analysis
description: "Pseudobulk DESeq2 differential expression for scRNA-seq. Use when running DE between conditions, comparing wound timepoints, or performing pseudobulk analysis."
---

# DESeq2 Pseudobulk Analysis Skill

## When to Use
- Differential expression between wound conditions
- Pseudobulk aggregation per sample/condition
- MAST single-cell DE as alternative

## Pseudobulk DESeq2 Workflow (R)
```r
library(DESeq2)
library(Seurat)

# Aggregate to pseudobulk
pseudo <- AggregateExpression(sobj, group.by = c("condition", "sample"),
                              return.seurat = TRUE)

# Run DESeq2
dds <- DESeqDataSetFromMatrix(
  countData = GetAssayData(pseudo, slot = "counts"),
  colData = pseudo@meta.data,
  design = ~ condition
)
dds <- DESeq(dds)
res <- results(dds, contrast = c("condition", "wound_7d", "control"),
               lfcThreshold = 0, alpha = 0.05)
res <- lfcShrink(dds, coef = "condition_wound_7d_vs_control", type = "ashr")
```

## Thresholds
- `padj < 0.05`
- `|log2FoldChange| > 1.0`
- Shrinkage method: `ashr`

## Output Format
CSV files with columns: `gene, log2FC, padj, baseMean`

```r
res_df <- as.data.frame(res) %>%
  tibble::rownames_to_column("gene") %>%
  dplyr::arrange(padj)
write.csv(res_df, "analysis/de/de_wound_7d_vs_control.csv", row.names = FALSE)
```

## Comparisons to Run
1. `wound_3d` vs `control`
2. `wound_7d` vs `control`
3. `wound_14d` vs `control`
4. Per cell type (subset → re-aggregate → DESeq2)
