#!/usr/bin/env python3
"""
scRNA-seq Analysis Pipeline — Wound Healing Tissue Fluidity
=============================================================
Author: Rahul M Sarate
Project: Dynamic regulation of tissue fluidity controls skin repair

Complete analysis pipeline:
1. Load data (synthetic or real)
2. QC & filtering
3. Normalization & HVG selection
4. Dimensionality reduction (PCA, UMAP)
5. Clustering (Leiden)
6. Cell type annotation
7. Differential expression (condition comparisons)
8. Tissue fluidity gene scoring
9. Save results

Usage:
    python scripts/python/01_scrna_analysis_pipeline.py
"""

import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
import os
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
sc.settings.verbosity = 2
sc.settings.set_figure_params(dpi=150, facecolor='white', frameon=False)
sc.settings.figdir = 'analysis/figures/'
os.makedirs('analysis/figures/', exist_ok=True)
os.makedirs('analysis/de/', exist_ok=True)
os.makedirs('analysis/clustering/', exist_ok=True)

SEED = 42
np.random.seed(SEED)

# Tissue fluidity gene sets
FLUIDITY_GENE_SETS = {
    'EMT_signature': ['Vim', 'Cdh1', 'Cdh2', 'Snai1', 'Snai2', 'Twist1', 'Zeb1', 'Zeb2'],
    'ECM_remodeling': ['Fn1', 'Col1a1', 'Col3a1', 'Mmp2', 'Mmp9', 'Mmp14', 'Timp1', 'Lox', 'Loxl2'],
    'Cell_migration': ['Rac1', 'Cdc42', 'RhoA', 'Itgb1', 'Itga6', 'Cxcl12', 'Cxcr4'],
    'Mechanotransduction': ['Yap1', 'Wwtr1', 'Piezo1', 'Trpv4', 'Lats1', 'Lats2'],
    'Wound_signals': ['Tgfb1', 'Tgfb2', 'Tgfb3', 'Pdgfa', 'Pdgfb', 'Fgf2', 'Vegfa', 'Wnt5a'],
}

# Skin cell type markers for annotation
CELL_MARKERS = {
    'Basal_Keratinocyte': ['Krt14', 'Krt5', 'Tp63'],
    'Diff_Keratinocyte': ['Krt10', 'Krt1', 'Ivl'],
    'Fibroblast': ['Col1a1', 'Col3a1', 'Dcn', 'Pdgfra'],
    'Myofibroblast': ['Acta2', 'Tagln', 'Cnn1'],
    'Macrophage': ['Cd68', 'Adgre1', 'Csf1r'],
    'Neutrophil': ['S100a8', 'S100a9', 'Ly6g'],
    'T_Cell': ['Cd3d', 'Cd3e'],
    'Endothelial': ['Pecam1', 'Cdh5', 'Kdr'],
    'Hair_Follicle_SC': ['Sox9', 'Lgr5', 'Cd34'],
    'Melanocyte': ['Dct', 'Tyrp1', 'Pmel'],
}

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
def load_data():
    """Load synthetic or real scRNA-seq data."""
    h5ad_path = 'data/synthetic/synthetic_counts.h5ad'
    csv_path = 'data/synthetic/synthetic_counts_matrix.csv'
    meta_path = 'data/synthetic/synthetic_metadata.csv'
    
    if os.path.exists(h5ad_path):
        print("[1] Loading H5AD data...")
        adata = sc.read_h5ad(h5ad_path)
    elif os.path.exists(csv_path):
        print("[1] Loading CSV count matrix...")
        counts = pd.read_csv(csv_path, index_col=0)
        metadata = pd.read_csv(meta_path, index_col=0)
        import anndata
        adata = anndata.AnnData(X=counts.values.astype(np.float32), 
                                 obs=metadata, 
                                 var=pd.DataFrame(index=counts.columns))
    else:
        raise FileNotFoundError(
            "No data found. Run generate_synthetic_data.py first:\n"
            "  python scripts/python/generate_synthetic_data.py"
        )
    
    print(f"    Loaded: {adata.shape[0]} cells x {adata.shape[1]} genes")
    print(f"    Conditions: {adata.obs['condition'].unique().tolist()}")
    return adata

# ============================================================================
# STEP 2: QC & FILTERING
# ============================================================================
def qc_filter(adata):
    """Quality control and cell filtering."""
    print("\n[2] Quality Control & Filtering...")
    
    # Calculate QC metrics
    adata.var['mt'] = adata.var_names.str.startswith('mt-') | adata.var_names.str.startswith('Mt-')
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)
    
    # Use pre-computed metrics if available
    if 'percent_mt' in adata.obs.columns and 'pct_counts_mt' not in adata.obs.columns:
        adata.obs['pct_counts_mt'] = adata.obs['percent_mt']
    
    # QC plots
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    sc.pl.violin(adata, 'n_genes_by_counts', groupby='condition', ax=axes[0], show=False)
    axes[0].set_title('Genes per Cell')
    sc.pl.violin(adata, 'total_counts', groupby='condition', ax=axes[1], show=False)
    axes[1].set_title('Total Counts per Cell')
    if 'pct_counts_mt' in adata.obs.columns:
        sc.pl.violin(adata, 'pct_counts_mt', groupby='condition', ax=axes[2], show=False)
        axes[2].set_title('% Mitochondrial')
    plt.tight_layout()
    plt.savefig('analysis/figures/01_qc_violins.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Filter
    n_before = adata.shape[0]
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=3)
    if 'pct_counts_mt' in adata.obs.columns:
        adata = adata[adata.obs.pct_counts_mt < 15, :].copy()
    
    print(f"    Before filter: {n_before} cells")
    print(f"    After filter: {adata.shape[0]} cells, {adata.shape[1]} genes")
    
    return adata

# ============================================================================
# STEP 3: NORMALIZATION & HVG
# ============================================================================
def normalize_and_hvg(adata):
    """Normalize, log-transform, and select highly variable genes."""
    print("\n[3] Normalization & HVG selection...")
    
    # Store raw counts
    adata.raw = adata.copy()
    
    # Normalize
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    
    # Highly variable genes
    sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
    
    # Ensure tissue fluidity genes are kept
    all_fluidity = set()
    for genes in FLUIDITY_GENE_SETS.values():
        all_fluidity.update(genes)
    for gene in all_fluidity:
        if gene in adata.var_names:
            adata.var.loc[gene, 'highly_variable'] = True
    
    n_hvg = adata.var.highly_variable.sum()
    print(f"    HVGs: {n_hvg} (including forced fluidity genes)")
    
    # Plot HVG
    sc.pl.highly_variable_genes(adata, save='_hvg.png', show=False)
    
    return adata

# ============================================================================
# STEP 4: PCA & UMAP
# ============================================================================
def dimensionality_reduction(adata):
    """PCA, neighbors, UMAP."""
    print("\n[4] Dimensionality Reduction...")
    
    # Scale (on HVGs only)
    adata_hvg = adata[:, adata.var.highly_variable].copy()
    sc.pp.scale(adata_hvg, max_value=10)
    
    # PCA
    sc.tl.pca(adata_hvg, svd_solver='arpack', n_comps=50, random_state=SEED)
    
    # Copy PCA results back
    adata.obsm['X_pca'] = adata_hvg.obsm['X_pca']
    adata.uns['pca'] = adata_hvg.uns['pca']
    
    # Elbow plot
    sc.pl.pca_variance_ratio(adata, n_pcs=50, save='_elbow.png', show=False)
    
    # Neighbors & UMAP
    sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30, random_state=SEED)
    sc.tl.umap(adata, random_state=SEED)
    
    print(f"    PCA: 50 components computed, using 30 for neighbors")
    
    return adata

# ============================================================================
# STEP 5: CLUSTERING
# ============================================================================
def cluster_cells(adata):
    """Leiden clustering at multiple resolutions."""
    print("\n[5] Clustering (Leiden)...")
    
    for res in [0.4, 0.6, 0.8, 1.0]:
        key = f'leiden_res{res}'
        sc.tl.leiden(adata, resolution=res, key_added=key, random_state=SEED)
        n_clusters = adata.obs[key].nunique()
        print(f"    Resolution {res}: {n_clusters} clusters")
    
    # Use 0.8 as default
    adata.obs['leiden'] = adata.obs['leiden_res0.8']
    
    # UMAP plots
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    sc.pl.umap(adata, color='leiden', ax=axes[0], show=False, title='Clusters')
    sc.pl.umap(adata, color='condition', ax=axes[1], show=False, title='Condition',
               palette=['#2166AC', '#F4A582', '#D6604D', '#B2182B'])
    if 'cell_type' in adata.obs.columns:
        sc.pl.umap(adata, color='cell_type', ax=axes[2], show=False, title='Cell Type (ground truth)')
    plt.tight_layout()
    plt.savefig('analysis/figures/02_umap_overview.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    return adata

# ============================================================================
# STEP 6: CELL TYPE ANNOTATION
# ============================================================================
def annotate_cell_types(adata):
    """Score and annotate cell types based on marker genes."""
    print("\n[6] Cell Type Annotation...")
    
    # Score each cell type signature
    for ct, markers in CELL_MARKERS.items():
        available = [g for g in markers if g in adata.var_names]
        if available:
            sc.tl.score_genes(adata, gene_list=available, score_name=f'score_{ct}')
    
    # Assign based on highest score
    score_cols = [c for c in adata.obs.columns if c.startswith('score_')]
    if score_cols:
        scores = adata.obs[score_cols].values
        ct_names = [c.replace('score_', '') for c in score_cols]
        best = np.argmax(scores, axis=1)
        adata.obs['predicted_cell_type'] = [ct_names[i] for i in best]
        
        print("    Predicted cell type distribution:")
        for ct in sorted(adata.obs['predicted_cell_type'].unique()):
            n = (adata.obs['predicted_cell_type'] == ct).sum()
            print(f"      {ct}: {n}")
    
    # Dot plot of markers
    marker_list = []
    for ct, markers in CELL_MARKERS.items():
        for g in markers:
            if g in adata.var_names:
                marker_list.append(g)
    
    if marker_list and 'predicted_cell_type' in adata.obs.columns:
        sc.pl.dotplot(adata, var_names=marker_list, groupby='predicted_cell_type',
                      save='_cell_type_markers.png', show=False)
    
    return adata

# ============================================================================
# STEP 7: DIFFERENTIAL EXPRESSION
# ============================================================================
def differential_expression(adata):
    """DE between conditions and clusters."""
    print("\n[7] Differential Expression...")
    
    # Cluster markers
    sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon', key_added='markers_leiden')
    sc.pl.rank_genes_groups(adata, n_genes=15, key='markers_leiden', 
                            save='_cluster_markers.png', show=False)
    
    # Save cluster markers
    markers_df = sc.get.rank_genes_groups_df(adata, group=None, key='markers_leiden')
    markers_df.to_csv('analysis/de/cluster_markers.csv', index=False)
    print(f"    Saved cluster markers: {len(markers_df)} gene-cluster pairs")
    
    # Condition DE (wound vs control)
    if 'condition' in adata.obs.columns:
        for condition in ['wound_3d', 'wound_7d', 'wound_14d']:
            if condition in adata.obs['condition'].values:
                mask = adata.obs['condition'].isin([condition, 'control'])
                adata_sub = adata[mask].copy()
                try:
                    sc.tl.rank_genes_groups(adata_sub, 'condition', method='wilcoxon',
                                            groups=[condition], reference='control',
                                            key_added=f'de_{condition}')
                    de_df = sc.get.rank_genes_groups_df(adata_sub, group=condition, 
                                                         key=f'de_{condition}')
                    de_df.to_csv(f'analysis/de/de_{condition}_vs_control.csv', index=False)
                    n_sig = (de_df['pvals_adj'] < 0.05).sum()
                    print(f"    {condition} vs control: {n_sig} significant genes (FDR < 0.05)")
                except Exception as e:
                    print(f"    [WARN] DE failed for {condition}: {e}")
    
    return adata

# ============================================================================
# STEP 8: TISSUE FLUIDITY SCORING
# ============================================================================
def tissue_fluidity_analysis(adata):
    """Score tissue fluidity gene sets and analyze across conditions."""
    print("\n[8] Tissue Fluidity Gene Set Scoring...")
    
    for name, genes in FLUIDITY_GENE_SETS.items():
        available = [g for g in genes if g in adata.var_names]
        if available:
            sc.tl.score_genes(adata, gene_list=available, score_name=f'fluidity_{name}')
            print(f"    {name}: {len(available)}/{len(genes)} genes scored")
    
    # Fluidity score UMAPs
    fluidity_scores = [c for c in adata.obs.columns if c.startswith('fluidity_')]
    if fluidity_scores:
        n_plots = len(fluidity_scores)
        ncols = min(3, n_plots)
        nrows = (n_plots + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 5 * nrows))
        if nrows * ncols == 1:
            axes = np.array([axes])
        axes = axes.flatten()
        
        for i, score in enumerate(fluidity_scores):
            sc.pl.umap(adata, color=score, ax=axes[i], show=False, 
                       cmap='RdBu_r', title=score.replace('fluidity_', ''))
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)
        
        plt.tight_layout()
        plt.savefig('analysis/figures/03_fluidity_scores_umap.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    # Box plots: fluidity scores by condition
    if fluidity_scores and 'condition' in adata.obs.columns:
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.flatten()
        cond_order = ['control', 'wound_3d', 'wound_7d', 'wound_14d']
        colors = {'control': '#2166AC', 'wound_3d': '#F4A582', 'wound_7d': '#D6604D', 'wound_14d': '#B2182B'}
        
        for i, score in enumerate(fluidity_scores[:6]):
            ax = axes[i]
            data_by_cond = []
            labels = []
            for cond in cond_order:
                if cond in adata.obs['condition'].values:
                    vals = adata.obs.loc[adata.obs['condition'] == cond, score].values
                    data_by_cond.append(vals)
                    labels.append(cond)
            
            bp = ax.boxplot(data_by_cond, labels=labels, patch_artist=True)
            for patch, label in zip(bp['boxes'], labels):
                patch.set_facecolor(colors.get(label, 'grey'))
                patch.set_alpha(0.7)
            ax.set_title(score.replace('fluidity_', ''), fontsize=12, fontweight='bold')
            ax.set_ylabel('Gene Set Score')
            ax.tick_params(axis='x', rotation=30)
        
        for j in range(len(fluidity_scores), len(axes)):
            axes[j].set_visible(False)
        
        plt.suptitle('Tissue Fluidity Scores Across Wound Healing Phases', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('analysis/figures/04_fluidity_boxplots.png', dpi=150, bbox_inches='tight')
        plt.close()
    
    # Feature plots for individual fluidity genes
    key_fluidity_genes = ['Vim', 'Cdh1', 'Fn1', 'Mmp2', 'Acta2', 'Tgfb1', 'Yap1', 'Piezo1']
    available_genes = [g for g in key_fluidity_genes if g in adata.var_names]
    if available_genes:
        sc.pl.umap(adata, color=available_genes, ncols=4, cmap='Reds', frameon=False,
                   save='_fluidity_genes.png', show=False)
    
    return adata

# ============================================================================
# STEP 9: SAVE RESULTS
# ============================================================================
def save_results(adata):
    """Save processed data and results."""
    print("\n[9] Saving Results...")
    
    # Save processed AnnData
    adata.write_h5ad('analysis/clustering/processed_adata.h5ad')
    print(f"    Saved: analysis/clustering/processed_adata.h5ad")
    
    # Save UMAP coordinates
    umap_df = pd.DataFrame(adata.obsm['X_umap'], columns=['UMAP1', 'UMAP2'], index=adata.obs_names)
    umap_df = pd.concat([umap_df, adata.obs], axis=1)
    umap_df.to_csv('analysis/clustering/umap_coordinates.csv')
    print(f"    Saved: analysis/clustering/umap_coordinates.csv")
    
    # Save cell metadata
    adata.obs.to_csv('analysis/clustering/cell_metadata.csv')
    print(f"    Saved: analysis/clustering/cell_metadata.csv")
    
    print("\n" + "=" * 70)
    print("ANALYSIS PIPELINE COMPLETE")
    print("=" * 70)
    print(f"Figures: analysis/figures/")
    print(f"DE results: analysis/de/")
    print(f"Clustering: analysis/clustering/")
    
    return adata

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 70)
    print("scRNA-seq Analysis Pipeline — Tissue Fluidity in Wound Healing")
    print("Author: Rahul M Sarate")
    print("=" * 70)
    
    adata = load_data()
    adata = qc_filter(adata)
    adata = normalize_and_hvg(adata)
    adata = dimensionality_reduction(adata)
    adata = cluster_cells(adata)
    adata = annotate_cell_types(adata)
    adata = differential_expression(adata)
    adata = tissue_fluidity_analysis(adata)
    adata = save_results(adata)
    
    return adata

if __name__ == '__main__':
    main()
