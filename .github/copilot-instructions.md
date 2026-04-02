# scRNA-seq Wound Healing Project — Copilot Instructions

## Project Identity
- **Project**: Dynamic regulation of tissue fluidity controls skin repair during wound healing
- **PI**: Rahul M Sarate
- **Organism**: Mus musculus (C57BL/6J) — mouse gene symbols (e.g., Krt14, Col1a1, mt-)
- **Genome**: GRCm39 (mm39), GENCODE vM33
- **GitHub**: https://github.com/rahulsarate/scRNA-seq-for-tissue-fluidity

## Data Security — CRITICAL
- NEVER include patient IDs, PHI, or clinical identifiers in code, commits, or prompts
- Raw FASTQ files in `data/raw/` are READ-ONLY — never modify or delete
- Do not commit files >50MB (use .gitignore — already configured)
- Do not paste unpublished results into external services

## Technology Stack
- **R** (v4.4.0): Seurat v5, DESeq2, clusterProfiler, ggplot2, ComplexHeatmap, EnhancedVolcano
- **Python** (3.11): Scanpy, AnnData, scVelo, CellChat (via rpy2), pandas, matplotlib, seaborn
- **Conda env**: `configs/conda_envs/scrna_wound_healing.yml`

## Coding Conventions
- R scripts: snake_case for variables, PascalCase for Seurat objects (e.g., `wound_sobj`)
- Python scripts: snake_case throughout, type hints for function signatures
- All scripts must set `set.seed(42)` (R) or `random_state=42` (Python) for reproducibility
- Save R objects as `.rds`, Python objects as `.h5ad`
- Always include `sessionInfo()` (R) or package version logging (Python)

## Directory Rules
| Directory | Policy | What goes here |
|-----------|--------|----------------|
| `data/raw/` | READ-ONLY | Raw FASTQ — never touch |
| `data/synthetic/` | Write | Generated test data |
| `data/counts/` | Write | Count matrices, Seurat/AnnData objects |
| `analysis/qc/` | Write | QC plots, metrics |
| `analysis/de/` | Write | DESeq2/MAST results (CSV + RDS) |
| `analysis/enrichment/` | Write | GO/KEGG/GSEA results |
| `analysis/clustering/` | Write | Processed objects, UMAP coords |
| `analysis/figures/` | Write | Publication figures (PDF, 300 DPI) |
| `analysis/trajectory/` | Write | Pseudotime, RNA velocity |
| `scripts/python/` | Write | Python analysis scripts |
| `scripts/R/` | Write | R analysis scripts |
| `reports/` | Write | Quarto/Rmarkdown reports |

## Key Datasets
| GEO ID | Description | Use |
|--------|-------------|-----|
| GSE234269 | Wound healing timepoints | Primary dataset |
| GSE159827 | Tissue mechanics in wounds | Mechanical validation |
| GSE188432 | Aged wound healing | Age comparison |

## Tissue Fluidity Gene Signatures (Core to this project)
- **EMT**: Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2
- **ECM remodeling**: Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2
- **Cell migration**: Rac1, Cdc42, Itgb1, Rhoa, Rock1, Rock2
- **Mechanotransduction**: Yap1, Wwtr1, Piezo1, Trpv4, Lats1, Lats2
- **Wound signals**: Tgfb1, Tgfb2, Tgfb3, Pdgfa, Vegfa, Wnt5a, Il6, Tnf

## Experimental Design
- 4 conditions: control, wound_3d, wound_7d, wound_14d
- 2 replicates per condition (8 samples total)
- 10X Chromium v3 (3' GEX), NovaSeq 6000
- 10 expected cell types: basal keratinocytes, differentiated keratinocytes, fibroblasts, myofibroblasts, macrophages, neutrophils, T cells, endothelial, HFSCs, melanocytes

## Analysis Pipeline Order
1. `scripts/python/generate_synthetic_data.py` — Create test data
2. `scripts/python/01_scrna_analysis_pipeline.py` — Full Scanpy pipeline
3. `scripts/python/02_visualization_suite.py` — Publication figures
4. `scripts/R/generate_synthetic_seurat.R` → `scripts/R/01_seurat_analysis.R` — R alternative

## QC Thresholds
- min_genes: 200, max_genes: 5000
- min_counts: 500, max_percent_mt: 15%
- min_cells_per_gene: 3, doublet_rate: ~5%

## DE Analysis Standards
- Method: Pseudobulk DESeq2 (gold standard for scRNA-seq)
- Shrinkage: ashr
- Thresholds: padj < 0.05, |log2FC| > 1.0
- Always compare against control condition

## Output Standards
- Figures: PDF format, 300 DPI, colorblind-safe palettes
- Tables: CSV with columns gene, log2FC, padj, baseMean
- Objects: .rds (R), .h5ad (Python)
- Reports: Quarto (.qmd) preferred
