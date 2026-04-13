# Day 10: Clustering & Cell Type Annotation

> **Goal**: Understand how cells are grouped into clusters and how we assign biological identities (cell types) to each cluster.

---

## Clustering: Finding Groups of Similar Cells

### What Clustering Does

```
Input: Cell neighbor graph (from Day 9)
Output: Each cell assigned to a group (cluster 0, 1, 2, ...)

Analogy: 
  Social network analysis — find "friend groups"
  where people (cells) who interact most (share genes)
  are placed in the same community
```

### Leiden Algorithm — How Our Clustering Works

```python
sc.tl.leiden(adata, resolution=0.8, key_added='leiden', random_state=42)
```

**Steps** (simplified):
1. Start with the neighbor graph (cells = nodes, similarities = edges)
2. Find "communities" — groups of cells more connected to each other than to outsiders
3. Optimize modularity — mathematical measure of community quality
4. Assign each cell a cluster label (0, 1, 2, 3, ...)

### Resolution Parameter — The Key Knob

```
Resolution = 0.4       Resolution = 0.8       Resolution = 1.5
(few, large clusters)  (balanced — our default) (many, small clusters)

  ╭──────────╮         ╭─────╮  ╭─────╮       ╭──╮ ╭──╮ ╭──╮
  │ cluster 0│         │  0  │  │  1  │       │0 │ │1 │ │2 │
  │          │         ╰─────╯  ╰─────╯       ╰──╯ ╰──╯ ╰──╯
  ╰──────────╯         ╭─────╮  ╭─────╮       ╭──╮ ╭──╮ ╭──╮
  ╭──────────╮         │  2  │  │  3  │       │3 │ │4 │ │5 │
  │ cluster 1│         ╰─────╯  ╰─────╯       ╰──╯ ╰──╯ ╰──╯
  ╰──────────╯
  
  3 clusters            7 clusters             12 clusters
```

**The trade-off**:
- Low resolution → merges distinct cell types (bad: macrophages + neutrophils = one cluster)
- High resolution → splits one cell type into meaningless sub-clusters (bad: 5 fibroblast clusters)
- **0.8 = balanced default** — typically gives 8-12 clusters matching known cell types

### Our Multi-Resolution Approach

```python
# We test 4 resolutions:
for res in [0.4, 0.6, 0.8, 1.0]:
    key = f'leiden_res{res}'
    sc.tl.leiden(adata, resolution=res, key_added=key, random_state=42)

# Choose the one that best matches known biology:
adata.obs['leiden'] = adata.obs['leiden_res0.8']
```

**Why test multiple?** No single resolution is universally correct. We pick the one where:
- Number of clusters ≈ expected cell types (10 in our case)
- Known marker genes map cleanly to single clusters
- No biologically distinct types are merged

---

## Cell Type Annotation: From Numbers to Biology

### The Problem
Clustering gives us: Cluster 0, 1, 2, 3, ...
We need: Fibroblast, Macrophage, Keratinocyte, ...

### Strategy: Marker Gene Scoring

```python
# For each cell type, score how strongly it expresses known markers:
CELL_MARKERS = {
    'Basal_Keratinocyte': ['Krt14', 'Krt5', 'Tp63'],
    'Fibroblast': ['Col1a1', 'Col3a1', 'Dcn', 'Pdgfra'],
    'Macrophage': ['Cd68', 'Adgre1', 'Csf1r'],
    # ... 10 total
}

for ct, markers in CELL_MARKERS.items():
    available = [g for g in markers if g in adata.var_names]
    sc.tl.score_genes(adata, gene_list=available, score_name=f'score_{ct}')
```

**How `sc.tl.score_genes` works**:
1. For each cell, calculate average expression of the marker genes
2. Subtract average expression of a random control gene set (background correction)
3. Result: a score — positive = this cell expresses these markers above background

### Assigning Cell Types

```python
# Each cell gets the cell type with its HIGHEST score:
score_cols = [c for c in adata.obs.columns if c.startswith('score_')]
scores = adata.obs[score_cols].values
ct_names = [c.replace('score_', '') for c in score_cols]
best = np.argmax(scores, axis=1)
adata.obs['predicted_cell_type'] = [ct_names[i] for i in best]
```

```
Cell 1: Krt14=high, Col1a1=low, Cd68=low → Basal_Keratinocyte
Cell 2: Krt14=low, Col1a1=high, Cd68=low → Fibroblast
Cell 3: Krt14=low, Col1a1=low, Cd68=high → Macrophage
```

### The Dot Plot — Verifying Annotation

```
                Krt14  Col1a1  Cd68  Acta2  S100a8  Pecam1
Basal_Kerat.     ●●●    ○      ○      ○      ○       ○
Fibroblast        ○    ●●●     ○      ○      ○       ○
Macrophage        ○     ○     ●●●     ○      ○       ○
Myofibroblast     ○    ●●    ○      ●●●     ○       ○
Neutrophil        ○     ○      ○      ○     ●●●      ○
Endothelial       ○     ○      ○      ○      ○      ●●●

●●● = highly expressed (large, dark dot)
○   = not expressed (small, light dot)
```

**If the dot plot shows** Krt14 is high ONLY in the cluster labeled Basal_Keratinocyte → annotation is correct.

### Generating the Dot Plot

```python
marker_list = ['Krt14', 'Krt5', 'Col1a1', 'Dcn', 'Cd68', 'Adgre1',
               'Acta2', 'S100a8', 'Pecam1', 'Sox9', 'Dct']

sc.pl.dotplot(adata, var_names=marker_list, groupby='predicted_cell_type',
              save='_cell_type_markers.png')
```

---

## Validating Our Annotations

### What Should Match Our Expectations?

From our config/biology (Day 3):

| Cell Type | Expected in wound_3d | Expected in wound_7d | Marker Check |
|-----------|--------------------|--------------------|-------------|
| Macrophage | ↑↑ HIGH (25%) | ↓ moderate | Cd68+, Adgre1+ |
| Neutrophil | ↑↑ HIGH (15%) | ↓↓ low | S100a8+, S100a9+ |
| Myofibroblast | ↑ moderate | ↑↑ HIGH (15%) | Acta2+, Tagln+ |
| Basal Keratinocyte | ↓ reduced (10%) | ↑ recovering | Krt14+, Krt5+ |

### Cell Type Proportions

```
              control   wound_3d   wound_7d   wound_14d
BasalKerat.   ████████   ███        ██████     ███████
Fibroblast    ████████   ██████     ████████   ████████
Macrophage    ███        █████████  █████      ████
Neutrophil    █          ███████    ██         █
Myofibro.     █          ████       ███████    ██
T_Cell        ██         ████       ███        ██
Endothelial   ████       ███        ████       ████
HFSC          ███        ██         ██         ███
Melanocyte    ██         ██         ██         ██
```

If proportions DON'T match expected biology → re-evaluate clustering resolution or marker definitions.

---

## Why Leiden Over K-Means?

| Feature | Leiden | K-Means |
|---------|--------|---------|
| Requires k (# clusters) | No — finds it | Yes — must specify |
| Works on graph | Yes | No (Euclidean space) |
| Handles irregular shapes | Yes | No (assumes spherical clusters) |
| Standard for scRNA-seq | Yes (2024+) | No |
| Predecessor | Louvain (older) | N/A |

**Leiden vs Louvain**: Leiden is the improved version — fixes a theoretical issue where Louvain could produce poorly connected clusters.

---

## Batch Effects — A Hidden Danger

### What Are Batch Effects?

```
Sample processed Monday    Sample processed Friday
        ○○○○                      ●●●●
       ○○○○○○                    ●●●●●●
        ○○○○                      ●●●●
        
    Both are fibroblasts, but they cluster SEPARATELY
    because of technical differences (reagent lot, temperature, operator)
```

### Solution: Batch Correction (Harmony)

```yaml
# From our config:
integration:
  method: "Harmony"
  group_by: "sample"
  dims: 30
```

**Harmony** adjusts PCA coordinates so that batch differences are removed while biological differences are preserved:

```
Before Harmony:                After Harmony:
○○ Monday fibroblasts          ○● Mixed fibroblasts
●● Friday fibroblasts          ●○ (batch effect removed)
                               
○○ Monday macrophages          ○● Mixed macrophages
●● Friday macrophages          ●○
```

---

## Interview Q&A

### Q: "How do you cluster cells and assign cell types?"

> "I use Leiden community detection on the nearest-neighbor graph — it finds natural cell communities without requiring a pre-specified number of clusters. I test multiple resolutions (0.4 to 1.0) and select the one that best matches expected cell types. For annotation, I score each cell against 10 known marker gene sets — each cell type has 3-6 known marker genes from literature. Each cell is assigned to the cell type with the highest marker score. I validate annotations with dot plots showing marker specificity, and cross-check proportions against expected wound healing biology."

### Q: "How do you choose clustering resolution?"

> "I test resolutions 0.4, 0.6, 0.8, and 1.0 which give 5 to 15 clusters. I choose the resolution where: (1) each known cell type maps to approximately one cluster, (2) marker genes show clean specificity in dot plots, (3) cell proportions match expected biology — for example, macrophage surge at wound day 3. Resolution 0.8 typically gives 8-12 clusters matching our 10 expected cell types."

### Q: "What are batch effects and how do you handle them?"

> "Batch effects are technical differences between samples processed at different times or conditions. They can cause cells from different batches to cluster separately even if they're the same cell type. We use Harmony integration — it adjusts PCA coordinates to minimize batch-driven variance while preserving biological variation. I verify success by checking that cell types from all conditions co-cluster."

---

## Self-Check Questions

1. **What algorithm do we use for clustering?** → Leiden
2. **What does resolution control?** → Number of clusters (higher = more clusters)
3. **Our default resolution?** → 0.8
4. **How do we assign cell type names?** → Score each cell against marker gene sets, assign highest score
5. **What is a dot plot?** → Shows marker gene expression per cell type — validates annotation
6. **Why Leiden over K-means?** → Doesn't require pre-specifying k, works on graphs, handles irregular shapes
7. **What are batch effects?** → Technical differences between samples that cause artificial clustering
8. **How does Harmony fix batch effects?** → Adjusts PCA coordinates to remove batch variance
9. **How many cell types do we expect?** → 10
10. **How do you validate annotations?** → Dot plot of markers + proportion check vs expected biology

---

**Next**: [Day 11 — Differential Expression Analysis](Day_11_Differential_Expression.md)
