# Day 4: Project Architecture — How Everything Is Organized

> **Goal**: Understand why every folder, file, and config exists. Be able to explain your architecture decisions in an interview.

---

## Why Architecture Matters

Even as a **solo developer**, project architecture is critical:

| Bad Architecture | Good Architecture |
|-----------------|-------------------|
| All scripts in one folder | Scripts organized by language and purpose |
| Parameters hardcoded in scripts | Central config file (`analysis_config.yaml`) |
| Raw and processed data mixed | Clear data lineage: raw → counts → analysis |
| "It works on my machine" | Reproducible environments (conda/pip) |
| Can't explain where anything is | Can walk someone through in 5 minutes |

---

## The Directory Structure — Fully Explained

```
scRNA_seq/                          ← PROJECT ROOT
│
├── AGENTS.md                       ← AI agent roles directory
├── PROJECT.md                      ← Current state tracker (what's done/pending)
├── README.md                       ← Anyone visiting sees this first
├── requirements.txt                ← Python packages (pip install -r)
│
├── configs/                        ← 🎛️ ALL PARAMETERS — ONE PLACE
│   ├── analysis_config.yaml        ← QC thresholds, gene lists, clustering params
│   └── conda_envs/
│       └── scrna_wound_healing.yml ← Full conda environment definition
│
├── data/                           ← 📦 DATA by processing stage
│   ├── raw/                        ← 🔒 READ-ONLY: Raw FASTQ (NEVER modify)
│   ├── synthetic/                  ← Generated test data (safe to regenerate)
│   ├── counts/                     ← Count matrices & imported datasets
│   │   ├── GSE234269/              ← Primary wound healing dataset
│   │   └── GSE159827/              ← Mechanics validation dataset
│   ├── metadata/                   ← Sample sheets, GEO metadata CSVs
│   └── references/                 ← Genome refs, dataset catalogs
│
├── scripts/                        ← 💻 CODE by language
│   ├── python/                     ← Scanpy pipeline
│   │   ├── generate_synthetic_data.py      (Step 0)
│   │   ├── 01_scrna_analysis_pipeline.py   (Step 1: full pipeline)
│   │   ├── 02_visualization_suite.py       (Step 2: figures)
│   │   └── prep_dashboard_data.py          (Step 3: dashboard)
│   ├── R/                          ← Seurat alternative
│   │   ├── generate_synthetic_seurat.R
│   │   └── 01_seurat_analysis.R
│   └── utils/                      ← Shared helpers
│
├── analysis/                       ← 📊 OUTPUT by analysis type
│   ├── qc/                         ← QC metrics, plots
│   ├── clustering/                 ← Processed .h5ad, UMAP coords
│   ├── de/                         ← Differential expression CSVs
│   ├── enrichment/                 ← GO/KEGG/GSEA results
│   ├── figures/                    ← Publication figures (PDF, 300 DPI)
│   └── trajectory/                 ← Pseudotime, RNA velocity
│
├── dashboard/                      ← 🌐 INTERACTIVE WEB APP
│   ├── backend/                    ← FastAPI REST API
│   │   └── app/
│   │       ├── main.py             ← Entry point
│   │       ├── routers/            ← Endpoint modules (umap, genes, de, fluidity)
│   │       └── services/           ← Data loading logic
│   └── frontend/                   ← React + TypeScript + Tailwind
│       └── src/
│           ├── App.tsx             ← Main app with routing
│           ├── components/         ← UMAPPlot, VolcanoPlot, etc.
│           └── pages/              ← Overview, GeneExplorer, DEResults
│
├── docs/                           ← 📖 DOCUMENTATION
│   ├── learning/                   ← This 30-day guide
│   └── methods/                    ← Paper methods sections
│
├── reports/                        ← Generated Quarto reports
├── logs/                           ← Pipeline run logs
│
└── .github/                        ← GITHUB + AI CONFIG
    ├── copilot-instructions.md     ← Always-on AI context
    ├── agents/                     ← Agent role definitions
    ├── skills/                     ← Domain knowledge files
    ├── instructions/               ← Coding rules (Python, R)
    └── workflows/                  ← CI/CD (lint, tests)
```

### The Kitchen Analogy

| Kitchen | Project | Why Separate? |
|---------|---------|---------------|
| Raw ingredients (fridge) | `data/raw/` | Never contaminate the source |
| Recipe book | `scripts/` | Reusable, modifiable |
| Seasoning preferences | `configs/` | Change taste without rewriting recipes |
| Cooked dishes | `analysis/` | Output of following recipes |
| Photo for Instagram | `analysis/figures/` | Presentation layer |
| Restaurant menu (website) | `dashboard/` | Interactive experience |

---

## Design Pattern 1: Separation of Concerns

**Principle**: Each part does ONE job.

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   configs/   │     │   scripts/   │     │   analysis/  │
│              │     │              │     │              │
│  WHAT to do  │────▶│  HOW to do   │────▶│  RESULTS     │
│  (parameters)│     │  (code)      │     │  (outputs)   │
└──────────────┘     └──────────────┘     └──────────────┘
```

- Want to change QC threshold? Edit `configs/analysis_config.yaml` — NOT the pipeline script
- Want to try different clustering? Change config — NOT code
- Want to add a gene signature? Add to config — the pipeline picks it up

---

## Design Pattern 2: Config-Driven Analysis

### Hardcoded vs Config-Driven

```python
# ❌ HARDCODED — bad
def qc_filter(adata):
    adata = adata[adata.obs['n_genes'] > 200]      # magic number
    adata = adata[adata.obs['pct_mt'] < 15]         # buried in code

# ✅ CONFIG-DRIVEN — good
import yaml
with open('configs/analysis_config.yaml') as f:
    config = yaml.safe_load(f)

def qc_filter(adata):
    min_genes = config['qc_thresholds']['min_genes_per_cell']   # 200
    max_mt = config['qc_thresholds']['max_percent_mt']           # 15
    adata = adata[adata.obs['n_genes'] > min_genes]
    adata = adata[adata.obs['pct_mt'] < max_mt]
```

### Key Config Sections

```yaml
qc_thresholds:
  min_genes_per_cell: 200     # Below = empty droplet
  max_genes_per_cell: 5000    # Above = likely doublet
  max_percent_mt: 15          # Above = dying cell

clustering:
  algorithm: "Leiden"          
  default_resolution: 0.8     # Tried 0.4, 0.6, 0.8, 1.0
  n_neighbors: 15
  n_pcs: 30

tissue_fluidity_signatures:    # The core research focus
  EMT:
    genes: [Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2]
  ECM_remodeling:
    genes: [Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2]
```

---

## Design Pattern 3: Data Lineage

Every data file has a **traceable origin**:

```
data/raw/ (FASTQ)                    ← Source: Sequencing facility
       ↓  Cell Ranger
data/counts/ (count matrices)        ← Source: Alignment pipeline
       ↓  01_scrna_pipeline.py
analysis/clustering/ (.h5ad)         ← Source: QC + normalization + clustering
       ↓
analysis/de/ (.csv)                  ← Source: Differential expression
       ↓
analysis/enrichment/                 ← Source: Pathway analysis
       ↓
analysis/figures/ (.pdf)             ← Source: Visualization suite
```

**Golden rule**: Downstream outputs can ALWAYS be regenerated. Raw data CANNOT.

---

## Design Pattern 4: Dual-Language Support

| Aspect | Python (Scanpy) | R (Seurat) |
|--------|-----------------|------------|
| Speed | Faster for large datasets | Slower but feature-rich |
| DE analysis | Basic (Wilcoxon) | Gold standard (DESeq2) |
| Dashboard | FastAPI backend | Shiny alternative |
| Reviewers | Accepted | Often preferred |
| Our use | Primary pipeline | Validation + DESeq2 |

---

## Design Pattern 5: Pipeline Assembly Line

```
generate_synthetic_data.py   → data/synthetic/
          ↓
01_scrna_analysis_pipeline.py → analysis/clustering/, analysis/de/
          ↓
02_visualization_suite.py    → analysis/figures/
          ↓
prep_dashboard_data.py       → dashboard-ready data
          ↓
dashboard/ (FastAPI + React) → interactive web UI
```

Each step is **independently re-runnable**.

---

## Security & Data Safety

### Three Rules

1. **`data/raw/` = READ-ONLY** — Raw FASTQ is irreplaceable
2. **No files >50MB in Git** — `.gitignore` excludes `.h5ad`, `.rds`, data dirs
3. **No secrets in code** — No API keys, no patient IDs, no credentials

### What .gitignore Excludes

```
.venv/              # Recreatable from requirements.txt
node_modules/       # Recreatable from package.json
*.h5ad              # Too large for Git
*.rds               # Too large for Git
data/raw/           # Irreplaceable source data
data/counts/        # Large processed files
.env                # Credentials
```

---

## The AI Agent Architecture (Unique Feature)

```
                    orchestrator
                    (plan & route)
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  data-wrangler    qc-analyst       scrna-analyst
  (import data)    (filtering)      (clustering)
        │                │                │
        ▼                ▼                ▼
   de-analyst      pathway-explorer  visualization
   (DE genes)      (GO/KEGG)         (figures)
```

Each agent has:
- A defined role (`.github/agents/*.agent.md`)
- Domain knowledge (`skills/*.md`)
- Handoff rules (who to delegate to next)

---

## Interview Q&A

### Q: "Walk me through your project architecture."

> "The project follows layered separation of concerns. Raw data is immutable in `data/raw/`. All parameters live in `configs/analysis_config.yaml` — nothing hardcoded. Scripts execute in numbered order, each producing outputs in `analysis/` subdirectories. The interactive dashboard has a FastAPI backend serving REST endpoints and a React frontend for visualization. Everything is Git-tracked with .gitignore excluding large data files."

### Q: "Why separate configs from code?"

> "Config-driven design lets me change any biological parameter — QC thresholds, gene signatures, clustering resolution — without modifying pipeline code. I tried clustering at four different resolutions by changing one YAML line. It also makes the analysis transparent and reproducible."

### Q: "How do you ensure reproducibility?"

> "Four mechanisms: (1) Fixed seeds (`random_state=42`) in every stochastic step. (2) Config file for all parameters. (3) Environment files specifying exact package versions. (4) Immutable raw data. Anyone can clone the repo and reproduce every result."

---

## Self-Check Questions

1. **Why is `data/raw/` read-only?** → Raw FASTQ is irreplaceable lab work
2. **Where do all parameters live?** → `configs/analysis_config.yaml`
3. **What's the script execution order?** → generate → 01_pipeline → 02_viz → prep_dashboard
4. **Why both Python and R?** → Python for speed/dashboard, R for DESeq2/reviewer confidence
5. **What does config-driven mean?** → Parameters read from YAML, not hardcoded
6. **Name 6 analysis subdirectories** → qc, clustering, de, enrichment, figures, trajectory
7. **Why YAML over JSON?** → Supports comments, more human-readable
8. **What does .gitignore exclude?** → Large files, environments, credentials, raw data
9. **How does the dashboard communicate?** → REST API (FastAPI) → JSON → React frontend
10. **What's the golden rule of data lineage?** → Downstream = regeneratable; raw = irreplaceable

---

**Next**: [Day 5 — Technology Stack Deep Dive](Day_05_Technology_Stack.md)
# Day 4: Project Architecture — How Everything Is Organized

> **Series**: 30-Day Interview Preparation Guide for scRNA-seq Wound Healing Project
> **Time**: ~2.5 hours of focused reading
> **Prerequisites**: Day 1 (Project Overview), Day 2 (scRNA-seq Technology), Day 3 (Wound Healing Biology)
> **Goal**: After today, you can explain exactly how this project is structured, why every folder exists, and how design decisions make the whole system maintainable, reproducible, and interview-ready.

---

## Why Architecture Matters

On Day 1 you learned *what* the project does. On Day 2 you learned *how* scRNA-seq works. On Day 3 you learned the *biology*. Today we zoom out and look at the **engineering**: how is the entire project organized on disk, and why?

### Even solo developers need architecture

You might think: "I am the only person working on this. Why does folder structure matter?" Three reasons:

1. **Future you is a different person.** Six months from now, you will open this project and need to find a specific analysis result. If everything is dumped in one folder, you will waste hours. If it is organized, you find it in seconds.

2. **Reproducibility demands structure.** A reviewer asks: "How did you generate Figure 3?" You need to trace the path from raw data → processing script → output figure. Good architecture makes that path visible.

3. **Interviews test this.** When you say "I built a complete scRNA-seq pipeline," the interviewer will ask: "Walk me through how you organized it." A clear, principled answer — with reasoning for each decision — separates a junior developer from a senior one.

### What bad architecture looks like

Imagine a project that looks like this:

```
my_project/
├── analysis.py
├── analysis_v2.py
├── analysis_final.py
├── analysis_FINAL_FINAL.py
├── data.csv
├── output.csv
├── output_old.csv
├── figure1.png
├── figure1_fixed.png
├── notes.txt
├── random_test.R
└── config_backup.yaml
```

This is the "it works on my machine" disaster. Nobody — including the person who created it — can tell what is current, what is obsolete, what depends on what, or where to find anything.

### What good architecture looks like

Our project uses a principled structure where:
- Every folder has one clear purpose
- Input data is separated from output results
- Code is separated from configuration
- Nothing is duplicated without reason
- The flow from raw data → final figures is traceable

Let's walk through every piece.

---

## 1. The Directory Structure — Explained

Here is the full directory tree for our project. Every single folder and key file is explained below.

```
scRNA_seq/
├── AGENTS.md                    ← AI agent directory (who does what)
├── PROJECT.md                   ← Project state tracker
├── README.md                    ← Project introduction
├── requirements.txt             ← Python package list
│
├── configs/                     ← ALL parameters in one place
│   ├── analysis_config.yaml     ← QC thresholds, gene lists, clustering params
│   └── conda_envs/
│       └── scrna_wound_healing.yml  ← Conda environment definition
│
├── data/                        ← DATA: organized by processing stage
│   ├── raw/                     ← 🔒 READ-ONLY: FASTQ files
│   ├── synthetic/               ← Generated test data
│   ├── counts/                  ← Count matrices (10X output)
│   ├── metadata/                ← Sample sheets, GEO metadata
│   └── references/              ← Genome refs, dataset catalogs
│
├── scripts/                     ← CODE: organized by language
│   ├── python/                  ← Scanpy pipeline scripts
│   │   ├── generate_synthetic_data.py
│   │   ├── 00_download_geo_data.py
│   │   ├── 01_scrna_analysis_pipeline.py
│   │   ├── 02_visualization_suite.py
│   │   └── prep_dashboard_data.py
│   ├── R/                       ← Seurat alternative pipeline
│   │   ├── generate_synthetic_seurat.R
│   │   └── 01_seurat_analysis.R
│   └── utils/                   ← Shared helpers
│
├── analysis/                    ← OUTPUT: organized by analysis type
│   ├── qc/                      ← QC metrics and plots
│   ├── clustering/              ← Processed AnnData/Seurat objects
│   ├── de/                      ← Differential expression results
│   ├── enrichment/              ← GO/KEGG/GSEA results
│   ├── figures/                 ← Publication figures
│   └── trajectory/              ← Pseudotime, RNA velocity
│
├── dashboard/                   ← INTERACTIVE WEB APP
│   ├── backend/                 ← FastAPI (Python REST API)
│   │   └── app/
│   │       ├── main.py          ← API entry point
│   │       ├── routers/         ← Endpoint modules
│   │       └── services/        ← Data loading logic
│   └── frontend/                ← React + TypeScript UI
│       └── src/
│           ├── App.tsx          ← Main app with routing
│           ├── components/      ← Reusable UI components
│           ├── pages/           ← Page-level views
│           └── lib/             ← API client, utilities
│
├── docs/                        ← DOCUMENTATION
│   ├── learning/                ← This learning guide (you are here!)
│   ├── methods/                 ← Paper methods sections
│   └── protocols/               ← Lab protocols
│
├── reports/                     ← Generated reports (Quarto)
├── logs/                        ← Pipeline run logs
├── templates/                   ← 🔒 Reference templates (copy before editing)
│
└── .github/                     ← GITHUB + AI CONFIGURATION
    ├── copilot-instructions.md  ← Always-on AI rules
    ├── agents/                  ← VS Code Copilot agent definitions
    ├── skills/                  ← Domain knowledge for AI agents
    ├── instructions/            ← Coding standard rules
    └── workflows/               ← CI/CD (lint, test)
```

That is a lot of folders. Let's go through them one category at a time.

---

## 2. Root-Level Files

These are the files sitting at the very top level of the project. Think of them as the "front door" — the first things a visitor sees.

### `README.md`
**What**: The project introduction page. If someone visits the GitHub repository, this is the first thing they read.
**Contains**: Project title, description, how to set up the environment, how to run the pipeline.
**Analogy**: The cover page of a report.

### `requirements.txt`
**What**: A plain text list of every Python package the project needs, with version numbers.
**Example content**:
```
scanpy==1.10.4
anndata==0.11.3
pandas==2.2.3
matplotlib==3.10.1
```
**Why it matters**: If you share this project, someone else can run `pip install -r requirements.txt` and get the exact same packages. Without it, they have to guess which packages you used and hope the versions are compatible.
**Analogy**: A recipe's ingredient list with exact measurements. "flour" is not enough — you need "200g all-purpose flour."

### `AGENTS.md`
**What**: A directory of AI agents configured for this project. Each agent has a specific role (QC analyst, visualization specialist, etc.).
**Why it is at the root**: It is always loaded by VS Code Copilot as context. Placing it at the root ensures it is discovered automatically.
**Non-IT explanation**: Think of it as an organizational chart for your AI assistants — which "person" handles which task.

### `PROJECT.md`
**What**: A living document that tracks the current state of the project — what has been done, what is in progress, what is next.
**Analogy**: A project status board on a wall. Updated regularly.

---

## 3. The `configs/` Directory — The Control Panel

```
configs/
├── analysis_config.yaml         ← The brain of the pipeline
└── conda_envs/
    └── scrna_wound_healing.yml  ← Environment recipe
```

### `analysis_config.yaml` — The Central Nervous System

This is one of the most important files in the entire project. It contains **every parameter** used in the analysis, in one place. Here is what each section does:

#### Project identity
```yaml
project:
  name: "Tissue Fluidity in Wound Healing"
  pi: "Rahul M Sarate"
  organism: "Mus musculus"
  genome_build: "GRCm39 (mm39)"
  annotation: "GENCODE vM33"
```
**Why**: Documents what organism, genome build, and annotation version we use. If a reviewer asks "which genome build?", the answer is here — not buried in a script.

#### Experimental design
```yaml
experimental_design:
  conditions:
    - control       # Homeostatic skin
    - wound_3d      # Inflammatory phase
    - wound_7d      # Proliferative phase
    - wound_14d     # Remodeling phase
  replicates_per_condition: 2
  total_samples: 8
  library_type: "10X Chromium v3 (3' gene expression)"
  sequencing: "Illumina NovaSeq 6000, 28+90 bp paired-end"
```
**Why**: Anyone reading this knows exactly what the experiment looks like — four conditions, two replicates each, eight samples total. No guessing.

#### QC thresholds
```yaml
qc_thresholds:
  min_genes_per_cell: 200
  max_genes_per_cell: 5000
  min_counts_per_cell: 500
  max_percent_mt: 15
  min_cells_per_gene: 3
  doublet_rate: 0.05
```
**Why**: These numbers decide which cells pass quality control. By putting them here, you can change the threshold (say, from 15% to 20% mitochondrial) in ONE file, without hunting through five different scripts. This is the **config-driven** philosophy explained in detail below.

#### Clustering parameters
```yaml
clustering:
  algorithm: "Leiden"
  resolutions: [0.4, 0.6, 0.8, 1.0]
  default_resolution: 0.8
  n_neighbors: 15
  n_pcs: 30
```
**Why**: Clustering is where we group similar cells together. These parameters control how many groups we get. Different resolutions give different numbers of clusters. We try several and pick the one that makes biological sense.

#### Differential expression
```yaml
differential_expression:
  method: "pseudobulk_DESeq2"
  alternative: "MAST"
  significance:
    padj_threshold: 0.05
    log2fc_threshold: 1.0
  shrinkage: "ashr"
```
**Why**: These are the rules for declaring a gene "significantly changed." `padj < 0.05` means less than 5% chance the result is a false positive. `|log2FC| > 1.0` means the gene must change by at least 2-fold. These are standard thresholds in the field, but having them in config means they can be adjusted without editing code.

#### Tissue fluidity gene signatures
```yaml
tissue_fluidity_signatures:
  EMT:
    genes: [Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2]
  ECM_remodeling:
    genes: [Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2]
  Cell_migration:
    genes: [Rac1, Cdc42, RhoA, Itgb1, Itga6, Cxcl12, Cxcr4]
  Mechanotransduction:
    genes: [Yap1, Wwtr1, Piezo1, Trpv4, Lats1, Lats2]
  Wound_signals:
    genes: [Tgfb1, Tgfb2, Tgfb3, Pdgfa, Pdgfb, Fgf2, Vegfa, Wnt5a]
```
**Why**: These are the core gene sets of the entire project (you learned what each does on Day 3). By listing them in config, every script that needs them reads from the same source. If you add a gene to a signature, you change it once and all scripts pick it up.

#### Cell type markers
```yaml
cell_type_markers:
  Basal_Keratinocyte: [Krt14, Krt5, Tp63, Itga6]
  Diff_Keratinocyte: [Krt10, Krt1, Ivl, Lor]
  Fibroblast: [Col1a1, Col3a1, Dcn, Pdgfra]
  Myofibroblast: [Acta2, Tagln, Cnn1, Postn]
  Macrophage: [Cd68, Adgre1, Csf1r, Mrc1]
  Neutrophil: [S100a8, S100a9, Ly6g]
  T_Cell: [Cd3d, Cd3e, Cd4, Cd8a]
  Endothelial: [Pecam1, Cdh5, Kdr]
  Hair_Follicle_SC: [Sox9, Lgr5, Cd34, Lhx2]
  Melanocyte: [Dct, Tyrp1, Pmel, Mitf]
```
**Why**: These are the genes that identify each cell type — the "name tags" for cells. When the clustering algorithm groups cells, we look at these markers to determine which group is which cell type. Having all 10 cell types and their markers in one place is essential for reproducibility.

### `conda_envs/scrna_wound_healing.yml`
**What**: A YAML file that defines the complete conda environment — every package, every version, including compiled C libraries.
**Why separate from requirements.txt?**: `requirements.txt` is for `pip` (Python-only packages). The conda YAML also handles non-Python dependencies like C compilers and system libraries that Scanpy needs under the hood.
**Analogy**: `requirements.txt` is a grocery list. The conda YAML is the entire kitchen setup — appliances, utensils, AND ingredients.

---

## 4. The `data/` Directory — Raw Materials

```
data/
├── raw/          ← 🔒 READ-ONLY: Original FASTQ files
├── synthetic/    ← Generated test data
├── counts/       ← Count matrices from Cell Ranger
├── metadata/     ← Sample information
└── references/   ← Genome references, dataset catalogs
```

This directory holds all **input** data. It is organized by the stage of processing.

### `data/raw/` — The Untouchable Vault

**What goes here**: Original FASTQ files — the raw output from the sequencing machine. These are the "digital negatives" of the experiment.

**Rule**: **NEVER modify, delete, or overwrite anything in this folder.** This is the single most important rule in the entire project.

**Why?** Raw data is **irreplaceable**. Each FASTQ file represents months of laboratory work — mice had to be bred, surgeries performed, cells isolated, libraries prepared, and sequencing run. If you accidentally corrupt a FASTQ file, you cannot re-do the experiment without repeating all of that. The cost could be thousands of euros and months of time.

**Analogy**: A photographer's original film negatives. You can print and reprint photos from negatives. You can crop, adjust brightness, add filters. But if you destroy the negatives, you can never recover the original image. `data/raw/` is the negative archive.

**How we enforce it**: The `.gitignore` excludes `data/raw/**/*.fastq.gz` so these files are never committed to Git. Project instructions mark it as READ-ONLY. AI agents are configured to refuse any operation that modifies this folder.

### `data/synthetic/` — The Test Kitchen

**What goes here**: Fake data that we generate ourselves for testing. Files like `synthetic_counts_matrix.csv` and `synthetic_counts.h5ad`.

**Why?**: Real scRNA-seq data files are very large (gigabytes). When you are developing a new script or testing a change, you do not want to wait 30 minutes for the processing to finish. Synthetic data is small, fast, and has known properties — so you can verify that your code is working correctly.

**Analogy**: A car manufacturer tests crash safety on dummies, not on people. Synthetic data is our crash test dummy.

### `data/counts/` — The Processed Ingredients

**What goes here**: Count matrices — the output of Cell Ranger (the 10X Genomics alignment software). These are tables where rows are genes, columns are cells, and values are "how many times gene X was detected in cell Y."

**Why separate from raw?**: FASTQ files are raw sequences (text). Count matrices are the result of aligning those sequences to a genome and counting gene hits. This is a one-directional transformation: counts come FROM raw data, but they are not raw data themselves.

**Contains**: Subdirectories per GEO dataset (e.g., `GSE234269/`, `GSE159827/`) with `.h5ad` files (AnnData format — the standard for Scanpy).

### `data/metadata/` — The Sample Sheet

**What goes here**: Information ABOUT the samples — which sample belongs to which condition, which replicate, which GEO accession number.

**Example**: `geo_sample_metadata.csv` might look like:
```
sample_id,condition,replicate,geo_accession
S1,control,rep1,GSM7373311
S2,control,rep2,GSM7373312
S3,wound_3d,rep1,GSM7373313
...
```

**Why**: Scripts need to know which sample is "wound_3d replicate 1." This file provides that mapping.

### `data/references/` — The Reference Library

**What goes here**: Genome reference files and dataset catalogs. For example, `geo_dataset_catalog.json` lists all GEO datasets relevant to our research.

**Why**: We need genome annotation to map genes to coordinates. Reference files are shared resources — they are not experiment-specific, but analysis-essential.

---

## 5. The `scripts/` Directory — The Recipe Book

```
scripts/
├── python/                  ← Scanpy pipeline
│   ├── generate_synthetic_data.py
│   ├── 00_download_geo_data.py
│   ├── 01_scrna_analysis_pipeline.py
│   ├── 02_visualization_suite.py
│   └── prep_dashboard_data.py
├── R/                       ← Seurat pipeline
│   ├── generate_synthetic_seurat.R
│   └── 01_seurat_analysis.R
└── utils/                   ← Shared helper functions
```

### Why scripts are numbered

Notice the numbering: `00_`, `01_`, `02_`. This is not random. The numbers tell you the **execution order**:

1. `00_download_geo_data.py` — Download raw data from GEO databases
2. `01_scrna_analysis_pipeline.py` — Run the full analysis (QC → normalization → clustering → DE)
3. `02_visualization_suite.py` — Create publication-quality figures from results

You run them in order. Script 02 needs the outputs of script 01. Script 01 needs the data that script 00 downloaded. This is a **pipeline** — a chain where each link depends on the previous one.

**Analogy**: A cooking recipe with steps. Step 1: prep ingredients. Step 2: cook the dish. Step 3: plate and photograph. You cannot photograph a dish you have not cooked.

### `generate_synthetic_data.py` — No number prefix

This script does not have a number because it is not part of the main pipeline. It generates fake test data for development purposes. You run it when you need test data, not as part of the production workflow.

### `prep_dashboard_data.py` — The bridge to the web app

This script takes the analysis outputs (`.h5ad` files, CSV tables) and reformats them into the JSON and CSV files that the web dashboard needs. It is the bridge between the "analysis world" and the "web app world."

### `scripts/R/` — The alternative pipeline

The R scripts do much the same analysis as the Python scripts, but using the Seurat library instead of Scanpy. Why have both? This is explained in the "Dual-Language Support" section below.

### `scripts/utils/` — Shared helpers

Utility functions used by multiple scripts. By putting shared code here, we avoid duplicating the same function in three different scripts.

---

## 6. The `analysis/` Directory — The Display Case

```
analysis/
├── qc/           ← Quality control outputs
├── clustering/   ← Processed data objects
├── de/           ← Differential expression tables
├── enrichment/   ← Pathway analysis results
├── figures/      ← Publication-ready figures
└── trajectory/   ← Pseudotime and velocity
```

This is where ALL results go. Every script writes its output here — never back into `data/`.

### Why each subfolder exists

| Subfolder | What goes here | File types | Example |
|-----------|---------------|------------|---------|
| `qc/` | QC metrics, filtering stats | `.csv`, `.png` | `qc_summary.csv` — cells before/after filtering |
| `clustering/` | Processed AnnData/Seurat objects with cluster labels | `.h5ad`, `.rds` | `wound_adata.h5ad` — 30,000 cells with types assigned |
| `de/` | Differential expression results | `.csv` | `wound_7d_vs_control.csv` — gene, log2FC, padj |
| `enrichment/` | GO/KEGG/GSEA pathway analysis | `.csv`, `.pdf` | GO terms enriched in fibroblast genes |
| `figures/` | Publication-ready figures | `.pdf`, `.png` | UMAP plots, volcano plots, heatmaps |
| `trajectory/` | Pseudotime analysis, RNA velocity | `.h5ad`, `.csv` | Cell differentiation trajectories |

### The critical rule: inputs and outputs never mix

Notice that all input data is in `data/` and all output results are in `analysis/`. They never share a folder. This means:
- You can delete everything in `analysis/` and regenerate it by re-running the pipeline
- You can NEVER delete `data/raw/` — it is the irreplaceable source
- The flow is always: `data/ → scripts/ → analysis/`

---

## 7. The `dashboard/` Directory — The Interactive Display

```
dashboard/
├── backend/                ← FastAPI server (Python)
│   ├── requirements.txt    ← Backend-specific packages
│   └── app/
│       ├── main.py         ← API entry point
│       ├── config.py       ← Dashboard configuration
│       ├── routers/        ← URL endpoint handlers
│       │   ├── umap.py     ← /api/umap endpoint
│       │   ├── genes.py    ← /api/genes endpoint
│       │   ├── de.py       ← /api/de endpoint
│       │   ├── qc.py       ← /api/qc endpoint
│       │   ├── cell_types.py
│       │   └── fluidity.py
│       └── services/
│           └── data_loader.py  ← Loads .h5ad and CSV files
│
└── frontend/               ← React + TypeScript UI
    ├── package.json        ← Frontend package list
    ├── index.html          ← Entry HTML page
    ├── vite.config.ts      ← Build tool config
    └── src/
        ├── App.tsx         ← Main application (routing)
        ├── main.tsx        ← React entry point
        ├── components/     ← Reusable UI building blocks
        │   ├── UMAPPlot.tsx
        │   ├── VolcanoPlot.tsx
        │   ├── GeneSearch.tsx
        │   ├── FluidityPanel.tsx
        │   └── ProportionChart.tsx
        ├── pages/          ← Full-page views
        │   ├── DEResults.tsx
        │   └── FluidityDash.tsx
        └── lib/            ← Shared utilities
            ├── api.ts      ← API client functions
            └── colors.ts   ← Color palette definitions
```

### What is a full-stack web application?

The dashboard is a web application that lets you interactively explore the analysis results through a browser. It has two parts:

**Backend (FastAPI)**: A Python server that reads the processed data files (`.h5ad`, `.csv`) and serves them as JSON over HTTP. Think of it as a waiter in a restaurant — it takes requests ("give me the UMAP coordinates") and delivers data.

**Frontend (React + TypeScript)**: A browser-based interface that displays interactive plots — UMAP scatter plots, volcano plots, gene expression overlays. Think of it as the dining table where the food is presented.

**How they talk**: The frontend sends HTTP requests to the backend API (e.g., `GET /api/umap`), the backend reads the data, and sends back JSON. The frontend renders that JSON as a plot.

```
[Browser]  ──HTTP request──►  [FastAPI Backend]  ──reads──►  [.h5ad / .csv files]
           ◄──JSON response──                    
```

### Why the dashboard exists

Looking at static PDF figures is fine for a paper, but during analysis you want to **interact** — zoom into a UMAP region, search for a gene, compare conditions dynamically. The dashboard provides that interactivity.

**Interview value**: Building a full-stack dashboard shows that you can go beyond analysis scripts. You understand APIs, frontend frameworks, and data serving — skills valued in both academia and industry.

---

## 8. The `docs/` Directory — Human Documentation

```
docs/
├── learning/          ← This 30-day interview prep guide
├── methods/           ← Methods sections for the manuscript
├── protocols/         ← Lab protocols and standard operating procedures
├── meeting-notes/     ← Meeting notes and decisions
└── research-paradigms/ ← Literature on new approaches
```

Documentation aimed at **humans** — you, your PI, reviewers, collaborators. This is separate from `.github/` which is aimed at machines (CI/CD, AI agents).

---

## 9. The `.github/` Directory — Machine Documentation

```
.github/
├── copilot-instructions.md    ← Rules loaded by VS Code Copilot on every conversation
├── agents/                    ← AI agent definitions (.agent.md files)
├── skills/                    ← Domain knowledge files (SKILL.md per topic)
├── instructions/              ← Coding standard rules (.instructions.md)
├── workflows/                 ← CI/CD pipeline definitions (GitHub Actions)
├── prompts/                   ← Reusable prompt templates
├── CODEOWNERS                 ← Who reviews which files
└── pull_request_template.md   ← PR checklist template
```

This directory is special. GitHub and VS Code Copilot automatically discover files here. Let's explain each:

### `copilot-instructions.md`
Loaded automatically in every Copilot conversation. Contains project identity, coding conventions, data safety rules, and gene nomenclature rules (e.g., mouse genes like `Krt14`, not human `KRT14`). Think of it as a permanent briefing sheet for the AI.

### `agents/`
Each `.agent.md` file defines a specialized AI agent — its role, what it can do, and who it hands off to. For example, `qc-analyst.agent.md` defines an agent that only handles quality control tasks.

### `skills/`
Each skill folder contains a `SKILL.md` with domain knowledge. For example, `skills/tissue-fluidity/SKILL.md` teaches the AI about the five fluidity gene signatures. Skills are like reference manuals the AI consults when needed.

### `instructions/`
Coding standard rules applied automatically to matching file types. For example, `python-standards.instructions.md` applies to all `*.py` files and enforces conventions like snake_case naming and type hints.

### `workflows/`
GitHub Actions CI/CD definitions. These run automatically when you push code — linting, testing, etc.

---

## 10. Supporting Directories

### `reports/`
Generated reports in Quarto (`.qmd`) or R Markdown format. These combine code, narrative, and figures into a single reproducible document — like a living lab notebook.

### `logs/`
Pipeline run logs and session logs. When a script runs, it can write a timestamped log here for debugging later.

### `templates/`
Reference templates (e.g., `sample_sheet_template.csv`). These are READ-ONLY. If you need to use one, **copy it first**, then edit the copy. Never modify the original template.

---

## 11. Design Pattern: Separation of Concerns

Now that you have seen every folder, let's step back and understand the **design philosophy** behind this structure. The overarching principle is **separation of concerns** — every category of "thing" gets its own home.

### Input vs Output

```
data/    ← INPUT (raw materials)
analysis/ ← OUTPUT (finished products)
```

**Why separate them?**
- **Deletability**: You can delete the entire `analysis/` folder and regenerate it. You can NEVER delete `data/raw/`.
- **Traceability**: When you see a file in `analysis/de/wound_7d_vs_control.csv`, you know it is a result, not source data. There is no ambiguity.
- **Size management**: `data/` holds the large binary files excluded from Git. `analysis/` holds smaller results that might be committed (or not, depending on size).

### Code vs Config

```
scripts/ ← CODE (logic: what to do)
configs/ ← CONFIG (parameters: how to do it)
```

**Why separate them?**
- **Change without risk**: Changing a QC threshold from 15% to 20% mitochondrial should not require editing analysis code. You change one number in `analysis_config.yaml`.
- **Sharing parameters**: Three scripts all need the same gene list. If it is in config, they all read from the same source. If it is hardcoded, you have to update three scripts and risk inconsistency.
- **Auditability**: A reviewer can look at `analysis_config.yaml` and see every parameter used in the analysis, in one place, without reading any code.

### Human docs vs Machine docs

```
docs/    ← For humans (methods sections, protocols, learning guides)
.github/ ← For machines (AI instructions, CI/CD, coding standards)
```

**Why separate them?**
- Different audiences, different formats. Humans need narrative explanation. CI/CD needs YAML syntax. AI agents need structured instructions.
- `.github/` is a GitHub convention — GitHub automatically discovers files here for Actions, Copilot, and other integrations.

### The Kitchen Analogy

This is a helpful way to explain the whole structure in an interview:

| Project folder | Kitchen equivalent | Purpose |
|---------------|-------------------|---------|
| `data/raw/` | Raw ingredients in the locked pantry | Can't be changed — you can only use them |
| `data/counts/` | Prepped ingredients on the counter | Washed, chopped, ready for cooking |
| `data/synthetic/` | Plastic food for training | Practice without wasting real ingredients |
| `configs/` | Recipe cards on the wall | All settings in one readable place |
| `scripts/` | The cook's technique knowledge | The procedures — HOW to cook |
| `analysis/` | Finished dishes on serving plates | Ready for the table (publication/review) |
| `dashboard/` | The restaurant dining room | Where guests interact with the food |
| `docs/` | The cookbook shelf | Written recipes, notes, and guides |
| `.github/` | Kitchen safety regulations | Rules posted for inspectors (CI/CD, AI) |
| `logs/` | Kitchen order tickets | Record of what was cooked and when |

---

## 12. Design Pattern: Config-Driven Analysis

### What does "config-driven" mean?

In a config-driven project, **all tunable parameters** live in a configuration file, not scattered throughout your code. Scripts read their parameters from the config file at runtime.

### The problem it solves

Imagine you hardcoded the QC threshold in three scripts:

```python
# In 01_scrna_analysis_pipeline.py
adata = adata[adata.obs['pct_counts_mt'] < 15, :]

# In generate_synthetic_data.py
mt_pct = np.random.uniform(0, 15, n_cells)

# In some_other_script.py
if row['pct_mt'] > 15:
    filter_out(row)
```

Now your PI says: "Try 20% instead." You have to:
1. Find every place "15" appears (hope you find them all)
2. Change each one
3. Pray you did not miss any
4. Pray you did not accidentally change a "15" that meant something else (like 15 PCs)

### The config-driven solution

```yaml
# configs/analysis_config.yaml
qc_thresholds:
  max_percent_mt: 15
```

```python
# In every script:
import yaml
with open('configs/analysis_config.yaml') as f:
    config = yaml.safe_load(f)

mt_threshold = config['qc_thresholds']['max_percent_mt']
adata = adata[adata.obs['pct_counts_mt'] < mt_threshold, :]
```

Now to change the threshold, you edit ONE file. Every script automatically uses the new value. Zero risk of inconsistency.

### Interview gold

When an interviewer asks "How do you handle configuration?", saying "I use a centralized YAML config that all scripts read from" demonstrates:
- You understand **Don't Repeat Yourself (DRY)** — a core software engineering principle
- You think about **maintainability** — making future changes easy
- You design for **reproducibility** — anyone can see exactly what parameters were used

---

## 13. Design Pattern: Data Lineage

Data lineage answers the question: "Where did this result come from?"

In our project, the lineage is crystal clear:

```
data/raw/                    FASTQ files (sequencer output)
    ↓  [Cell Ranger]
data/counts/                 Count matrices (genes × cells)
    ↓  [01_scrna_analysis_pipeline.py]
analysis/clustering/         Processed .h5ad with clusters + cell types
    ↓  [01_scrna_analysis_pipeline.py]
analysis/de/                 CSV files: gene, log2FC, padj
    ↓  [pathway enrichment scripts]
analysis/enrichment/         GO/KEGG/GSEA result tables
    ↓  [02_visualization_suite.py]
analysis/figures/            PDF figures (UMAP, volcano, heatmap)
```

### Why this matters

1. **Reproducibility**: If a reviewer questions a figure, you can trace it back through every processing step to the original raw data.

2. **Debugging**: If you get a strange result in `analysis/de/`, you can check the intermediate object in `analysis/clustering/` to see if the issue started earlier.

3. **Re-running**: If you change a parameter (e.g., resolution from 0.8 to 1.0), you know exactly which downstream outputs need regeneration.

### The one-way flow rule

Data flows **one direction**: `data/ → analysis/`. Never the reverse. A script in `scripts/` reads from `data/` or earlier `analysis/` outputs, and writes to `analysis/`. It never writes back to `data/`.

```
NEVER do this:

analysis/ ──writes back──► data/     ← WRONG: breaks lineage

ALWAYS do this:

data/ ──reads──► scripts/ ──writes──► analysis/   ← CORRECT: one-way flow
```

---

## 14. Design Pattern: Dual-Language Support

### Why both Python AND R?

Our project maintains parallel pipelines in both Python (Scanpy) and R (Seurat). This is unusual — most projects pick one. Here is why we support both:

### Python (Scanpy) — Our primary pipeline

**Strengths**:
- **Speed**: Scanpy processes large datasets faster than Seurat for most operations
- **Memory**: AnnData (Scanpy's data format) is more memory-efficient than Seurat objects
- **ML/DL integration**: Python is the language of machine learning, deep learning, and general programming. If you want to apply a neural network to your data, Python is the natural choice
- **Dashboard**: Our web dashboard backend is written in Python (FastAPI). Keeping the analysis in Python means no language boundary for serving data
- **Industry**: Most bioinformatics positions in industry use Python

### R (Seurat) — Our validation and specialized pipeline

**Strengths**:
- **Publishing standard**: The majority of scRNA-seq papers use Seurat. Reviewers expect Seurat-style figures and methods descriptions
- **DESeq2**: The gold-standard differential expression package is R-only. There is no Python equivalent of the same quality
- **Bioconductor ecosystem**: Thousands of biology-specific R packages for enrichment analysis, annotation, and visualization
- **Statistics**: R was designed for statistics. Complex statistical modeling is often more natural in R

### Our approach

```
Python (Scanpy)           R (Seurat)
───────────────           ──────────
Primary pipeline          Validation pipeline
Fast data processing      DESeq2 differential expression
Dashboard data source     Publication-standard figures
End-to-end capability     Specialized analyses
```

We run the primary analysis in Python. We then validate key results in R (if results agree in two independent tools, confidence is higher). We also use R for any analysis where R packages are clearly superior (DESeq2, certain enrichment tools).

### How to explain this in an interview

> "I chose to implement dual pipelines because they serve complementary purposes. Python is our workhorse — faster for large datasets and naturally integrated with our web dashboard. R is essential for pseudobulk DESeq2, which remains the gold standard for differential expression in scRNA-seq. Running both also serves as a validation strategy: if Scanpy and Seurat agree on the clusters and DE genes, we have higher confidence in our results."

---

## 15. The Pipeline as an Assembly Line

Here is how the scripts connect, step by step:

```
┌─────────────────────────────────┐
│  generate_synthetic_data.py     │  OPTIONAL: Creates fake data in data/synthetic/
│  (no number — not part of       │  for testing scripts without waiting for real data.
│   the main pipeline)            │
└───────────────┬─────────────────┘
                │ (or use real data)
                ▼
┌─────────────────────────────────┐
│  00_download_geo_data.py        │  STEP 0: Downloads raw data from GEO.
│  Reads: GEO accession numbers   │  Writes to: data/counts/
│  Writes: data/counts/*.h5ad     │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│  01_scrna_analysis_pipeline.py  │  STEP 1: The main analysis.
│  Reads: data/counts/ or         │  - QC filtering
│         data/synthetic/          │  - Normalization
│  Reads: configs/analysis_       │  - Dimensionality reduction (PCA, UMAP)
│         config.yaml              │  - Clustering (Leiden)
│  Writes: analysis/qc/           │  - Cell type annotation
│          analysis/clustering/    │  - Differential expression
│          analysis/de/            │  - Tissue fluidity scoring
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│  02_visualization_suite.py      │  STEP 2: Create figures.
│  Reads: analysis/clustering/    │  - UMAP plots (colored by type, condition)
│         analysis/de/             │  - Volcano plots (DE genes)
│  Writes: analysis/figures/       │  - Heatmaps (gene expression)
│          (PDF, 300 DPI)          │  - Dot plots (marker genes)
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│  prep_dashboard_data.py         │  STEP 3: Prepare web app data.
│  Reads: analysis/clustering/    │  Reformats analysis outputs into
│         analysis/de/             │  JSON/CSV for the dashboard API.
│  Writes: dashboard-ready files  │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│  dashboard/                     │  INTERACTIVE: Explore results in browser.
│  backend/ serves data via API   │  Browse UMAP, search genes,
│  frontend/ renders plots        │  view DE results, score fluidity.
└─────────────────────────────────┘
```

### Key point: each step depends on the previous one

You cannot visualize (step 2) before you have analyzed (step 1). You cannot analyze before you have data (step 0). This is a **linear pipeline**, not a random collection of scripts. The numbered prefixes make the order explicit.

---

## 16. Security Architecture

### Data Safety Rules — Why They Exist

Security is not just about hackers. In bioinformatics, data safety means protecting **irreplaceable experimental data** and **complying with regulations**.

#### Rule 1: `data/raw/` is READ-ONLY

**Why**: As explained above, raw FASTQ files are irreplaceable. Corrupting them costs thousands of euros and months of lab work. We enforce this through:
- Project instructions that mark the directory as READ-ONLY
- AI agent configurations that refuse write operations to this path
- Cultural convention — every developer knows this rule

#### Rule 2: No files >50MB in Git

**Why**: Git is a version control system designed for **code** (small text files). It was NEVER designed for large binary files. If you commit a 2GB `.h5ad` file:
- Every clone of the repository downloads that 2GB (even if the file was later deleted)
- Repository size balloons, making everything slow
- GitHub may reject pushes over their file size limits

**Solution**: `.gitignore` excludes large file types (`*.h5ad`, `*.rds`, `*.fastq.gz`). These files stay on your local machine (or a shared server) but are never tracked by Git.

#### Rule 3: No patient IDs or PHI (Protected Health Information)

**Why**: Even though we work with mouse data (not human patients), we follow good data protection practices. In human genomics, accidentally committing a patient ID to a public GitHub repository would violate HIPAA (US) or GDPR (EU) regulations. Fines can reach millions of euros. Practicing this discipline with mouse data means you will not make the mistake when you eventually handle human data.

**What PHI includes**: Names, dates of birth, addresses, medical record numbers, genomic identifiers that can re-identify individuals.

#### Rule 4: API keys and tokens never in code

**Why**: If you commit an API key (e.g., a GEO download token or a cloud service credential) to a public repository, bots will find it within minutes and use it to rack up charges on your cloud account, or steal data.

**Solution**: Store credentials in `.env` files (which are in `.gitignore` and never committed) or in environment variables.

### What Goes in `.gitignore` — Explained

Our `.gitignore` file excludes many types of files. Here is why for each category:

```
# LARGE DATA FILES — too big for Git
data/raw/**/*.fastq.gz      ← Raw sequencing files (GB each)
data/raw/**/*.bam            ← Aligned sequence files (GB each)
data/counts/**/*.h5ad        ← Count matrices (hundreds of MB)
analysis/clustering/*.h5ad   ← Processed objects (hundreds of MB)

# REGENERABLE OUTPUTS — can be recreated by running scripts
analysis/figures/*.pdf       ← Re-run 02_visualization_suite.py
data/synthetic/*.h5ad        ← Re-run generate_synthetic_data.py

# ENVIRONMENT FILES — recreatable from requirements.txt
.venv/                       ← Python virtual environment (hundreds of MB)
node_modules/                ← JavaScript packages (hundreds of MB)

# SENSITIVE FILES — must never be public
.env                         ← API keys, tokens, passwords

# IDE SETTINGS — personal preferences, not project code
.vscode/settings.json        ← Your editor preferences (might conflict with others)

# BUILD ARTIFACTS — temporary compilation results
__pycache__/                 ← Python bytecode cache
dist/                        ← Frontend build output
*.pyc                        ← Compiled Python files
```

**The principle**: Git should contain only things that are (a) small, (b) cannot be regenerated, and (c) are not secrets. Everything else stays out.

---

## 17. The Environment System — Why Two Ways to Install Packages

You might have noticed we have TWO ways to set up the Python environment:

### `requirements.txt` — The simple way (pip)

```
pip install -r requirements.txt
```

This installs Python packages only. Works on any system with Python installed. Simple, fast, lightweight.

**When to use**: Quick setup for development. When you only need Python packages and don't need compiled C libraries.

### `conda_envs/scrna_wound_healing.yml` — The complete way (conda)

```
conda env create -f configs/conda_envs/scrna_wound_healing.yml
```

This creates an entire isolated environment with Python, R, C compilers, and all dependencies. Heavier but more reliable.

**When to use**: Full production runs where you need everything — including packages with C extensions that are tricky to install via pip.

**Analogy**:
- `pip install -r requirements.txt` = "Install just the apps on my phone" (quick, but assumes the phone already works)
- `conda env create` = "Give me a new phone with the OS and all apps pre-configured" (slower, but guaranteed to work)

---

## 18. Interview Questions & Model Answers

### Q1: "Walk me through your project architecture."

> "The project follows a separation-of-concerns structure. Input data lives in `data/`, organized by processing stage — raw FASTQ files are read-only, count matrices are in a separate folder, and reference files have their own space. All analysis code is in `scripts/`, organized by language — Python for the primary Scanpy pipeline, R for validation and DESeq2. Every tunable parameter lives in a single YAML config file so that nothing is hardcoded. All outputs go to `analysis/`, split by analysis type — QC, clustering, differential expression, enrichment, figures, and trajectory. We also have a full-stack web dashboard in `dashboard/` for interactive exploration, and comprehensive documentation in `docs/` and `.github/`."

### Q2: "Why did you separate configs from code?"

> "Maintainability and reproducibility. If I hardcode a QC threshold in three scripts and need to change it, I have to find and update all three — and risk inconsistency. With a centralized config, I change one value in one file, and every script picks it up. It also means a reviewer can see every analysis parameter in one place, without reading through hundreds of lines of code. This follows the DRY principle — Don't Repeat Yourself."

### Q3: "How do you ensure data safety?"

> "Three layers. First, raw data in `data/raw/` is treated as strictly read-only — our project instructions, AI agent configs, and team convention all enforce this. Second, `.gitignore` prevents large binary files, credentials, and regenerable outputs from being committed. Third, we never include patient identifiers or PHI in code, commits, or prompts — even though this is mouse data, we practice the discipline required for human genomics compliance."

### Q4: "How do you handle reproducibility?"

> "Four mechanisms. First, seeds — every script sets `random_state=42` for all stochastic operations (PCA, UMAP, Leiden clustering). Second, config-driven parameters — all thresholds live in `analysis_config.yaml`, so you know exactly what was used. Third, environment pinning — `requirements.txt` and the conda YAML lock exact package versions. Fourth, data lineage — the pipeline's one-directional flow from raw data to figures means every result is traceable to its source."

### Q5: "Why this directory structure?"

> "It mirrors the scientific method: raw observations (`data/raw/`), processed data (`data/counts/`), methods (`scripts/`), parameters (`configs/`), results (`analysis/`), and publication (`docs/`, `reports/`). Each step of the pipeline maps to a folder. The structure also enforces safety — you physically cannot mix raw and processed data because they live in different directory trees. And it scales well — adding a new analysis type just means adding a new subfolder in `analysis/`, not reorganizing everything."

---

## 19. Self-Check Questions

Test yourself on today's material. Try to answer each question before looking at the answer.

### Question 1
**Why is `data/raw/` read-only?**

<details>
<summary>Answer</summary>
Raw FASTQ files are irreplaceable. They represent months of lab work (breeding mice, performing surgeries, isolating cells, sequencing). If corrupted or deleted, the experiment must be entirely repeated — costing thousands of euros and months of time. By keeping them read-only, we guarantee that any processing mistake can be recovered by re-running from the original data.
</details>

### Question 2
**What is the difference between `data/` and `analysis/`?**

<details>
<summary>Answer</summary>
`data/` holds INPUT — raw materials and intermediate processed data that feeds into scripts. `analysis/` holds OUTPUT — the results produced by running scripts. Data flows one way: `data/ → scripts/ → analysis/`. You can delete `analysis/` and regenerate it. You can never delete `data/raw/`.
</details>

### Question 3
**Why do all scripts read parameters from `analysis_config.yaml` instead of hardcoding them?**

<details>
<summary>Answer</summary>
Config-driven design ensures: (1) a single source of truth — no inconsistencies between scripts, (2) easy modification — change one number, not five scripts, (3) auditability — a reviewer sees every parameter in one file, (4) follows the DRY (Don't Repeat Yourself) principle.
</details>

### Question 4
**What does the script numbering (`00_`, `01_`, `02_`) tell you?**

<details>
<summary>Answer</summary>
Execution order. Scripts must be run in numerical sequence because each depends on the outputs of the previous one: 00 downloads data, 01 processes it, 02 visualizes the results. The numbering makes the pipeline order explicit and unambiguous.
</details>

### Question 5
**Why do we support both Python (Scanpy) and R (Seurat)?**

<details>
<summary>Answer</summary>
They have complementary strengths. Python is faster, more memory-efficient, integrates with the web dashboard, and is standard in industry. R has the gold-standard DESeq2 package for differential expression, a vast Bioconductor ecosystem, and is the publishing standard in biology journals. Running both also provides cross-validation — agreement between two independent tools increases confidence.
</details>

### Question 6
**What goes in `.gitignore` and why?**

<details>
<summary>Answer</summary>
Files excluded from Git fall into four categories: (1) large files (FASTQ, h5ad, rds) because Git is designed for small text files, (2) regenerable outputs (figures, compiled code) because they can be recreated, (3) environment directories (.venv/, node_modules/) because they are recreatable from requirements files, (4) secrets (.env files with API keys) because they must never be public.
</details>

### Question 7
**What is the role of the `dashboard/` directory?**

<details>
<summary>Answer</summary>
It contains a full-stack web application for interactive data exploration. The backend (FastAPI) reads processed analysis files and serves them as JSON over HTTP. The frontend (React + TypeScript) renders interactive plots — UMAP, volcano plots, gene search, fluidity scoring. It lets you explore results dynamically instead of only looking at static PDF figures.
</details>

### Question 8
**Explain the "kitchen analogy" for the directory structure.**

<details>
<summary>Answer</summary>
`data/raw/` = locked pantry (raw ingredients, untouchable). `data/counts/` = prepped ingredients on the counter. `configs/` = recipe cards on the wall (all parameters visible). `scripts/` = the cook's technique knowledge (procedures). `analysis/` = finished dishes on serving plates (results). `dashboard/` = the restaurant dining room (interactive guest experience). `docs/` = the cookbook shelf (written documentation). `.github/` = kitchen safety regulations (rules for inspectors/machines).
</details>

### Question 9
**What is "data lineage" and why does it matter?**

<details>
<summary>Answer</summary>
Data lineage is the ability to trace any result back through every processing step to the original raw data. It matters because: (1) reviewers may question a figure — you can show exactly how it was produced, (2) debugging — if a result looks wrong, you can check each intermediate step, (3) re-running — if you change a parameter, you know which downstream outputs are affected. Our pipeline's one-directional flow (`data/ → scripts/ → analysis/`) makes lineage explicit.
</details>

### Question 10
**Why are `docs/` and `.github/` in separate directories even though both contain documentation?**

<details>
<summary>Answer</summary>
Different audiences. `docs/` contains documentation for humans — methods sections, learning guides, protocols, meeting notes. `.github/` contains documentation for machines — AI agent instructions, CI/CD workflow definitions, coding standard rules. GitHub and VS Code Copilot automatically discover files in `.github/`, so it must follow specific conventions. Human documentation has no such constraint.
</details>

---

## Summary

Today you learned the engineering backbone of the project:

| Concept | Key Takeaway |
|---------|-------------|
| **Directory structure** | Every folder has one clear purpose; inputs, code, config, and outputs are separated |
| **Config-driven analysis** | All parameters in `analysis_config.yaml`; never hardcode |
| **Data lineage** | One-directional flow: `data/ → scripts/ → analysis/`; always traceable |
| **Data safety** | `data/raw/` is read-only; large files, secrets, and PHI stay out of Git |
| **Dual-language support** | Python for speed and dashboard; R for DESeq2 and publishing convention |
| **Pipeline order** | Numbered scripts enforce execution sequence |
| **Full-stack dashboard** | FastAPI backend + React frontend for interactive exploration |
| **Separation of concerns** | Human docs vs machine docs, code vs config, input vs output |

**Tomorrow (Day 5)**: We will dive into the Python environment and package ecosystem — what each package does, how virtual environments work, and how to explain your technology choices in an interview.