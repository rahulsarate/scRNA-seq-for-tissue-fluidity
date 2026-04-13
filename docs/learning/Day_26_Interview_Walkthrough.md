# Day 26: Interview Prep — Project Walkthrough

> **Goal**: Practice delivering a concise, confident 5-minute project overview.

---

## The Elevator Pitch (30 seconds)

> "I built a complete single-cell RNA sequencing analysis pipeline to study how tissue fluidity — the ability of cells to collectively migrate and remodel their environment — changes during skin wound healing in mice. The project covers the full stack: a Python/R computational pipeline from raw data to differential expression, tissue fluidity gene scoring, and an interactive React + FastAPI dashboard for exploring results."

---

## The Full Walkthrough (5 minutes)

### Part 1: The Biology (1 minute)

> "Wound healing happens in four phases: hemostasis, inflammation, proliferation, and remodeling. We study mouse skin wounds at four time points — control, 3 days, 7 days, and 14 days — capturing how 10 cell types coordinate repair.

> The central question is **tissue fluidity**: cells need to become more motile to close wounds, then return to a stable state. We track this through five gene signature categories — EMT, ECM remodeling, cell migration, mechanotransduction, and wound signals."

### Part 2: The Technology (1 minute)

> "Data comes from 10X Chromium single-cell sequencing — each cell gets a molecular barcode, captured in a droplet, RNA is sequenced. We expect ~8,000 cells across 8 samples.

> The primary pipeline uses Python with Scanpy for processing — QC filtering, normalization, PCA, UMAP, Leiden clustering. For differential expression, we use pseudobulk DESeq2 in R, which is the gold standard for scRNA-seq. Pathway enrichment uses clusterProfiler."

### Part 3: The Pipeline (1.5 minutes)

> "The pipeline runs in 8 steps:
> 1. Load data — AnnData objects from 10X output
> 2. QC — filter by gene count (200–5000), mitochondrial % (<15%)
> 3. Normalize — library size normalization + log transform
> 4. Dimensionality reduction — PCA (30 components), UMAP
> 5. Clustering — Leiden algorithm at resolution 0.8
> 6. Cell type annotation — marker gene scoring
> 7. Differential expression — pseudobulk DESeq2 per condition
> 8. Tissue fluidity scoring — score 5 gene signatures per cell

> Everything is config-driven — all parameters in one YAML file."

### Part 4: The Dashboard (30 seconds)

> "I also built an interactive dashboard — FastAPI backend serving scRNA-seq data through REST APIs, React + TypeScript frontend with UMAP exploration, gene search, volcano plots, and fluidity scoring panels. It lets you explore results without running code."

### Part 5: Engineering (1 minute)

> "As a solo developer, I designed this for reproducibility and maintainability:
> - Config-driven design — one YAML file for all parameters
> - Dual-language support — Python and R share the same config
> - 12 AI agents for task-specific assistance
> - CI/CD with GitHub Actions for automated linting
> - Git with proper .gitignore for data safety
> - All seeds set to 42 for reproducibility"

---

## Practice These Transitions

| From → To | Transition Phrase |
|----------|------------------|
| Biology → Tech | "To study this, we use..." |
| Tech → Pipeline | "The analysis flows through 8 steps..." |
| Pipeline → Dashboard | "Beyond the pipeline, I also built..." |
| Dashboard → Engineering | "What ties it all together is the engineering..." |

---

## Common Follow-Up Questions

After your walkthrough, expect these:

| Question | Where to Find Answer |
|----------|---------------------|
| "Why this biological question?" | Day 3 (Wound Healing Biology) |
| "Why single-cell over bulk?" | Day 2 (scRNAseq Technology) |
| "Walk me through QC" | Day 7 (Quality Control) |
| "Why pseudobulk over Wilcoxon?" | Day 11, Day 22 |
| "What is tissue fluidity exactly?" | Day 12 (Fluidity Scoring) |
| "How do you handle batch effects?" | Day 23 (Batch Effects) |
| "Why both Python AND R?" | Day 22 (R Integration) |
| "How is this reproducible?" | Day 16 (Reproducibility) |

---

## What to Emphasize vs Skip

### Emphasize (shows deep understanding)
- Trade-off decisions (pseudobulk vs cell-level DE, Harmony vs scVI)
- Config-driven design philosophy
- Why tissue fluidity is the unifying theme
- Full-stack capability (pipeline + dashboard)

### Skip (unless asked)
- Low-level library version numbers
- Exact code syntax
- Mathematical formulas
- Implementation details of Leiden/UMAP algorithms

---

## Interview Q&A

### Q: "Tell me about your project."

> Use the 5-minute walkthrough above. Adapt length to context — 30 seconds for elevator, 2 minutes for casual, 5 minutes for detailed.

### Q: "What was the hardest part?"

> "Designing the analysis to be both statistically rigorous and reproducible as a solo developer. The key challenge was choosing the right DE method — cell-level tests inflate significance for scRNA-seq, so I implemented pseudobulk DESeq2 which is the benchmarked gold standard. Config-driven design was essential to keep 8 scripts consistent."

### Q: "What would you do differently?"

> "I'd add automated integration testing — currently CI checks linting but not analysis outputs. I'd also implement Nextflow/Snakemake for pipeline orchestration instead of sequential scripts, and add a metadata schema validator for sample sheets."

---

## Self-Check Questions

1. **Can you deliver the 30-second pitch?** → Practice out loud
2. **Can you name the 4 wound healing phases?** → Hemostasis, inflammation, proliferation, remodeling
3. **Can you list the 8 pipeline steps?** → Load, QC, normalize, dim reduction, cluster, annotate, DE, fluidity
4. **Can you explain why pseudobulk?** → Cells aren't independent; pseudobulk gives proper statistics
5. **What 5 fluidity signature categories?** → EMT, ECM remodeling, cell migration, mechanotrans, wound signals
6. **What's the dashboard stack?** → FastAPI + React + TypeScript + Tailwind + Plotly
7. **How many cell types?** → 10 expected
8. **How many samples?** → 8 (4 conditions × 2 replicates)
9. **Can you explain config-driven design in 1 sentence?** → All parameters in one YAML file, loaded by every script
10. **What's the project's central question?** → How does tissue fluidity change during wound healing?

---

**Next**: [Day 27 — Interview Prep: Technical Deep Dives](Day_27_Technical_Deep_Dives.md)
