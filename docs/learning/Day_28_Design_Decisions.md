# Day 28: Interview Prep — Design Decisions & Trade-offs

> **Goal**: Articulate WHY you made specific design choices — interviewers love trade-off discussions.

---

## Decision 1: Python + R (Not Just One)

### The Trade-off
```
Option A: Python only (Scanpy)
  + Simpler stack, one language
  - DE stats less mature (Wilcoxon, not pseudobulk DESeq2)
  - Fewer enrichment tools

Option B: R only (Seurat)
  + Gold-standard stats
  - Slower on large datasets
  - No web framework for dashboard

Option C: Both (our choice)
  + Best tool for each job
  - Two environments to maintain
  - Cross-language data exchange
```

### How to Answer
> "I use Python for the primary pipeline and dashboard because Scanpy scales well and FastAPI enables the interactive frontend. R handles differential expression (DESeq2 is the gold standard for pseudobulk) and pathway enrichment (clusterProfiler). Both languages read the same analysis_config.yaml, ensuring parameter consistency. The trade-off is maintaining two environments, but the statistical rigor is worth it."

---

## Decision 2: Pseudobulk DESeq2 (Not Wilcoxon)

### The Trade-off
```
Wilcoxon (simpler):
  + Built into Scanpy/Seurat
  + Fast, one-line call
  - Treats cells as independent (pseudoreplication)
  - Inflated p-values, high false positive rate

DESeq2 pseudobulk (our choice):
  + Proper statistical model
  + Benchmarked best performer
  + ashr shrinkage for reliable fold changes
  - Requires R
  - More complex pipeline
  - Needs ≥2 replicates per condition
```

### How to Answer
> "We chose pseudobulk DESeq2 because benchmarking studies show Wilcoxon inflates significance by treating cells as independent. With 500 cells per sample, Wilcoxon has false-positive rates exceeding 50%. DESeq2 uses sample-level replicates (n=2 per condition), giving proper type-1 error control. The trade-off is complexity — we need R and at least 2 replicates — but statistical validity outweighs convenience."

---

## Decision 3: Config-Driven (Not Hardcoded)

### The Trade-off
```
Hardcoded parameters:
  + Faster to write
  + Self-contained scripts
  - Parameters scattered across files
  - Easy to get inconsistent
  - Hard to reproduce

Config-driven (our choice):
  + Single source of truth
  + Easy to change parameters
  + Version-controlled parameter history
  - Extra file to manage
  - Scripts depend on config path
```

### How to Answer
> "All parameters live in configs/analysis_config.yaml. When I change the mt% threshold from 15 to 20, I edit one line and every script picks it up. Without this, I'd need to hunt through scripts and risk inconsistency. It's a small upfront cost for huge reproducibility gains."

---

## Decision 4: Harmony (Not scVI or BBKNN)

### The Trade-off
```
Harmony (our choice):
  + Fast, memory-efficient
  + Corrects PCA embeddings only (clean separation)
  + Good for 8-sample datasets
  - May under-correct complex batches

scVI (alternative):
  + Best correction quality
  + Deep learning model
  - Slow, GPU-hungry
  - Overkill for 8 samples
  - Corrects counts (harder to interpret)

BBKNN (alternative):
  + Very simple
  + No new embeddings
  - Can distort distances
  - Less flexible
```

### How to Answer
> "Harmony operates on PCA embeddings, preserving raw counts for DE analysis. It's fast, memory-efficient, and well-suited for our 8-sample design. scVI would be better for larger, more complex batches, but it's computationally expensive and modifies count representations. BBKNN is too simple for condition-aware integration. Harmony provides the right balance."

---

## Decision 5: Interactive Dashboard (Not Just Static Plots)

### The Trade-off
```
Static plots only:
  + Simpler to build
  + PDF/PNG for papers
  - Can't explore interactively
  - Collaborators need code to filter

Interactive dashboard (our choice):
  + Explore UMAP, filter genes, view fluidity live
  + Non-coders can explore
  + Real-time parameter adjustment
  - Full-stack development effort
  - Server must be running
  - Additional dependencies
```

### How to Answer
> "Static plots cover publication needs, but the dashboard lets collaborators explore data without writing code. A PI can search for their gene of interest, see it on UMAP, check its DE significance, and view fluidity scores — all in a browser. The engineering investment is significant (FastAPI + React + TypeScript), but it dramatically accelerates collaborative analysis."

---

## Decision 6: 12 AI Agents (Not One General Agent)

### The Trade-off
```
One general agent:
  + Simple to configure
  - Gets confused switching contexts
  - All knowledge loaded at once

12 specialized agents (our choice):
  + Right expert for each task
  + Domain-specific skills loaded on demand
  + Clear handoff pipeline
  - More configuration files
  - Need orchestrator for routing
```

### How to Answer
> "Specialization reduces errors. The qc-analyst knows QC thresholds and doublet detection; the de-analyst knows pseudobulk DESeq2 and shrinkage; the visualization-specialist knows publication figure standards. Each agent loads only relevant skills, reducing noise. The orchestrator coordinates handoffs. It mirrors how real research teams work — specialists collaborating, not one generalist doing everything."

---

## The Meta-Skill: Answering Trade-off Questions

### Framework

```
1. State what you chose
2. Name 1-2 alternatives you considered
3. Give 2-3 reasons for your choice
4. Acknowledge the trade-off
5. Say when you'd choose differently
```

### Example Applied

> "We chose [Harmony] over [scVI and BBKNN] because [it's fast, operates on embeddings not counts, and suits our 8-sample scale]. The trade-off is [it may under-correct complex batches]. For a [50-sample multi-site study], I'd switch to [scVI]."

---

## Self-Check Questions

1. **Why Python + R together?** → Python for pipeline + dashboard speed; R for gold-standard stats (DESeq2, clusterProfiler)
2. **When would you use Wilcoxon over DESeq2?** → Quick exploration, no replicates available, or large-scale screening
3. **What's the main risk of hardcoded parameters?** → Inconsistency across scripts; forgotten updates
4. **When would you choose scVI over Harmony?** → Large multi-site studies with complex batch structures
5. **Why build a dashboard for a research project?** → Lets non-coding collaborators explore data interactively
6. **Why 12 agents instead of 1?** → Specialization reduces errors; right context loaded per task
7. **What's the trade-off of config-driven design?** → Extra file dependency; scripts crash if config missing
8. **When would you skip the dashboard?** → Short-term analysis, no collaborators, publication-only output
9. **What makes pseudobulk "gold standard"?** → Benchmarking papers show best type-1 error control
10. **Apply the trade-off framework to Leiden vs Louvain** → Leiden: guaranteed connected communities, slightly slower. Louvain: faster but can produce disconnected clusters. Choose Leiden for reliability.

---

**Next**: [Day 29 — Interview Prep: Common Questions & Red Flags](Day_29_Common_Questions.md)
