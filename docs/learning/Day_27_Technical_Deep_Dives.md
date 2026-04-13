# Day 27: Interview Prep — Technical Deep Dives

> **Goal**: Prepare for deep-dive technical questions interviewers might ask about specific methods.

---

## Deep Dive 1: Quality Control

### Q: "Walk me through your QC strategy."

> "We filter at both gene and cell level. Cells must have 200–5,000 detected genes (removes empty droplets and potential doublets), at least 500 UMI counts, and less than 15% mitochondrial reads (high mt% indicates dying cells with cytoplasmic RNA leaked). For genes, we require expression in at least 3 cells. Doublets are detected computationally using Scrublet at an expected ~5% rate. All thresholds come from our analysis_config.yaml."

### Follow-up: "Why 15% mt, not 10% or 20%?"

> "It's tissue-dependent. Skin cells have moderate mitochondrial content. 10% is often too strict for wound tissue where cells are metabolically active. 20% risks keeping damaged cells. 15% is standard for mouse skin scRNA-seq based on published studies. We validate by checking QC violin plots — if we see a bimodal distribution, we adjust."

### Follow-up: "How do you detect doublets?"

> "Scrublet simulates synthetic doublets by randomly combining pairs of real cell transcriptomes, then scores each real cell based on similarity to simulated doublets. Cells with high doublet scores (>0.25 typically) are flagged. We expect ~5% doublet rate for 10X Chromium v3 at standard loading."

---

## Deep Dive 2: Normalization

### Q: "Why normalize_total + log1p instead of SCTransform?"

> "We use Scanpy's standard pipeline: normalize_total to 10,000 counts per cell (corrects for sequencing depth), then log1p to reduce skewness (highly expressed genes don't dominate). SCTransform is Seurat-specific and uses a regularized negative binomial model — mathematically elegant but computationally heavier. For our R pipeline, we do offer SCTransform as an alternative. The key is consistency: all samples normalized the same way."

### Follow-up: "What is CPM?"

> "Counts Per Million — normalize each cell to 1,000,000 total counts. We use a variant: normalize to 10,000 (target_sum=1e4) as recommended by Scanpy. After log1p, this becomes log-normalized counts, the standard input for PCA, HVG selection, and gene scoring."

---

## Deep Dive 3: Clustering

### Q: "How does Leiden clustering work?"

> "Leiden is a community detection algorithm on a cell-cell nearest-neighbor graph. Steps: (1) Compute PCA (30 components), (2) Build a k-nearest-neighbor graph (k=15), (3) Leiden optimizes a modularity function to partition the graph into communities where cells within a community are more connected to each other than to other communities. Resolution=0.8 controls granularity — higher means more clusters."

### Follow-up: "How did you choose resolution 0.8?"

> "We expect 10 cell types. Start at 0.8 (Scanpy default), check if clusters map cleanly to known markers. If clusters merge cell types, increase resolution. If they oversplit, decrease. We also check stability — does slight resolution change drastically alter results? Our 10 expected types (basal kerats, diff kerats, fibroblasts, myofibroblasts, macrophages, neutrophils, T cells, endothelial, HFSCs, melanocytes) typically resolve well at 0.8."

---

## Deep Dive 4: Differential Expression

### Q: "Explain pseudobulk DESeq2 step by step."

> "Step 1: For each sample × cell_type combination, sum raw counts across all cells — creating one pseudobulk sample. E.g., 500 fibroblasts from sample_1 → one column of summed counts. Step 2: Build a DESeq2 object with the design formula ~condition. Step 3: DESeq2 estimates size factors (sequencing depth correction), dispersion (per-gene variability), and fits a negative binomial GLM. Step 4: Wald test determines if the condition coefficient is significantly non-zero. Step 5: BH correction adjusts for multiple testing. Step 6: ashr shrinkage stabilizes log2FC for low-expression genes."

### Follow-up: "What's wrong with Wilcoxon for scRNA-seq?"

> "Wilcoxon treats each cell as an independent observation. But cells from the same sample share technical and biological variation — they're pseudoreplicates. With 500 fibroblasts per sample, Wilcoxon has enormous power from pseudoreplication, producing inflated p-values and many false positives. Pseudobulk with DESeq2 uses the 2 biological replicates per condition as the true sample size, giving proper type-1 error control."

---

## Deep Dive 5: Tissue Fluidity

### Q: "What exactly is your tissue fluidity score?"

> "We score 5 gene signature categories per cell using Scanpy's score_genes function. For each signature (e.g., EMT: Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2), we compute the mean expression of signature genes minus the mean expression of a random reference set of similar-expression genes. This gives a relative enrichment score. We then compare scores across conditions and cell types to map fluidity changes during wound healing."

### Follow-up: "What do you expect to find?"

> "We expect tissue fluidity to peak at wound_7d — the active repair phase. Fibroblasts should show high ECM remodeling scores (MMPs active, collagen deposition). Keratinocytes at wound edges should show high EMT scores (gaining migration capacity). By wound_14d, as the wound resolves, fluidity scores should decrease back toward control levels. This rise-peak-resolve pattern would support the hypothesis that transient fluidity enables repair."

---

## Deep Dive 6: The Dashboard

### Q: "Tell me about the dashboard architecture."

> "Backend: FastAPI (Python) with a DataLoader singleton that loads the h5ad file once at startup and serves data through REST endpoints — /umap, /genes, /de, /fluidity, /qc. It computes UMAP coordinates, gene expression, and fluidity scores on demand. Frontend: React with TypeScript, Tailwind CSS for styling, Plotly.js for interactive plots. Vite for build tooling. The frontend makes fetch calls to the API and renders UMAP scatter plots, volcano plots, cell proportion bar charts, and fluidity heatmaps."

### Follow-up: "Why FastAPI over Flask/Django?"

> "Three reasons: (1) async support — important for I/O-heavy data loading, (2) automatic API documentation via OpenAPI/Swagger, (3) type validation with Pydantic models. Flask would work but lacks native async. Django is overkill — we don't need ORM, sessions, or admin panel. FastAPI is exactly right for a data-serving API."

---

## Response Framework

For ANY technical question, use this structure:

```
1. WHAT: State the concept (1 sentence)
2. WHY: Why this method/tool (1-2 sentences)
3. HOW: Technical details (2-3 sentences)
4. RESULT: What you get/expect (1 sentence)
```

Example:
> **WHAT**: "Pseudobulk DESeq2 is our differential expression method."
> **WHY**: "We chose it because cell-level tests produce false positives from pseudoreplication."
> **HOW**: "It sums counts per sample, fits a negative binomial GLM, and uses BH correction with ashr shrinkage."
> **RESULT**: "This gives us reliable DE gene lists with proper statistical control."

---

## Self-Check Questions

1. **Explain QC filtering in 3 sentences** → Filter cells by genes (200-5000), UMI (>500), mt (<15%). Filter genes by min cells (3). Detect doublets with Scrublet.
2. **Why log1p after normalization?** → Reduces skewness; prevents highly expressed genes from dominating
3. **What does Leiden resolution control?** → Granularity of clustering — higher = more clusters
4. **What is pseudoreplication?** → Treating cells as independent when they're from the same biological sample
5. **Name the 5 fluidity gene categories** → EMT, ECM remodeling, cell migration, mechanotransduction, wound signals
6. **How does score_genes work?** → Mean(signature genes) - Mean(random reference genes)
7. **Why FastAPI over Flask?** → Async support, auto API docs, Pydantic validation
8. **What is ashr shrinkage?** → Stabilizes log2FC for low-expression genes
9. **What does a DataLoader singleton do?** → Loads data once at startup, serves all requests
10. **Use the WHAT-WHY-HOW-RESULT framework for Harmony** → WHAT: Batch effect correction. WHY: Technical variation obscures biology. HOW: Iteratively adjusts PCA embeddings per sample. RESULT: Cells cluster by biology, not batch.

---

**Next**: [Day 28 — Interview Prep: Design Decisions](Day_28_Design_Decisions.md)
