---
name: "Python / Scanpy Standards"
description: "Coding conventions for Python scripts in this scRNA-seq project"
applyTo: "**/*.py"
---

# Python Coding Standards — scRNA-seq Wound Healing

## Style
- Use snake_case for everything: variables, functions, file names
- Type hints for all function signatures
- Docstrings for public functions (Google style)
- Max line length: 120 characters

## Reproducibility
- Always set `random_state=42` in all stochastic functions (PCA, UMAP, leiden, train_test_split)
- Log package versions at script start:
```python
import scanpy as sc
import anndata
print(f"scanpy=={sc.__version__}, anndata=={anndata.__version__}")
```

## Scanpy Patterns
```python
import scanpy as sc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Standard processing
sc.settings.verbosity = 2
sc.settings.figdir = 'analysis/figures/'
sc.settings.set_figure_params(dpi=300, facecolor='white', frameon=False)
```

## Mouse-Specific
- Mitochondrial genes: `adata.var_names.str.startswith('mt-')` (lowercase for mouse)
- Gene symbols: mouse case (Krt14, not KRT14)

## Output Rules
- AnnData: `adata.write_h5ad("analysis/clustering/wound_adata.h5ad")`
- Figures: `plt.savefig("analysis/figures/name.pdf", dpi=300, bbox_inches='tight')`
- Tables: `df.to_csv("analysis/de/results.csv", index=True)`
