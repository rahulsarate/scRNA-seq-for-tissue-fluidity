# Day 7: Quality Control — The First Critical Step

> **Goal**: Master QC filtering logic, understand every metric, and explain decisions. QC is the #1 interview topic for bioinformatics.

---

## Why QC is the Most Important Step

```
    Garbage In  →  Garbage Out
    
    If you include dead cells, doublets, or empty droplets
    in your analysis, EVERY downstream result is wrong:
    - Wrong clusters
    - Wrong cell types
    - Wrong DE genes
    - Wrong biological conclusions
```

QC is where you prove you understand the data. In interviews, QC questions are the first filter.

---

## The Three QC Metrics — Explained

### 1. Number of Genes per Cell (`n_genes_by_counts`)

```
           Cell Quality by Gene Count
    
    ◄── empty/dead ──┤  ◄── normal ──┤  ◄── doublet ──►
    
    0    100   200         2000          5000   8000
    │▓▓▓▓│▓▓▓▓│░░░░░░░░░░░│████████████│░░░░░░│▓▓▓▓│
         ▲                                    ▲
     min_genes=200                      max_genes=5000
```

**Too few genes (< 200)**: 
- Empty droplet with ambient RNA floating around
- Dead/dying cell that has degraded
- These are NOT real cells — they're noise

**Too many genes (> 5000)**:
- Likely a "doublet" — two cells captured in one droplet
- One cell expresses ~2000-3000 genes; a doublet would express 4000-6000
- Including doublets creates fake "hybrid" cell types

**Our threshold**: 200 ≤ n_genes ≤ 5000

### 2. Total UMI Counts (`total_counts`)

```
    Counts = total number of RNA molecules captured
    
    Low counts → poor capture (bad cell)
    Very high counts → probably doublet
    
    Our threshold: minimum 500 counts
```

**Why 500?** Below 500 UMIs, there isn't enough information to reliably determine cell type or gene expression patterns. It's like trying to understand a conversation when you can only hear 1% of the words.

### 3. Mitochondrial Gene Percentage (`pct_counts_mt`)

```
       Healthy Cell              Dying Cell
    ┌─────────────────┐     ┌─────────────────┐
    │  nucleus         │     │  nucleus         │
    │  ┌──────────┐   │     │  ┌──────────┐   │
    │  │ mRNA:95% │   │     │  │ mRNA:80% │   │
    │  └──────────┘   │     │  └──────────┘   │
    │  [mt: 5%]       │     │                 ╱│  ← membrane
    │  ○○             │     │  [mt: 20%+] ○○╱ │    breaking
    └─────────────────┘     │             ╱   │
                            └────────────╱────┘
                            
    Nuclear mRNA leaks OUT     Mitochondrial RNA
    through broken membrane    becomes higher PROPORTION
```

**Why high mt% = bad?**
- When a cell is dying, its membrane breaks down
- Cytoplasmic mRNA leaks OUT of the cell
- Mitochondrial mRNA (inside mitochondria) is protected longer
- Result: dying cells have a higher PROPORTION of mt genes
- Mouse mt genes: start with `mt-` (e.g., `mt-Co1`, `mt-Atp6`)

**Our threshold: max 15% mt**
- Standard is 10-20%
- We chose 15% because skin keratinocytes are metabolically active (naturally higher mt%)
- This is a BIOLOGICAL decision, not arbitrary — documented in our config

---

## QC Code Walk-Through

From `01_scrna_analysis_pipeline.py`:

```python
def qc_filter(adata):
    """Quality control and cell filtering."""
    
    # Step 1: Identify mitochondrial genes
    adata.var['mt'] = adata.var_names.str.startswith('mt-')
    
    # Step 2: Calculate QC metrics for each cell
    sc.pp.calculate_qc_metrics(
        adata, 
        qc_vars=['mt'],      # Calculate mt% for each cell
        percent_top=None, 
        log1p=False, 
        inplace=True          # Add results to adata.obs
    )
    # After this, every cell has:
    #   adata.obs['n_genes_by_counts'] — number of detected genes
    #   adata.obs['total_counts'] — total UMI count
    #   adata.obs['pct_counts_mt'] — % mitochondrial
    
    # Step 3: Generate QC violin plots (BEFORE filtering)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    sc.pl.violin(adata, 'n_genes_by_counts', groupby='condition', ax=axes[0])
    sc.pl.violin(adata, 'total_counts', groupby='condition', ax=axes[1])
    sc.pl.violin(adata, 'pct_counts_mt', groupby='condition', ax=axes[2])
    plt.savefig('analysis/figures/01_qc_violins.png')
    
    # Step 4: Apply filters
    n_before = adata.shape[0]
    sc.pp.filter_cells(adata, min_genes=200)    # Remove empty droplets
    sc.pp.filter_genes(adata, min_cells=3)       # Remove ultra-rare genes
    adata = adata[adata.obs.pct_counts_mt < 15]  # Remove dying cells
    
    print(f"Before: {n_before} cells → After: {adata.shape[0]} cells")
    
    return adata
```

### Why Filter GENES Too? (`min_cells=3`)

A gene detected in only 1-2 cells out of 8,000 is:
- Probably noise (sequencing error or ambient RNA)
- Not informative for clustering or DE
- Removing it reduces computation without losing biology

---

## Doublet Detection

### What is a Doublet?

```
    Normal capture:              Doublet:
    
    ┌─────────────────┐         ┌─────────────────┐
    │  ○  one cell     │         │  ○○  TWO cells   │
    │     one bead     │         │     one bead     │
    │     one barcode  │         │     one barcode  │
    └─────────────────┘         └─────────────────┘
    
    Result: accurate profile      Result: MIXED profile
                                  Looks like a "hybrid" cell type
                                  e.g., half fibroblast + half macrophage
```

**Expected doublet rate**: ~5% for 10X Chromium (~1 in 20 droplets has two cells)

### Why Doublets Are Dangerous

A fibroblast + macrophage doublet would:
- Express BOTH fibroblast markers (Col1a1) AND macrophage markers (Cd68)
- Create a fake cluster that doesn't exist in biology
- Lead to false biological conclusions

### Detection Methods

| Tool | Approach | Our Project |
|------|----------|-------------|
| Scrublet | Simulates artificial doublets, compares | Python |
| DoubletFinder | Similar simulation approach | R/Seurat |
| max_genes filter | >5000 genes = likely doublet | Both |

---

## QC Report — What Good Results Look Like

```
QC Summary:
    Total cells before QC:    8,000
    Cells removed (low genes):  120  (1.5%)
    Cells removed (high mt):    250  (3.1%)
    Cells removed (doublets):   380  (4.8%)
    Total cells after QC:     7,250  (90.6% retained)
    
    ✓ Acceptable: 85-95% retention is normal
    ✗ Red flags:
        - >20% removed → too stringent, or tissue quality issue
        - <5% removed → thresholds too lenient, noise retained
```

### QC Metrics by Condition (from our qc_summary.csv)

| Condition | Cells Pre-QC | Cells Post-QC | Median Genes | Median Counts | Mean MT% |
|-----------|-------------|---------------|--------------|---------------|----------|
| control | 2,000 | 1,850 | 2,200 | 5,500 | 4.2% |
| wound_3d | 2,000 | 1,780 | 1,800 | 4,200 | 6.8% |
| wound_7d | 2,000 | 1,810 | 2,100 | 5,100 | 5.5% |
| wound_14d | 2,000 | 1,810 | 2,150 | 5,300 | 4.8% |

**Note**: wound_3d has higher MT% and lower gene counts — expected because inflammatory environment has more dying cells.

---

## The QC Violin Plot — How to Read It

```
    Genes per Cell           Counts per Cell         % Mitochondrial
    
    |                        |                        |
    |    ┌───┐               |    ┌───┐               |
    │ ┌──│   │──┐    ← max   │ ┌──│   │──┐            │          
    │ │  │   │  │            │ │  │   │  │            │  ┌─┐
    │ │  │   │  │   ← IQR    │ │  │   │  │            │  │ │
    │ └──│   │──┘            │ └──│   │──┘            │  │ │
    │    └───┘      ← median │    └───┘               │  │ │
    │                ← min   │                        │  └─┘
    └────────────            └────────────            └────────────
     ctrl w3d w7d w14d        ctrl w3d w7d w14d       ctrl w3d w7d w14d
```

**What to look for**:
- Consistent distributions across conditions → good batch quality
- Outlier-heavy samples → investigate potential technical issues
- Condition-specific differences → biological, not technical (e.g., wound_3d higher mt%)

---

## Making QC Decisions — The Thought Process

### 1. Start with Standard Thresholds

Use community defaults as starting points:
- min_genes: 200
- max_genes: 5000
- max_mt: 10-20%

### 2. Adjust Based on YOUR Data

Look at the distributions:
- If 30% of cells have >15% mt → maybe your threshold is too strict, try 20%
- If you see a clear bimodal distribution in n_genes → the upper peak might be doublets
- If one condition loses most cells → investigate, don't just accept

### 3. Document Your Reasoning

In our `configs/analysis_config.yaml`:
```yaml
qc_thresholds:
  max_percent_mt: 15  # Higher threshold for skin (keratinocytes high mt)
```

The comment explains WHY 15% not 10%.

### 4. Compare Pre vs Post QC

Always report what was removed and why. Reviewers WILL ask.

---

## Advanced: Ambient RNA

### What is Ambient RNA?

```
After tissue dissociation, some cells break open:

    Broken cells → mRNA floats freely in the solution
    
    When a REAL cell is captured, some ambient RNA
    gets captured WITH it:
    
    ┌────────────────┐
    │  Real cell mRNA │  ← 95% correct signal
    │  + ambient mRNA │  ← 5% contamination from other cells
    └────────────────┘
```

**Impact**: A fibroblast might show low-level expression of macrophage genes (not real, just contamination)

**Tools**: SoupX, CellBender — remove ambient RNA computationally

---

## Interview Q&A

### Q: "Walk me through your QC approach."

> "I apply three filters: minimum 200 genes per cell to remove empty droplets, maximum 5000 genes to flag potential doublets, and maximum 15% mitochondrial content to remove dying cells. I chose 15% mt because skin keratinocytes are metabolically active — a standard 10% would remove healthy cells. I always visualize QC distributions before and after filtering, split by condition, and document the retention rate. For our dataset, we retain about 90% of cells."

### Q: "How do you handle doublets?"

> "Two approaches: First, our max_genes filter catches most doublets since they express roughly double the normal gene count. Second, tools like Scrublet simulate artificial doublets and score each real cell's similarity to these simulations. We expect about 5% doublet rate with 10X Chromium. Removing doublets is critical because they create fake hybrid cell populations that don't exist biologically."

### Q: "Why 15% and not 10% for mitochondrial percentage?"

> "This is tissue-specific. Skin keratinocytes are metabolically active cells with naturally higher mitochondrial content. Using 10% would filter out healthy keratinocytes and bias our cell type proportions. I validated this by examining the mt% distribution — there's a clear unimodal distribution peaking around 5-8%, with a tail extending to ~12%. The 15% threshold sits above this healthy distribution while still catching genuinely apoptotic cells above 15%."

---

## Self-Check Questions

1. **What are the three QC metrics?** → n_genes, total_counts, pct_counts_mt
2. **Why does high mt% indicate a dying cell?** → Cytoplasmic mRNA leaks out, mt-RNA stays, proportion rises
3. **What is a doublet?** → Two cells captured in one droplet, creating a hybrid profile
4. **Why 15% mt instead of 10%?** → Skin keratinocytes are metabolically active with naturally higher mt%
5. **What does `min_cells=3` do for genes?** → Removes genes detected in <3 cells (likely noise)
6. **What's a normal QC retention rate?** → 85-95%
7. **What is ambient RNA?** → Free-floating mRNA from broken cells that contaminates real cells
8. **Why plot QC distributions BEFORE filtering?** → To see the full picture and choose appropriate thresholds
9. **What would happen if you skip QC?** → Wrong clusters, fake cell types, false DE results
10. **Expected doublet rate for 10X?** → ~5%

---

**Next**: [Day 8 — Normalization & Feature Selection](Day_08_Normalization.md)
