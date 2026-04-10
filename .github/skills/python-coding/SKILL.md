---
name: python-coding
description: "Python/Scanpy coding conventions for the scRNA-seq wound healing project. Use when writing or editing Python scripts."
---

# Python Coding Skill — scRNA-seq Project

## When to Use
- Writing new Python scripts
- Editing existing `.py` files
- Reviewing Python code

## Standard Imports
```python
import scanpy as sc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
warnings.filterwarnings('ignore')

# Settings
sc.settings.verbosity = 2
sc.settings.figdir = 'analysis/figures/'
sc.settings.set_figure_params(dpi=300, facecolor='white', frameon=False)

# Reproducibility
SEED = 42
np.random.seed(SEED)
```

## Naming Conventions
- Variables: `snake_case` — `wound_adata`, `de_results`
- Functions: `snake_case` — `def run_qc_filter():`
- Constants: `UPPER_SNAKE` — `SEED = 42`
- Files: `snake_case` — `01_scrna_analysis_pipeline.py`

## Type Hints (required)
```python
def filter_cells(adata: sc.AnnData, min_genes: int = 200) -> sc.AnnData:
    """Filter cells by minimum gene count."""
    ...
```

## Mouse Gene Symbols
- Use proper case: `Krt14`, `Col1a1`, `Acta2`
- NOT human case: ~~`KRT14`~~, ~~`COL1A1`~~
- Mitochondrial prefix: `mt-` (lowercase for mouse)

## Output Patterns
```python
# AnnData
adata.write_h5ad("analysis/clustering/processed_adata.h5ad")

# Figures
plt.savefig("analysis/figures/name.pdf", dpi=300, bbox_inches='tight')
plt.savefig("analysis/figures/name.png", dpi=300, bbox_inches='tight')
plt.close()

# Tables
df.to_csv("analysis/de/results.csv", index=True)
```

## Scanpy Workflow Pattern
```python
# Standard processing order
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.tl.pca(adata, random_state=42)
sc.pp.neighbors(adata, n_pcs=30, random_state=42)
sc.tl.umap(adata, random_state=42)
sc.tl.leiden(adata, resolution=0.8, random_state=42)
```

## Always Use random_state=42
Any stochastic function MUST use `random_state=42`:
- `sc.tl.pca(..., random_state=42)`
- `sc.tl.umap(..., random_state=42)`
- `sc.tl.leiden(..., random_state=42)`
- `train_test_split(..., random_state=42)`
