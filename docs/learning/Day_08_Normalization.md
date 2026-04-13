# Day 8: Normalization & Feature Selection

> **Goal**: Understand why raw counts can't be compared directly, how normalization works, and why we select highly variable genes.

---

## The Problem: Raw Counts Are Misleading

### Why You Can't Compare Raw Counts Between Cells

```
Cell A: captured 10,000 total mRNAs (deep sequencing)
Cell B: captured 2,000 total mRNAs (shallow capture)

Gene X:
    Cell A → 100 counts (100/10,000 = 1.0%)
    Cell B → 20 counts  (20/2,000  = 1.0%)

Raw counts say A >> B  (100 vs 20)
But the TRUTH: both cells express Gene X at 1%

Without normalization, you'd conclude Cell A has 5x more Gene X.
That's wrong — it just had better sequencing.
```

**Analogy**: Comparing test scores when Student A took a 100-question exam and Student B took a 20-question exam. You need percentages, not raw scores.

---

## Step-by-Step Normalization

### Our Pipeline Uses Three Steps:

```
Raw Counts → Normalize Total → Log Transform → Scale
```

### Step 1: Normalize Total (Library Size Normalization)

```python
sc.pp.normalize_total(adata, target_sum=1e4)
```

**What it does**: Make every cell sum to 10,000 total counts.

```
Before:                          After (target_sum=10000):
Cell A: [100, 50, 0, 200, ...]  Cell A: [28.6, 14.3, 0, 57.1, ...]
        (total = 3500)                   (total = 10000)
Cell B: [10, 5, 0, 20, ...]     Cell B: [28.6, 14.3, 0, 57.1, ...]
        (total = 350)                    (total = 10000)
```

Now Cell A and Cell B are comparable — both have the same "denominator."

**Why 10,000?** Convention. Any constant works. The point is every cell gets the same total.

### Step 2: Log Transform

```python
sc.pp.log1p(adata)  # log(x + 1)
```

**What it does**: `log(count + 1)` for every value.

**Why log?**
- Gene expression is wildly skewed — most genes at 0-5, a few at 1000+
- Log compresses high values and spreads low values:
  ```
  Before log:  0, 1, 10, 100, 1000, 10000
  After log:   0, 0.7, 2.3, 4.6, 6.9, 9.2
  ```
- Makes data more symmetric → better for PCA and statistical tests
- `+1` prevents log(0) which is undefined

### Step 3: Scale (for PCA only)

```python
sc.pp.scale(adata, max_value=10)
```

**What it does**: Z-score normalization — each gene gets mean=0, variance=1.

```
Before scaling:
  Gene A: [2.3, 2.5, 2.1, 2.4]  → mean=2.3, variance=small
  Gene B: [0.1, 8.5, 0.2, 7.9]  → mean=4.2, variance=HUGE

After scaling:
  Gene A: [-0.1, 0.8, -1.1, 0.4]  → mean=0, variance=1
  Gene B: [-1.1, 1.1, -1.0, 1.0]  → mean=0, variance=1
```

**Why scale?** Without scaling, PCA would be dominated by highly-expressed genes. Scaling gives every gene equal weight.

**max_value=10**: Caps extreme outliers. A gene at 50 standard deviations is probably an artifact.

---

## Feature Selection: Highly Variable Genes (HVGs)

### The Problem: 20,000 Genes Is Too Many

```
Total genes in mouse genome: ~22,000
Genes that vary between cell types: ~2,000-3,000
Housekeeping genes (same in all cells): ~15,000+

Using all 22,000 genes:
  - Slow computation
  - Noise drowns out signal
  - PCA dominated by irrelevant genes
```

### What Are HVGs?

**Highly Variable Genes** = genes whose expression varies a LOT across cells.

```
Gene Variability:

    Expression ↑
    Level      │
    8  │         ★                    ★ = Highly Variable
    6  │       ★   ★                  • = Low Variance
    4  │  •  ★       ★  •
    2  │  •  •    ★     •  •         HVGs are informative:
    0  │  •  •    •     •  •         they differ between cell types
       └──────────────────────
         Cell 1  2  3  4  5  6
         
    Krt14 (HVG): High in keratinocytes, zero in macrophages
    Actb (housekeeping): Similar in ALL cells → not informative
```

### How Scanpy Selects HVGs

```python
sc.pp.highly_variable_genes(
    adata, 
    min_mean=0.0125,  # Gene must have some expression
    max_mean=3,        # Not too highly expressed (housekeeping)
    min_disp=0.5       # Must be dispersed (variable)
)
```

**Result**: ~2,000-3,000 genes flagged as `highly_variable = True`

### Critical: Forcing Tissue Fluidity Genes

```python
# From our pipeline:
all_fluidity = set()
for genes in FLUIDITY_GENE_SETS.values():
    all_fluidity.update(genes)

for gene in all_fluidity:
    if gene in adata.var_names:
        adata.var.loc[gene, 'highly_variable'] = True
```

**Why force them?** Some fluidity genes might not pass the HVG filter (e.g., a gene that's moderately variable). But they're scientifically essential — we MUST include them for our research question.

**Interview point**: "I force-included tissue fluidity genes in the HVG set. Standard HVG selection might exclude them, but they're central to our research hypothesis. This is a scientifically-motivated override of a computational default."

---

## Storing Raw Counts

```python
# BEFORE normalizing:
adata.raw = adata.copy()
```

**Why?** After normalization, the original counts are gone. But:
- DE analysis sometimes needs raw counts
- Gene expression heatmaps use raw values
- `adata.raw` preserves the pre-normalization state

---

## Alternative: SCTransform (R/Seurat)

Our R pipeline uses SCTransform instead of the three-step process:

```r
wound_sobj <- SCTransform(wound_sobj, vars.to.regress = "percent.mt")
```

**What SCTransform does differently**:
- Uses regularized negative binomial regression
- Normalizes, selects HVGs, and scales in ONE step
- Accounts for sequencing depth more rigorously
- Generally regarded as superior to log-normalize for HVG selection

**Our config specifies both options**:
```yaml
normalization:
  method: "SCTransform"    # R pipeline
  # method: "LogNormalize"  # Alternative
  regress_vars: ["percent.mt"]
  n_variable_features: 3000
```

---

## Summary: The Normalization Pipeline

```
Raw Counts (adata.X)
    │
    ├── Save to adata.raw (preserve originals)
    │
    ├── sc.pp.normalize_total(target_sum=1e4)
    │   └── Every cell sums to 10,000
    │
    ├── sc.pp.log1p()
    │   └── Compress dynamic range, stabilize variance
    │
    ├── sc.pp.highly_variable_genes()
    │   ├── Select ~2000-3000 informative genes
    │   └── Force-include tissue fluidity genes
    │
    └── sc.pp.scale(max_value=10)  [for PCA only]
        └── Mean=0, variance=1 per gene
```

---

## Interview Q&A

### Q: "Why do you normalize scRNA-seq data?"

> "Raw counts are confounded by sequencing depth — a cell with 10,000 total UMIs will have higher counts for every gene compared to a cell with 2,000 UMIs, regardless of actual expression differences. Normalization removes this technical artifact by scaling all cells to the same total, then log-transforming to stabilize variance across the expression range."

### Q: "What are highly variable genes and why select them?"

> "HVGs are genes whose expression varies significantly across cells — these are the informative genes that distinguish cell types. About 2,000-3,000 out of 22,000 total genes are HVGs. Using only HVGs removes housekeeping gene noise and speeds computation. I also force-include our tissue fluidity signature genes regardless of their variability score, since they're essential for our research question."

### Q: "Why log-transform?"

> "Gene expression has extreme dynamic range — a few genes at 10,000 counts versus thousands at 0-10. Log compression makes the distribution more symmetric, which is required for PCA (assumes roughly Gaussian input) and improves statistical power for DE testing."

---

## Self-Check Questions

1. **Why can't you compare raw counts directly?** → Different cells have different sequencing depths
2. **What does normalize_total do?** → Scales every cell to the same total count (10,000)
3. **Why log(x+1) not log(x)?** → log(0) is undefined; +1 avoids this
4. **What does scaling achieve?** → Mean=0, variance=1 per gene; prevents high-expression genes from dominating PCA
5. **What are HVGs?** → Genes with high variability across cells — informative for clustering
6. **Why ~2000-3000 HVGs, not all 22,000?** → Noise reduction, speed, focus on informative variation
7. **Why force-include fluidity genes?** → Scientifically essential even if not statistically top-variable
8. **What does adata.raw store?** → Pre-normalization counts for downstream use (DE, heatmaps)
9. **How does SCTransform differ?** → Single-step regularized negative binomial; more rigorous
10. **What's the full normalization order?** → Save raw → normalize total → log1p → HVG → scale

---

**Next**: [Day 9 — Dimensionality Reduction: PCA & UMAP](Day_09_Dimensionality_Reduction.md)
