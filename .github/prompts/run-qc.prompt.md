---
description: "Run full QC pipeline on scRNA-seq data"
---

Run quality control on the wound healing scRNA-seq data:

1. Load data from `data/counts/` or `data/synthetic/`
2. Calculate QC metrics: nFeature_RNA, nCount_RNA, percent.mt (mouse: `mt-` prefix)
3. Generate QC violin plots grouped by sample
4. Create scatter plots: nCount vs percent.mt, nCount vs nFeature
5. Apply filters: 200 < nFeature < 5000, nCount > 500, percent.mt < 15%
6. Run doublet detection (DoubletFinder/Scrublet)
7. Save filtered object and QC plots to `analysis/qc/`
8. Report cell counts per sample before/after filtering

Follow thresholds in `configs/analysis_config.yaml`.
