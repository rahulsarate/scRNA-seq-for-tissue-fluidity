# Continuation Plan — scRNA-seq Tissue Fluidity Project
> **Last updated**: 2026-06-08
> **Status**: Phase 2 — Real Data Analysis (QC complete, clustering next)
> **Read this first** if you are an agent continuing work on this project.

---

## Repository Boundary Update

As of 2026-05-26, this folder is only the mouse scRNA-seq wound-healing tissue-fluidity project.
The TCGA pathology / Clinical NLP EMT project has been moved to:

- Local folder: `D:\VS CODE Project\clinical-nlp-emt-tcga`
- GitHub: `https://github.com/rahulsarate/clinical-nlp-emt-tcga` (private)

Use that sibling repo for anything involving `clinical_nlp`, `tcga_pathology_emt`, pathology reports, TCGA bulk RNA EMT scoring, or scripts `10_*.py` through `18_*.py`.
See `docs/REPO_SPLIT_AND_HANDOFF.md` for the full moved-file map.

---

## What Has Been Done (Completed)

### Phase 1: Infrastructure & Synthetic Pipeline ✅
- Workspace structure, 10 agents, 11 skills, CI/CD, documentation
- Synthetic data: 8,000 cells, 10 cell types, 4 conditions (`data/synthetic/synthetic_counts.h5ad`)
- Full pipeline validated on synthetic: QC → clustering → DE → visualization
- Interactive React + FastAPI dashboard built and tested (`dashboard/`)

### Phase 1.5: GEO Data Import ✅ (completed 2026-04-13)
All 3 GEO datasets are downloaded, imported, and validated.

### Phase 1.75: Gene ID Conversion ✅ (completed 2026-06-08)
- Converted GSE234269 Ensembl IDs → gene symbols using GSE188432 features as reference
- 94.5% mapped (30,506/32,285 genes), 1,779 kept as Ensembl IDs
- Original Ensembl IDs stored in `adata.var['ensembl_id']`
- 13 mt- genes and 8/8 key fluidity genes confirmed present

### Phase 1.8: QC Filtering ✅ (completed 2026-06-08)

| Dataset | Pre-filter | Post-filter | Final (−doublets) | Genes | Doublets |
|---------|-----------|-------------|-------------------|-------|----------|
| GSE159827 | 2,803 | 2,787 | 2,772 | 12,370 | 15 (0.5%) |
| GSE234269_wound_3d | 5,158 | 4,337 | 4,318 | 14,770 | 19 (0.4%) |
| GSE234269_wound_7d | 22,924 | 21,932 | 20,706 | 19,226 | 1,226 (5.6%) |
| GSE234269_wound_14d | 16,611 | 14,861 | 13,972 | 19,605 | 889 (6.0%) |
| GSE188432 | 84,012 | 64,636 | 64,636* | 23,067 | *scrublet int32 overflow |

**Total post-QC cells**: 106,404
**QC thresholds**: min_genes=200, max_genes=5000, min_counts=500, max_mt=15%, min_cells=3
**GSE188432 note**: Scrublet failed due to int32 overflow on 64K cells. TODO: run per-batch scrublet.

### Key Technical Issues Resolved
1. **pandas C-engine gzip chunked read bug** → Read from uncompressed CSV instead
2. **dtype=np.float32 conflict with gene name index** → Removed dtype, cast during sparse conversion
3. **Scanpy 1.11.5 v2 MTX format bug** → Convert 2-column genes.tsv to 3-column features.tsv
4. **Memory safety**: Chunked sparse reading peaks at ~1 GB for largest file (vs 12+ GB dense)

### Scripts Created/Modified
- `scripts/python/_import_gse234269_safe.py` — Memory-safe per-sample CSV→h5ad importer
- `scripts/python/00_download_geo_data.py` — Fixed `read_10x_from_files()` for v2/v3 compatibility

---

## What Needs To Be Done Next

### IMMEDIATE NEXT STEP: Normalize + Integrate + Cluster (scrna-analyst)
**Input**: QC-filtered h5ad files (`*_qc.h5ad`)

Recommended approach:
1. Load QC'd GSE234269 samples (wound_3d + wound_7d + wound_14d)
2. Concatenate with batch_key='timepoint'
3. Optionally add GSE159827 as 'control' condition
4. Normalization: LogNormalize → `sc.pp.normalize_total(target_sum=1e4)` + `sc.pp.log1p()`
5. HVG selection: `sc.pp.highly_variable_genes()` — force fluidity genes as highly variable
6. PCA: 30 components
7. Integration: Harmony (group_by='sample') — if batch effects visible
8. Clustering: Leiden at resolutions [0.4, 0.6, 0.8, 1.0], default 0.8
9. Cell type annotation using known markers from `configs/analysis_config.yaml`
10. UMAP visualization

**Memory strategy**: Load one file at a time, concatenate, then discard originals

```python
# Quick start
import scanpy as sc
import anndata as ad

samples = [
    ('wound_3d', 'data/counts/GSE234269/GSE234269_wound_3d_qc.h5ad'),
    ('wound_7d', 'data/counts/GSE234269/GSE234269_wound_7d_qc.h5ad'),
    ('wound_14d', 'data/counts/GSE234269/GSE234269_wound_14d_qc.h5ad'),
]
adatas = []
for name, path in samples:
    a = sc.read_h5ad(path)
    a.obs['timepoint'] = name
    adatas.append(a)
adata = ad.concat(adatas, join='inner')
```
- Concatenate GSE234269 samples (3d + 7d + 14d) — NO control sample in GSE234269
- Consider GSE159827 as "control" (unwounded skin)
- Normalization: SCTransform or LogNormalize
- Integration: Harmony (group_by=sample)
- Clustering: Leiden at multiple resolutions (0.4, 0.6, 0.8, 1.0)
- Expected 10 cell types: basal keratinocytes, differentiated keratinocytes, fibroblasts, myofibroblasts, macrophages, neutrophils, T cells, endothelial, HFSCs, melanocytes

### THEN: DE Analysis (de-analyst)
- Method: Pseudobulk DESeq2 with ashr shrinkage
- Comparisons: wound_3d vs control, wound_7d vs control, wound_14d vs control
- Per cell type analysis
- Check tissue fluidity genes in every cell type

### THEN: Pathway Enrichment + Fluidity Scoring (pathway-explorer + scrna-analyst)
- GO/KEGG/GSEA on DE gene lists
- Score fluidity gene modules: EMT, ECM, migration, mechanotransduction, wound signals

---

## System Constraints (Important!)

### Memory
- **Total RAM**: 15.8 GB, typically ~5-7 GB free
- **Safe budget**: Keep Python process under 4 GB peak
- **Large files**: Load one dataset at a time, use `gc.collect()` between  
- **GSE188432 warning**: 84K cells, 1.27 GB h5ad — may need chunked processing

### CSV Import Gotchas
- pandas C engine fails on gzip chunked reads → use uncompressed files
- GSE234269 CSVs are genes×cells (transpose needed for AnnData cells×genes convention)  
- Always use `chunksize=1000` + sparse conversion for large CSVs

### Scanpy/AnnData
- scanpy 1.11.5, anndata 0.11.4, numpy 2.2.6
- Scanpy v2 MTX bug: convert genes.tsv to features.tsv with 3rd column
- Always `adata.var_names_make_unique()` and `adata.obs_names_make_unique()`

### Environment
- Python 3.10.11 in `.venv/`
- Activate: `.venv\Scripts\activate` (Windows)
- All packages from `requirements.txt`
- Windows OS (PowerShell)

---

## File Map (Key Locations)

```
PROJECT.md                          — Project state tracker (CLAW-style)
AGENTS.md                           — Agent directory and handoff map
configs/analysis_config.yaml        — All analysis parameters
docs/decision_log.md                — Analysis decision log
docs/CONTINUATION_PLAN.md           — THIS FILE
logs/sessions/session_log.json      — Session history

data/counts/GSE234269/GSE234269_wound_3d_qc.h5ad  — 4,318 cells (QC'd, gene symbols)
data/counts/GSE234269/GSE234269_wound_7d_qc.h5ad   — 20,706 cells (QC'd, gene symbols)
data/counts/GSE234269/GSE234269_wound_14d_qc.h5ad  — 13,972 cells (QC'd, gene symbols)
data/counts/GSE159827/GSE159827_qc.h5ad            — 2,772 cells (QC'd, gene symbols)
data/counts/GSE188432/GSE188432_qc.h5ad            — 64,636 cells (QC'd, no doublet removal)

data/synthetic/synthetic_counts.h5ad — Synthetic test data (8K cells)
analysis/clustering/wound_adata.h5ad — Processed synthetic data
analysis/de/wound_*_vs_control.csv   — Synthetic DE results
analysis/qc/qc_summary.csv          — QC results for all 5 datasets
analysis/qc/*_qc_violins_*.png       — Pre/post-filter violin plots
analysis/qc/*_qc_scatter_pre.png     — QC scatter plots
analysis/qc/*_doublet_histogram.png  — Doublet score distributions

scripts/python/00_download_geo_data.py          — GEO download & import
scripts/python/_import_gse234269_safe.py         — Memory-safe CSV importer
scripts/python/_convert_ensembl_to_symbols.py    — Ensembl→symbol converter
scripts/python/03_qc_real_data.py                — QC script for real GEO data
scripts/python/01_scrna_analysis_pipeline.py     — Main analysis pipeline
scripts/python/02_visualization_suite.py         — Publication figures
scripts/python/generate_synthetic_data.py        — Synthetic data generator
```

---

## Quick Resume Commands

```bash
# Activate environment
.venv\Scripts\activate

# Check QC'd data state
python -c "import anndata; a=anndata.read_h5ad('data/counts/GSE234269/GSE234269_wound_7d_qc.h5ad'); print(a)"

# Load and concatenate for clustering
python -c "
import scanpy as sc, anndata as ad
files = ['data/counts/GSE234269/GSE234269_wound_3d_qc.h5ad',
         'data/counts/GSE234269/GSE234269_wound_7d_qc.h5ad',
         'data/counts/GSE234269/GSE234269_wound_14d_qc.h5ad']
adatas = [sc.read_h5ad(f) for f in files]
adata = ad.concat(adatas, join='inner')
print(adata)
"

# Start dashboard
cd dashboard/backend && python main.py &
cd dashboard/frontend && npm run dev
```
