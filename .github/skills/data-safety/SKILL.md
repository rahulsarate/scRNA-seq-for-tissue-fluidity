---
name: data-safety
description: "Data protection rules for the scRNA-seq project. Use when modifying files, running scripts that write data, or working with raw/processed data directories."
---

# Data Safety Skill

## When to Use
- Before modifying any files in `data/` directories
- Before running destructive operations (overwrite, delete)
- When working with patient data or sensitive information

## READ-ONLY Directories — NEVER modify
- `data/raw/` — Raw FASTQ files, untouchable
- `templates/` — Reference templates, copy before modifying

## NEVER Commit
- Files >50MB (enforced by .gitignore)
- Patient IDs, PHI, or clinical identifiers
- Unpublished results to public channels
- API keys, tokens, or credentials

## Safe Output Locations
| Directory | What goes here |
|-----------|---------------|
| `data/synthetic/` | Generated test data |
| `data/counts/` | Processed count matrices |
| `analysis/qc/` | QC plots, metrics |
| `analysis/de/` | Differential expression results |
| `analysis/enrichment/` | GO/KEGG/GSEA results |
| `analysis/clustering/` | Processed objects, UMAP coords |
| `analysis/figures/` | Publication figures |
| `analysis/trajectory/` | Pseudotime, RNA velocity |
| `reports/` | Generated reports |

## Before Any Destructive Operation
1. Check if output files exist before overwriting
2. Use timestamped filenames for iterative analyses
3. Back up Seurat/AnnData objects before re-processing
4. Never use `rm -rf` on data directories

## File Format Rules
- R objects: `.rds` format
- Python objects: `.h5ad` format
- Tables: `.csv` with proper column headers
- Figures: `.pdf` (vector) + `.png` (300 DPI)
