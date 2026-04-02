---
description: "Run pseudobulk DESeq2 differential expression for wound conditions"
---

Run pseudobulk differential expression using DESeq2:

1. Aggregate counts by (cell_type + condition + sample) to create pseudobulk
2. For each major cell type, compare:
   - wound_3d vs control
   - wound_7d vs control
   - wound_14d vs control
3. Apply lfcShrink (type = "ashr")
4. Filter significant genes: padj < 0.05, |log2FC| > 1.0
5. Save results as CSV in `analysis/de/` with columns: gene, log2FC, padj, baseMean
6. Highlight tissue fluidity genes: Vim, Fn1, Mmp2, Mmp9, Tgfb1, Acta2, Yap1, Snai1, Zeb1
7. Create summary table: which fluidity genes are DE in which cell types
