---
description: "Create publication-quality multi-panel figure"
---

Create a publication-quality multi-panel figure (Figure 1) for the manuscript:

Panel A: UMAP colored by cell type with labels (no legend overlap)
Panel B: UMAP colored by wound condition using palette:
  - control: #2166AC
  - wound_3d: #F4A582
  - wound_7d: #D6604D
  - wound_14d: #B2182B
Panel C: UMAP split by condition (4 panels side-by-side)
Panel D: Cell type proportion stacked bar chart across conditions

Requirements:
- Colorblind-safe palette
- 300 DPI
- Export as PDF to `analysis/figures/`
- Arial font, 8-12pt
- Clean theme (no gridlines, minimal)
- Panel labels A, B, C, D in top-left corners
