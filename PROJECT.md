# PROJECT.md — scRNA-seq Tissue Fluidity Analysis State

> Inspired by CLAW.md pattern: a single file that tells any agent everything about the current project state.

## Identity
- **Project**: Dynamic regulation of tissue fluidity controls skin repair during wound healing
- **PI**: Rahul M Sarate
- **GitHub**: https://github.com/rahulsarate/scRNA-seq-for-tissue-fluidity
- **Started**: 2026-04-02

## Current State
| Component | Status | Last Updated |
|-----------|--------|-------------|
| Workspace structure | ✅ Complete | 2026-04-02 |
| Agent configuration | ✅ Complete (10 agents) | 2026-04-02 |
| Synthetic test data | ⬜ Not started | — |
| GEO data download | ⬜ Not started | — |
| QC analysis | ⬜ Not started | — |
| Clustering | ⬜ Not started | — |
| DE analysis | ⬜ Not started | — |
| Pathway enrichment | ⬜ Not started | — |
| Tissue fluidity scoring | ⬜ Not started | — |
| Trajectory analysis | ⬜ Not started | — |
| Publication figures | ⬜ Not started | — |
| Manuscript draft | ⬜ Not started | — |

## Next Actions (Priority Order)
1. Generate synthetic data → validate pipeline end-to-end
2. Download GSE234269 (primary wound healing dataset)
3. Run QC → clustering → DE → pathway on real data
4. Tissue fluidity scoring and trajectory analysis
5. Publication figures and manuscript

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
