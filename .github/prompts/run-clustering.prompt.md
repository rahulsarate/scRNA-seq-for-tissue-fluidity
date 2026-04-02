---
description: "Run clustering pipeline: normalize, integrate, cluster, annotate cell types"
---

Process the QC-filtered scRNA-seq object through the full clustering pipeline:

1. SCTransform normalization (regress percent.mt)
2. PCA (50 components), generate elbow plot
3. Harmony integration (group.by = "sample")
4. UMAP (dims 1:30)
5. Leiden clustering at resolutions 0.4, 0.6, 0.8, 1.0
6. Generate clustree plot to pick optimal resolution
7. Annotate cell types using known markers:
   - Basal keratinocytes: Krt14, Krt5, Tp63
   - Differentiated keratinocytes: Krt10, Krt1, Ivl
   - Fibroblasts: Col1a1, Dcn, Pdgfra
   - Myofibroblasts: Acta2, Tagln, Postn
   - Macrophages: Cd68, Adgre1, Csf1r
   - Neutrophils: S100a8, S100a9
   - Endothelial: Pecam1, Cdh5
   - HFSCs: Sox9, Lgr5
8. Create dot plot and feature plots for markers
9. Save annotated object to `analysis/clustering/`
