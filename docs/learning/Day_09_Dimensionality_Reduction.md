# Day 9: Dimensionality Reduction — PCA & UMAP

> **Goal**: Understand why we reduce 2,000 gene dimensions to 2, how PCA and UMAP work conceptually, and how to interpret UMAP plots.

---

## The Problem: The Curse of Dimensionality

```
Each cell is described by ~2,000 HVG expression values.
Each gene = 1 dimension.

You live in 3D (x, y, z). Imagine 2,000 dimensions.
- Distances become meaningless
- Visualization is impossible
- Clustering algorithms struggle
- Computation is extremely slow

Solution: Reduce from 2,000 dimensions to 2 (for plotting)
          or ~30 (for analysis)
```

**Analogy**: Describing a person with 2,000 measurements (height, weight, shoe size, eye color, blood pressure, ...) vs just 2 (height and weight). Two numbers still capture a LOT of the variation.

---

## Step 1: PCA (Principal Component Analysis)

### What PCA Does — In Plain English

```
2,000 genes → 50 Principal Components (PCs)

PC1 captures the MOST variation in the data
PC2 captures the NEXT most variation (independent of PC1)
PC3 = next most
...
PC50 = very little remaining variation
```

**Think of it this way**:
- PC1 might = "keratinocyte vs immune cell" (the BIGGEST difference)
- PC2 might = "wound vs control" (next biggest)
- PC3 might = "fibroblast subtype" (smaller)
- PC30+ = mostly noise

### Visual Analogy

```
Imagine photographing a 3D sculpture:

Photo from front (PC1) → captures MOST info
Photo from side  (PC2) → captures NEXT most
Photo from top   (PC3) → captures remaining info

2 photos (2 PCs) give you ~80% understanding
All 3 photos (3 PCs) give you 100%

Same logic: 30 PCs capture ~90% of the biology in 2,000 genes
```

### Our PCA Code

```python
def dimensionality_reduction(adata):
    # PCA on HVGs only
    adata_hvg = adata[:, adata.var.highly_variable].copy()
    sc.pp.scale(adata_hvg, max_value=10)
    
    sc.tl.pca(adata_hvg, svd_solver='arpack', n_comps=50, random_state=42)
    
    # Copy PCA results back to full object
    adata.obsm['X_pca'] = adata_hvg.obsm['X_pca']
```

### The Elbow Plot — How Many PCs to Use?

```
    Variance Explained
    │
    │█
    │█
    │██
    │███
    │████
    │██████
    │█████████                    ← "elbow" around PC 15-30
    │█████████████████████
    │████████████████████████████████
    └────────────────────────────────
     PC1  5   10   15   20   30   50
    
    We use n_pcs=30 → captures most signal, ignores noise
```

**How to read it**: The steep drop-off means PC1-10 capture most variation. After ~30, each PC adds negligible information (mostly noise).

**Our setting**: `n_pcs = 30` (from `configs/analysis_config.yaml`)

---

## Step 2: Nearest Neighbors

### Building the Cell-Cell Graph

```python
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30, random_state=42)
```

**What this does**:
1. Take each cell's 30-dimensional PCA coordinates
2. Find its 15 nearest neighbors (most similar cells)
3. Build a graph: cells = nodes, connections = edges

```
    Cell Neighbor Graph:
    
    ○─○         ○─○─○
    │ │         │/ \│
    ○─○─○       ○   ○       ← Keratinocyte cluster
                │
    ○─○─○       ○─○
    │ │\│       │ │
    ○─○ ○       ○─○         ← Fibroblast cluster
```

**Why n_neighbors=15?** 
- Too few (5): graph too sparse, clusters fragment
- Too many (50): overconnected, distinct populations merge
- 15: standard default, balances resolution and connectivity

---

## Step 3: UMAP (Uniform Manifold Approximation and Projection)

### What UMAP Does

```
30 PCA dimensions → 2 UMAP dimensions (x, y for plotting)

The key property:
  Cells that are NEIGHBORS in 30D → placed NEAR each other in 2D
  Cells that are DIFFERENT in 30D → placed FAR apart in 2D
```

### How to READ a UMAP Plot

```
    UMAP2 ↑
          │     ○○○○
          │    ○○○○○○    ← Macrophages (clustered together)
          │     ○○○○
          │
          │  ●●●●●          ▲▲▲▲
          │ ●●●●●●●●       ▲▲▲▲▲▲
          │  ●●●●●●        ▲▲▲▲▲
          │                 
          └──────────────────────→ UMAP1
            Fibroblasts     Keratinocytes
    
    Clusters = groups of similar cells
    Distance between clusters ≈ biological difference
    (but don't over-interpret exact distances!)
```

### UMAP in Our Code

```python
sc.tl.umap(adata, random_state=42)

# Now adata.obsm['X_umap'] has 2D coordinates for every cell
# Plot colored by different properties:
sc.pl.umap(adata, color='leiden', title='Clusters')
sc.pl.umap(adata, color='condition', title='Condition')
sc.pl.umap(adata, color='cell_type', title='Cell Type')
```

### Our Three-Panel UMAP

```python
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
sc.pl.umap(adata, color='leiden', ax=axes[0])     # By cluster
sc.pl.umap(adata, color='condition', ax=axes[1])   # By wound timepoint
sc.pl.umap(adata, color='cell_type', ax=axes[2])   # By cell type
plt.savefig('analysis/figures/02_umap_overview.png')
```

This overview figure shows:
1. Do clusters separate cleanly?
2. Do conditions mix or segregate?
3. Do clusters correspond to expected cell types?

---

## Important UMAP Caveats

### What UMAP Does NOT Tell You

| Common Mistake | Reality |
|---------------|---------|
| "These clusters are far apart, so they're very different" | UMAP distances are NOT proportional to real distances |
| "This cluster is bigger, so there are more cells" | Density in UMAP ≠ cell count |
| "These cells are in the same cluster, so they're identical" | UMAP is a 2D projection — some differences are hidden |
| "UMAP doesn't show a cluster, so it doesn't exist" | UMAP parameters (n_neighbors, min_dist) affect what you see |

### UMAP vs t-SNE

| Feature | UMAP | t-SNE |
|---------|------|-------|
| Speed | Faster | Slower |
| Global structure | Better preserved | Only local structure |
| Reproducibility | With seed, yes | More variable |
| Current preference | Standard in 2024+ | Legacy (older papers) |

We use UMAP (industry standard as of 2024+).

---

## The Full Dimensionality Reduction Pipeline

```
2,000 HVGs per cell (normalized, scaled)
        │
        ▼
    PCA (50 components)
        │  ← Keep top 30 (elbow test)
        ▼
    Nearest Neighbors (k=15 in 30D PCA space)
        │
        ├──▶ UMAP (2D for visualization)
        │
        └──▶ Leiden Clustering (on the neighbor graph)
                                ← Day 10 topic
```

---

## Interview Q&A

### Q: "Why do you use PCA before UMAP?"

> "PCA serves as a noise reduction step. The 2,000 HVGs include noise, especially in the lower-variance genes. By running PCA first and keeping only the top 30 components, we concentrate the signal and discard noise. UMAP then works on this cleaner 30-dimensional representation rather than the noisy 2,000-dimensional original. This is called the 'PCA pre-processing' or 'denoising' step."

### Q: "How do you choose the number of PCs?"

> "I use the elbow plot — a scree plot of variance explained per PC. The 'elbow' is where the curve flattens, typically around PC 15-30 for scRNA-seq data. Using too few PCs loses biological signal; too many includes noise. Our config specifies 30 PCs, which is a well-validated default for 10X datasets."

### Q: "What is UMAP actually showing?"

> "UMAP projects each cell from 30 PCA dimensions to 2 dimensions for visualization, preserving local neighborhood relationships. Cells that were similar in 30D (share many expressed genes) appear close in 2D. Clusters represent groups of transcriptionally similar cells. However, I'm careful not to over-interpret distances between clusters or cluster sizes — UMAP distorts these."

### Q: "Why not just use PCA for visualization?"

> "PCA is a linear method — it can only show linear relationships between genes. Cell types often have non-linear relationships. UMAP captures non-linear structure, producing cleaner separation of cell populations. PCA plots (PC1 vs PC2) often show mixed clusters that UMAP cleanly resolves."

---

## Self-Check Questions

1. **Why reduce dimensions?** → 2,000 dims: visualization impossible, distances meaningless, computation slow
2. **What does PC1 capture?** → The direction of maximum variance in the data
3. **How many PCs do we use?** → 30 (chosen by elbow plot)
4. **What does the nearest-neighbor graph represent?** → Each cell connected to its 15 most similar cells
5. **What does UMAP preserve?** → Local neighborhood relationships (nearby cells stay near)
6. **Can you interpret UMAP cluster distances literally?** → No — UMAP distorts global distances
7. **Why PCA before UMAP?** → Denoising — PCA concentrates signal in top components
8. **What's n_neighbors=15?** → Each cell connected to 15 nearest cells for graph construction
9. **UMAP vs t-SNE?** → UMAP is faster, preserves global structure better, current standard
10. **Where are UMAP coordinates stored?** → `adata.obsm['X_umap']`

---

**Next**: [Day 10 — Clustering & Cell Type Annotation](Day_10_Clustering.md)
