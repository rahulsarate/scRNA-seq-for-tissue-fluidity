# Single-cell analytics for tissue fluidity and wound healing

**Python / Scanpy · R / Seurat · Experimental data QC · Cell-state analysis · Scientific visualisation**

A scientific analytics portfolio project by **Rahul Sarate, PhD**, exploring gene programmes relevant to cell migration, extracellular matrix remodelling, and mouse skin repair.

The project connects an experimental tissue-biology question with single-cell data exploration: **which cell states and molecular programmes might help explain changes in tissue behaviour during wound healing?**

> **Current scope:** The quick-start Python and R workflows use synthetic data. Real GEO data import and QC are described in project records, but the complete real-data analysis is still in progress. This repository is a transcriptomics project, not a microscopy segmentation or tracking pipeline. Gene-set scores are exploratory proxies and do not directly measure mechanical tissue fluidity.

## Why this project is relevant to scientific analytics

| Capability | Evidence in this repository |
| --- | --- |
| Experimental data handling | Count-matrix import utilities, sample metadata, and QC summaries |
| Python scientific computing | Scanpy/AnnData workflow with NumPy, pandas, Matplotlib, and Seaborn |
| R scientific computing | Seurat workflow with ggplot2, dplyr, and patchwork |
| Biological interpretation | Marker panels and gene sets related to skin cell identity, EMT, ECM, migration, and mechanotransduction |
| Exploratory statistics | Cluster-marker and condition comparisons; limitations below distinguish cell-level exploration from biological-replicate inference |
| Communication with scientists | QC plots, UMAPs, marker plots, gene-score visualisations, and an interactive dashboard |

**Start with:** [Python analysis](scripts/python/01_scrna_analysis_pipeline.py) · [R analysis](scripts/R/01_seurat_analysis.R) · [Dashboard](dashboard/README.md) · [Sample-sheet template](templates/sample_sheet_template.csv)

## Implemented workflow and current status

### Synthetic-data demonstration

1. Generate synthetic counts and sample metadata.
2. Calculate QC metrics and filter cells/genes.
3. Normalise expression and identify variable genes.
4. Run PCA, UMAP, and clustering.
5. Explore cell-type markers and expression patterns.
6. Generate exploratory differential-expression tables.
7. Score gene sets associated with wound-repair biology.
8. Export processed objects, tables, and figures.

The Python script uses Scanpy and cell-level Wilcoxon comparisons. The R script currently uses log normalisation and Seurat marker analysis. Although some script comments describe SCTransform, Harmony, or pseudobulk DESeq2, those methods are **not executed by the current R demonstration**.

### Real-data work

The [continuation plan](docs/CONTINUATION_PLAN.md) records GEO import and QC work and identifies integration, clustering, and replicate-aware downstream analysis as next steps. Some locally generated scripts and processed objects referenced there are not included in this checkout.

The checked-in [QC summary](analysis/qc/qc_summary.csv) contains four 2,000-cell demonstration samples. It should not be presented as validation of the larger real-data analysis described in the continuation plan. Existing synthetic differential-expression tables are demonstration outputs, not biological findings.

## Quick start: Python demonstration

Run from the repository root:

```bash
git clone https://github.com/rahulsarate/scRNA-seq-for-tissue-fluidity.git
cd scRNA-seq-for-tissue-fluidity
conda env create -f configs/conda_envs/scrna_wound_healing.yml
conda activate scrna_wound
python scripts/python/generate_synthetic_data.py
python scripts/python/01_scrna_analysis_pipeline.py
python scripts/python/02_visualization_suite.py
```

Alternatively, install [requirements.txt](requirements.txt) in an isolated Python environment. These are the repository's demonstration entry points; dependency versions are not fully pinned, so a fresh environment requires validation.

The main Python loader reads from `data/synthetic/`. Downloading GEO data does **not** automatically switch this workflow to real data.

Expected output locations:

| Location | Contents |
| --- | --- |
| `analysis/figures/` | QC, UMAP, marker, and gene-score figures |
| `analysis/de/` | Exploratory marker and condition-comparison tables |
| `analysis/clustering/` | Processed AnnData object, UMAP coordinates, and cell metadata |

For the interactive interface, follow the separate [dashboard setup guide](dashboard/README.md). Confirm which input dataset the dashboard has loaded before interpreting its displays.

## R companion workflow

The Python environment above does not install R or its packages. In an R environment with Seurat, ggplot2, dplyr, and patchwork installed, run:

```bash
Rscript scripts/R/generate_synthetic_seurat.R
Rscript scripts/R/01_seurat_analysis.R
```

The R workflow uses its own synthetic input and exports a Seurat object, tables, figures, and session information. Python and R outputs should not be assumed numerically equivalent.

## Statistical interpretation and limitations

- **Biological replication:** Cells from the same animal or sample are not independent biological replicates. Current cell-level comparisons are exploratory; study-level inference requires suitable replicate-aware models.
- **Condition versus composition:** A difference across all cells can reflect changing cell-type proportions as well as within-cell-type expression. Interpret these questions separately.
- **Batch confounding:** Samples from different studies must not be treated as interchangeable controls without checking design and technical differences. Integration cannot establish an identifiable treatment effect when study and condition are confounded.
- **Expression scale:** Verify the expression matrix and `use_raw` behaviour before interpreting differential expression or scores. The Python script saves counts into `adata.raw` before normalisation, and downstream Scanpy defaults need review before quantitative inference.
- **Annotation:** Marker-score assignments are provisional and need biological review. Synthetic ground-truth labels are not externally validated real-data annotations.
- **Gene scores:** EMT and related modules are exploratory summaries, not calibrated physical measurements or validated predictive biomarkers.
- **Reporting:** Real experimental conclusions should include biological sample counts, effect sizes, uncertainty, multiple-testing correction, and sensitivity to analysis choices.

## Connection to imaging and wet-lab studies

My research background includes confocal and intravital microscopy, lineage tracing, cell culture/organoids, and animal models. That experimental perspective motivates the biological questions in this project.

A future multimodal study could compare transcriptomic programmes with measured migration, cell shape, or tissue organisation. Such analysis would require matched sample identifiers, validated image measurements, and an appropriate experimental design. **No completed image-analysis or multimodal validation workflow is claimed here.**

## Repository guide

| Path | Purpose |
| --- | --- |
| [scripts/python/](scripts/python/) | Synthetic data, import utilities, analysis, and visualisation |
| [scripts/R/](scripts/R/) | Synthetic-data generator and Seurat analysis |
| [configs/](configs/) | Environment and analysis configuration files; check each script for parameters it actually uses |
| [data/metadata/](data/metadata/) | Experimental metadata |
| [data/references/](data/references/) | Candidate dataset catalogue; verify metadata against source records before use |
| [analysis/](analysis/) | Checked-in example outputs |
| [dashboard/](dashboard/) | Interactive React/FastAPI interface |
| [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) | Development and agent-assisted workflow guide |
| [docs/CONTINUATION_PLAN.md](docs/CONTINUATION_PLAN.md) | Historical progress record and planned work |
| [docs/research-paradigms/](docs/research-paradigms/) | Research proposals, not completed results |

This repository stays focused on wound-healing scRNA-seq. The separate TCGA pathology/NLP project is described in the [repository handoff note](docs/REPO_SPLIT_AND_HANDOFF.md).

## Research context and reuse

The repository includes the paper *Dynamic regulation of tissue fluidity controls skin repair during wound healing* as scientific background. This portfolio workflow should not be assumed to reproduce the publication's analysis or establish its findings.

The earlier README described analysis scripts as MIT-licensed, but this checkout has no standalone LICENSE file. Confirm reuse terms with the repository owner. External data and publications remain subject to their original terms.
