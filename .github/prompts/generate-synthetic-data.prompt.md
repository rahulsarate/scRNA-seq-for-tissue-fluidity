---
description: "Generate synthetic scRNA-seq test data for pipeline validation"
---

Generate a synthetic scRNA-seq dataset for the wound healing project with these specs:
- 8000 cells, 2000 genes
- 10 cell types: basal keratinocytes, differentiated keratinocytes, fibroblasts, myofibroblasts, macrophages, neutrophils, T cells, endothelial, HFSCs, melanocytes
- 4 conditions: control, wound_3d, wound_7d, wound_14d (2 replicates each)
- Include tissue fluidity signatures (EMT, ECM, mechanotransduction genes)
- Use negative binomial distribution with realistic dropout
- Save to `data/synthetic/` as both .h5ad and .csv
- Set random_state=42

Use the script at `scripts/python/generate_synthetic_data.py` as a starting point.
Read `configs/analysis_config.yaml` for gene signatures and thresholds.
