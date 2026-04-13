# Day 5: Technology Stack Deep Dive

> **Goal**: Know every tool, library, and framework in the project. Explain why each was chosen.

---

## The Full Stack at a Glance

```
┌─────────────────────────────────────────────────────────┐
│                    OUR TECH STACK                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  LANGUAGES          ANALYSIS              WEB STACK     │
│  ┌─────────┐       ┌──────────┐          ┌──────────┐  │
│  │ Python  │       │ Scanpy   │          │ FastAPI  │  │
│  │ 3.10    │       │ AnnData  │          │ (backend)│  │
│  │         │       │ pandas   │          ├──────────┤  │
│  │ R 4.4   │       │ numpy    │          │ React    │  │
│  │         │       │ scipy    │          │ TypeScript│  │
│  └─────────┘       │ sklearn  │          │ Tailwind │  │
│                    ├──────────┤          │ Plotly   │  │
│  ENVIRONMENT       │ Seurat v5│          └──────────┘  │
│  ┌─────────┐       │ DESeq2   │                        │
│  │ pip/venv│       │ ggplot2  │          INFRA          │
│  │ conda   │       └──────────┘          ┌──────────┐  │
│  └─────────┘                             │ Git/GH   │  │
│                    VISUALIZATION          │ CI/CD    │  │
│  IDE               ┌──────────┐          │ .gitignore│  │
│  ┌─────────┐       │matplotlib│          └──────────┘  │
│  │ VS Code │       │ seaborn  │                        │
│  │ Copilot │       │ Plotly   │                        │
│  └─────────┘       └──────────┘                        │
└─────────────────────────────────────────────────────────┘
```

---

## Python Libraries — Explained One by One

### Scanpy (`scanpy`) — The Heart of Our Analysis

**What it is**: The main library for single-cell RNA-seq analysis in Python.

**What it does in our project**:
| Function | Purpose | Our Script |
|----------|---------|------------|
| `sc.read_h5ad()` | Load AnnData files | Pipeline step 1 |
| `sc.pp.filter_cells()` | QC filtering | Pipeline step 2 |
| `sc.pp.normalize_total()` | Normalize counts | Pipeline step 3 |
| `sc.pp.highly_variable_genes()` | Find informative genes | Pipeline step 3 |
| `sc.tl.pca()` | Dimensionality reduction | Pipeline step 4 |
| `sc.tl.umap()` | 2D visualization embedding | Pipeline step 4 |
| `sc.tl.leiden()` | Cluster cells | Pipeline step 5 |
| `sc.tl.score_genes()` | Score gene signatures | Pipeline step 8 |
| `sc.tl.rank_genes_groups()` | Find DE genes | Pipeline step 7 |
| `sc.pl.umap()` | Plot UMAP | Visualization |
| `sc.pl.dotplot()` | Marker dotplot | Visualization |

**Why Scanpy over alternatives?**
- Faster than R/Seurat for large datasets (>100K cells)
- Python ecosystem integrates with ML, dashboard, and automation
- AnnData format is memory-efficient
- Active development by the Theis Lab (world leaders in single-cell)

### AnnData (`anndata`) — The Data Container

```
AnnData object (adata)
├── .X              → The count matrix (cells × genes)
│                     Shape: (8000, 2000) in our synthetic data
│
├── .obs            → Cell metadata (one row per cell)
│   ├── cell_type     "Fibroblast", "Macrophage", etc.
│   ├── condition     "control", "wound_3d", "wound_7d", "wound_14d"
│   ├── sample        "control_rep1", "wound_3d_rep2", etc.
│   ├── n_genes       Number of genes detected in this cell
│   ├── pct_counts_mt Mitochondrial gene percentage
│   └── leiden        Cluster assignment
│
├── .var            → Gene metadata (one row per gene)
│   ├── gene_name     "Krt14", "Col1a1", etc.
│   └── highly_variable  True/False
│
├── .obsm           → Cell embeddings
│   ├── X_pca        PCA coordinates (50 dimensions)
│   └── X_umap       UMAP coordinates (2 dimensions)
│
├── .uns            → Unstructured data
│   ├── pca          PCA variance info
│   └── leiden       Clustering parameters
│
└── .layers         → Alternative count representations
    ├── raw          Original counts
    └── normalized   Normalized counts
```

**Analogy**: AnnData is like a spreadsheet workbook:
- `.X` = the main data sheet
- `.obs` = a "cell info" sheet (rows match the main sheet)
- `.var` = a "gene info" sheet (columns match the main sheet)
- `.obsm` = extra sheets with calculated coordinates

### pandas — Data Manipulation

**What it does**: Reads/writes CSV, filters data, groups and summarizes.

**In our project**:
```python
# Load DE results
de_df = pd.read_csv('analysis/de/wound_7d_vs_control.csv')

# Filter significant genes
sig_genes = de_df[de_df['padj'] < 0.05]

# Sort by fold change
top_genes = sig_genes.sort_values('log2FC', ascending=False).head(20)
```

### NumPy — Numerical Computing

**What it does**: Fast array operations, random number generation, linear algebra.

**In our project**: Behind every matrix operation in Scanpy. Also:
```python
np.random.seed(42)  # Reproducibility
```

### scikit-learn — Machine Learning

**What it does**: PCA, clustering, preprocessing.

**In our project**: Scanpy uses sklearn internally for:
- PCA (Principal Component Analysis)
- K-nearest neighbors
- Scaling/normalization

### matplotlib + seaborn — Plotting

**What it does**: Creates all static figures.

```python
# matplotlib = low-level (full control)
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(x, y)
ax.set_title('UMAP')

# seaborn = high-level (statistical plots)
sns.boxplot(data=df, x='condition', y='fluidity_score')
```

### leidenalg — Clustering Algorithm

**What it does**: Community detection on cell neighborhood graphs.

**Why Leiden over k-means?**
- Leiden finds natural communities in the cell graph — doesn't require you to specify k
- Works on the nearest-neighbor graph (cells similar to each other are connected)
- Resolution parameter controls how many clusters: higher = more clusters

---

## R Libraries — Explained

### Seurat v5 — The R Equivalent of Scanpy

| Seurat Function | Scanpy Equivalent | What It Does |
|----------------|-------------------|--------------|
| `CreateSeuratObject()` | `sc.read_h5ad()` | Create data object |
| `NormalizeData()` | `sc.pp.normalize_total()` | Normalize |
| `FindVariableFeatures()` | `sc.pp.highly_variable_genes()` | HVG selection |
| `ScaleData()` | `sc.pp.scale()` | Scale |
| `RunPCA()` | `sc.tl.pca()` | PCA |
| `RunUMAP()` | `sc.tl.umap()` | UMAP |
| `FindClusters()` | `sc.tl.leiden()` | Cluster |
| `FindAllMarkers()` | `sc.tl.rank_genes_groups()` | DE |

### DESeq2 — Gold Standard for Differential Expression

**Why DESeq2 is special**:
- Designed for count data (RNA-seq is count data)
- Models gene expression with negative binomial distribution
- Handles small sample sizes well (we have 2 replicates per condition)
- Pseudobulk approach: aggregate single cells → per-sample → treat like bulk RNA-seq
- `ashr` shrinkage: reduces false positives by shrinking noisy fold changes

### clusterProfiler — Pathway Enrichment

**What it does**: Takes a list of DE genes → finds what biological pathways they belong to.
- GO (Gene Ontology): biological process, molecular function, cellular component
- KEGG: metabolic and signaling pathways
- GSEA: Gene Set Enrichment Analysis (ranks ALL genes, not just significant ones)

---

## Web Stack — The Dashboard

### FastAPI (Backend)

**What it is**: Modern Python web framework for building APIs.

**Why FastAPI?**
- Automatic API documentation (Swagger UI at `/docs`)
- Type validation with Pydantic
- Async support (fast)
- Python-native (same language as our analysis pipeline)

**Our API endpoints**:
```
GET /api/v1/umap          → UMAP coordinates for all cells
GET /api/v1/genes/{gene}  → Expression values for one gene  
GET /api/v1/de/{comparison}→ DE results table
GET /api/v1/fluidity      → Fluidity scores per cell
GET /api/v1/cell-types    → Cell type proportions
GET /api/v1/qc            → QC metrics summary
GET /api/v1/config        → Project configuration
```

### React + TypeScript (Frontend)

**What it is**: JavaScript framework for building interactive UIs.

**Why React?**
- Component-based: each plot is a reusable component (`UMAPPlot`, `VolcanoPlot`)
- TypeScript adds type safety (catch errors before running)
- Huge ecosystem (Plotly for interactive plots)

**Our components**:
```
App.tsx
├── Overview page      → UMAP + cell proportions + QC summary
├── GeneExplorer page  → Search any gene, see expression on UMAP
├── DEResults page     → Volcano plots, DE tables
└── FluidityDash page  → Fluidity scores across conditions
```

### Tailwind CSS — Styling

**What it is**: Utility-first CSS framework — style directly in HTML/JSX.

```jsx
// Instead of writing external CSS files:
<div className="bg-gray-900 text-white p-4 rounded">
  Dashboard
</div>
```

### Plotly — Interactive Charts

**What it is**: Library for interactive, zoomable, hoverable plots.
- Hover over a dot on UMAP → see cell type, condition, gene expression
- Zoom into specific clusters
- Download plots as PNG

---

## Environment Management

### pip + venv (Lightweight)

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

**requirements.txt** lists exact packages:
```
scanpy>=1.9
anndata>=0.10
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
fastapi>=0.104
uvicorn>=0.24
```

### conda (Full)

```bash
# Create environment from YAML
conda env create -f configs/conda_envs/scrna_wound_healing.yml

# Activate
conda activate scrna_wound_healing
```

**When to use which?**
- pip: development, quick iteration, pure-Python packages
- conda: production, compiled packages (HDF5, BLAS), reproducible environments

---

## Version Control — Git

### What Git Tracks
- All code (scripts, configs, dashboard source)
- Documentation (docs, README, AGENTS.md)
- CI/CD workflows

### What Git Does NOT Track (.gitignore)
- Data files (`.h5ad`, `.rds`, `data/raw/`)
- Environments (`.venv/`, `node_modules/`)
- Credentials (`.env`)
- IDE settings (`.vscode/`)

---

## CI/CD — GitHub Actions

Our project has automated checks:

```yaml
# .github/workflows/lint.yml
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint Python
        run: flake8 scripts/python/
      - name: Lint R
        run: lintr::lint_dir("scripts/R/")
```

**What this means**: Every time you push code, GitHub automatically checks for syntax errors and style violations.

---

## Interview Q&A

### Q: "What's your tech stack and why?"

> "Python 3.10 with Scanpy for the primary scRNA-seq pipeline — it's the fastest framework for large single-cell datasets. R with Seurat v5 and DESeq2 for differential expression validation — DESeq2 is the community gold standard for pseudobulk analysis. FastAPI + React for an interactive dashboard that lets collaborators explore the data without writing code. All configurations in YAML, versioned in Git with CI/CD."

### Q: "Why Scanpy over Seurat?"

> "Scanpy is faster for datasets over 100K cells due to its sparse matrix implementation. It also integrates natively with the Python ecosystem — our FastAPI dashboard, numpy/scipy stack, and ML tools. However, I also maintain a Seurat pipeline for reviewer confidence and to use DESeq2 which has no Python equivalent of equal quality."

### Q: "How do you handle dependencies?"

> "Two tracks: pip with a virtual environment for development speed, and conda for production with compiled dependencies. Both are pinned — requirements.txt for pip, a YAML spec for conda. This ensures any collaborator gets the exact same environment."

---

## Self-Check Questions

1. **What library does our pipeline primarily use?** → Scanpy
2. **What is AnnData?** → Data container holding count matrix + metadata + embeddings
3. **Why DESeq2 over Scanpy's built-in DE?** → DESeq2 handles pseudobulk properly, has shrinkage
4. **What does Leiden clustering do?** → Finds communities in cell nearest-neighbor graph
5. **Name 3 FastAPI endpoints we serve** → /umap, /genes/{gene}, /de/{comparison}
6. **Why React for the frontend?** → Component-based, TypeScript safety, Plotly integration
7. **What's in requirements.txt?** → Python package names and minimum versions
8. **Why both pip and conda?** → pip for speed/development, conda for compiled packages
9. **What does CI/CD do in our project?** → Automatically lints Python/R code on every push
10. **What's the difference between matplotlib and Plotly?** → matplotlib = static publication figures, Plotly = interactive web plots

---

**Next**: [Day 6 — Data: From GEO to Count Matrix](Day_06_Data_Journey.md)
