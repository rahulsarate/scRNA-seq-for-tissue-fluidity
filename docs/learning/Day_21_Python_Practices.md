# Day 21: Python Best Practices for Bioinformatics

> **Goal**: Master the Python conventions used in this project — coding style, patterns, and common pitfalls.

---

## Our Python Stack

```
Core Analysis:           Data Handling:         Visualization:
  scanpy                   pandas                 matplotlib
  anndata                  numpy                  seaborn
  scipy                    yaml

Environment:             Dashboard:
  Python 3.10              FastAPI
  pip + .venv              uvicorn
  requirements.txt
```

---

## Coding Conventions

### Naming
```python
# Variables and functions: snake_case
wound_adata = sc.read_h5ad("wound_adata.h5ad")
min_genes = config['qc']['min_genes']

def filter_cells(adata, min_genes=200):
    ...

# Classes: PascalCase (rare in our scripts)
class DataLoader:
    ...

# Constants: UPPER_SNAKE_CASE
RANDOM_STATE = 42
DEFAULT_RESOLUTION = 0.8
```

### Imports — Standard Order
```python
# 1. Standard library
import os
import logging
from pathlib import Path

# 2. Third-party packages
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
import yaml

# 3. Local/project imports
from app.services.data_loader import DataLoader
```

### Type Hints
```python
def filter_cells(
    adata: sc.AnnData,
    min_genes: int = 200,
    max_percent_mt: float = 15.0
) -> sc.AnnData:
    """Filter cells based on QC metrics."""
    ...
    return adata
```

---

## Reproducibility Patterns

### Always Set Seeds
```python
import numpy as np
import scanpy as sc

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Pass to every function that uses randomness
sc.tl.pca(adata, random_state=RANDOM_STATE)
sc.tl.umap(adata, random_state=RANDOM_STATE)
sc.tl.leiden(adata, random_state=RANDOM_STATE)
```

### Always Log Versions
```python
import scanpy as sc
import anndata
import pandas as pd
import numpy as np

logging.info(f"scanpy: {sc.__version__}")
logging.info(f"anndata: {anndata.__version__}")
logging.info(f"pandas: {pd.__version__}")
logging.info(f"numpy: {np.__version__}")
```

### Config-Driven — No Magic Numbers
```python
# BAD
adata = adata[adata.obs['n_genes'] > 200]

# GOOD
min_genes = config['qc']['min_genes']
adata = adata[adata.obs['n_genes'] > min_genes]
```

---

## Common Patterns in Our Pipeline

### Pattern 1: Load → Process → Save
```python
# Every script follows this pattern
def main():
    # Load
    config = load_config()
    adata = sc.read_h5ad(config['input_path'])

    # Process
    adata = filter_cells(adata, config)
    adata = normalize(adata, config)

    # Save
    adata.write_h5ad(config['output_path'])
    logging.info(f"Saved to {config['output_path']}")
```

### Pattern 2: Pipeline Functions
```python
# Each step is a function that takes and returns AnnData
def step_1_qc(adata: sc.AnnData, config: dict) -> sc.AnnData:
    sc.pp.filter_cells(adata, min_genes=config['qc']['min_genes'])
    return adata

def step_2_normalize(adata: sc.AnnData, config: dict) -> sc.AnnData:
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    return adata

# Chain: adata flows through each step
adata = step_1_qc(adata, config)
adata = step_2_normalize(adata, config)
```

### Pattern 3: AnnData Slots
```python
# Know where data lives in AnnData
adata.X           # Expression matrix (sparse)
adata.obs         # Cell metadata (DataFrame)
adata.var         # Gene metadata (DataFrame)
adata.obsm        # Embeddings (PCA, UMAP)
adata.uns         # Unstructured (colors, params)

# Add results to appropriate slots
adata.obs['cell_type'] = annotations          # Per-cell
adata.var['highly_variable'] = hvg_mask       # Per-gene
adata.obsm['X_umap'] = umap_coords           # Embedding
adata.uns['leiden_params'] = {'resolution': 0.8}  # Metadata
```

---

## Common Pitfalls

### 1. Modifying Views Instead of Copies
```python
# BAD — might modify a view, not actual data
subset = adata[adata.obs['cell_type'] == 'Fibroblast']
subset.obs['label'] = 'fib'  # Warning!

# GOOD — explicit copy
subset = adata[adata.obs['cell_type'] == 'Fibroblast'].copy()
subset.obs['label'] = 'fib'  # Safe
```

### 2. Gene Name Case
```python
# BAD — human gene symbols
genes = ['KRT14', 'VIM', 'COL1A1']

# GOOD — mouse gene symbols
genes = ['Krt14', 'Vim', 'Col1a1']
```

### 3. Not Checking Gene Existence
```python
# BAD — crashes if gene doesn't exist
sc.pl.umap(adata, color='Krt14')

# GOOD — check first
gene = 'Krt14'
if gene in adata.var_names:
    sc.pl.umap(adata, color=gene)
else:
    logging.warning(f"{gene} not found in dataset")
```

### 4. Memory: Dense vs Sparse
```python
# BAD — converting to dense eats memory
dense_matrix = adata.X.toarray()  # 50K cells × 20K genes = 8GB!

# GOOD — work with sparse matrices
import scipy.sparse as sp
if sp.issparse(adata.X):
    gene_means = np.array(adata.X.mean(axis=0)).flatten()
```

---

## File I/O Standards

```python
# Saving
adata.write_h5ad("analysis/clustering/wound_adata.h5ad")  # AnnData
df.to_csv("analysis/de/wound_7d_vs_control.csv", index=False)  # Table

# Loading
adata = sc.read_h5ad("analysis/clustering/wound_adata.h5ad")
df = pd.read_csv("analysis/de/wound_7d_vs_control.csv")

# Figures
fig.savefig("analysis/figures/umap.pdf", dpi=300, bbox_inches='tight')
```

---

## Interview Q&A

### Q: "What Python coding conventions do you follow?"

> "We follow PEP 8 with bioinformatics adaptations: snake_case for variables and functions, type hints for all function signatures, config-driven parameters instead of magic numbers. Every script follows a load → process → save pattern. AnnData is our core data structure, and we use its slot system (obs, var, obsm, uns) to organize results. Seeds are set to 42 for reproducibility, and package versions are logged at every run."

### Q: "How do you handle large datasets in Python?"

> "We keep data in sparse matrices (scipy.sparse) — a 50K × 20K dense matrix would be ~8GB, but sparse is ~500MB. We use AnnData's lazy loading, avoid unnecessary `.toarray()` calls, and process in chunks when possible. H5AD format supports partial reads for exploration without loading everything into memory."

---

## Self-Check Questions

1. **Variable naming convention?** → snake_case for variables/functions
2. **What seed do we use?** → 42, set via `np.random.seed(42)` and `random_state=42`
3. **Where does cell metadata live in AnnData?** → `adata.obs`
4. **Where do UMAP coordinates live?** → `adata.obsm['X_umap']`
5. **How to safely subset AnnData?** → Use `.copy()` to avoid view issues
6. **Mouse vs human gene case?** → Mouse: `Krt14`, Human: `KRT14`
7. **Save format for AnnData?** → `.h5ad`
8. **Import order?** → Standard library → third-party → local
9. **Why sparse matrices?** → 10-100x less memory for scRNA-seq data
10. **What's a magic number?** → A hardcoded value (like `200`) without config reference or explanation

---

**Next**: [Day 22 — R Integration & DESeq2 Deep Dive](Day_22_R_Integration.md)
