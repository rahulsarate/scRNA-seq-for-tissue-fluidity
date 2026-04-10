---
name: publication-figures
description: "Create publication-quality figures: UMAP, volcano, heatmap, dotplot, cell proportions. Use when generating figures for papers or presentations."
---

# Publication Figures Skill

## When to Use
- Creating UMAP overview panels
- Volcano plots for DE results
- Heatmaps and dotplots
- Cell proportion bar charts
- Any figure for publication

## Standards
- Format: PDF (vector) + PNG (300 DPI)
- Colorblind-safe palettes
- White background, no frame
- Font size ≥ 8pt for labels

## Color Palettes
```python
# Wound conditions
wound_colors = {
    "control": "#2166AC", "wound_3d": "#F4A582",
    "wound_7d": "#D6604D", "wound_14d": "#B2182B"
}

# Cell types (10 expected)
cell_type_colors = {
    "Basal KC": "#1f77b4", "Differentiated KC": "#aec7e8",
    "Fibroblast": "#ff7f0e", "Myofibroblast": "#ffbb78",
    "Macrophage": "#2ca02c", "Neutrophil": "#98df8a",
    "T cell": "#d62728", "Endothelial": "#9467bd",
    "HFSC": "#8c564b", "Melanocyte": "#e377c2"
}
```

## Figure Templates

### UMAP (Python)
```python
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
sc.pl.umap(adata, color='cell_type', ax=axes[0], show=False,
           palette=cell_type_colors, title='Cell Types')
sc.pl.umap(adata, color='condition', ax=axes[1], show=False,
           palette=wound_colors, title='Conditions')
plt.tight_layout()
plt.savefig('analysis/figures/Fig1_UMAP_overview.pdf', dpi=300, bbox_inches='tight')
plt.savefig('analysis/figures/Fig1_UMAP_overview.png', dpi=300, bbox_inches='tight')
plt.close()
```

### Volcano Plot
```python
from adjustText import adjust_text

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(de['log2FC'], -np.log10(de['padj']), c='grey', alpha=0.5, s=5)
sig = de[(de['padj'] < 0.05) & (abs(de['log2FC']) > 1)]
up = sig[sig['log2FC'] > 0]
down = sig[sig['log2FC'] < 0]
ax.scatter(up['log2FC'], -np.log10(up['padj']), c='#D6604D', s=10)
ax.scatter(down['log2FC'], -np.log10(down['padj']), c='#2166AC', s=10)
ax.axhline(-np.log10(0.05), ls='--', c='grey', lw=0.5)
ax.axvline(-1, ls='--', c='grey', lw=0.5)
ax.axvline(1, ls='--', c='grey', lw=0.5)
```

### Cell Proportions
```python
props = adata.obs.groupby(['condition', 'cell_type']).size().unstack(fill_value=0)
props = props.div(props.sum(axis=1), axis=0) * 100
props.plot(kind='bar', stacked=True, color=cell_type_colors, figsize=(10, 6))
```

## Save Pattern
Always save both PDF and PNG:
```python
for ext in ['pdf', 'png']:
    plt.savefig(f'analysis/figures/{name}.{ext}', dpi=300, bbox_inches='tight')
plt.close()
```
