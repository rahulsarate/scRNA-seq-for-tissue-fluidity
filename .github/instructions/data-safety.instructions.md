---
name: "Data Safety Rules"
description: "Data protection rules for all files in this project"
applyTo: "**/*"
---

# Data Safety Rules

## READ-ONLY Directories
- `data/raw/` — NEVER modify, delete, or overwrite raw FASTQ files
- `templates/` — Reference templates, copy before modifying

## NEVER Commit
- Files >50MB (enforced by .gitignore)
- Patient IDs, PHI, or clinical identifiers
- Unpublished results to public channels
- API keys, tokens, or credentials

## Safe Output Locations
- `data/synthetic/` — Generated test data
- `data/counts/` — Processed count matrices
- `analysis/` — All analysis outputs (QC, DE, enrichment, figures, clustering, trajectory)
- `reports/` — Generated reports

## Before Running Destructive Operations
- Always check if output files exist before overwriting
- Use timestamped filenames for iterative analyses
- Back up Seurat/AnnData objects before re-processing
