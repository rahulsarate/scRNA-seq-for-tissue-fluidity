# Day 30: Final Review & Mock Discussion

> **Goal**: Consolidate everything. Run a mock interview. Walk away confident.

---

## 30-Day Knowledge Map

```
Week 1: Foundation
  Day 01: Project Overview          ← The big picture
  Day 02: scRNAseq Technology       ← How cells become data
  Day 03: Wound Healing Biology     ← The biology we study
  Day 04: Project Architecture      ← Directory structure & design
  Day 05: Technology Stack          ← Tools we use

Week 2: The Pipeline
  Day 06: Data Journey              ← From GEO to AnnData
  Day 07: Quality Control           ← Filtering bad cells
  Day 08: Normalization             ← Making data comparable
  Day 09: Dimensionality Reduction  ← PCA + UMAP
  Day 10: Clustering                ← Finding cell types

Week 3: Analysis
  Day 11: Differential Expression   ← Finding changing genes
  Day 12: Tissue Fluidity Scoring   ← Our central metric
  Day 13: Pathway Enrichment        ← Biological meaning
  Day 14: Visualization             ← Communicating results
  Day 15: Interactive Dashboard     ← Exploring data live
  Day 16: Reproducibility           ← Making it trustworthy

Week 4: Engineering & Advanced
  Day 17: Git Workflow              ← Version control
  Day 18: AI Agent Architecture     ← 12 specialized agents
  Day 19: CI/CD                     ← Automated quality checks
  Day 20: Config-Driven Design      ← One YAML to rule them all
  Day 21: Python Best Practices     ← Coding conventions
  Day 22: R Integration & DESeq2    ← Statistical rigor
  Day 23: Batch Effects             ← Harmony integration
  Day 24: Trajectory Analysis       ← Pseudotime & RNA velocity
  Day 25: Cell Communication        ← CellChat & signaling

Week 5: Interview Preparation
  Day 26: Project Walkthrough       ← The 5-minute pitch
  Day 27: Technical Deep Dives      ← Method-level answers
  Day 28: Design Decisions          ← Trade-off reasoning
  Day 29: Common Questions          ← Top 20 Q&A
  Day 30: Final Review (this file)  ← Consolidation & mock
```

---

## Quick Reference Card

### Project Identity
- **Title**: Dynamic regulation of tissue fluidity controls skin repair
- **PI**: Rahul M Sarate
- **Organism**: Mus musculus (C57BL/6J), GRCm39 (mm39)
- **GitHub**: rahulsarate/scRNA-seq-for-tissue-fluidity

### Numbers to Remember
| What | Value |
|------|-------|
| Conditions | 4 (control, wound_3d, wound_7d, wound_14d) |
| Replicates/condition | 2 |
| Total samples | 8 |
| Platform | 10X Chromium v3, NovaSeq 6000 |
| Expected cells | ~8,000 |
| Expected cell types | 10 |
| Fluidity signatures | 5 categories |
| AI agents | 12 |
| Pipeline steps | 8 |
| Random seed | 42 |

### QC Thresholds
| Parameter | Value |
|-----------|-------|
| min_genes | 200 |
| max_genes | 5,000 |
| min_counts | 500 |
| max_percent_mt | 15% |
| min_cells_per_gene | 3 |

### Key Methods
| Step | Method | Justification |
|------|--------|---------------|
| Normalization | normalize_total + log1p | Standard, library-size correction |
| Integration | Harmony | Fast, embedding-only correction |
| Clustering | Leiden (res=0.8) | Connected communities, resolution for 10 types |
| DE | Pseudobulk DESeq2 + ashr | Gold standard, proper stats |
| Enrichment | clusterProfiler (GO/KEGG) | Comprehensive, well-maintained |
| Fluidity | sc.tl.score_genes | Per-cell signature scoring |

### 5 Fluidity Signatures
1. **EMT**: Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2
2. **ECM remodeling**: Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2
3. **Cell migration**: Rac1, Cdc42, Itgb1, Rhoa, Rock1, Rock2
4. **Mechanotransduction**: Yap1, Wwtr1, Piezo1, Trpv4, Lats1, Lats2
5. **Wound signals**: Tgfb1, Tgfb2, Tgfb3, Pdgfa, Vegfa, Wnt5a, Il6, Tnf

### 10 Cell Types & Markers
| Cell Type | Key Markers |
|-----------|------------|
| Basal Keratinocyte | Krt14, Krt5, Itga6 |
| Diff Keratinocyte | Krt1, Krt10, Lor |
| Fibroblast | Col1a1, Dcn, Pdgfra |
| Myofibroblast | Acta2, Tagln, Myl9 |
| Macrophage | Cd68, Adgre1, Csf1r |
| Neutrophil | S100a8, S100a9, Ly6g |
| T Cell | Cd3d, Cd3e, Cd8a |
| Endothelial | Pecam1, Cdh5, Kdr |
| HFSC | Cd34, Lgr5, Sox9 |
| Melanocyte | Dct, Tyrp1, Pmel |

---

## Mock Interview Script

Have someone (or yourself) ask these in order. Time yourself — aim for the times shown.

### Round 1: Overview (5 minutes)

**Q1** (2 min): "Tell me about your project."
→ Use Day 26 walkthrough

**Q2** (1 min): "What's tissue fluidity?"
→ Cells collectively migrating, loosening junctions, remodeling matrix, transient fluid state during repair

**Q3** (2 min): "Why single-cell instead of bulk?"
→ 10 cell types with different responses, bulk averages them, need cell-type resolution

### Round 2: Technical (10 minutes)

**Q4** (2 min): "Walk me through QC."
→ Day 7 + Day 27 answers

**Q5** (2 min): "Why pseudobulk DESeq2?"
→ Pseudoreplication problem, benchmarking, proper type-1 error control

**Q6** (2 min): "How do you handle batch effects?"
→ Harmony on PCA embeddings, not counts, validated by UMAP mixing

**Q7** (2 min): "What's your dashboard architecture?"
→ FastAPI + React + TypeScript + Plotly, DataLoader singleton

**Q8** (2 min): "How do you ensure reproducibility?"
→ Seeds (42), config-driven, environment files, version logging

### Round 3: Design (5 minutes)

**Q9** (2 min): "Why Python AND R?"
→ Day 28 trade-off answer

**Q10** (1 min): "What's the hardest design decision?"
→ Pseudobulk vs cell-level DE trade-off

**Q11** (2 min): "What would you improve?"
→ Snakemake automation, more replicates, spatial transcriptomics, integration testing

### Round 4: Curveballs (5 minutes)

**Q12** (2 min): "What if your fluidity hypothesis is wrong?"
→ Still valid science, verify technique, compare datasets, report null result

**Q13** (1 min): "What's a limitation you'd mention proactively?"
→ 2 replicates per condition limits power; no spatial information

**Q14** (2 min): "How do your 12 agents help you?"
→ Specialization, domain-specific knowledge, orchestrator coordination, reduced errors

---

## Final Confidence Checklist

Before the interview, can you:

- [ ] Deliver the 30-second elevator pitch from memory?
- [ ] Name all 10 cell types?
- [ ] List the 8 pipeline steps?
- [ ] Explain pseudobulk vs cell-level DE?
- [ ] Name the 5 fluidity signatures?
- [ ] Explain why Harmony corrects embeddings, not counts?
- [ ] Describe the dashboard architecture?
- [ ] Articulate 3 design trade-offs with the WHAT-WHY-HOW-RESULT framework?
- [ ] Handle "What would you do differently?" gracefully?
- [ ] Handle "What if you're wrong?" confidently?

If all 10 are checked, you're ready.

---

## Self-Check Questions (Final 10)

1. **Elevator pitch — go** → Practice out loud (30 seconds)
2. **8 pipeline steps from memory** → Load, QC, normalize, dim reduction, cluster, annotate, DE, fluidity
3. **Why this project matters** → Understanding tissue fluidity mechanisms could inform wound healing therapeutics
4. **Your biggest contribution** → Designed a full-stack, config-driven, reproducible pipeline with interactive dashboard
5. **One thing that surprised you** → The importance of pseudobulk over cell-level DE (massive false positive difference)
6. **How AI agents help research** → Right expert for each task, domain knowledge loaded on demand, consistent standards
7. **What you'd do with more time** → Spatial transcriptomics, more replicates, automated pipeline orchestration
8. **Simplest explanation of scRNA-seq** → Capture individual cells, read their RNA, count which genes are active
9. **Why mouse, not human?** → Model organism, controlled experiments, time-course wounding impossible in human
10. **Are you ready?** → Yes.

---

## Congratulations!

You've completed the 30-day learning guide. You now understand:
- The biology of wound healing and tissue fluidity
- The full scRNA-seq analysis pipeline
- Every major tool and method in the project
- The engineering and architecture decisions
- How to present and defend this work in an interview

Go back to any day for deeper review. The knowledge map above tells you exactly where each topic lives.

**You built this. You understand this. You can talk about this.**
