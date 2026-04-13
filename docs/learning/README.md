# 30-Day Learning Guide: scRNA-seq Wound Healing Project

## Purpose

A **project-focused interview preparation guide** for the scRNA-seq tissue fluidity project.
Each day covers one topic with code examples from the actual project, interview Q&A, and self-check questions.

**Goal**: Prepare to discuss this project confidently as a solo developer in an interview setting.

---

## How to Use This Guide

- **Study 1 day per session** (about 1-2 hours each)
- **Read in order** — each day builds on the previous
- **Practice the interview Q&A** sections out loud
- **Answer the 10 self-check questions** at the end of each day
- **Review Days 26-30** before any interview

---

## 30-Day Curriculum

### Week 1: Project Foundation (Days 1-5)
| Day | Topic | What You'll Learn |
|-----|-------|-------------------|
| [Day 01](Day_01_Project_Overview.md) | Project Overview | Elevator pitch, clinical relevance, pipeline overview |
| [Day 02](Day_02_scRNAseq_Technology.md) | scRNAseq Technology | 10X Chromium, Cell Ranger, count matrices, AnnData |
| [Day 03](Day_03_Wound_Healing_Biology.md) | Wound Healing Biology | 4 phases, 10 cell types, tissue fluidity concept |
| [Day 04](Day_04_Project_Architecture.md) | Project Architecture | Directory structure, separation of concerns, data lineage |
| [Day 05](Day_05_Technology_Stack.md) | Technology Stack | Scanpy, Seurat, DESeq2, FastAPI, React, Plotly |

### Week 2: The Analysis Pipeline (Days 6-10)
| Day | Topic | What You'll Learn |
|-----|-------|-------------------|
| [Day 06](Day_06_Data_Journey.md) | Data Journey | GEO datasets, synthetic data, file formats |
| [Day 07](Day_07_Quality_Control.md) | Quality Control | QC metrics, filtering thresholds, doublet detection |
| [Day 08](Day_08_Normalization.md) | Normalization & Feature Selection | Library size correction, HVG selection |
| [Day 09](Day_09_Dimensionality_Reduction.md) | Dimensionality Reduction | PCA, nearest neighbors, UMAP |
| [Day 10](Day_10_Clustering.md) | Clustering & Cell Types | Leiden algorithm, marker scoring, annotation |

### Week 3: Analysis Methods (Days 11-16)
| Day | Topic | What You'll Learn |
|-----|-------|-------------------|
| [Day 11](Day_11_Differential_Expression.md) | Differential Expression | Pseudobulk DESeq2, log2FC, p-value correction |
| [Day 12](Day_12_Tissue_Fluidity.md) | Tissue Fluidity Scoring | 5 gene signatures, score_genes algorithm |
| [Day 13](Day_13_Pathway_Enrichment.md) | Pathway Enrichment | GO, KEGG, GSEA, clusterProfiler |
| [Day 14](Day_14_Visualization.md) | Visualization & Figures | UMAP, volcano, heatmap, publication standards |
| [Day 15](Day_15_Dashboard.md) | Interactive Dashboard | FastAPI backend, React frontend, API design |
| [Day 16](Day_16_Reproducibility.md) | Reproducibility | Seeds, environments, config, version logging |

### Week 4: Engineering & Advanced Topics (Days 17-25)
| Day | Topic | What You'll Learn |
|-----|-------|-------------------|
| [Day 17](Day_17_Git_Workflow.md) | Git Workflow | Version control, branching, CI integration |
| [Day 18](Day_18_AI_Agents.md) | AI Agent Architecture | 12 agents, skills, instructions, handoffs |
| [Day 19](Day_19_CICD.md) | CI/CD & GitHub Actions | Automated linting, smoke tests |
| [Day 20](Day_20_Config_Design.md) | Config-Driven Design | analysis_config.yaml, single source of truth |
| [Day 21](Day_21_Python_Practices.md) | Python Best Practices | Coding conventions, AnnData patterns, pitfalls |
| [Day 22](Day_22_R_Integration.md) | R Integration & DESeq2 | Seurat, DESeq2 deep dive, dual-language design |
| [Day 23](Day_23_Batch_Effects.md) | Batch Effects & Integration | Harmony, embedding correction, LISI |
| [Day 24](Day_24_Trajectory.md) | Trajectory Analysis | Pseudotime, RNA velocity, scVelo |
| [Day 25](Day_25_Cell_Communication.md) | Cell Communication | CellChat, ligand-receptor, signaling pathways |

### Week 5: Interview Preparation (Days 26-30)
| Day | Topic | What You'll Learn |
|-----|-------|-------------------|
| [Day 26](Day_26_Interview_Walkthrough.md) | Project Walkthrough | 5-minute pitch, transitions, follow-up prep |
| [Day 27](Day_27_Technical_Deep_Dives.md) | Technical Deep Dives | Method-level answers, WHAT-WHY-HOW-RESULT |
| [Day 28](Day_28_Design_Decisions.md) | Design Decisions | Trade-offs: Python+R, DESeq2, Harmony, config |
| [Day 29](Day_29_Common_Questions.md) | Common Questions | Top 20 Q&A, red flags, delivery tips |
| [Day 30](Day_30_Final_Review.md) | Final Review & Mock | Knowledge map, quick reference, mock interview |

---

## Quick Reference

```
scRNA_seq/
├── configs/analysis_config.yaml  ← All parameters (Day 20)
├── scripts/python/               ← Pipeline + synthetic data (Days 6-12)
├── scripts/R/                    ← Seurat + DESeq2 (Day 22)
├── analysis/                     ← All outputs (Days 7-14)
├── dashboard/                    ← FastAPI + React (Day 15)
├── .github/agents/               ← 12 AI agents (Day 18)
├── .github/skills/               ← Domain knowledge (Day 18)
└── docs/learning/                ← YOU ARE HERE!
```

---

## Tips

1. **Focus on WHY** — interviewers care about reasoning, not memorization
2. **Practice out loud** — saying answers builds confidence
3. **Use the WHAT-WHY-HOW-RESULT framework** (Day 27) for any technical question
4. **Know your trade-offs** (Day 28) — this is what separates juniors from seniors
5. **Review Day 30** the night before any interview

Let's begin! Start with [Day 01: The Big Picture](Day_01_Big_Picture.md) →
