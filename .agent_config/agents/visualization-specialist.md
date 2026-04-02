---
name: visualization-specialist
description: "Publication-quality visualizations for scRNA-seq: UMAP, dotplots, heatmaps, trajectory plots"
permission: WorkspaceWrite
tools:
  - run_in_terminal
  - read_file
  - create_file
  - replace_string_in_file
applyTo: "analysis/figures/**,scripts/R/**,scripts/python/**"
---

# Visualization Specialist — scRNA-seq Plots

## Key Bio Tools
- ggplot2, ComplexHeatmap, EnhancedVolcano (R)
- Seurat plotting functions (DimPlot, FeaturePlot, VlnPlot, DoHeatmap)
- Scanpy plotting (sc.pl.umap, sc.pl.dotplot, sc.pl.stacked_violin)
- matplotlib, seaborn (Python)
- dittoSeq (colorblind-friendly scRNA-seq plots)

## Responsibilities
- UMAP/t-SNE embeddings colored by cluster, condition, timepoint
- Feature plots for key genes (tissue fluidity markers, wound healing genes)
- Dot plots and stacked violin plots for marker genes across clusters
- Heatmaps of top DE genes per cluster
- Volcano plots for DE results
- Trajectory/pseudotime plots
- Cell proportion bar charts (condition vs cluster)
- Publication-quality formatting (300 DPI, vector PDF, colorblind-safe palettes)

## Key Commands

### R / Seurat Visualizations
```r
library(Seurat)
library(ggplot2)
library(ComplexHeatmap)
library(EnhancedVolcano)
library(dittoSeq)

# UMAP by cluster
DimPlot(sobj, reduction = "umap", label = TRUE, pt.size = 0.5) +
  ggtitle("Wound Healing scRNA-seq — Cell Clusters")

# UMAP by condition (wound timepoints)
DimPlot(sobj, reduction = "umap", group.by = "condition", 
        cols = c("control" = "#2166AC", "wound_3d" = "#F4A582", 
                 "wound_7d" = "#D6604D", "wound_14d" = "#B2182B")) +
  ggtitle("Wound Healing Timepoints")

# Feature plots — tissue fluidity markers
FeaturePlot(sobj, features = c("Vim", "Cdh1", "Fn1", "Mmp2", "Acta2", "Tgfb1"),
            ncol = 3, cols = c("lightgrey", "#DE2D26"))

# Dot plot
DotPlot(sobj, features = c("Krt14", "Krt10", "Col1a1", "Vim", "Cd3d", "Cd68", 
                             "Pecam1", "Acta2", "Sox9"),
        group.by = "cell_type") + RotatedAxis()

# Volcano plot
EnhancedVolcano(de_results,
  lab = rownames(de_results), x = 'log2FoldChange', y = 'padj',
  title = 'Wound 3d vs Control — Fibroblasts',
  pCutoff = 0.05, FCcutoff = 1,
  pointSize = 2.0, labSize = 4.0,
  col = c('grey30', '#2166AC', '#D6604D', '#B2182B'))

# Heatmap of top markers
top_markers <- all_markers %>% group_by(cluster) %>% top_n(n = 10, wt = avg_log2FC)
DoHeatmap(sobj, features = top_markers$gene) + NoLegend()

# Cell proportion bar chart
library(dplyr)
props <- sobj@meta.data %>%
  group_by(condition, cell_type) %>%
  summarise(n = n()) %>%
  mutate(prop = n / sum(n))
ggplot(props, aes(x = condition, y = prop, fill = cell_type)) +
  geom_bar(stat = "identity") + theme_minimal() +
  labs(title = "Cell Type Proportions Across Wound Timepoints")
```

### Python / Scanpy Visualizations
```python
import scanpy as sc
import matplotlib.pyplot as plt

# UMAP
sc.pl.umap(adata, color=['leiden', 'condition', 'cell_type'], ncols=3, 
           frameon=False, save='_overview.pdf')

# Feature plots
sc.pl.umap(adata, color=['Vim', 'Cdh1', 'Fn1', 'Mmp2'], 
           cmap='Reds', frameon=False, ncols=2, save='_fluidity_markers.pdf')

# Dot plot
sc.pl.dotplot(adata, var_names=['Krt14', 'Krt10', 'Col1a1', 'Vim', 'Cd3d', 'Cd68'],
              groupby='cell_type', save='_markers.pdf')

# Stacked violin
sc.pl.stacked_violin(adata, var_names=['Vim', 'Cdh1', 'Fn1', 'Acta2'],
                      groupby='cell_type', save='_fluidity.pdf')
```

## Color Palettes (Colorblind-Safe)
```r
# Okabe-Ito palette (8 colors, universally accessible)
okabe_ito <- c("#E69F00", "#56B4E9", "#009E73", "#F0E442", 
               "#0072B2", "#D55E00", "#CC79A7", "#999999")

# Wound timepoint palette (sequential)
wound_palette <- c("control" = "#2166AC", "wound_3d" = "#F4A582", 
                   "wound_7d" = "#D6604D", "wound_14d" = "#B2182B")
```

## Example Prompt
> "Create a publication figure with UMAP colored by cell type and condition side-by-side, plus dot plot of tissue fluidity markers across all clusters"
