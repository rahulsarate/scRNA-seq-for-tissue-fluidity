# Day 29: Interview Prep — Common Questions & Red Flags

> **Goal**: Prepare for frequently asked questions and learn what NOT to say.

---

## Top 20 Interview Questions

### Biology Questions

**1. "What is single-cell RNA sequencing?"**
> "A technology that measures gene expression in individual cells. Unlike bulk RNA-seq, which averages thousands of cells, scRNA-seq reveals cellular heterogeneity — different cell types, states, and responses within the same tissue."

**2. "Why single-cell instead of bulk?"**
> "Wound healing involves 10+ cell types with different roles. Bulk RNA-seq would average a fibroblast's activation signal with a macrophage's inflammatory signal — making both undetectable. Single-cell lets us see each cell type's response independently."

**3. "What is tissue fluidity?"**
> "The ability of cells to collectively migrate and remodel their extracellular matrix. During wound healing, tissue transiently becomes more 'fluid' — cells loosen junctions (EMT), degrade matrix (MMPs), and migrate to close the wound. We quantify this through 5 gene signature categories."

**4. "What are your 10 cell types?"**
> "Basal keratinocytes, differentiated keratinocytes, fibroblasts, myofibroblasts, macrophages, neutrophils, T cells, endothelial cells, hair follicle stem cells, and melanocytes."

**5. "How do you annotate cell types?"**
> "Marker gene scoring. Each cell type has known markers — Krt14 for basal keratinocytes, Col1a1 for fibroblasts, Cd68 for macrophages. We score cells against these marker sets and assign the highest-scoring type. We also validate by checking cluster-specific gene expression patterns."

---

### Technical Questions

**6. "Walk me through your pipeline."**
> "8 steps: load data → QC filter (200-5000 genes, <15% mt) → normalize (library size + log) → PCA + UMAP → Leiden clustering (res=0.8) → cell type annotation → pseudobulk DESeq2 → tissue fluidity scoring."

**7. "What's your data format?"**
> "AnnData (.h5ad) — a container with the expression matrix (X, sparse), cell metadata (obs), gene metadata (var), embeddings (obsm), and unstructured data (uns). It's the standard for Scanpy/Python scRNA-seq."

**8. "How many cells, how many genes?"**
> "We expect ~8,000 cells across 8 samples (4 conditions × 2 replicates) and ~2,000 variable genes after filtering from ~20,000 total genes. 10X Chromium v3 on NovaSeq 6000."

**9. "What is the Leiden algorithm?"**
> "A community detection algorithm on the cell-cell nearest-neighbor graph. It partitions cells into clusters by optimizing modularity — cells within a cluster are more connected to each other than to other clusters. Resolution parameter controls granularity."

**10. "What is UMAP?"**
> "Uniform Manifold Approximation and Projection — a dimensionality reduction method that reduces 30-dimensional PCA space to 2D for visualization. It preserves local structure (nearby cells stay nearby) better than t-SNE and is faster. Important caveat: distances between distant clusters aren't meaningful."

---

### Engineering Questions

**11. "How is this reproducible?"**
> "Four pillars: (1) all seeds set to 42, (2) package versions logged at every run, (3) all parameters in analysis_config.yaml with git history, (4) conda/pip environment files pin exact versions."

**12. "Describe your project architecture."**
> "Separation of concerns: scripts/ for code, configs/ for parameters, data/ for inputs/outputs, analysis/ for results, dashboard/ for the web app, docs/ for documentation. Config-driven design — no hardcoded parameters. Dual-language (Python + R) sharing one config file."

**13. "How do you handle data security?"**
> "data/raw/ is read-only, .gitignore excludes files >50MB, no PHI or patient IDs ever in code, credentials never committed, raw FASTQ never modified."

**14. "What's your dashboard stack?"**
> "FastAPI backend (Python) serving REST endpoints for UMAP, gene expression, DE results, and fluidity scores. React frontend (TypeScript) with Tailwind CSS and Plotly.js for interactive plots. Vite for development/build tooling."

**15. "How do your AI agents work?"**
> "12 specialized agents configured in .agent.md files with YAML frontmatter. Each has specific tools and skills. An orchestrator routes tasks. Skills (SKILL.md) provide domain knowledge loaded on demand. Instructions (.instructions.md) enforce coding standards by file type."

---

### Analytical Questions

**16. "What results do you expect?"**
> "Tissue fluidity peaks at wound_7d — EMT and ECM remodeling scores highest in fibroblasts and keratinocytes. Inflammatory signals (Il6, Tnf) peak at wound_3d. Resolution markers appear at wound_14d. Myofibroblasts are most abundant at wound_7d."

**17. "What if you find no fluidity change?"**
> "That's still a valid result — it would challenge the tissue fluidity hypothesis. I'd verify by checking individual genes (are known markers like Vim, Mmp2, Fn1 unchanged?), confirm technical quality (did QC/normalization work?), and compare with published datasets."

**18. "What are the limitations?"**
> "2 replicates per condition limits statistical power. 10X captures only poly-A RNA, missing non-coding RNAs. scRNA-seq doesn't measure spatial information (where cells are in the tissue) or protein levels. Pseudotime is inferred, not measured."

**19. "What would you add next?"**
> "Spatial transcriptomics (Visium/MERFISH) to map fluidity changes to wound location. More replicates for statistical power. Integration with publicly available wound healing datasets for validation. Automated pipeline orchestration with Snakemake."

**20. "How do you validate your results?"**
> "Cross-reference with published single-cell wound healing studies (GSE234269, GSE159827). Check marker gene expression matches known biology. Compare DESeq2 results with alternative methods (MAST, Wilcoxon). Validate key findings in the independent aged wound healing dataset (GSE188432)."

---

## Red Flags: What NOT to Say

| Red Flag | Why It's Bad | Say Instead |
|----------|-------------|-------------|
| "I just followed a tutorial" | Shows no understanding | "I designed the pipeline based on benchmarking studies" |
| "I don't know why we use that" | Can't justify decisions | "We chose X because..." (use trade-off framework) |
| "It works on my machine" | No reproducibility | "We use pinned environments and config files" |
| "I tested it visually" | No statistical rigor | "We use statistical thresholds: padj<0.05, \|log2FC\|>1" |
| "The AI wrote it" | Devalues your knowledge | "I architected the system including AI agent configuration" |
| "We use all default parameters" | No optimization | "We tuned resolution at 0.8 to match our 10 expected cell types" |
| "I didn't check for batch effects" | Major oversight | "We run Harmony integration on sample-level batches" |
| "p < 0.05 means it's true" | Misunderstanding stats | "padj < 0.05 controls false discovery rate at 5%" |

---

## Body Language & Delivery Tips

- **Own the project**: Say "I designed" and "I chose" — not "we did" or "it was done"
- **Pause before answering**: Shows you're thinking, not reciting
- **Draw diagrams**: Sketch the pipeline on a whiteboard if available
- **Admit unknowns gracefully**: "That's a great question — I haven't evaluated that yet, but my approach would be..."
- **Connect to biology**: Always tie technical answers back to the wound healing question

---

## Self-Check Questions

1. **Can you answer all 20 questions above without looking?** → Practice until you can
2. **Can you explain scRNA-seq to a non-biologist?** → Measuring gene activity in individual cells
3. **What's one limitation you'd mention proactively?** → 2 replicates per condition limits statistical power
4. **Why say "I" not "we" in an interview?** → You're presenting as a solo developer
5. **What's the biggest red flag?** → "I don't know why we use that" — always justify decisions
6. **How to handle a question you don't know?** → "I haven't evaluated that yet, but my approach would be..."
7. **Name 3 datasets in the project** → GSE234269 (primary), GSE159827 (mechanics), GSE188432 (aged)
8. **What's the "neutral result" answer?** → No fluidity change is still valid science
9. **What would you add next?** → Spatial transcriptomics, more replicates, Snakemake automation
10. **Can you draw the pipeline from memory?** → load → QC → normalize → PCA/UMAP → cluster → annotate → DE → fluidity

---

**Next**: [Day 30 — Final Review & Mock Discussion](Day_30_Final_Review.md)
