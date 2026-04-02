# 25 Ready-to-Use Prompts for scRNA-seq Wound Healing Analysis
# ============================================================
# Project: Tissue Fluidity Controls Skin Repair (Sarate Lab)
# 
# Copy-paste these prompts into your AI coding agent (GitHub Copilot,
# Claude, Cursor, etc.) to accelerate your analysis workflow.
# ============================================================

## --- DATA ACQUISITION & IMPORT ---

### Prompt 1: Download wound healing datasets
> Download the scRNA-seq datasets GSE234269 (wound timepoints) and GSE159827
> (tissue mechanics in wound healing) from GEO. Parse the supplementary count
> matrices into a Seurat object in R, adding sample metadata columns for
> condition (control, wound_3d, wound_7d, wound_14d) and organism (Mus musculus).
> Save as data/counts/merged_wound_healing.rds

### Prompt 2: Create synthetic test data
> Generate a synthetic scRNA-seq dataset with 8000 cells, 2000 genes, and
> 10 skin cell types (basal/differentiated keratinocytes, fibroblasts,
> myofibroblasts, macrophages, neutrophils, T cells, endothelial, HFSCs,
> melanocytes) across 4 wound healing conditions (control, 3d, 7d, 14d).
> Include tissue fluidity gene signatures (EMT, ECM remodeling, mechanotransduction).
> Use negative binomial distribution with realistic dropout.

### Prompt 3: Build sample metadata sheet
> Create a sample metadata CSV for my wound healing experiment with the
> following columns: sample_id, condition, timepoint, replicate, sex, age,
> organism, library_prep, sequencing_platform, n_cells_expected. Include
> 2 replicates per condition (control, wound_3d, wound_7d, wound_14d),
> all from C57BL/6J mice, 10X Chromium v3, NovaSeq 6000.


## --- QUALITY CONTROL ---

### Prompt 4: Run comprehensive QC
> Run quality control on the wound healing scRNA-seq Seurat object: calculate
> percent mitochondrial (mouse mt- prefix), make QC violin plots for
> nFeature_RNA, nCount_RNA, and percent.mt grouped by sample, create scatter
> plots of nCount vs percent.mt, then filter cells keeping
> 200 < nFeature < 5000, nCount > 500, and percent.mt < 15%.
> Run DoubletFinder on each sample. Save QC report figures to analysis/qc/.

### Prompt 5: Ambient RNA removal
> Run SoupX to estimate and remove ambient RNA contamination from my 10X
> Cell Ranger output. Process each sample separately using the raw and
> filtered matrices. Adjust counts, then create a corrected Seurat object.
> Compare before/after for known marker genes (Krt14, Col1a1, Cd68).


## --- CLUSTERING & ANNOTATION ---

### Prompt 6: Full clustering pipeline
> Process the QC-filtered Seurat object: SCTransform normalization (regressing
> percent.mt), run PCA (50 components), create elbow plot, integrate samples
> using Harmony (group.by = "sample"), compute UMAP (dims 1:30), find neighbors,
> test clustering at resolutions 0.4, 0.6, 0.8, 1.0 using Leiden algorithm.
> Generate clustree plot to choose optimal resolution.

### Prompt 7: Cell type annotation
> Annotate my skin wound healing scRNA-seq clusters using these marker genes:
> Basal keratinocytes (Krt14, Krt5, Tp63), differentiated keratinocytes
> (Krt10, Krt1, Ivl), fibroblasts (Col1a1, Dcn, Pdgfra), myofibroblasts
> (Acta2, Tagln, Postn), macrophages (Cd68, Adgre1, Csf1r),
> neutrophils (S100a8, S100a9), endothelial (Pecam1, Cdh5),
> hair follicle SCs (Sox9, Lgr5). Create a dot plot and feature plots.
> Also run SingleR with the Mouse RNA-seq reference for validation.

### Prompt 8: Sub-cluster fibroblasts
> Subset the fibroblast cluster from the wound healing Seurat object and
> re-cluster to identify sub-populations: resting fibroblasts (Dcn+, Pdgfra+),
> activated fibroblasts (Postn+, Tnc+), myofibroblasts (Acta2+, Tagln+),
> and any tissue-fluidity-related states. Run UMAP, find markers for each
> sub-cluster, and make feature plots for ECM genes (Col1a1, Fn1, Mmp2, Lox).


## --- DIFFERENTIAL EXPRESSION ---

### Prompt 9: Pseudobulk DESeq2 (recommended for scRNA-seq)
> Run pseudobulk differential expression using DESeq2 on my wound healing
> scRNA-seq data. Aggregate counts by cell_type + condition + sample, then
> for each cell type, compare wound_3d vs control, wound_7d vs control,
> and wound_14d vs control. Apply lfcShrink (ashr method). Save results
> as CSV files in analysis/de/ with columns: gene, log2FC, padj, baseMean.
> Focus on tissue fluidity genes (Vim, Fn1, Mmp2/9, Tgfb1, Acta2, Yap1).

### Prompt 10: Time-series DE analysis
> Analyze the temporal dynamics of gene expression across wound healing phases
> (control → 3d → 7d → 14d) using the tradeSeq or splineTimeR approach.
> Identify genes with significant temporal patterns in fibroblasts and
> macrophages. Cluster gene trajectories into early-response, mid-response,
> and late-response groups. Create a heatmap of the top 50 temporally
> dynamic genes ordered by peak expression time.

### Prompt 11: Cell-type-specific condition comparison
> For each major cell type (fibroblast, macrophage, keratinocyte), run
> Seurat FindMarkers comparing wound_7d vs control using MAST test.
> Create a comparison table showing: which tissue fluidity genes are
> differentially expressed in which cell types. Make a bubble plot
> where x = cell type, y = gene, size = -log10(padj), color = log2FC.


## --- PATHWAY ANALYSIS ---

### Prompt 12: GO enrichment for wound fibroblasts
> Run GO enrichment analysis (Biological Process, Molecular Function,
> Cellular Component) using clusterProfiler on the upregulated genes
> (log2FC > 1, padj < 0.05) from wound_7d vs control in fibroblasts.
> Generate dotplot (top 20 terms), cnetplot (top 5 with gene networks),
> and enrichment map. Highlight wound-healing-relevant terms:
> ECM organization, cell migration, wound healing, TGF-β signaling.

### Prompt 13: GSEA with Hallmark gene sets
> Run GSEA using fgsea on the full ranked gene list (by log2FC) from
> pseudobulk DE for fibroblasts. Use MSigDB Hallmark gene sets.
> Create enrichment plots for: EMT, TGF-β signaling, inflammatory response,
> myogenesis, angiogenesis. Save NES scores and plot the top 10 positive
> and top 10 negative pathways.

### Prompt 14: Pathway activity per cell
> Use decoupleR to compute per-cell pathway activity scores for PROGENy
> pathways (TGFb, WNT, NFkB, VEGF, MAPK, JAK-STAT) in my wound healing
> scRNA-seq data. Visualize pathway activities on UMAP. Create violin
> plots comparing pathway activity across conditions for fibroblasts.


## --- TISSUE FLUIDITY ANALYSIS ---

### Prompt 15: Tissue fluidity gene scoring
> Score each cell for 5 tissue fluidity gene signatures using Seurat
> AddModuleScore: 1) EMT (Vim, Cdh1/2, Snai1/2, Twist1, Zeb1/2),
> 2) ECM remodeling (Fn1, Col1a1/3a1, Mmp2/9/14, Lox),
> 3) Cell migration (Rac1, Cdc42, Itgb1),
> 4) Mechanotransduction (Yap1, Piezo1, Trpv4),
> 5) Wound signals (Tgfb1/2/3, Pdgfa, Vegfa, Wnt5a).
> Create UMAP feature plots and violin plots by condition.
> Identify which cell types have the highest fluidity scores.

### Prompt 16: Fluidity state transition analysis
> Use Monocle3 to infer the pseudotime trajectory of fibroblasts transitioning
> from a quiescent state (control) through activated (wound_3d) to
> myofibroblast (wound_7d) and back to resolved (wound_14d).
> Plot tissue fluidity scores along pseudotime. Identify the "tipping point"
> where fluidity peaks. Use RNA velocity (scVelo) to validate
> directionality of the fibroblast → myofibroblast transition.


## --- VISUALIZATION ---

### Prompt 17: Publication UMAP figure
> Create a publication-quality multi-panel figure (Figure 1) with:
> A) UMAP colored by cell cluster with labels
> B) UMAP colored by wound condition (use palette: control=#2166AC,
>    wound_3d=#F4A582, wound_7d=#D6604D, wound_14d=#B2182B)
> C) UMAP colored by cell type with legend
> D) UMAP split by condition (4 panels)
> Use colorblind-safe palette, 300 DPI, export as PDF.

### Prompt 18: Volcano plot panel
> Create a 3-panel volcano plot for wound_3d, wound_7d, wound_14d
> vs control (pseudobulk DESeq2 results for fibroblasts). Highlight
> tissue fluidity genes in red. Use EnhancedVolcano with:
> pCutoff = 0.05, FCcutoff = 1, label top 10 genes.
> Add dashed lines at significance thresholds.

### Prompt 19: Heatmap of fluidity genes
> Create a ComplexHeatmap of the 40 tissue fluidity genes (EMT + ECM +
> migration + mechanotransduction) showing average expression per cell type
> per condition. Use the blue-white-red color scale. Add column annotations
> for condition and cell type. Cluster genes by expression pattern.
> Export as PDF (8 x 12 inches).

### Prompt 20: Cell proportion dynamics
> Create a stacked bar chart showing cell type proportions across
> wound healing phases. Add a line plot overlay highlighting the
> myofibroblast and macrophage proportion changes. Perform chi-squared
> test for proportion differences between conditions. Use the
> Okabe-Ito colorblind-safe palette.


## --- ADVANCED ANALYSIS ---

### Prompt 21: Cell-cell communication
> Run CellChat on the wound healing scRNA-seq data to identify
> ligand-receptor interactions between cell types. Compare signaling
> networks across conditions. Focus on: TGF-β signaling (fibroblast →
> keratinocyte), WNT signaling (HFSC → fibroblast), chemokine signaling
> (macrophage → neutrophil). Create chord diagrams and signaling
> pathway hierarchy plots.

### Prompt 22: Batch correction comparison
> Compare 3 integration methods (Harmony, RPCA, scVI) on my wound
> healing dataset. Compute kBET, LISI, and silhouette scores for each.
> Create side-by-side UMAPs. Recommend the best method based on:
> a) mixing of batches within cell types, b) separation of cell types,
> c) preservation of biological condition differences.

### Prompt 23: Spatial deconvolution prep
> Prepare my scRNA-seq data as a reference for spatial transcriptomics
> deconvolution using RCTD (spacexr) or cell2location. Generate the
> reference matrix with cell type profiles, validate marker gene
> specificity, and create the compatibility report.


## --- REPORTING ---

### Prompt 24: Methods section for manuscript
> Write a complete methods section for our manuscript describing
> the scRNA-seq analysis of mouse skin wound healing. Include:
> experimental design (4 conditions × 2 replicates), 10X Chromium v3 library
> prep, NovaSeq sequencing, Cell Ranger alignment (mm10/GRCm38),
> QC filtering criteria, Seurat normalization, Harmony integration,
> Leiden clustering, cell type annotation (markers used),
> pseudobulk DESeq2 for DE, clusterProfiler for enrichment,
> tissue fluidity gene scoring, Monocle3 trajectory analysis.
> Include software versions. Format for Nature Methods style.

### Prompt 25: Reproducibility report
> Generate a complete reproducibility report for this analysis:
> 1) R sessionInfo() and Python package versions
> 2) Conda environment export (YAML)
> 3) Random seeds used at each step
> 4) All parameter choices documented
> 5) File checksums for input data
> 6) Git commit hash for analysis scripts
> Save as reports/reproducibility_report.html using Quarto.
