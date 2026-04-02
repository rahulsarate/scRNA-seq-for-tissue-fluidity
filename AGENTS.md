# AGENTS.md — scRNA-seq Tissue Fluidity Project

## Project Context
This workspace analyzes single-cell RNA sequencing data from mouse skin wound healing experiments.
The central question: How does **tissue fluidity** — collective cell migration and ECM remodeling — change across wound healing phases?

## Available Agents
Select the right agent for your task:

| Agent | Role | Use When |
|-------|------|----------|
| `orchestrator` | Plan & route | Starting any multi-step analysis |
| `qc-analyst` | Quality control | QC metrics, filtering, doublet removal |
| `scrna-analyst` | Clustering & annotation | Normalization, UMAP, cell typing, trajectory |
| `de-analyst` | Differential expression | FindMarkers, pseudobulk DESeq2, MAST |
| `pathway-explorer` | Pathway analysis | GO, KEGG, GSEA, Reactome, PROGENy |
| `visualization-specialist` | Plotting | UMAP, volcano, heatmap, publication figures |
| `data-wrangler` | Data management | Import CSV/RDS/h5ad, metadata, sample sheets |
| `pipeline-builder` | Workflow automation | Snakemake, Nextflow, conda environments |
| `report-writer` | Documentation | Methods sections, Quarto reports, figure legends |
| `reviewer` | Code review | Statistical validation, reproducibility checks |

## Handoff Order (typical analysis)
```
orchestrator → qc-analyst → scrna-analyst → de-analyst → pathway-explorer
                                                    ↘ visualization-specialist
                                                            ↘ report-writer → reviewer
```

## Rules for All Agents
1. **Mouse genes**: Use proper symbol case — `Krt14` not `KRT14`, `mt-` prefix not `MT-`
2. **Reproducibility**: Always set seeds (42), log package versions
3. **Data safety**: Never modify `data/raw/`, never commit large binaries
4. **Save outputs**: R→`.rds`, Python→`.h5ad`, tables→`.csv`, figures→`.pdf`
5. **Tissue fluidity focus**: Always consider EMT, ECM, migration, mechanotransduction gene signatures
6. **Config-driven**: Read parameters from `configs/analysis_config.yaml`, don't hardcode
