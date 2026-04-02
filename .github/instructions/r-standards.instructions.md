---
name: "R / Bioconductor Standards"
description: "Coding conventions for R scripts in this scRNA-seq project"
applyTo: "**/*.R,**/*.Rmd,**/*.qmd"
---

# R Coding Standards — scRNA-seq Wound Healing

## Style
- Use snake_case for variables and functions: `filtered_counts`, `run_deseq2()`
- Use PascalCase for Seurat objects: `wound_sobj`, `Fibroblast_sobj`
- Indent with 2 spaces (Tidyverse convention)
- Max line length: 100 characters

## Reproducibility
- Always start with `set.seed(42)`
- End every script with `sessionInfo()`
- Save objects as `.rds` using `saveRDS()`, not `save()`
- Load configs from `configs/analysis_config.yaml` using `yaml::read_yaml()`

## Bioconductor Patterns
```r
# Standard library loading order
library(Seurat)        # scRNA-seq framework
library(DESeq2)        # Differential expression
library(clusterProfiler)  # Enrichment analysis
library(org.Mm.eg.db)  # Mouse gene annotations
library(ggplot2)       # Plotting
library(ComplexHeatmap) # Heatmaps
library(EnhancedVolcano) # Volcano plots
library(harmony)       # Integration
```

## Mouse-Specific
- Mitochondrial genes: `pattern = "^mt-"` (lowercase for mouse)
- Use `org.Mm.eg.db` for mouse gene annotations
- Gene symbols: proper mouse case (Krt14, Col1a1, not KRT14, COL1A1)

## Output Rules
- Figures: `ggsave("analysis/figures/name.pdf", width=8, height=6, dpi=300)`
- Tables: `write.csv(res, "analysis/de/results.csv", row.names=TRUE)`
- Objects: `saveRDS(sobj, "analysis/clustering/wound_sobj.rds")`
