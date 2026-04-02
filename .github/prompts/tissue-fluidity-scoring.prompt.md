---
description: "Score cells for tissue fluidity gene signatures and analyze dynamics"
---

Score each cell for these 5 tissue fluidity gene signatures using Seurat AddModuleScore or Scanpy sc.tl.score_genes:

1. **EMT**: Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2
2. **ECM remodeling**: Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2
3. **Cell migration**: Rac1, Cdc42, Itgb1, Rhoa, Rock1, Rock2
4. **Mechanotransduction**: Yap1, Wwtr1, Piezo1, Trpv4, Lats1, Lats2
5. **Wound signals**: Tgfb1, Tgfb2, Tgfb3, Pdgfa, Vegfa, Wnt5a, Il6, Tnf

Then:
- Create UMAP feature plots colored by each signature score
- Create violin plots by condition for each signature
- Identify which cell types have the highest fluidity scores
- Find the condition where fluidity peaks (the "tipping point")
- Save scored object and plots to `analysis/clustering/` and `analysis/figures/`
