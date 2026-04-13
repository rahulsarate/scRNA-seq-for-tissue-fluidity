# Day 6: Data Journey — From GEO to Count Matrix

> **Goal**: Understand how raw sequencing data becomes the count matrix we analyze. Know data formats, sources, and our synthetic data strategy.

---

## The Data Landscape

```
                    THE DATA JOURNEY
                    
Sequencing Facility          Public Database
      │                           │
      ▼                           ▼
  FASTQ files              GEO (NCBI)
  (raw reads)              ┌─────────────┐
      │                    │ GSE234269   │ ← primary
      ▼                    │ GSE159827   │ ← validation
  Cell Ranger              │ GSE188432   │ ← comparison
  (alignment)              └──────┬──────┘
      │                           │
      ▼                           ▼
  Count Matrix            Downloaded .h5ad
  (cells × genes)         (already processed)
      │                           │
      └───────────┬───────────────┘
                  ▼
          Our Analysis Pipeline
```

---

## GEO — Where Bioinformatics Data Lives

### What is GEO?
- **Gene Expression Omnibus** — NCBI's public database for genomics data
- Every published study must deposit its data here (journal requirement)
- Accession numbers: GSE (series) → GSM (samples) → SRR (runs)

### Our Three Datasets

| Dataset | GEO ID | Description | Role in Project |
|---------|--------|-------------|-----------------|
| Wound healing | GSE234269 | Mouse skin at 4 wound timepoints | **Primary dataset** |
| Tissue mechanics | GSE159827 | Mechanical properties of wound tissue | Validation |
| Aged wounds | GSE188432 | Wound healing in old vs young mice | Comparison |

### What We Download from GEO

```
data/counts/GSE234269/
├── GSE234269_wound_3d.h5ad          ← Processed AnnData
└── extracted/
    ├── GSM_control_rep1/
    │   ├── matrix.mtx.gz            ← Sparse count matrix
    │   ├── barcodes.tsv.gz          ← Cell barcodes
    │   └── features.tsv.gz          ← Gene names
    └── GSM_wound_3d_rep1/
        └── ...
```

### The Three File Formats from 10X

1. **matrix.mtx** — The counts (sparse format: only stores non-zero values)
2. **barcodes.tsv** — List of cell barcodes (row labels)
3. **features.tsv** — List of gene names (column labels)

```
# Example: what the data actually looks like

barcodes.tsv:          features.tsv:        matrix.mtx:
AAACCTGCAGCTGGTT-1     Krt14                cell 1, gene 3, count=15
AAACGGGAGTCGATAA-1     Col1a1               cell 1, gene 7, count=8
AAACGGGCATTTCACT-1     Vim                  cell 2, gene 1, count=22
...                    ...                  ...
```

---

## Synthetic Data — Why and How

### Why Generate Fake Data?

**Critical concept**: Before running on real data, test your entire pipeline on simulated data.

| Benefit | Explanation |
|---------|-------------|
| Pipeline validation | Catch bugs without wasting expensive compute on real data |
| Ground truth | We KNOW the cell types (because we assigned them) — can verify annotation accuracy |
| Speed | 8,000 synthetic cells vs 50,000+ real cells = faster debugging |
| Safety | No risk of corrupting real data during development |
| Reproducibility | Same seed (42) = same synthetic data every time |

### How Our Synthetic Data Generator Works

File: `scripts/python/generate_synthetic_data.py`

**Step 1: Define Cell Proportions Per Condition**

```python
# What we encode in our synthetic data:
CELL_TYPE_PROPORTIONS = {
    'Basal_Keratinocyte': {
        'control': 0.25,    # 25% in healthy skin
        'wound_3d': 0.10,   # Drops during inflammation
        'wound_7d': 0.20,   # Recovers during proliferation
        'wound_14d': 0.22   # Nearly back to normal
    },
    'Macrophage': {
        'control': 0.08,    # Low in healthy skin
        'wound_3d': 0.25,   # SURGE during inflammation
        'wound_7d': 0.12,   # Tapering off
        'wound_14d': 0.10   # Resolving
    },
    # ... 10 cell types total
}
```

These proportions reflect REAL biology — macrophages flood in at day 3, myofibroblasts peak at day 7, etc.

**Step 2: Generate Realistic Gene Expression**

```python
# Gene expression follows negative binomial distribution
# (most genes lowly expressed, few highly expressed)
counts = np.random.negative_binomial(n=r, p=p, size=n_cells)
```

Why **negative binomial**? Because real scRNA-seq data has:
- Many zeros (most genes not expressed in any given cell)
- Overdispersion (more variance than a Poisson distribution)
- Negative binomial captures both properties

**Step 3: Add Cell-Type Signatures**

```python
# Fibroblasts get high Col1a1, Col3a1, Dcn
# Macrophages get high Cd68, Adgre1, Csf1r
for cell_type, markers in MARKER_GENES.items():
    boost = np.random.poisson(lam=15) + 10
    counts[cell_idx, gene_idx] += boost
```

**Step 4: Add Tissue Fluidity Signatures with Wound-Phase Effects**

```python
# EMT genes upregulated 3x at wound_7d (peak fluidity)
FLUIDITY_CONDITION_EFFECTS = {
    'emt_markers': {
        'control': 1.0,    # baseline
        'wound_3d': 2.5,   # starting to increase
        'wound_7d': 3.0,   # PEAK
        'wound_14d': 1.5   # declining
    },
}
```

**Step 5: Output Files**

```
data/synthetic/
├── synthetic_counts.h5ad           ← Full AnnData (used by pipeline)
├── synthetic_counts_matrix.csv     ← Count matrix as CSV (backup)
├── synthetic_metadata.csv          ← Cell metadata (cell_type, condition, etc.)
└── gene_info.csv                   ← Gene annotations
```

---

## Data Loading in Our Pipeline

### How `01_scrna_analysis_pipeline.py` Loads Data

```python
def load_data():
    """Load synthetic or real scRNA-seq data."""
    h5ad_path = 'data/synthetic/synthetic_counts.h5ad'
    csv_path = 'data/synthetic/synthetic_counts_matrix.csv'
    
    if os.path.exists(h5ad_path):
        adata = sc.read_h5ad(h5ad_path)    # Preferred: fast
    elif os.path.exists(csv_path):
        counts = pd.read_csv(csv_path, index_col=0)
        metadata = pd.read_csv(meta_path, index_col=0)
        adata = anndata.AnnData(X=counts.values, obs=metadata)
    else:
        raise FileNotFoundError("Run generate_synthetic_data.py first!")
    
    return adata
```

**Key design**: The pipeline doesn't care WHERE the data came from — synthetic or real. Same code, same analysis.

---

## Metadata — The Context Around Your Data

### What is Metadata?

The **data about your data**:

```csv
# data/metadata/geo_sample_metadata.csv
sample_id,condition,replicate,organism,library_type
GSM_ctrl_1,control,1,Mus musculus,10X Chromium v3
GSM_ctrl_2,control,2,Mus musculus,10X Chromium v3
GSM_w3d_1,wound_3d,1,Mus musculus,10X Chromium v3
GSM_w3d_2,wound_3d,2,Mus musculus,10X Chromium v3
GSM_w7d_1,wound_7d,1,Mus musculus,10X Chromium v3
GSM_w7d_2,wound_7d,2,Mus musculus,10X Chromium v3
GSM_w14d_1,wound_14d,1,Mus musculus,10X Chromium v3
GSM_w14d_2,wound_14d,2,Mus musculus,10X Chromium v3
```

Without metadata, a count matrix is just numbers. Metadata tells you:
- Which condition each cell belongs to
- Which replicate (for statistical power)
- Technical details (library type, sequencing platform)

---

## File Format Comparison

| Format | Extension | Size (8K cells) | Read Speed | Software |
|--------|-----------|-----------------|------------|----------|
| H5AD | `.h5ad` | ~5 MB | Fast | Scanpy |
| RDS | `.rds` | ~8 MB | Fast | R/Seurat |
| CSV | `.csv` | ~50 MB | Slow | Any |
| MTX | `.mtx.gz` | ~2 MB | Fast | 10X tools |
| H5 | `.h5` | ~10 MB | Fast | Cell Ranger |

**Why we prefer H5AD**: Stores the entire AnnData object — counts, metadata, embeddings, results — in one compressed file. Load it once, everything is there.

---

## The Import Validation Report

We validate data after import:

```csv
# data/counts/import_validation_report.csv
dataset,n_cells,n_genes,conditions,ready
GSE234269,45000,22000,"control;wound_3d;wound_7d;wound_14d",true
GSE159827,32000,20500,"control;stretched;relaxed",true
```

This catches problems early: missing conditions, too few cells, unexpected gene counts.

---

## Interview Q&A

### Q: "Where does your data come from?"

> "Primary data is from GEO (GSE234269) — four wound healing timepoints in mouse skin with two replicates each. We also use GSE159827 for mechanical validation. Before touching real data, I validated the entire pipeline on synthetic data with known ground truth — 8,000 cells across 10 cell types and 4 conditions, with realistic negative binomial expression profiles and tissue fluidity gene signatures built in."

### Q: "Why synthetic data first?"

> "Three reasons: (1) Pipeline debugging is faster on 8K cells vs 50K+. (2) Ground truth validation — since I assigned the cell types, I can verify annotation accuracy. (3) Data safety — no risk of corrupting irreplaceable real data during development."

### Q: "How do you ensure data quality?"

> "Multi-layered: import validation report checks sample completeness, QC filtering removes low-quality cells (min 200 genes, max 15% mitochondrial), and doublet detection removes cell multiplets at ~5% rate."

---

## Self-Check Questions

1. **What is GEO?** → NCBI's public genomics database; required for publication data deposit
2. **What are the three 10X output files?** → matrix.mtx, barcodes.tsv, features.tsv
3. **Why synthetic data before real data?** → Pipeline validation, ground truth, speed, data safety
4. **What distribution is used for synthetic counts?** → Negative binomial (captures zeros + overdispersion)
5. **What does .h5ad store?** → Complete AnnData: counts + metadata + embeddings + results
6. **How many cells/conditions in our synthetic data?** → 8,000 cells, 4 conditions, 10 cell types
7. **What makes metadata critical?** → Without it, counts are just numbers — metadata provides context
8. **What seed do we use?** → 42 (set everywhere for reproducibility)
9. **Why is fluidity gene expression condition-dependent in synthetic data?** → To simulate real biology where EMT/ECM/migration peak at wound_7d
10. **What does the import validation report check?** → Cell counts, gene counts, condition completeness

---

**Next**: [Day 7 — Quality Control: The First Critical Step](Day_07_Quality_Control.md)
