---
name: tissue-fluidity
description: "Tissue fluidity gene signatures and scoring for wound healing analysis. Use when working with EMT, ECM, migration, mechanotransduction, or wound signal genes."
---

# Tissue Fluidity Scoring Skill

## When to Use
- Scoring cells for tissue fluidity signatures
- Analyzing EMT, ECM remodeling, cell migration genes
- Comparing fluidity across wound healing conditions
- Highlighting tissue fluidity genes in DE results

## Gene Signatures

### EMT (Epithelial-Mesenchymal Transition)
`Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2`

### ECM Remodeling
`Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2`

### Cell Migration
`Rac1, Cdc42, Itgb1, Rhoa, Rock1, Rock2, Itga6, Cxcl12, Cxcr4`

### Mechanotransduction
`Yap1, Wwtr1, Piezo1, Trpv4, Lats1, Lats2`

### Wound Signals
`Tgfb1, Tgfb2, Tgfb3, Pdgfa, Pdgfb, Fgf2, Vegfa, Wnt5a`

## Scoring Pattern (Python/Scanpy)
```python
fluidity_sets = {
    'EMT_signature': ['Vim', 'Cdh1', 'Cdh2', 'Snai1', 'Snai2', 'Twist1', 'Zeb1', 'Zeb2'],
    'ECM_remodeling': ['Fn1', 'Col1a1', 'Col3a1', 'Mmp2', 'Mmp9', 'Mmp14', 'Timp1', 'Lox', 'Loxl2'],
    'Cell_migration': ['Rac1', 'Cdc42', 'RhoA', 'Itgb1', 'Itga6', 'Cxcl12', 'Cxcr4'],
    'Mechanotransduction': ['Yap1', 'Wwtr1', 'Piezo1', 'Trpv4', 'Lats1', 'Lats2'],
    'Wound_signals': ['Tgfb1', 'Tgfb2', 'Tgfb3', 'Pdgfa', 'Pdgfb', 'Fgf2', 'Vegfa', 'Wnt5a'],
}

for name, genes in fluidity_sets.items():
    available = [g for g in genes if g in adata.var_names]
    if available:
        sc.tl.score_genes(adata, gene_list=available, score_name=f'fluidity_{name}')
```

## Scoring Pattern (R/Seurat)
```r
fluidity_sets <- list(
  EMT = c("Vim", "Cdh1", "Cdh2", "Snai1", "Snai2", "Twist1", "Zeb1", "Zeb2"),
  ECM = c("Fn1", "Col1a1", "Col3a1", "Mmp2", "Mmp9", "Mmp14", "Timp1", "Lox"),
  Migration = c("Rac1", "Cdc42", "RhoA", "Itgb1", "Itga6"),
  Mechanotx = c("Yap1", "Piezo1", "Trpv4", "Lats1", "Lats2"),
  WoundSig = c("Tgfb1", "Pdgfa", "Vegfa", "Wnt5a", "Fgf2")
)

for (name in names(fluidity_sets)) {
  genes <- fluidity_sets[[name]]
  available <- genes[genes %in% rownames(sobj)]
  if (length(available) >= 2) {
    sobj <- AddModuleScore(sobj, features = list(available), name = paste0("fluidity_", name))
  }
}
```

## Expected Biology
- **Control**: Low fluidity scores (homeostatic skin)
- **wound_3d**: High EMT + wound signals (inflammatory phase)
- **wound_7d**: Peak ECM + mechanotransduction (proliferative phase)
- **wound_14d**: Declining fluidity (remodeling/resolution)
- **Key cell types**: Fibroblasts and myofibroblasts show highest ECM/migration scores
