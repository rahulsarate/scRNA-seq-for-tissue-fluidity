# Usage Guide — scRNA-seq Agents & Repository

> How to use the 10 AI agents and this repo to efficiently analyze wound healing scRNA-seq data.

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [How Agents Work](#how-agents-work)
3. [Agent Reference](#agent-reference)
4. [Common Workflows](#common-workflows)
5. [Prompt Templates](#prompt-templates)
6. [Directory Cheat Sheet](#directory-cheat-sheet)
7. [Tips for Efficiency](#tips-for-efficiency)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Open this repo in VS Code
```
code d:\VS CODE Project\scRNA_seq
```

### 2. Install VS Code Extensions
- **GitHub Copilot** + **GitHub Copilot Chat** (required for agents)
- **Python** (ms-python)
- **R Extension** (REditorSupport.r)

### 3. Set Up Conda Environment
```bash
conda env create -f configs/conda_envs/scrna_wound_healing.yml
conda activate scrna_wound
```

### 4. Run Your First Analysis
Open Copilot Chat (Ctrl+Shift+I) and type:
```
@orchestrator generate synthetic data and run the full analysis pipeline
```

---

## How Agents Work

### What Are Agents?
Agents are specialized AI assistants defined in `.github/agents/`. Each one has:
- A **role** (e.g., QC, clustering, visualization)
- **Tools** it can use (search, edit files, run terminal commands)
- **Handoffs** to pass work to the next agent in the pipeline

### How VS Code Discovers Them
VS Code Copilot automatically discovers `.agent.md` files in `.github/agents/`. They appear in the chat as `@agent-name`.

### How to Invoke
In VS Code Copilot Chat:
```
@agent-name your request here
```

### The Orchestrator Pattern
For complex tasks, start with `@orchestrator`. It will:
1. Analyze your request
2. Break it into steps
3. Route each step to the right specialist agent

---

## Agent Reference

### @orchestrator — The Entry Point
**When to use**: Starting any multi-step workflow, unsure which agent to pick
```
@orchestrator plan the full analysis for GSE234269
@orchestrator what should I do next?
@orchestrator I have count matrices, run DE and pathway analysis
```

### @qc-analyst — Quality Control
**When to use**: Filtering cells, checking data quality, removing doublets
```
@qc-analyst run QC on data/synthetic/synthetic_counts.h5ad
@qc-analyst what's the doublet rate in my data?
@qc-analyst filter with min_genes=200 max_mt=15%
```
**Output**: QC plots in `analysis/qc/`, filtered data in `analysis/clustering/`

### @scrna-analyst — Clustering & Cell Types
**When to use**: After QC, for normalization through cell type annotation
```
@scrna-analyst normalize and cluster the QC-filtered data
@scrna-analyst annotate cell types using known wound healing markers
@scrna-analyst run trajectory analysis on fibroblasts
@scrna-analyst test multiple clustering resolutions (0.4, 0.6, 0.8, 1.0)
```
**Output**: Processed objects in `analysis/clustering/`, UMAP coordinates

### @de-analyst — Differential Expression
**When to use**: Comparing conditions, finding marker genes
```
@de-analyst pseudobulk DESeq2 wound_7d vs control for all cell types
@de-analyst find markers for each cluster
@de-analyst run time-series DE across wound phases for fibroblasts
@de-analyst which tissue fluidity genes are DE in myofibroblasts?
```
**Output**: CSV tables in `analysis/de/`, volcano plot data

### @pathway-explorer — Pathway Analysis
**When to use**: After DE, for biological function interpretation
```
@pathway-explorer GO enrichment on upregulated fibroblast genes (wound_7d vs control)
@pathway-explorer GSEA using Hallmark gene sets on macrophage DE results
@pathway-explorer which pathways are enriched across all cell types?
@pathway-explorer score PROGENy pathways per cell
```
**Output**: Enrichment tables + plots in `analysis/enrichment/`

### @visualization-specialist — Figures
**When to use**: Publication-quality plots at any stage
```
@visualization-specialist create Figure 1 (UMAP + proportions panel)
@visualization-specialist volcano plot for fibroblast DE results
@visualization-specialist heatmap of tissue fluidity genes across conditions
@visualization-specialist dotplot of markers for all 10 cell types
```
**Output**: PDF figures in `analysis/figures/` (300 DPI, colorblind-safe)

### @data-wrangler — Data Import
**When to use**: Getting data into the pipeline, format conversion
```
@data-wrangler download GSE234269 from GEO
@data-wrangler convert Seurat .rds to AnnData .h5ad
@data-wrangler create sample sheet from metadata
@data-wrangler merge multiple 10X samples into one AnnData
```
**Output**: Data files in `data/counts/` or `data/metadata/`

### @pipeline-builder — Automation
**When to use**: Reproducible workflows, environment setup
```
@pipeline-builder create Snakemake pipeline for full analysis
@pipeline-builder update conda environment with new packages
@pipeline-builder create a Makefile for one-command pipeline run
```
**Output**: Workflow files in `scripts/pipelines/`, env files in `configs/`

### @report-writer — Documentation
**When to use**: Writing up results, methods sections
```
@report-writer write methods for QC + clustering steps
@report-writer create figure legend for Figure 1
@report-writer generate Quarto report for the DE results
```
**Output**: Reports in `reports/`, methods in `docs/methods/`

### @reviewer — Validation
**When to use**: Before finalizing results, checking statistical rigor
```
@reviewer validate the DE analysis code
@reviewer check reproducibility of the clustering pipeline
@reviewer are there statistical issues with this comparison?
```
**Output**: Review comments (does not modify files — read-only)

---

## Common Workflows

### Workflow 1: Full Pipeline (Synthetic → Publication)
```
Step 1: @data-wrangler generate synthetic test data
Step 2: @qc-analyst run quality control
Step 3: @scrna-analyst normalize, cluster, and annotate
Step 4: @de-analyst pseudobulk DE for all conditions vs control
Step 5: @pathway-explorer GO/KEGG enrichment on DE results
Step 6: @visualization-specialist create all publication figures
Step 7: @report-writer write methods section
Step 8: @reviewer validate everything

Or simply: @orchestrator run the complete analysis pipeline
```

### Workflow 2: Quick DE Check
```
Step 1: @de-analyst DESeq2 wound_7d vs control for fibroblasts
Step 2: @visualization-specialist volcano plot for the DE results
Step 3: @pathway-explorer GO enrichment on significant genes
```

### Workflow 3: Tissue Fluidity Deep Dive
```
Step 1: @scrna-analyst score all fluidity signatures (EMT, ECM, migration, mechanotransduction, wound signals)
Step 2: @visualization-specialist feature plots + violin plots of fluidity scores by condition
Step 3: @de-analyst test which fluidity genes are DE in each cell type
Step 4: @pathway-explorer GSEA with custom fluidity gene sets
```

### Workflow 4: New Dataset Integration
```
Step 1: @data-wrangler download and import GSE188432
Step 2: @qc-analyst run QC independently
Step 3: @scrna-analyst integrate with existing data using Harmony
Step 4: @de-analyst compare fluidity patterns across datasets
```

---

## Prompt Templates

Six reusable prompt templates are in `.github/prompts/`. Use them in VS Code:

| Prompt File | What It Does |
|-------------|-------------|
| `run-qc.prompt.md` | Full QC workflow with thresholds |
| `run-clustering.prompt.md` | Normalize → cluster → annotate pipeline |
| `run-de-analysis.prompt.md` | Pseudobulk DESeq2 with fluidity gene focus |
| `generate-synthetic-data.prompt.md` | Create test data matching project specs |
| `tissue-fluidity-scoring.prompt.md` | Score all 5 fluidity gene signatures |
| `create-publication-figure.prompt.md` | Standard Figure 1 panel layout |

To use a prompt template, open it and copy the content to Copilot Chat, or reference it with `#file:.github/prompts/run-qc.prompt.md`.

---

## Directory Cheat Sheet

| You Want To... | Look In / Save To |
|----------------|-------------------|
| Find raw data | `data/raw/` (READ-ONLY) |
| Find processed counts | `data/counts/` |
| See test data | `data/synthetic/` |
| See QC results | `analysis/qc/` |
| See DE results | `analysis/de/` |
| See pathway results | `analysis/enrichment/` |
| See cluster objects | `analysis/clustering/` |
| See figures | `analysis/figures/` |
| See trajectory results | `analysis/trajectory/` |
| Edit Python scripts | `scripts/python/` |
| Edit R scripts | `scripts/R/` |
| Check analysis config | `configs/analysis_config.yaml` |
| Read prompts | `.github/prompts/` |
| Check agent definitions | `.github/agents/` |
| Log decisions | `docs/decision_log.md` |
| Track project state | `PROJECT.md` |

---

## Tips for Efficiency

### 1. Start with the Orchestrator
When in doubt, ask `@orchestrator`. It reads the whole project context and routes to the right agent.

### 2. Use Config, Don't Hardcode
All thresholds live in `configs/analysis_config.yaml`. Tell agents to read from config:
```
@qc-analyst filter cells using thresholds from the config file
```

### 3. Chain Agents for Complex Tasks
Instead of one massive prompt, break work into agent-sized steps:
```
@qc-analyst filter → @scrna-analyst cluster → @de-analyst DE → @pathway-explorer enrich
```

### 4. Refer to Existing Files
Agents work better with context. Reference existing results:
```
@de-analyst run DE using the clustered object in analysis/clustering/
@visualization-specialist plot DE results from analysis/de/fibroblast_wound7d_vs_control.csv
```

### 5. Check PROJECT.md Before Starting
`PROJECT.md` tracks what's done and what's next. Start each session by reading it.

### 6. Log Your Decisions
After key analysis choices, update `docs/decision_log.md`:
```
@report-writer log decision: chose resolution 0.8 because clustree showed stability
```

### 7. Use the 25 Ready Prompts
`docs/25_ready_prompts.md` has copy-paste prompts for every analysis step. Start there if you're unsure what to ask.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent not appearing in VS Code | Ensure `.github/agents/*.agent.md` files have valid YAML frontmatter |
| "No data found" error | Generate synthetic data first: `python scripts/python/generate_synthetic_data.py` |
| Pipeline fails mid-way | Check `analysis/` subdirectories for partial outputs; re-run from last successful step |
| Wrong gene casing | Mouse genes use format `Krt14` (not `KRT14`). Check `configs/analysis_config.yaml` for reference |
| Conda env issues | Recreate: `conda env remove -n scrna_wound; conda env create -f configs/conda_envs/scrna_wound_healing.yml` |
| Agent gives generic advice | Provide more context: reference specific files, conditions, cell types |

---

## Key Files for Agents
These files are automatically loaded by VS Code Copilot as context:
- `.github/copilot-instructions.md` — Project bootstrap (always active)
- `AGENTS.md` — Agent directory and rules (always active)
- `.github/instructions/*.instructions.md` — Coding standards (auto-applied by file type)
- `configs/analysis_config.yaml` — All analysis parameters
