# AGENTS.md — scRNA-seq Tissue Fluidity Project

## Project Context
This workspace analyzes single-cell RNA sequencing data from mouse skin wound healing experiments.
The central question: How does **tissue fluidity** — collective cell migration and ECM remodeling — change across wound healing phases?

## Available Agents
Select the right agent for your task:

| Agent | Role | Use When |
|-------|------|----------|
| `orchestrator` | Plan & route | Starting any multi-step analysis |
| `coder` | Implementation | Writing, editing, debugging, running Python/R code |
| `qc-analyst` | Quality control | QC metrics, filtering, doublet removal |
| `scrna-analyst` | Clustering & annotation | Normalization, UMAP, cell typing, trajectory |
| `de-analyst` | Differential expression | FindMarkers, pseudobulk DESeq2, MAST |
| `pathway-explorer` | Pathway analysis | GO, KEGG, GSEA, Reactome, PROGENy |
| `visualization-specialist` | Plotting | UMAP, volcano, heatmap, publication figures |
| `data-wrangler` | Data management | Import CSV/RDS/h5ad, metadata, sample sheets |
| `pipeline-builder` | Workflow automation | Snakemake, Nextflow, conda environments |
| `report-writer` | Documentation | Methods sections, Quarto reports, figure legends |
| `reviewer` | Code review | Statistical validation, reproducibility checks |

## How to Invoke (VS Code Copilot Chat)
```
@orchestrator plan the full analysis for GSE234269
@coder write the script to generate synthetic data
@qc-analyst filter cells: min_genes=200, max_mt=15%
@scrna-analyst cluster and annotate cell types
@de-analyst pseudobulk DESeq2 wound_7d vs control for fibroblasts
@pathway-explorer GO enrichment on upregulated fibroblast genes
@visualization-specialist create Figure 1 panel (UMAP + proportions)
@data-wrangler download and parse GSE234269
@pipeline-builder create Snakemake workflow for full pipeline
@report-writer write methods section for the QC + clustering steps
@reviewer validate the DE analysis for statistical correctness
```

## Handoff Order (typical analysis)
```
orchestrator → data-wrangler → qc-analyst → scrna-analyst → de-analyst → pathway-explorer
                                                                    ↘ visualization-specialist
                                                                            ↘ report-writer → reviewer
```
The `coder` agent can be invoked at any step to write, edit, debug, or run scripts.

## Agent Handoff Map
Every agent can hand off forward in the pipeline AND return to the orchestrator for re-routing.

| Agent | Hands Off To | Returns To |
|-------|-------------|------------|
| `orchestrator` | ALL agents (auto-delegates with `send: true`) | — |
| `data-wrangler` | qc-analyst, coder | orchestrator |
| `qc-analyst` | scrna-analyst, data-wrangler, coder | orchestrator |
| `scrna-analyst` | de-analyst, visualization-specialist, pathway-explorer, coder | orchestrator |
| `de-analyst` | pathway-explorer, visualization-specialist, coder | orchestrator |
| `pathway-explorer` | visualization-specialist, report-writer, coder | orchestrator |
| `visualization-specialist` | report-writer, coder | orchestrator |
| `report-writer` | reviewer, coder | orchestrator |
| `reviewer` | coder (fix issues), report-writer (document findings) | orchestrator |
| `coder` | qc-analyst, scrna-analyst, visualization-specialist, reviewer, pipeline-builder | orchestrator |

### Handoff Behavior
- **`send: true`**: Automatic task transfer — the target agent starts working immediately
- **`send: false`**: Manual transfer — user reviews/edits the prompt before sending (used for "Implement Code" handoffs where context needs refinement)

## Agent Locations
| Location | Format | Discovery |
|----------|--------|-----------|
| `.github/agents/` | VS Code `.agent.md` (YAML frontmatter) | Auto-discovered by VS Code Copilot |
| `.agent_config/agents/` | Custom `.md` | Referenced by orchestrator + bootstrap |
| `AGENTS.md` (this file) | Root directory | Always loaded by Copilot as context |

## Available Skills
Skills are in `.github/skills/<name>/SKILL.md` and are auto-discovered by VS Code Copilot.

| Skill | Description | Used By |
|-------|-------------|--------|
| `scrna-pipeline` | Full pipeline execution steps | coder, orchestrator |
| `data-safety` | Data protection rules | all agents |
| `python-coding` | Python/Scanpy coding conventions | coder, scrna-analyst, de-analyst |
| `r-coding` | R/Seurat coding conventions | coder, scrna-analyst, de-analyst |
| `tissue-fluidity` | Fluidity gene signatures and scoring | scrna-analyst, de-analyst, coder |
| `deseq2-analysis` | Pseudobulk DESeq2 workflow | de-analyst, coder |
| `enrichment-analysis` | GO/KEGG/GSEA enrichment | pathway-explorer, coder |
| `publication-figures` | Publication-quality figure templates | visualization-specialist, coder |
| `qc-workflow` | QC filtering and doublet detection | qc-analyst, coder |
| `data-import` | GEO/10X data import patterns | data-wrangler, coder |
| `methods-writing` | Methods sections and figure legends | report-writer |

## Python Environment
- **pip**: `.venv/` (Python 3.10) — `requirements.txt` for core packages
- **conda**: `configs/conda_envs/scrna_wound_healing.yml` — full environment with C-compiled packages
- Activate: `.venv\Scripts\activate` (Windows) or `conda activate scrna_wound_healing`

## Rules for All Agents
1. **Mouse genes**: Use proper symbol case — `Krt14` not `KRT14`, `mt-` prefix not `MT-`
2. **Reproducibility**: Always set seeds (42), log package versions
3. **Data safety**: Never modify `data/raw/`, never commit large binaries
4. **Save outputs**: R→`.rds`, Python→`.h5ad`, tables→`.csv`, figures→`.pdf`
5. **Tissue fluidity focus**: Always consider EMT, ECM, migration, mechanotransduction gene signatures
6. **Config-driven**: Read parameters from `configs/analysis_config.yaml`, don't hardcode
