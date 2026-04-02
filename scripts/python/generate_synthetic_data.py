#!/usr/bin/env python3
"""
Synthetic scRNA-seq Data Generator for Wound Healing / Tissue Fluidity Research
===============================================================================
Author: Rahul M Sarate
Project: Dynamic regulation of tissue fluidity controls skin repair during wound healing

Generates realistic synthetic scRNA-seq data mimicking mouse skin wound healing
with multiple cell types, conditions (control, wound_3d, wound_7d, wound_14d),
and tissue fluidity gene signatures.

Usage:
    python scripts/python/generate_synthetic_data.py

Output:
    data/synthetic/synthetic_counts.h5ad
    data/synthetic/synthetic_metadata.csv
    data/synthetic/synthetic_counts_matrix.csv
"""

import numpy as np
import pandas as pd
import scipy.sparse as sp
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
SEED = 42
np.random.seed(SEED)

N_CELLS = 8000          # Total cells (reasonable for demo analysis)
N_GENES = 2000          # Number of genes
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'synthetic')

# Conditions and their cell proportions
CONDITIONS = {
    'control':   {'n_cells': 2000, 'label': 'Homeostatic skin'},
    'wound_3d':  {'n_cells': 2000, 'label': 'Inflammatory phase'},
    'wound_7d':  {'n_cells': 2000, 'label': 'Proliferative phase'},
    'wound_14d': {'n_cells': 2000, 'label': 'Remodeling phase'},
}

# Cell types with expected proportions per condition
# Format: {cell_type: {condition: proportion}}
CELL_TYPE_PROPORTIONS = {
    'Basal_Keratinocyte':    {'control': 0.25, 'wound_3d': 0.10, 'wound_7d': 0.20, 'wound_14d': 0.22},
    'Diff_Keratinocyte':     {'control': 0.20, 'wound_3d': 0.05, 'wound_7d': 0.10, 'wound_14d': 0.18},
    'Fibroblast':            {'control': 0.20, 'wound_3d': 0.15, 'wound_7d': 0.20, 'wound_14d': 0.20},
    'Myofibroblast':         {'control': 0.02, 'wound_3d': 0.08, 'wound_7d': 0.15, 'wound_14d': 0.05},
    'Macrophage':            {'control': 0.08, 'wound_3d': 0.25, 'wound_7d': 0.12, 'wound_14d': 0.10},
    'Neutrophil':            {'control': 0.02, 'wound_3d': 0.15, 'wound_7d': 0.03, 'wound_14d': 0.02},
    'T_Cell':                {'control': 0.05, 'wound_3d': 0.08, 'wound_7d': 0.06, 'wound_14d': 0.05},
    'Endothelial':           {'control': 0.08, 'wound_3d': 0.06, 'wound_7d': 0.08, 'wound_14d': 0.08},
    'Hair_Follicle_SC':      {'control': 0.06, 'wound_3d': 0.03, 'wound_7d': 0.03, 'wound_14d': 0.05},
    'Melanocyte':            {'control': 0.04, 'wound_3d': 0.05, 'wound_7d': 0.03, 'wound_14d': 0.05},
}

# Cell-type-specific marker genes (mouse gene symbols)
MARKER_GENES = {
    'Basal_Keratinocyte':    ['Krt14', 'Krt5', 'Tp63', 'Itga6', 'Itgb1', 'Col17a1'],
    'Diff_Keratinocyte':     ['Krt10', 'Krt1', 'Ivl', 'Lor', 'Flg', 'Dsg1'],
    'Fibroblast':            ['Col1a1', 'Col3a1', 'Dcn', 'Pdgfra', 'Lum', 'Fbln1'],
    'Myofibroblast':         ['Acta2', 'Tagln', 'Cnn1', 'Myh11', 'Postn', 'Tgfbi'],
    'Macrophage':            ['Cd68', 'Adgre1', 'Csf1r', 'Mrc1', 'Lyz2', 'Fcgr1'],
    'Neutrophil':            ['S100a8', 'S100a9', 'Ly6g', 'Cxcr2', 'Mmp8', 'Il1b'],
    'T_Cell':                ['Cd3d', 'Cd3e', 'Cd4', 'Cd8a', 'Lck', 'Trac'],
    'Endothelial':           ['Pecam1', 'Cdh5', 'Kdr', 'Flt1', 'Vwf', 'Emcn'],
    'Hair_Follicle_SC':      ['Sox9', 'Lgr5', 'Cd34', 'Lhx2', 'Tcf3', 'Nfatc1'],
    'Melanocyte':            ['Dct', 'Tyrp1', 'Pmel', 'Sox10', 'Mitf', 'Tyr'],
}

# Tissue fluidity gene signature (key for the research focus)
TISSUE_FLUIDITY_GENES = {
    'emt_markers':           ['Vim', 'Cdh1', 'Cdh2', 'Snai1', 'Snai2', 'Twist1', 'Zeb1', 'Zeb2'],
    'ecm_remodeling':        ['Fn1', 'Col1a1', 'Col3a1', 'Mmp2', 'Mmp9', 'Mmp14', 'Timp1', 'Lox', 'Loxl2'],
    'cell_migration':        ['Rac1', 'Cdc42', 'RhoA', 'Itgb1', 'Itga6', 'Cxcl12', 'Cxcr4'],
    'mechanotransduction':   ['Yap1', 'Wwtr1', 'Piezo1', 'Trpv4', 'Lats1', 'Lats2'],
    'wound_signals':         ['Tgfb1', 'Tgfb2', 'Tgfb3', 'Pdgfa', 'Pdgfb', 'Fgf2', 'Vegfa', 'Wnt5a'],
    'cytoskeleton':          ['Actb', 'Actg1', 'Tuba1a', 'Tubb3', 'Msn', 'Ezr', 'Rdx'],
}

# Wound-phase-specific upregulation factors for fluidity genes
FLUIDITY_CONDITION_EFFECTS = {
    'emt_markers':         {'control': 1.0, 'wound_3d': 2.5, 'wound_7d': 3.0, 'wound_14d': 1.5},
    'ecm_remodeling':      {'control': 1.0, 'wound_3d': 1.5, 'wound_7d': 3.5, 'wound_14d': 2.0},
    'cell_migration':      {'control': 1.0, 'wound_3d': 3.0, 'wound_7d': 2.5, 'wound_14d': 1.2},
    'mechanotransduction': {'control': 1.0, 'wound_3d': 2.0, 'wound_7d': 3.5, 'wound_14d': 2.5},
    'wound_signals':       {'control': 1.0, 'wound_3d': 4.0, 'wound_7d': 2.5, 'wound_14d': 1.5},
    'cytoskeleton':        {'control': 1.0, 'wound_3d': 2.0, 'wound_7d': 2.5, 'wound_14d': 1.8},
}

# ============================================================================
# FUNCTIONS
# ============================================================================

def get_all_special_genes():
    """Collect all named marker and fluidity genes."""
    genes = set()
    for markers in MARKER_GENES.values():
        genes.update(markers)
    for category_genes in TISSUE_FLUIDITY_GENES.values():
        genes.update(category_genes)
    return sorted(genes)


def generate_gene_names(n_genes, special_genes):
    """Generate gene name list including all special genes plus random ones."""
    gene_names = list(special_genes)
    n_random = n_genes - len(gene_names)
    if n_random > 0:
        random_genes = [f"Gene_{i:04d}" for i in range(n_random)]
        gene_names.extend(random_genes)
    return gene_names[:n_genes]


def generate_base_expression(n_cells, n_genes):
    """Generate base expression using negative binomial (realistic scRNA-seq)."""
    # Most genes lowly expressed, some highly expressed (gamma-Poisson)
    mu = np.random.exponential(scale=0.5, size=n_genes)
    dispersion = np.random.uniform(0.1, 2.0, size=n_genes)
    
    counts = np.zeros((n_cells, n_genes), dtype=np.float32)
    for g in range(n_genes):
        r = 1.0 / dispersion[g]
        p = r / (r + mu[g])
        counts[:, g] = np.random.negative_binomial(max(1, int(r)), min(0.99, max(0.01, p)), size=n_cells)
    
    return counts


def add_cell_type_signatures(counts, gene_names, cell_types, conditions):
    """Add cell-type-specific marker gene expression."""
    gene_idx = {g: i for i, g in enumerate(gene_names)}
    
    for i, (ct, cond) in enumerate(zip(cell_types, conditions)):
        if ct in MARKER_GENES:
            for gene in MARKER_GENES[ct]:
                if gene in gene_idx:
                    # Strong upregulation of marker genes in the correct cell type
                    boost = np.random.poisson(lam=15) + 10
                    counts[i, gene_idx[gene]] += boost
    
    return counts


def add_fluidity_signatures(counts, gene_names, cell_types, conditions):
    """Add tissue-fluidity gene expression that varies by condition and cell type."""
    gene_idx = {g: i for i, g in enumerate(gene_names)}
    
    # Cell types most affected by tissue fluidity changes
    fluidity_responsive = {
        'Fibroblast': 1.5, 'Myofibroblast': 2.0, 'Basal_Keratinocyte': 1.3,
        'Endothelial': 1.2, 'Macrophage': 1.0, 'Hair_Follicle_SC': 0.8,
    }
    
    for i, (ct, cond) in enumerate(zip(cell_types, conditions)):
        ct_factor = fluidity_responsive.get(ct, 0.5)
        
        for category, genes in TISSUE_FLUIDITY_GENES.items():
            cond_effect = FLUIDITY_CONDITION_EFFECTS[category].get(cond, 1.0)
            for gene in genes:
                if gene in gene_idx:
                    boost = np.random.poisson(lam=3 * cond_effect * ct_factor)
                    counts[i, gene_idx[gene]] += boost
    
    return counts


def add_dropout(counts, dropout_rate=0.3):
    """Add realistic dropout (zero-inflation) typical of scRNA-seq."""
    mask = np.random.binomial(1, 1 - dropout_rate, size=counts.shape)
    counts = counts * mask
    return counts


def generate_metadata(cell_types, conditions, n_cells_per_condition):
    """Generate cell-level metadata."""
    barcodes = [f"CELL_{i:06d}" for i in range(sum(n_cells_per_condition))]
    
    # Add sample replicates
    samples = []
    for cond, n in zip(conditions, n_cells_per_condition):
        half = n // 2
        samples.extend([f"{cond}_rep1"] * half)
        samples.extend([f"{cond}_rep2"] * (n - half))
    
    metadata = pd.DataFrame({
        'barcode': barcodes[:len(cell_types)],
        'cell_type': cell_types,
        'condition': [c for c, n in zip(conditions, n_cells_per_condition) for _ in range(n)],
        'sample': samples[:len(cell_types)],
        'organism': 'Mus musculus',
        'tissue': 'skin',
        'wound_phase': [
            {'control': 'homeostasis', 'wound_3d': 'inflammatory', 
             'wound_7d': 'proliferative', 'wound_14d': 'remodeling'}[c]
            for c, n in zip(conditions, n_cells_per_condition) for _ in range(n)
        ],
    })
    
    return metadata


def main():
    print("=" * 70)
    print("Synthetic scRNA-seq Data Generator")
    print("Project: Tissue Fluidity in Wound Healing (Sarate Lab)")
    print("=" * 70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Determine cell assignments
    print("\n[1/6] Assigning cells to types and conditions...")
    all_cell_types = []
    all_conditions = []
    n_cells_list = []
    condition_names = []
    
    for cond, info in CONDITIONS.items():
        n = info['n_cells']
        n_cells_list.append(n)
        condition_names.append(cond)
        
        # Assign cell types based on proportions
        props = [CELL_TYPE_PROPORTIONS[ct][cond] for ct in CELL_TYPE_PROPORTIONS]
        props = np.array(props) / sum(props)  # normalize
        ct_names = list(CELL_TYPE_PROPORTIONS.keys())
        
        cell_assignments = np.random.choice(ct_names, size=n, p=props)
        all_cell_types.extend(cell_assignments)
        all_conditions.extend([cond] * n)
    
    total_cells = len(all_cell_types)
    print(f"    Total cells: {total_cells}")
    for ct in CELL_TYPE_PROPORTIONS:
        ct_count = all_cell_types.count(ct) if isinstance(all_cell_types, list) else sum(1 for x in all_cell_types if x == ct)
        print(f"    {ct}: {ct_count}")
    
    # Step 2: Generate gene names
    print("\n[2/6] Generating gene names...")
    special_genes = get_all_special_genes()
    gene_names = generate_gene_names(N_GENES, special_genes)
    print(f"    Total genes: {len(gene_names)}")
    print(f"    Special genes (markers + fluidity): {len(special_genes)}")
    
    # Step 3: Generate base expression
    print("\n[3/6] Generating base expression (negative binomial)...")
    counts = generate_base_expression(total_cells, len(gene_names))
    print(f"    Matrix shape: {counts.shape}")
    print(f"    Mean counts per cell: {counts.sum(axis=1).mean():.0f}")
    
    # Step 4: Add biological signals
    print("\n[4/6] Adding cell type signatures...")
    counts = add_cell_type_signatures(counts, gene_names, all_cell_types, all_conditions)
    
    print("\n[5/6] Adding tissue fluidity signatures + dropout...")
    counts = add_fluidity_signatures(counts, gene_names, all_cell_types, all_conditions)
    counts = add_dropout(counts, dropout_rate=0.3)
    counts = counts.astype(np.int32)
    counts = np.clip(counts, 0, None)  # ensure non-negative
    
    print(f"    Sparsity: {(counts == 0).sum() / counts.size:.1%}")
    print(f"    Mean counts per cell: {counts.sum(axis=1).mean():.0f}")
    print(f"    Mean genes per cell: {(counts > 0).sum(axis=1).mean():.0f}")
    
    # Step 5: Create metadata
    print("\n[6/6] Creating metadata and saving...")
    metadata = generate_metadata(all_cell_types, condition_names, n_cells_list)
    
    # Add QC-like metrics to metadata
    metadata['nCount_RNA'] = counts.sum(axis=1)
    metadata['nFeature_RNA'] = (counts > 0).sum(axis=1)
    metadata['percent_mt'] = np.random.uniform(1, 12, size=total_cells).round(2)
    
    # Save as CSV count matrix
    counts_df = pd.DataFrame(counts, columns=gene_names, index=metadata['barcode'])
    counts_df.to_csv(os.path.join(OUTPUT_DIR, 'synthetic_counts_matrix.csv'))
    print(f"    Saved: synthetic_counts_matrix.csv")
    
    # Save metadata
    metadata.to_csv(os.path.join(OUTPUT_DIR, 'synthetic_metadata.csv'), index=False)
    print(f"    Saved: synthetic_metadata.csv")
    
    # Save as H5AD (if scanpy available)
    try:
        import anndata
        adata = anndata.AnnData(
            X=sp.csr_matrix(counts),
            obs=metadata.set_index('barcode'),
            var=pd.DataFrame(index=gene_names)
        )
        adata.var['gene_name'] = gene_names
        adata.var['is_marker'] = [g in special_genes for g in gene_names]
        
        # Add fluidity category annotation
        fluidity_flat = {}
        for cat, genes in TISSUE_FLUIDITY_GENES.items():
            for g in genes:
                fluidity_flat[g] = cat
        adata.var['fluidity_category'] = [fluidity_flat.get(g, 'none') for g in gene_names]
        
        adata.write_h5ad(os.path.join(OUTPUT_DIR, 'synthetic_counts.h5ad'))
        print(f"    Saved: synthetic_counts.h5ad")
    except ImportError:
        print("    [WARN] anndata not installed — skipped H5AD output. Install: pip install anndata")
    
    # Save gene info
    gene_info = pd.DataFrame({
        'gene': gene_names,
        'is_marker': [g in special_genes for g in gene_names],
        'fluidity_category': [fluidity_flat.get(g, 'none') for g in gene_names],
    })
    gene_info.to_csv(os.path.join(OUTPUT_DIR, 'gene_info.csv'), index=False)
    print(f"    Saved: gene_info.csv")
    
    print("\n" + "=" * 70)
    print("DONE. Synthetic data generated successfully!")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 70)
    
    # Summary statistics
    print("\n--- Summary ---")
    print(f"Cells: {total_cells}")
    print(f"Genes: {len(gene_names)}")
    print(f"Conditions: {list(CONDITIONS.keys())}")
    print(f"Cell types: {list(CELL_TYPE_PROPORTIONS.keys())}")
    print(f"Tissue fluidity gene categories: {list(TISSUE_FLUIDITY_GENES.keys())}")
    print(f"Total fluidity genes: {sum(len(v) for v in TISSUE_FLUIDITY_GENES.values())}")


if __name__ == '__main__':
    main()
