# Day 23: Batch Effects & Integration

> **Goal**: Understand batch effects — why they arise, how to detect them, and how Harmony fixes them.

---

## What Are Batch Effects?

Technical variation between samples that aren't biological.

```
Biological signal:                 Batch effect:
  Control vs Wound_7d               Sample processed Monday vs Friday
  Different gene programs            Different reagent lots
  Real biology                       Sequencing depth differences

We want to KEEP biology            We want to REMOVE batch effects
```

### Where Batch Effects Come From

```
Source                    →  Effect on Data
Different sequencing runs →  Depth/coverage differences
Different 10X reactions   →  Capture efficiency varies
Different operators       →  Library prep variation
Different days            →  Reagent degradation
```

---

## Detecting Batch Effects

### Visual Check: UMAP Before Integration

```
BAD — cells cluster by sample, not biology:

UMAP before integration:
  ○○○○   ●●●●
  ○○○○   ●●●●     ○ = sample_1
  ○○○○   ●●●●     ● = sample_2

  Samples form separate clusters!
  → Batch effect is dominating


GOOD — cells cluster by cell type:

UMAP after integration:
  ○●○●●
  ●○●○●     ○ = sample_1
  ○●●○●     ● = sample_2

  Samples are mixed within cell type clusters
  → Biology is dominating
```

### Quantitative Check
```python
# Calculate mixing metric
# LISI: Local Inverse Simpson Index
# Higher LISI = better mixing across batches
import scib
lisi_scores = scib.metrics.ilisi(adata, batch_key='sample')
```

---

## Harmony Integration (Our Method)

### Why Harmony?

| Method | Speed | Memory | Quality | Our Use |
|--------|-------|--------|---------|---------|
| Harmony | Fast | Low | Good | ✅ Primary |
| Scanorama | Medium | Medium | Good | Alternative |
| BBKNN | Fast | Low | Medium | Simple option |
| scVI | Slow | High | Excellent | Deep learning |

Harmony is configured in our `analysis_config.yaml`:
```yaml
integration:
  method: "harmony"
  batch_key: "sample"
  max_iter: 20
```

### How Harmony Works (Intuition)

```
Step 1: Run PCA normally
  → 30 PCs capture both biology + batch effects

Step 2: Harmony iterates:
  a) Group cells into clusters in PC space
  b) Within each cluster, SHIFT cells to remove
     batch-specific displacement
  c) Repeat until convergence

Step 3: Result = corrected PC embeddings
  → Input to UMAP, neighbors, clustering
```

```
Before Harmony:              After Harmony:
PCA captures batch effect    PCA captures biology only

PC1: 40% batch, 30% bio     PC1: 60% bio, 10% batch
PC2: 20% batch, 25% bio     PC2: 55% bio, 5% batch
```

### Code Implementation

```python
import scanpy as sc
import scanpy.external as sce

# Standard PCA first
sc.tl.pca(adata, n_comps=30, random_state=42)

# Run Harmony on PCA embeddings
sce.pp.harmony_integrate(
    adata,
    key='sample',                    # Batch variable
    max_iter_harmony=20,
    adjusted_basis='X_pca_harmony'   # Corrected PCs stored here
)

# Use corrected PCs for downstream
sc.pp.neighbors(adata, use_rep='X_pca_harmony', n_neighbors=15)
sc.tl.umap(adata, random_state=42)
sc.tl.leiden(adata, resolution=0.8, random_state=42)
```

---

## Critical Distinction: What Gets Corrected

```
Corrected:
  adata.obsm['X_pca_harmony']  ← Corrected PCs
  adata.obsm['X_umap']        ← UMAP from corrected PCs
  Clustering assignments       ← From corrected neighbors

NOT corrected (and shouldn't be):
  adata.X                      ← Raw/normalized counts stay original
  DE analysis                  ← Uses original counts (not corrected)
```

**Why?** DE analysis needs real count data. Batch correction on counts can introduce artifacts. Harmony corrects the embedding space only.

---

## Our 8-Sample Design

```
Condition    Samples    Harmony handles:
control      rep1, rep2   → technical variation between reps
wound_3d     rep1, rep2   → sequencing depth differences
wound_7d     rep1, rep2   → 10X reaction batch effects
wound_14d    rep1, rep2   → processing day differences
```

With 2 replicates per condition and 4 conditions, batch effects could confound time-point comparisons if not corrected.

---

## Interview Q&A

### Q: "What are batch effects and how do you handle them?"

> "Batch effects are technical variations between samples — different sequencing runs, reagent lots, or processing days. They can dominate over biological signal, making cells cluster by sample instead of cell type. We use Harmony integration, which corrects PC embeddings by iteratively removing batch-specific displacements while preserving biological variation. Importantly, we only correct the embedding space — raw counts stay unchanged for downstream DE analysis."

### Q: "Why Harmony over other integration methods?"

> "Harmony is fast, memory-efficient, and performs well on datasets of our size (8 samples). It operates on PCA embeddings rather than raw counts, which is methodologically clean — corrected embeddings for clustering/UMAP but original counts for DE. For larger or more complex datasets, I'd consider scVI (deep learning-based), but for our 8-sample design, Harmony is the standard choice."

### Q: "What stays corrected and what doesn't?"

> "Only the PCA embeddings get corrected. These corrected PCs feed into neighbor computation, UMAP, and clustering. The raw/normalized expression matrix stays untouched — DE analysis uses original counts, not corrected values, because count correction can introduce statistical artifacts."

---

## Self-Check Questions

1. **What is a batch effect?** → Technical variation between samples unrelated to biology
2. **How to visually detect batch effects?** → UMAP: cells cluster by sample instead of cell type
3. **What integration method do we use?** → Harmony
4. **What does Harmony correct?** → PCA embeddings (not raw counts)
5. **Why NOT correct raw counts?** → Could introduce artifacts; DE needs real counts
6. **What is the batch key in our config?** → `sample`
7. **Where are corrected PCs stored?** → `adata.obsm['X_pca_harmony']`
8. **How many samples need integration?** → 8 (2 reps × 4 conditions)
9. **What is LISI?** → Local Inverse Simpson Index — measures batch mixing quality
10. **What feeds into UMAP after integration?** → Corrected PCA embeddings, not raw data

---

**Next**: [Day 24 — Trajectory Analysis & RNA Velocity](Day_24_Trajectory.md)
