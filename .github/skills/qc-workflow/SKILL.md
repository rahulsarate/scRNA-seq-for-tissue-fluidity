---
name: qc-workflow
description: "scRNA-seq quality control: filtering, doublet detection, ambient RNA removal, QC plots. Use when performing data quality checks."
---

# QC Workflow Skill

## When to Use
- Filtering cells by gene counts, UMI counts, mt%
- Doublet detection (scrublet, DoubletFinder)
- Ambient RNA removal (SoupX, CellBender)
- Generating QC violin/scatter plots

## QC Thresholds (Project Standard)
| Metric | Threshold |
|--------|-----------|
| min_genes | 200 |
| max_genes | 5000 |
| min_counts | 500 |
| max_percent_mt | 15% |
| min_cells_per_gene | 3 |
| doublet_rate | ~5% |

## Python/Scanpy QC
```python
import scanpy as sc

# Calculate QC metrics
adata.var['mt'] = adata.var_names.str.startswith('mt-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None,
                            log1p=False, inplace=True)

# QC plots
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             multi_panel=True, save='_qc_violins.png')

# Filter
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_cells(adata, min_counts=500)
adata = adata[adata.obs.n_genes_by_counts < 5000, :]
adata = adata[adata.obs.pct_counts_mt < 15, :]
sc.pp.filter_genes(adata, min_cells=3)
```

## R/Seurat QC
```r
sobj[["percent.mt"]] <- PercentageFeatureSet(sobj, pattern = "^mt-")

VlnPlot(sobj, features = c("nFeature_RNA", "nCount_RNA", "percent.mt"),
        ncol = 3)

sobj <- subset(sobj,
  nFeature_RNA > 200 & nFeature_RNA < 5000 &
  nCount_RNA > 500 & percent.mt < 15)
```

## QC Report Checklist
- [ ] Pre-filter cell count
- [ ] Post-filter cell count
- [ ] Genes retained
- [ ] Median genes/cell
- [ ] Median UMI/cell
- [ ] Median mt%
- [ ] QC violin plots saved to `analysis/qc/`
