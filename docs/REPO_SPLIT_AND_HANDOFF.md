# Repository Split and Handoff

Last updated: 2026-05-26

## Current Repository Boundary

This repository, `D:\VS CODE Project\scRNA_seq`, is the mouse scRNA-seq wound-healing tissue-fluidity project.

GitHub:

- `https://github.com/rahulsarate/scRNA-seq-for-tissue-fluidity`
- Visibility: public
- Default branch: `master`

## Separated Project

The TCGA pathology report NLP plus molecular EMT linkage project has been split into a sibling folder and separate GitHub repository.

Local folder:

- `D:\VS CODE Project\clinical-nlp-emt-tcga`

GitHub:

- `https://github.com/rahulsarate/clinical-nlp-emt-tcga`
- Visibility: private
- Default branch: `master`

## What Was Moved Out

The following Clinical NLP / TCGA EMT project assets were moved out of this scRNA repo:

- `configs/clinical_nlp_config.yaml`
- `configs/clinical_nlp_ontology.yaml`
- `scripts/python/10_download_tcga_pathology_data.py`
- `scripts/python/11_extract_and_normalize_reports.py`
- `scripts/python/12_build_pathology_ontology_and_labelset.py`
- `scripts/python/13_prepare_annotation_queue.py`
- `scripts/python/14_train_pathology_baselines.py`
- `scripts/python/15_train_pathology_transformer.py`
- `scripts/python/16_score_tcga_bulk_emt.py`
- `scripts/python/17_link_pathology_to_rna.py`
- `scripts/python/18_update_clinical_nlp_benchmarks.py`
- `scripts/python/utils/clinical_nlp_*`
- `analysis/clinical_nlp/`
- `data/counts/tcga_pathology_emt/`
- `data/metadata/tcga_pathology_emt/`
- `docs/methods/`
- `docs/career/`
- `reports/clinical_nlp/`
- `logs/pipeline_runs/clinical_nlp/`

## What Stays Here

Keep this repo focused on:

- GEO/scRNA-seq data import and QC.
- Mouse gene-symbol processing.
- GSE234269, GSE159827, and GSE188432 wound-healing analyses.
- Tissue-fluidity scoring for EMT, ECM remodeling, migration, mechanotransduction, and wound signals.
- Clustering, DE, enrichment, figures, reports, and dashboard work for the scRNA project.

## Data Safety

Large generated artifacts and TCGA/NLP paths are ignored in `.gitignore`.

Agents should not commit:

- Raw or processed large sequencing data.
- TCGA pathology PDFs.
- TCGA RNA TSV files.
- `.h5ad`, `.rds`, large `.parquet`, model outputs, or regenerated figures unless explicitly requested.

## Practical Rule for Future Agents

If a task mentions TCGA, pathology reports, clinical NLP, transformer pathology classification, `clinical_nlp`, or `tcga_pathology_emt`, switch to:

`D:\VS CODE Project\clinical-nlp-emt-tcga`

If a task mentions wound healing scRNA-seq, GSE234269, GSE159827, GSE188432, mouse skin, Scanpy/Seurat clustering, tissue fluidity, or pseudobulk DE for wound timepoints, stay in:

`D:\VS CODE Project\scRNA_seq`
