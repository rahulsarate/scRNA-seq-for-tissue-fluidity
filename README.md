# scRNA-seq Analysis: Tissue Fluidity in Wound Healing

> **PI**: Rahul M Sarate  
> **Project**: Dynamic regulation of tissue fluidity controls skin repair during wound healing  
> **Organism**: *Mus musculus* (C57BL/6J)  
> **Created**: 2026-04-02

---

## Overview

This project investigates how **tissue fluidity** — the mechanical property governing collective cell migration and ECM remodeling — is dynamically regulated during skin wound healing, using **single-cell RNA sequencing (scRNA-seq)** to dissect cell-type-specific gene programs across wound healing phases.

### Research Questions
1. How does tissue fluidity change across wound healing phases (homeostasis → inflammatory → proliferative → remodeling)?
2. Which cell types are the primary drivers of fluidity changes?
3. What are the key gene regulatory networks controlling the fluidity transition?
4. Can tissue fluidity signatures predict wound healing outcomes?

---

## Project Structure

```
scRNA_seq/
├── .agent_config/          # AI agent definitions (10 agents, 10 skills)
│   ├── agents/             # orchestrator, qc-analyst, de-analyst, etc.
│   ├── skills/             # fastqc-pipeline, deseq2-analysis, etc.
│   └── pipelines/          # Pipeline state tracking
├── data/
│   ├── raw/                # Raw FASTQ (READ-ONLY)
│   ├── counts/             # Cell Ranger output / count matrices
│   ├── synthetic/          # Synthetic test data
│   ├── references/         # Genome refs + GEO dataset catalog
│   └── metadata/           # Sample sheets
├── analysis/
│   ├── qc/                 # QC reports & plots
│   ├── de/                 # Differential expression results
│   ├── enrichment/         # GO/KEGG/GSEA results
│   ├── clustering/         # Processed AnnData/Seurat + UMAP coords
│   ├── figures/            # Publication-quality figures
│   └── trajectory/         # Pseudotime & RNA velocity
├── scripts/
│   ├── python/             # Analysis pipeline (3 main scripts)
│   ├── R/                  # R/Seurat scripts
│   └── bash/               # Download & shell scripts
├── configs/                # Analysis parameters & conda envs
├── docs/                   # 25 prompts, research paradigms, methods
├── reports/                # Rmarkdown/Quarto reports
├── templates/              # Sample sheet & analysis templates
└── logs/                   # Session & pipeline logs
```

---

## Quick Start

### 1. Set Up Environment
```bash
conda env create -f configs/conda_envs/scrna_wound_healing.yml
conda activate scrna_wound
```

### 2. Generate Synthetic Data (for testing)
```bash
python scripts/python/generate_synthetic_data.py
```

### 3. Run Analysis Pipeline
```bash
python scripts/python/01_scrna_analysis_pipeline.py
```

### 4. Generate Visualizations
```bash
python scripts/python/02_visualization_suite.py
```

### 5. Explore Real Data
```bash
python scripts/python/00_download_geo_data.py
```

---

## Key Datasets

| GEO ID | Description | Relevance | Samples |
|--------|-------------|-----------|---------|
| **GSE234269** | Wound healing scRNA-seq (3d, 7d, 14d) | ★★★★★ | 3 |
| **GSE159827** | Tissue mechanics in wound-induced regeneration | ★★★★★ | 1 |
| **GSE188432** | Young vs aged wound healing scRNA-seq | ★★★★☆ | 11 |
| **GSE203244** | Macrophage heterogeneity during wound healing | ★★★★☆ | 3 |
| **GSE186821** | Diabetic wound immune cells | ★★★☆☆ | 8 |
| **GSE197588** | Wound epigenetic memory in stem cells | ★★★★☆ | 310 |

---

## AI Agents

This project uses **10 specialized AI agents** defined in `.github/agents/` (VS Code native) with backups in `.agent_config/agents/`:

| Agent | Role | Invoke in VS Code |
|-------|------|--------------------|
| `orchestrator` | Route tasks to the right agent | `@orchestrator plan full analysis` |
| `qc-analyst` | Cell filtering, doublet removal, SoupX | `@qc-analyst run QC on synthetic data` |
| `scrna-analyst` | Clustering, annotation, trajectory | `@scrna-analyst cluster and annotate` |
| `de-analyst` | Pseudobulk DESeq2, MAST, FindMarkers | `@de-analyst run DE wound_7d vs control` |
| `pathway-explorer` | GO, KEGG, GSEA, decoupleR | `@pathway-explorer GO enrichment on DE results` |
| `visualization-specialist` | UMAP, volcano, heatmap, dot plots | `@visualization-specialist create Figure 1` |
| `data-wrangler` | Import GEO data, merge samples | `@data-wrangler download GSE234269` |
| `pipeline-builder` | Snakemake/Nextflow workflows | `@pipeline-builder create Snakemake pipeline` |
| `report-writer` | Methods sections, Quarto reports | `@report-writer write methods section` |
| `reviewer` | Statistical & reproducibility review | `@reviewer validate DE results` |

> **New to agents?** See [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) for a complete walkthrough.

---

## Tissue Fluidity Gene Signatures

| Category | Genes | Role |
|----------|-------|------|
| **EMT** | Vim, Cdh1/2, Snai1/2, Twist1, Zeb1/2 | Epithelial-mesenchymal transition |
| **ECM remodeling** | Fn1, Col1a1/3a1, Mmp2/9/14, Lox | Matrix dynamics |
| **Cell migration** | Rac1, Cdc42, RhoA, Itgb1 | Motility machinery |
| **Mechanotransduction** | Yap1, Wwtr1/TAZ, Piezo1, Trpv4 | Force sensing |
| **Wound signals** | Tgfb1/2/3, Pdgfa, Vegfa, Wnt5a | Repair signals |

---

## New Research Paradigms

See [docs/research-paradigms/new_research_paradigms.md](docs/research-paradigms/new_research_paradigms.md) for 8 proposed paradigms:

1. **Mechano-Transcriptomics** — Forces → gene expression at single-cell resolution
2. **Fluidity-Guided Therapy** — Drug targets modulating tissue stiffness
3. **Temporal Cell State Atlas** — 12+ timepoint scRNA-seq wound atlas
4. **Spatial Fluidity Mapping** — Visium/MERFISH fluidity gradients
5. **Predictive Healing Models** — ML from early gene signatures
6. **Cross-Tissue Fluidity** — Compare skin, gut, liver, lung repair
7. **Epigenetic Fluidity Memory** — Chromatin-level wound memory
8. **Single-Cell Mechanical Phenotyping** — Stiffness + transcriptome

---

## CI/CD & Automation

| Workflow | Trigger | What It Does |
|----------|---------|-------|
| `lint.yml` | Push/PR to main | Runs flake8 (Python) + lintr (R) |
| `smoke-test.yml` | Push/PR when scripts change | Generates small synthetic dataset, validates output |

Run locally:
```bash
# Lint Python
flake8 scripts/python/ --max-line-length=120
# Run smoke test
python scripts/python/generate_synthetic_data.py
```

---

## References

1. Sarate RM et al. "Dynamic regulation of tissue fluidity controls skin repair during wound healing"
2. Love MI et al. (2014) DESeq2. *Genome Biology*
3. Stuart T et al. (2019) Comprehensive Integration of Single-Cell Data. *Cell*
4. Wolf FA et al. (2018) Scanpy. *Genome Biology*
5. Bergen V et al. (2020) RNA velocity. *Nature Biotechnology*

---

## License

Analysis scripts: MIT License  
Data: Subject to GEO terms and original publication restrictions.
