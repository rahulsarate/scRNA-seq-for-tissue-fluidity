# Day 11: Differential Expression Analysis

> **Goal**: Understand what DE is, why pseudobulk DESeq2 is the gold standard, and how to interpret results.

---

## What is Differential Expression?

```
Question: Which genes change between conditions?

    Control (healthy skin) vs Wound Day 7 (proliferative)
    
    Gene X:  Control = low    →  Wound 7d = HIGH    (UPREGULATED)
    Gene Y:  Control = high   →  Wound 7d = LOW     (DOWNREGULATED)
    Gene Z:  Control = medium →  Wound 7d = medium  (NOT CHANGED)
    
    DE analysis finds Gene X and Gene Y — the biologically interesting ones.
```

**Analogy**: Before-and-after blood test. Which values changed? Those that changed point to what's happening biologically.

---

## Two Approaches to DE in scRNA-seq

### Approach 1: Cell-Level (What Scanpy Does)

```python
# Wilcoxon test on every cell
sc.tl.rank_genes_groups(adata, 'condition', method='wilcoxon',
                        groups=['wound_7d'], reference='control')
```

**How it works**: Compare expression of each gene in ALL wound_7d cells vs ALL control cells.

**Problem**: Each cell is treated as an independent replicate — but cells from the same sample are NOT independent (they share the same mouse, same processing). This inflates p-values → too many false "significant" genes.

```
reality:                            what the test sees:
2 mice per condition                2000 cells per condition
↓                                   ↓
n = 2 (low statistical power)       n = 2000 (fake high power)
```

### Approach 2: Pseudobulk DESeq2 (Gold Standard — What We Use)

```
Step 1: Aggregate cells back to sample level
        wound_7d_rep1: average of 1000 cells → one "pseudobulk" sample
        wound_7d_rep2: average of 1000 cells → one "pseudobulk" sample
        
Step 2: Treat like bulk RNA-seq
        n = 2 replicates per condition (honest)
        
Step 3: Use DESeq2 (designed for this exact problem)
```

**Why pseudobulk is better**:
- Honest about sample size (n=2, not n=2000)
- Controls for within-sample correlation
- Community validated: recommended by Harvard Bioinformatics Core, Theis Lab, etc.
- Uses the negative binomial model (matches count data)

---

## DESeq2 — How It Works

### The Statistical Model

```
DESeq2 models each gene with:

    count ~ condition + replicate_variation

    1. Estimate size factors (normalize for library size)
    2. Estimate gene-wise dispersion (how noisy is this gene?)
    3. Fit negative binomial regression
    4. Test: is the "condition" coefficient significantly different from 0?
    5. Adjust p-values for multiple testing (FDR correction)
```

### Key Output Columns

| Column | Meaning | Example |
|--------|---------|---------|
| `gene` | Gene name | Mmp9 |
| `log2FC` | Log2 fold change | 2.5 (= 5.7× increase) |
| `padj` | Adjusted p-value (FDR) | 0.001 |
| `baseMean` | Average expression across all samples | 250 |

### Interpreting log2 Fold Change

```
log2FC = 0   → No change (1×)
log2FC = 1   → 2× increase
log2FC = 2   → 4× increase
log2FC = 3   → 8× increase
log2FC = -1  → 2× decrease (0.5×)
log2FC = -2  → 4× decrease (0.25×)
```

### Our Significance Thresholds

```yaml
# From configs/analysis_config.yaml:
differential_expression:
  significance:
    padj_threshold: 0.05     # FDR < 5%
    log2fc_threshold: 1.0    # At least 2-fold change
  shrinkage: "ashr"          # Reduces noisy fold changes
```

**Both conditions must be met**:
- padj < 0.05 → statistically significant
- |log2FC| > 1.0 → biologically meaningful (at least 2-fold change)

A gene with padj=0.001 but log2FC=0.1 is statistically significant but biologically irrelevant (only 7% change).

---

## Log2FC Shrinkage (ashr)

### The Problem

```
Gene with 2 reads in control, 10 reads in wound:
  log2FC = log2(10/2) = 2.3  (4.9× change!)

But is this real? With only 2 reads, the estimate is very noisy.
A gene with 200 reads vs 1000 reads:
  log2FC = log2(1000/200) = 2.3  (same fold change)

But this one is much more reliable (more data).
```

### What ashr Shrinkage Does

```
Low-count genes: noisy estimates → SHRINK toward 0
High-count genes: reliable estimates → barely changed

Before shrinkage:  Gene_rare: log2FC = 4.5  (noisy!)
After shrinkage:   Gene_rare: log2FC = 1.2  (more realistic)

Before shrinkage:  Mmp9: log2FC = 2.5  (reliable)
After shrinkage:   Mmp9: log2FC = 2.4  (barely changed)
```

**Result**: Fewer false positives, more trustworthy fold changes.

---

## Our DE Comparisons

### What We Compare

```
wound_3d  vs control  →  analysis/de/wound_3d_vs_control.csv
wound_7d  vs control  →  analysis/de/wound_7d_vs_control.csv
wound_14d vs control  →  analysis/de/wound_14d_vs_control.csv
```

**Always against control** — control is the "reference."

### Cell-Type-Specific DE (Advanced)

Not just "wound_7d vs control overall" but "wound_7d vs control **within fibroblasts**":

```
Overall DE:     What genes change in the whole tissue?
Cell-type DE:   What genes change specifically in fibroblasts?
                In macrophages? In keratinocytes?

The cell-type-specific view is far more powerful because:
  - A gene might go up in fibroblasts but DOWN in macrophages
  - The overall signal cancels out → you miss it
  - Cell-type resolution reveals the actual biology
```

---

## The DE Pipeline Code

### Cluster-Level DE (Quick, Exploratory)

```python
# Find marker genes for each cluster
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon', key_added='markers_leiden')
markers_df = sc.get.rank_genes_groups_df(adata, group=None, key='markers_leiden')
markers_df.to_csv('analysis/de/cluster_markers.csv', index=False)
```

### Condition-Level DE

```python
# For each wound timepoint vs control:
for condition in ['wound_3d', 'wound_7d', 'wound_14d']:
    mask = adata.obs['condition'].isin([condition, 'control'])
    adata_sub = adata[mask].copy()
    
    sc.tl.rank_genes_groups(adata_sub, 'condition', method='wilcoxon',
                            groups=[condition], reference='control')
    
    de_df = sc.get.rank_genes_groups_df(adata_sub, group=condition)
    de_df.to_csv(f'analysis/de/de_{condition}_vs_control.csv', index=False)
    
    n_sig = (de_df['pvals_adj'] < 0.05).sum()
    print(f"{condition} vs control: {n_sig} significant genes")
```

---

## Reading DE Results

### Example: wound_7d_vs_control.csv

```
gene      log2FC    padj        baseMean
Mmp9      3.2       1.2e-08     850        ← Strong up in wound
Col1a1    2.8       3.5e-07     1200       ← ECM remodeling
Vim       2.1       4.2e-06     950        ← EMT marker
Acta2     2.5       8.1e-06     600        ← Myofibroblast
Cdh1     -1.8       2.3e-05     400        ← E-cadherin DOWN (EMT!)
Krt10    -2.2       5.6e-05     300        ← Keratinocyte diff. DOWN
```

**What this tells us**: At wound day 7, ECM remodeling is active (Mmp9, Col1a1 up), EMT is happening (Vim up, Cdh1 down), myofibroblasts are appearing (Acta2 up). This is exactly what tissue fluidity predicts for the proliferative phase.

---

## Multiple Testing Correction

### Why Not Just Use p-values?

```
If you test 20,000 genes with threshold p < 0.05:
    20,000 × 0.05 = 1,000 false positives EXPECTED
    That's 1,000 genes that look significant but aren't!
```

### Benjamini-Hochberg FDR Correction

```
Raw p-values → Adjusted p-values (padj)

padj < 0.05 means: among ALL genes you call significant,
                    fewer than 5% are expected to be false positives

padj is ALWAYS larger than p-value (more conservative)
```

---

## Interview Q&A

### Q: "Why pseudobulk instead of cell-level DE?"

> "Cell-level DE treats each cell as an independent replicate, but cells from the same sample are correlated — they share the same mouse and processing. This leads to inflated p-values and thousands of false 'significant' genes. Pseudobulk aggregates cells back to the sample level (n=2 per condition), which is honest about the true sample size and controls for within-sample correlation. It's the approach recommended by the field's leading computational biology groups."

### Q: "What are your DE significance thresholds?"

> "I require both statistical significance (adjusted p-value < 0.05, Benjamini-Hochberg FDR) AND biological significance (absolute log2 fold change > 1.0, meaning at least 2-fold change). I also apply ashr shrinkage to reduce noisy fold change estimates in lowly-expressed genes."

### Q: "What were key DE findings in your wound healing data?"

> "At wound day 7 (proliferative phase), we see strong upregulation of ECM remodeling genes like Mmp9 and Col1a1, EMT indicators — Vim up and Cdh1 down — consistent with tissue fluidity. Myofibroblast markers like Acta2 peak at day 7. Inflammatory genes like Il6 and Tnf peak at day 3 and then decline. These patterns validate our tissue fluidity hypothesis."

---

## Self-Check Questions

1. **What is DE analysis?** → Finding genes that change significantly between conditions
2. **Why pseudobulk over cell-level?** → Cells within a sample aren't independent; pseudobulk respects true sample size
3. **What does log2FC = 2 mean?** → 4-fold increase
4. **What is padj?** → P-value corrected for multiple testing (Benjamini-Hochberg FDR)
5. **Why do we need BOTH padj and log2FC thresholds?** → Small but significant changes aren't biologically relevant
6. **What does ashr shrinkage do?** → Reduces noisy fold changes for lowly-expressed genes
7. **What comparisons do we make?** → wound_3d vs control, wound_7d vs control, wound_14d vs control
8. **Why cell-type-specific DE?** → A gene might go up in one cell type but down in another; overall DE misses this
9. **What's the multiple testing problem?** → Testing 20,000 genes at p<0.05 gives ~1,000 false positives
10. **Name 3 genes expected to be upregulated at wound_7d** → Mmp9 (ECM), Vim (EMT), Acta2 (myofibroblast)

---

**Next**: [Day 12 — Tissue Fluidity Scoring](Day_12_Fluidity_Scoring.md)
