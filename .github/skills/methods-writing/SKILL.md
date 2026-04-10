---
name: methods-writing
description: "Write methods sections, figure legends, and reproducibility documentation for the scRNA-seq wound healing manuscript. Use when creating paper content."
---

# Methods Writing Skill

## When to Use
- Writing methods sections for manuscripts
- Creating figure legends
- Documenting reproducibility information
- Writing Quarto/Rmarkdown reports

## Methods Section Template

### Single-cell RNA sequencing
Mouse skin samples were collected from C57BL/6J mice at four wound healing timepoints: control (unwounded), 3 days, 7 days, and 14 days post-wounding, with two biological replicates per condition (n=8 samples total). Single-cell suspensions were prepared and loaded onto the 10X Chromium platform (v3 chemistry). Libraries were sequenced on the Illumina NovaSeq 6000.

### Data Processing
Raw sequencing reads were aligned to the GRCm39 (mm39) reference genome (GENCODE vM33) using Cell Ranger. Quality control filtering retained cells with 200–5,000 detected genes, ≥500 UMI counts, and <15% mitochondrial reads. Genes detected in fewer than 3 cells were excluded. [Report: X cells retained from Y total.]

### Clustering and Cell Type Annotation
Count matrices were normalized (total-count normalization to 10,000, log-transformed), highly variable genes identified, and PCA performed. Batch correction was applied using Harmony. UMAP embedding and Leiden clustering (resolution 0.8) were computed. Cell types were annotated based on canonical marker expression.

### Differential Expression
Pseudobulk differential expression was performed using DESeq2 with ashr shrinkage. Significant genes were defined as padj < 0.05 and |log2FC| > 1.0. Comparisons were made between each wound timepoint and unwounded controls.

### Tissue Fluidity Analysis
Tissue fluidity was quantified using curated gene signatures for EMT, ECM remodeling, cell migration, mechanotransduction, and wound signaling pathways. Module scores were calculated using Scanpy's `score_genes` function.

## Figure Legend Template
**Figure X. [Title].** (A) UMAP embedding of [N] cells colored by [cell type/condition]. (B) [Description]. Scale bar: [if applicable]. Data shown as [mean ± SEM / individual replicates]. Statistical test: [Wilcoxon / DESeq2 Wald test], *p < 0.05, **p < 0.01, ***p < 0.001.

## Reproducibility Block
All analyses used R v4.4.0 / Python 3.10, with random seed 42 throughout. Full package versions are recorded in session logs. Code available at: https://github.com/rahulsarate/scRNA-seq-for-tissue-fluidity
