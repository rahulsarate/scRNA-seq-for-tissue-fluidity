# Day 14: Visualization & Publication Figures

> **Goal**: Know every plot type we create, what it shows, and publication standards.

---

## Our Visualization Pipeline

`scripts/python/02_visualization_suite.py` generates all figures:

```
Figures created:
├── UMAP overview (clusters, conditions, cell types)
├── Tissue fluidity feature plots
├── Cell proportion stacked bars
├── Dot plots of marker genes
├── Volcano plots (DE results)
├── Heatmaps (top DE genes)
├── Fluidity score violin/box plots
└── Cell-cell communication network (simplified)
```

---

## Plot Types Explained

### 1. UMAP Plot
**Shows**: Every cell as a dot in 2D, colored by cluster/condition/cell type
**Purpose**: Overview of cell populations and how conditions differ
**Key question answered**: "Are the expected cell types present? Do conditions separate?"

### 2. Volcano Plot
**Shows**: Every gene plotted by log2FC (x-axis) vs -log10(padj) (y-axis)
```
    -log10(padj)
    │    ●                    ●
    │   ● ●                ● ●
    │  ●   ●    . . .    ●   ●
    │ . . . . . . . . . . . . .  ← padj=0.05 line
    │. . . . . . . . . . . . .
    └─────────────────────────
    -4   -2    0    +2   +4
         log2 Fold Change
         
    Left: downregulated    Right: upregulated
    Top: significant       Bottom: not significant
    Colored dots: significant + biologically meaningful
```

### 3. Dot Plot
**Shows**: Gene expression per cell type — dot SIZE = % cells expressing, dot COLOR = expression level
**Purpose**: Validate cell type annotation via marker gene specificity

### 4. Heatmap
**Shows**: Expression of top DE genes across conditions/cell types
**Purpose**: Visualize patterns — which genes co-regulate, which conditions cluster together

### 5. Cell Proportion Stacked Bar
**Shows**: Fraction of each cell type per condition
**Purpose**: See how cell composition changes across wound healing phases

### 6. Fluidity Score Box/Violin Plots
**Shows**: Distribution of fluidity scores per condition
**Purpose**: Quantify the fluidity trajectory (control → wound_3d → wound_7d → wound_14d)

---

## Publication Standards

### Our Requirements (from config)

| Setting | Value | Why |
|---------|-------|-----|
| DPI | 300 | Minimum for print journals |
| Format | PDF | Vector graphics, scalable |
| Color palette | Colorblind-safe | Wong et al. 2011, ~8% of men are colorblind |
| Font size | 11pt body, 13pt titles | Readable in two-column journal layout |
| Figure size | Specified per plot type | Match journal column widths |

### Colorblind-Safe Palettes

```python
# Our condition colors (diverging blue→red):
CONDITION_COLORS = {
    'control': '#2166AC',    # Blue
    'wound_3d': '#F4A582',   # Light salmon
    'wound_7d': '#D6604D',   # Red
    'wound_14d': '#B2182B',  # Dark red
}

# Our cell type colors (Wong palette + extended):
CELL_TYPE_COLORS = {
    'Basal_Keratinocyte': '#E69F00',  # Orange
    'Fibroblast': '#56B4E9',          # Sky blue
    'Macrophage': '#D55E00',          # Vermilion
    # ...
}
```

### Publication Style Setup

```python
def set_publication_style():
    plt.rcParams.update({
        'font.size': 11,
        'font.family': 'sans-serif',
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'figure.dpi': 300,
    })
```

---

## Creating Multi-Panel Figures

### Why Multi-Panel?

Journals prefer compact figures with multiple related panels:

```
    Figure 1: Wound Healing Cell Atlas
    ┌─────────────────────────────────────┐
    │  A) UMAP by cluster  │ B) UMAP by  │
    │                      │   condition  │
    ├──────────────────────┼──────────────┤
    │  C) Cell proportions │ D) Marker    │
    │     stacked bar      │   dot plot   │
    └─────────────────────────────────────┘
```

```python
fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, hspace=0.3, wspace=0.3)

ax1 = fig.add_subplot(gs[0, 0])  # A
ax2 = fig.add_subplot(gs[0, 1])  # B
ax3 = fig.add_subplot(gs[1, 0])  # C
ax4 = fig.add_subplot(gs[1, 1])  # D

plt.savefig('analysis/figures/figure1_atlas.pdf', dpi=300, bbox_inches='tight')
```

---

## Interview Q&A

### Q: "What visualization standards do you follow?"

> "All figures are PDF at 300 DPI for publication quality. I use colorblind-safe palettes — the Wong palette for categorical data and diverging RdBu for continuous scores. Multi-panel figures use matplotlib GridSpec for precise layout. Font sizes follow journal guidelines. Every plot has a clear title, axis labels, and legend."

### Q: "Walk me through your key figures."

> "Figure 1 is the cell atlas overview — UMAP colored by cluster, condition, and cell type, with cell proportion bars. Figure 2 shows tissue fluidity with UMAP feature plots for each of the 5 signatures plus box plots showing fluidity trajectories across conditions. Figure 3 is the DE analysis — volcano plots for each timepoint comparison plus a heatmap of top differentially expressed fluidity genes."

---

## Self-Check Questions

1. **What DPI for publication figures?** → 300 minimum
2. **Why colorblind-safe palettes?** → ~8% of men have color vision deficiency
3. **Preferred figure format?** → PDF (vector, scalable)
4. **What does a volcano plot show?** → log2FC vs -log10(padj) for every gene
5. **What does dot SIZE mean in a dot plot?** → Percentage of cells expressing the gene
6. **Why multi-panel figures?** → Journal preference, compact, related panels together
7. **Where are figures saved?** → analysis/figures/
8. **What axes does a volcano plot have?** → x: log2FC, y: -log10(padj)
9. **What do cell proportion bars show?** → How cell type composition changes across conditions
10. **What python library handles multi-panel layouts?** → matplotlib.gridspec

---

**Next**: [Day 15 — The Interactive Dashboard](Day_15_Dashboard.md)
