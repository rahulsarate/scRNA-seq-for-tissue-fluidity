---
name: data-import
description: "Import and parse scRNA-seq datasets from GEO, 10X, and other sources. Use when downloading data, parsing sample sheets, or managing metadata."
---

# Data Import Skill

## When to Use
- Downloading GEO datasets (GSE234269, GSE159827, GSE188432)
- Parsing 10X Cell Ranger outputs
- Managing sample sheets and metadata
- Converting between formats (h5ad, rds, csv)

## Key Datasets
| GEO ID | Description | Use |
|--------|-------------|-----|
| GSE234269 | Wound healing timepoints | Primary dataset |
| GSE159827 | Tissue mechanics in wounds | Mechanical validation |
| GSE188432 | Aged wound healing | Age comparison |

## Download Script
```bash
python scripts/python/00_download_geo_data.py
```

## Reading 10X Data (Python)
```python
import scanpy as sc
# From Cell Ranger output
adata = sc.read_10x_h5('data/counts/sample/filtered_feature_bc_matrix.h5')
# From MTX directory
adata = sc.read_10x_mtx('data/counts/sample/filtered_feature_bc_matrix/')
```

## Reading 10X Data (R)
```r
library(Seurat)
data <- Read10X(data.dir = "data/counts/sample/filtered_feature_bc_matrix/")
sobj <- CreateSeuratObject(counts = data, project = "wound_healing")
```

## Metadata Structure
```python
# Required columns in adata.obs:
# - sample: e.g., "ctrl_rep1", "wound_3d_rep1"
# - condition: "control", "wound_3d", "wound_7d", "wound_14d"
# - replicate: "rep1", "rep2"
```

## Sample Sheet (8 samples)
| sample | condition | replicate |
|--------|-----------|-----------|
| ctrl_rep1 | control | rep1 |
| ctrl_rep2 | control | rep2 |
| w3d_rep1 | wound_3d | rep1 |
| w3d_rep2 | wound_3d | rep2 |
| w7d_rep1 | wound_7d | rep1 |
| w7d_rep2 | wound_7d | rep2 |
| w14d_rep1 | wound_14d | rep1 |
| w14d_rep2 | wound_14d | rep2 |

## Format Conversion
```python
# h5ad → csv
adata = sc.read_h5ad("data/counts/data.h5ad")
pd.DataFrame(adata.X.toarray(), index=adata.obs_names, columns=adata.var_names).to_csv("matrix.csv")

# csv → h5ad
import anndata as ad
adata = ad.read_csv("matrix.csv")
adata.write_h5ad("data.h5ad")
```
