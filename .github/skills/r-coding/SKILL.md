---
name: r-coding
description: "R/Seurat coding conventions for the scRNA-seq wound healing project. Use when writing or editing R scripts."
---

# R Coding Skill — scRNA-seq Project

## When to Use
- Writing new R scripts (`.R`, `.Rmd`, `.qmd`)
- Editing existing R files
- Reviewing R code

## Standard Setup
```r
#!/usr/bin/env Rscript
set.seed(42)

suppressPackageStartupMessages({
  library(Seurat)
  library(ggplot2)
  library(dplyr)
  library(patchwork)
})
```

## Naming Conventions
- Variables: `snake_case` — `wound_data`, `de_results`
- Seurat objects: `PascalCase`-ish — `wound_sobj`, `ctrl_sobj`
- Functions: `snake_case` — `run_qc_filter()`
- Files: `snake_case` — `01_seurat_analysis.R`

## Mouse Gene Symbols
- Use proper case: `Krt14`, `Col1a1`, `Acta2`
- Mitochondrial pattern: `"^mt-|^Mt-"`

## Output Patterns
```r
# Seurat objects
saveRDS(sobj, "analysis/clustering/wound_sobj.rds")

# Figures
ggsave("analysis/figures/name.png", plot, width = 10, height = 8, dpi = 300)
ggsave("analysis/figures/name.pdf", plot, width = 10, height = 8)

# Tables
write.csv(results, "analysis/de/results.csv", row.names = FALSE)

# Session info (always at end)
sink("analysis/clustering/R_sessionInfo.txt")
sessionInfo()
sink()
```

## Seurat Workflow Pattern
```r
# Standard processing
sobj <- NormalizeData(sobj)
sobj <- FindVariableFeatures(sobj, nfeatures = 3000)
sobj <- ScaleData(sobj, vars.to.regress = "percent.mt")
sobj <- RunPCA(sobj, npcs = 50)
sobj <- RunHarmony(sobj, group.by.vars = "sample")
sobj <- RunUMAP(sobj, reduction = "harmony", dims = 1:30)
sobj <- FindNeighbors(sobj, reduction = "harmony", dims = 1:30)
sobj <- FindClusters(sobj, resolution = 0.8, algorithm = 4)  # Leiden
```

## Colorblind-Safe Palettes
```r
# Wound condition colors
wound_colors <- c(
  "control" = "#2166AC", "wound_3d" = "#F4A582",
  "wound_7d" = "#D6604D", "wound_14d" = "#B2182B"
)
```
