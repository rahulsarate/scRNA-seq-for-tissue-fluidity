---
name: scrna-pipeline
description: "Run the complete scRNA-seq analysis pipeline: synthetic data generation, QC, clustering, DE, fluidity scoring, and visualization. Use when asked to run the pipeline end-to-end or any pipeline step."
---

# scRNA-seq Pipeline Execution Skill

## When to Use
- Running the full pipeline or any pipeline step
- Generating synthetic test data
- Executing QC, clustering, DE, or visualization scripts
- Debugging pipeline failures

## Environment Setup
```bash
# Option 1: .venv (pip)
cd "d:\VS CODE Project\scRNA_seq"
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# Option 2: conda
conda activate scrna_wound
```

## Pipeline Steps (in order)

### Step 1: Generate Synthetic Data
```bash
python scripts/python/generate_synthetic_data.py
```
**Expected outputs:**
- `data/synthetic/synthetic_counts.h5ad` — 8000 cells × 2000 genes
- `data/synthetic/synthetic_counts_matrix.csv`
- `data/synthetic/synthetic_metadata.csv`
- `data/synthetic/gene_info.csv`

### Step 2: Run Analysis Pipeline
```bash
python scripts/python/01_scrna_analysis_pipeline.py
```
**Expected outputs:**
- `analysis/clustering/processed_adata.h5ad`
- `analysis/clustering/umap_coordinates.csv`
- `analysis/clustering/cell_metadata.csv`
- `analysis/de/cluster_markers.csv`
- `analysis/de/de_wound_3d_vs_control.csv`
- `analysis/de/de_wound_7d_vs_control.csv`
- `analysis/de/de_wound_14d_vs_control.csv`
- `analysis/figures/01_qc_violins.png`
- `analysis/figures/02_umap_overview.png`
- `analysis/figures/03_fluidity_scores_umap.png`
- `analysis/figures/04_fluidity_boxplots.png`

### Step 3: Generate Publication Figures
```bash
python scripts/python/02_visualization_suite.py
```
**Expected outputs:**
- `analysis/figures/Fig1_UMAP_overview.png` + `.pdf`
- `analysis/figures/Fig2_cell_proportions.png` + `.pdf`
- `analysis/figures/Fig3_fluidity_scores.png` + `.pdf`
- `analysis/figures/Fig4_wound_healing_schematic.png` + `.pdf`
- `analysis/figures/Fig5_research_paradigms.png` + `.pdf`

### Step 4 (optional): R Pipeline
```bash
Rscript scripts/R/generate_synthetic_seurat.R
Rscript scripts/R/01_seurat_analysis.R
```

## Validation Script
After running all steps, verify outputs exist:
```python
import os
expected = [
    'data/synthetic/synthetic_counts.h5ad',
    'data/synthetic/synthetic_metadata.csv',
    'analysis/clustering/processed_adata.h5ad',
    'analysis/de/cluster_markers.csv',
    'analysis/figures/Fig1_UMAP_overview.png',
]
for f in expected:
    status = 'PASS' if os.path.exists(f) else 'FAIL'
    print(f'  {status}  {f}')
```

## Troubleshooting
| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: scanpy` | Activate .venv or conda env |
| `FileNotFoundError: synthetic_counts.h5ad` | Run Step 1 first |
| `No data found` in pipeline | Run `generate_synthetic_data.py` |
| Memory error | Reduce N_CELLS in generate script |

## Configuration
All parameters live in `configs/analysis_config.yaml`. Key settings:
- `qc_thresholds.min_genes_per_cell: 200`
- `qc_thresholds.max_percent_mt: 15`
- `clustering.default_resolution: 0.8`
- `output.seed: 42`
