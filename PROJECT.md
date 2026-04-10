# PROJECT.md — scRNA-seq Tissue Fluidity Analysis State

> Inspired by CLAW.md pattern: a single file that tells any agent everything about the current project state.
> **Last updated**: 2026-04-02

## Identity
- **Project**: Dynamic regulation of tissue fluidity controls skin repair during wound healing
- **PI**: Rahul M Sarate
- **GitHub**: https://github.com/rahulsarate/scRNA-seq-for-tissue-fluidity
- **Started**: 2026-04-02

## Current State
| Component | Status | Last Updated | Owner Agent |
|-----------|--------|-------------|-------------|
| Workspace structure | ✅ Complete | 2026-04-02 | pipeline-builder |
| Agent configuration | ✅ Complete (10 agents) | 2026-04-02 | orchestrator |
| CI/CD workflows | ✅ Complete (lint + smoke) | 2026-04-02 | pipeline-builder |
| Documentation | ✅ Complete | 2026-04-02 | report-writer |
| Synthetic test data | ⬜ Not started | — | data-wrangler |
| GEO data download | ⬜ Not started | — | data-wrangler |
| QC analysis | ⬜ Not started | — | qc-analyst |
| Clustering & annotation | ⬜ Not started | — | scrna-analyst |
| DE analysis | ⬜ Not started | — | de-analyst |
| Pathway enrichment | ⬜ Not started | — | pathway-explorer |
| Tissue fluidity scoring | ⬜ Not started | — | scrna-analyst |
| Trajectory analysis | ⬜ Not started | — | scrna-analyst |
| Publication figures | ⬜ Not started | — | visualization-specialist |
| Methods & report | ⬜ Not started | — | report-writer |
| Final review | ⬜ Not started | — | reviewer |

## Next Actions (Priority Order)
1. **Generate synthetic data** → validate pipeline end-to-end (`generate_synthetic_data.py`)
2. **Run full pipeline on synthetic** → QC → cluster → DE → pathway → figures
3. **Download GSE234269** (primary wound healing dataset)
4. **Run QC → clustering → DE → pathway on real data**
5. **Tissue fluidity scoring and trajectory analysis**
6. **Publication figures and methods section**
7. **Code review and reproducibility validation**

## Automation Opportunities
| Opportunity | Impact | Difficulty | Status |
|-------------|--------|------------|--------|
| Makefile for one-command pipeline run | High | Low | ⬜ Planned |
| Config-driven batch processing | High | Medium | ⬜ Planned |
| Auto-generate QC report after filtering | Medium | Low | ⬜ Planned |
| Snakemake DAG for full pipeline | High | Medium | ⬜ Planned |
| Pre-commit hooks (lint + data safety) | Medium | Low | ⬜ Planned |

## Datasets
| ID | Status | Location | Description |
|----|--------|----------|-------------|
| Synthetic | ⬜ Pending | `data/synthetic/` | 8000 cells, 10 types, 4 conditions |
| GSE234269 | ⬜ Pending | `data/counts/` | Primary wound healing timepoints |
| GSE159827 | ⬜ Pending | `data/counts/` | Tissue mechanics validation |
| GSE188432 | ⬜ Pending | `data/counts/` | Aged wound healing comparison |

## Key Files
| File | Purpose |
|------|---------|
| `configs/analysis_config.yaml` | All analysis parameters |
| `.github/copilot-instructions.md` | Agent bootstrap (always-on) |
| `AGENTS.md` | Agent directory and rules |
| `.agent_config/pipelines/project_state.json` | Machine-readable pipeline state |
| `scripts/python/01_scrna_analysis_pipeline.py` | Main analysis script |

## Quality Gates
Each analysis step must pass before proceeding:

### QC Gate
- [ ] All samples have >500 cells post-filtering
- [ ] Median genes/cell: 1000-3000
- [ ] Doublet rate: ~5% per sample
- [ ] QC plots reviewed and saved

### Clustering Gate
- [ ] PCA elbow plot shows clear inflection
- [ ] Harmony removes batch effects without losing biology
- [ ] All 10 expected cell types identified
- [ ] Marker genes validate annotations

### DE Gate
- [ ] PCA shows condition separation within cell types
- [ ] Pseudobulk aggregation has ≥2 replicates per group
- [ ] lfcShrink applied to all results
- [ ] Tissue fluidity genes checked in every cell type

### Publication Gate
- [ ] All figures: PDF, 300 DPI, colorblind-safe
- [ ] Methods section complete with versions
- [ ] Reproducibility report generated
- [ ] Code pushed to GitHub

## Roadmap — Phase Plan

### Phase 1: Pipeline Validation (Current)
> Goal: Prove the entire pipeline works end-to-end on synthetic data
- [ ] Run `generate_synthetic_data.py` → 8000 cells, 10 types, 4 conditions
- [ ] Run `01_scrna_analysis_pipeline.py` → QC → cluster → DE → fluidity scores
- [ ] Run `02_visualization_suite.py` → all publication figure types
- [ ] Fix any pipeline bugs, log results
- [ ] Push validated pipeline to GitHub

### Phase 2: Real Data Analysis
> Goal: Analyze primary wound healing dataset (GSE234269)
- [ ] Download GSE234269 via `00_download_geo_data.py` or manual GEO
- [ ] Run QC (qc-analyst) → document filtering decisions
- [ ] Normalize + integrate + cluster (scrna-analyst) → annotate 10 cell types
- [ ] Pseudobulk DE per cell type: wound_3d/7d/14d vs control (de-analyst)
- [ ] Pathway enrichment on DE results (pathway-explorer)
- [ ] Tissue fluidity scoring across conditions and cell types

### Phase 3: Cross-Dataset Validation
> Goal: Validate findings using independent datasets
- [ ] Download GSE159827 (tissue mechanics) + GSE188432 (aged wounds)
- [ ] Integrate with GSE234269 (Harmony, assess batch)
- [ ] Confirm fluidity gene programs replicate across datasets
- [ ] Compare young vs aged wound fluidity

### Phase 4: Publication
> Goal: Figures, methods, manuscript
- [ ] Generate all publication figures (visualization-specialist)
- [ ] Write methods section (report-writer)
- [ ] Reviewer validates statistical rigor
- [ ] Interactive cellxgene browser for supplementary
- [ ] Push final code + archive to Zenodo

## Identified Improvement Opportunities
| # | Improvement | Impact | Effort | Status |
|---|-------------|--------|--------|--------|
| 1 | Add Makefile for one-command pipeline | High | Low | ⬜ |
| 2 | Pre-commit hooks (lint + data safety check) | Medium | Low | ⬜ |
| 3 | Snakemake DAG for reproducible pipeline | High | Medium | ⬜ |
| 4 | Auto-QC report generation (Quarto) | Medium | Medium | ⬜ |
| 5 | Config validation script (check YAML before run) | Medium | Low | ⬜ |
| 6 | Sample sheet auto-generator from GEO metadata | Medium | Low | ⬜ |
| 7 | Pipeline resume/checkpoint system | High | Medium | ⬜ |
| 8 | Interactive fluidity dashboard (cellxgene) | High | Medium | ⬜ |
| 9 | Unit tests for utility functions | Medium | Low | ⬜ |
| 10 | CHANGELOG.md for tracking analysis versions | Low | Low | ⬜ |
