#!/usr/bin/env python3
"""
Publication-Quality Visualization Suite — Wound Healing scRNA-seq
================================================================
Author: Rahul M Sarate
Project: Tissue fluidity controls skin repair during wound healing

Generates:
1. UMAP overview (clusters, conditions, cell types)
2. Tissue fluidity feature plots
3. Cell proportion analysis
4. Dot plots of key markers
5. Heatmap of DE genes
6. Fluidity score violin plots
7. Trajectory-style pseudotime visualization
8. Cell-cell communication network (simplified)

Usage:
    python scripts/python/02_visualization_suite.py
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyArrowPatch
import seaborn as sns
import warnings
import os
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
FIGDIR = 'analysis/figures/'
os.makedirs(FIGDIR, exist_ok=True)

# Colorblind-friendly palettes
CONDITION_COLORS = {
    'control': '#2166AC',
    'wound_3d': '#F4A582',
    'wound_7d': '#D6604D',
    'wound_14d': '#B2182B',
}

CELL_TYPE_COLORS = {
    'Basal_Keratinocyte': '#E69F00',
    'Diff_Keratinocyte': '#F0E442',
    'Fibroblast': '#56B4E9',
    'Myofibroblast': '#009E73',
    'Macrophage': '#D55E00',
    'Neutrophil': '#CC79A7',
    'T_Cell': '#0072B2',
    'Endothelial': '#999999',
    'Hair_Follicle_SC': '#882255',
    'Melanocyte': '#44AA99',
}

WOUND_PHASE_LABELS = {
    'control': 'Homeostasis',
    'wound_3d': 'Day 3\n(Inflammatory)',
    'wound_7d': 'Day 7\n(Proliferative)',
    'wound_14d': 'Day 14\n(Remodeling)',
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def set_publication_style():
    """Set matplotlib parameters for publication figures."""
    plt.rcParams.update({
        'font.size': 11,
        'font.family': 'sans-serif',
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 9,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'axes.spines.top': False,
        'axes.spines.right': False,
    })

set_publication_style()


def load_data():
    """Load processed data from the analysis pipeline."""
    try:
        import scanpy as sc
        adata_path = 'analysis/clustering/processed_adata.h5ad'
        if os.path.exists(adata_path):
            return sc.read_h5ad(adata_path)
    except ImportError:
        pass
    
    # Fallback: load from CSV
    umap_path = 'analysis/clustering/umap_coordinates.csv'
    meta_path = 'data/synthetic/synthetic_metadata.csv'
    
    if os.path.exists(umap_path):
        return pd.read_csv(umap_path, index_col=0)
    elif os.path.exists(meta_path):
        return pd.read_csv(meta_path)
    else:
        print("[INFO] No processed data found. Generating visualization from synthetic metadata...")
        return generate_mock_visualization_data()


def generate_mock_visualization_data():
    """Generate mock UMAP + metadata for visualization development."""
    np.random.seed(42)
    n = 8000
    
    conditions = np.random.choice(['control', 'wound_3d', 'wound_7d', 'wound_14d'], n)
    cell_types = np.random.choice(list(CELL_TYPE_COLORS.keys()), n, 
                                   p=[0.2, 0.12, 0.18, 0.08, 0.15, 0.05, 0.06, 0.07, 0.05, 0.04])
    
    # Generate UMAP coordinates with cell-type-dependent clustering
    ct_centers = {ct: (np.random.randn() * 3, np.random.randn() * 3) for ct in CELL_TYPE_COLORS}
    umap1 = np.array([ct_centers[ct][0] + np.random.randn() * 0.8 for ct in cell_types])
    umap2 = np.array([ct_centers[ct][1] + np.random.randn() * 0.8 for ct in cell_types])
    
    # Generate fluidity scores
    fluidity_emt = np.random.randn(n) * 0.5
    fluidity_ecm = np.random.randn(n) * 0.5
    
    # Boost scores based on condition
    for i in range(n):
        if conditions[i] == 'wound_3d':
            fluidity_emt[i] += 0.8
        elif conditions[i] == 'wound_7d':
            fluidity_ecm[i] += 1.0
            fluidity_emt[i] += 0.5
    
    df = pd.DataFrame({
        'UMAP1': umap1, 'UMAP2': umap2,
        'condition': conditions, 'cell_type': cell_types,
        'leiden': np.random.randint(0, 15, n).astype(str),
        'fluidity_EMT_signature': fluidity_emt,
        'fluidity_ECM_remodeling': fluidity_ecm,
        'fluidity_Cell_migration': np.random.randn(n) * 0.5 + (conditions == 'wound_3d') * 0.7,
        'fluidity_Mechanotransduction': np.random.randn(n) * 0.5 + (conditions == 'wound_7d') * 0.9,
        'nCount_RNA': np.random.lognormal(8, 0.5, n).astype(int),
        'nFeature_RNA': np.random.lognormal(6.5, 0.4, n).astype(int),
        'percent_mt': np.random.uniform(1, 12, n),
    })
    
    return df


# ============================================================================
# FIGURE 1: OVERVIEW UMAP PANEL
# ============================================================================
def plot_umap_overview(data):
    """Multi-panel UMAP: clusters, condition, cell type."""
    print("Generating Figure 1: UMAP Overview...")
    
    # Handle both AnnData and DataFrame
    if hasattr(data, 'obsm'):
        umap1 = data.obsm['X_umap'][:, 0]
        umap2 = data.obsm['X_umap'][:, 1]
        obs = data.obs
    else:
        umap1 = data['UMAP1'].values
        umap2 = data['UMAP2'].values
        obs = data
    
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    # Panel A: Clusters
    ax = axes[0]
    clusters = obs['leiden'].astype(str).values
    unique_clusters = sorted(set(clusters), key=lambda x: int(x) if x.isdigit() else x)
    cluster_colors = plt.cm.tab20(np.linspace(0, 1, len(unique_clusters)))
    color_map = {c: cluster_colors[i] for i, c in enumerate(unique_clusters)}
    colors = [color_map[c] for c in clusters]
    ax.scatter(umap1, umap2, c=colors, s=1, alpha=0.5, rasterized=True)
    ax.set_title('A. Cell Clusters', fontweight='bold')
    ax.set_xlabel('UMAP 1')
    ax.set_ylabel('UMAP 2')
    
    # Panel B: Condition
    ax = axes[1]
    for cond, color in CONDITION_COLORS.items():
        mask = obs['condition'] == cond
        ax.scatter(umap1[mask], umap2[mask], c=color, s=1, alpha=0.5, 
                   label=WOUND_PHASE_LABELS.get(cond, cond), rasterized=True)
    ax.legend(markerscale=5, frameon=False, fontsize=8)
    ax.set_title('B. Wound Healing Phase', fontweight='bold')
    ax.set_xlabel('UMAP 1')
    
    # Panel C: Cell Type
    ax = axes[2]
    ct_col = 'predicted_cell_type' if 'predicted_cell_type' in obs.columns else 'cell_type'
    if ct_col in obs.columns:
        for ct, color in CELL_TYPE_COLORS.items():
            mask = obs[ct_col] == ct
            if mask.any():
                ax.scatter(umap1[mask], umap2[mask], c=color, s=1, alpha=0.5,
                           label=ct.replace('_', ' '), rasterized=True)
        ax.legend(markerscale=5, frameon=False, fontsize=7, ncol=2, loc='lower right')
    ax.set_title('C. Cell Type', fontweight='bold')
    ax.set_xlabel('UMAP 1')
    
    for ax in axes:
        ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGDIR, 'Fig1_UMAP_overview.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(FIGDIR, 'Fig1_UMAP_overview.pdf'), bbox_inches='tight')
    plt.close()
    print("    Saved: Fig1_UMAP_overview.png/pdf")


# ============================================================================
# FIGURE 2: CELL PROPORTION ANALYSIS
# ============================================================================
def plot_cell_proportions(data):
    """Stacked bar chart of cell type proportions across conditions."""
    print("Generating Figure 2: Cell Proportions...")
    
    obs = data.obs if hasattr(data, 'obs') else data
    ct_col = 'predicted_cell_type' if 'predicted_cell_type' in obs.columns else 'cell_type'
    
    if ct_col not in obs.columns:
        print("    [SKIP] No cell type column found")
        return
    
    # Compute proportions
    props = obs.groupby(['condition', ct_col]).size().reset_index(name='count')
    totals = props.groupby('condition')['count'].transform('sum')
    props['proportion'] = props['count'] / totals
    
    # Pivot for stacked bar
    pivot = props.pivot(index='condition', columns=ct_col, values='proportion').fillna(0)
    order = ['control', 'wound_3d', 'wound_7d', 'wound_14d']
    pivot = pivot.reindex([c for c in order if c in pivot.index])
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Stacked bar
    ax = axes[0]
    pivot.plot(kind='bar', stacked=True, ax=ax, 
               color=[CELL_TYPE_COLORS.get(c, '#999') for c in pivot.columns],
               edgecolor='white', linewidth=0.5)
    ax.set_xticklabels([WOUND_PHASE_LABELS.get(c, c) for c in pivot.index], rotation=0)
    ax.set_ylabel('Proportion')
    ax.set_title('A. Cell Type Proportions', fontweight='bold')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=7, frameon=False)
    
    # Highlight: Myofibroblast & Macrophage dynamics
    ax = axes[1]
    highlight_types = ['Myofibroblast', 'Macrophage', 'Neutrophil', 'Fibroblast']
    x_labels = [WOUND_PHASE_LABELS.get(c, c).replace('\n', ' ') for c in order if c in pivot.index]
    conditions_present = [c for c in order if c in pivot.index]
    
    for ct in highlight_types:
        if ct in pivot.columns:
            vals = [pivot.loc[c, ct] if c in pivot.index else 0 for c in conditions_present]
            ax.plot(range(len(conditions_present)), vals, 'o-', 
                    color=CELL_TYPE_COLORS.get(ct, '#999'), label=ct, linewidth=2, markersize=8)
    
    ax.set_xticks(range(len(conditions_present)))
    ax.set_xticklabels(x_labels, fontsize=9)
    ax.set_ylabel('Proportion')
    ax.set_title('B. Key Cell Type Dynamics', fontweight='bold')
    ax.legend(frameon=False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGDIR, 'Fig2_cell_proportions.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(FIGDIR, 'Fig2_cell_proportions.pdf'), bbox_inches='tight')
    plt.close()
    print("    Saved: Fig2_cell_proportions.png/pdf")


# ============================================================================
# FIGURE 3: TISSUE FLUIDITY SCORES
# ============================================================================
def plot_fluidity_scores(data):
    """Violin + box plots of tissue fluidity scores across conditions."""
    print("Generating Figure 3: Tissue Fluidity Scores...")
    
    obs = data.obs if hasattr(data, 'obs') else data
    fluidity_cols = [c for c in obs.columns if c.startswith('fluidity_')]
    
    if not fluidity_cols:
        print("    [SKIP] No fluidity score columns found")
        return
    
    n_scores = len(fluidity_cols)
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    cond_order = ['control', 'wound_3d', 'wound_7d', 'wound_14d']
    
    for i, col in enumerate(fluidity_cols[:6]):
        ax = axes[i]
        plot_data = []
        positions = []
        
        for j, cond in enumerate(cond_order):
            if cond in obs['condition'].values:
                vals = obs.loc[obs['condition'] == cond, col].dropna().values
                plot_data.append(vals)
                positions.append(j)
        
        parts = ax.violinplot(plot_data, positions=positions, showmeans=False, showextrema=False)
        for k, pc in enumerate(parts['bodies']):
            color = list(CONDITION_COLORS.values())[k] if k < len(CONDITION_COLORS) else '#999'
            pc.set_facecolor(color)
            pc.set_alpha(0.6)
        
        bp = ax.boxplot(plot_data, positions=positions, widths=0.15, patch_artist=True,
                        showfliers=False, zorder=10)
        for patch in bp['boxes']:
            patch.set_facecolor('white')
            patch.set_alpha(0.8)
        
        ax.set_xticks(range(len(cond_order)))
        ax.set_xticklabels([WOUND_PHASE_LABELS.get(c, c) for c in cond_order], fontsize=8)
        title = col.replace('fluidity_', '').replace('_', ' ')
        ax.set_title(title, fontweight='bold')
        ax.set_ylabel('Score')
    
    for j in range(len(fluidity_cols), len(axes)):
        axes[j].set_visible(False)
    
    plt.suptitle('Tissue Fluidity Gene Signatures Across Wound Healing Phases', 
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGDIR, 'Fig3_fluidity_scores.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(FIGDIR, 'Fig3_fluidity_scores.pdf'), bbox_inches='tight')
    plt.close()
    print("    Saved: Fig3_fluidity_scores.png/pdf")


# ============================================================================
# FIGURE 4: WOUND HEALING TIMELINE SCHEMATIC
# ============================================================================
def plot_wound_healing_schematic():
    """Conceptual figure: wound healing phases with key molecular events."""
    print("Generating Figure 4: Wound Healing Schematic...")
    
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Phase boxes
    phases = [
        {'name': 'Homeostasis', 'x': 0, 'color': '#2166AC', 
         'events': ['Intact barrier', 'Low turnover', 'Quiescent stem cells']},
        {'name': 'Inflammatory\n(Day 1-3)', 'x': 3.5, 'color': '#F4A582',
         'events': ['Neutrophil influx', 'Macrophage recruitment', 'EMT activation',
                    '↑ MMP2/9', '↑ Tissue fluidity']},
        {'name': 'Proliferative\n(Day 4-7)', 'x': 7, 'color': '#D6604D',
         'events': ['Fibroblast proliferation', 'Myofibroblast activation', 
                    'ECM deposition', '↑ YAP/TAZ', '↑↑ Tissue fluidity']},
        {'name': 'Remodeling\n(Day 7-14+)', 'x': 10.5, 'color': '#B2182B',
         'events': ['ECM crosslinking', 'Scar maturation', 'Myofibroblast apoptosis',
                    '↓ Tissue fluidity', 'Barrier restoration']},
    ]
    
    for phase in phases:
        rect = plt.Rectangle((phase['x'], 1), 2.5, 6, 
                              facecolor=phase['color'], alpha=0.15, edgecolor=phase['color'],
                              linewidth=2, zorder=1)
        ax.add_patch(rect)
        ax.text(phase['x'] + 1.25, 7.3, phase['name'], ha='center', va='bottom',
                fontsize=12, fontweight='bold', color=phase['color'])
        
        for j, event in enumerate(phase['events']):
            ax.text(phase['x'] + 0.15, 6.2 - j * 1.0, f"• {event}", fontsize=9, va='top')
    
    # Arrows between phases
    for i in range(len(phases) - 1):
        ax.annotate('', xy=(phases[i + 1]['x'] - 0.2, 4),
                     xytext=(phases[i]['x'] + 2.7, 4),
                     arrowprops=dict(arrowstyle='->', color='#333', lw=2))
    
    # Tissue fluidity curve
    x_curve = np.linspace(0, 13, 100)
    # Bell-shaped curve peaking at day 7 (proliferative phase)
    fluidity = 0.3 + 0.7 * np.exp(-((x_curve - 8) ** 2) / 8)
    
    ax2 = ax.twinx()
    ax2.plot(x_curve, fluidity, 'k-', linewidth=3, alpha=0.7, label='Tissue Fluidity')
    ax2.fill_between(x_curve, fluidity, alpha=0.1, color='#333')
    ax2.set_ylabel('Relative Tissue Fluidity', fontsize=11)
    ax2.set_ylim(0, 1.2)
    ax2.legend(loc='upper right', frameon=False)
    
    ax.set_xlim(-0.5, 13.5)
    ax.set_ylim(0, 8.5)
    ax.set_xlabel('Wound Healing Timeline', fontsize=12, fontweight='bold')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    plt.title('Dynamic Regulation of Tissue Fluidity During Skin Wound Healing\n(Sarate et al.)',
              fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGDIR, 'Fig4_wound_healing_schematic.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(FIGDIR, 'Fig4_wound_healing_schematic.pdf'), bbox_inches='tight')
    plt.close()
    print("    Saved: Fig4_wound_healing_schematic.png/pdf")


# ============================================================================
# FIGURE 5: RESEARCH PARADIGM CONCEPT MAP
# ============================================================================
def plot_research_paradigm():
    """Conceptual figure: new research paradigms emerging from tissue fluidity + scRNA-seq."""
    print("Generating Figure 5: Research Paradigm Concept Map...")
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Central node
    ax.add_patch(plt.Circle((8, 8), 1.5, facecolor='#2166AC', alpha=0.3, edgecolor='#2166AC', lw=2))
    ax.text(8, 8, 'Tissue\nFluidity\nin Wound\nHealing', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='#2166AC')
    
    # Paradigm nodes
    paradigms = [
        {'name': 'Mechano-\nTranscriptomics', 'x': 3, 'y': 13, 'color': '#E69F00',
         'desc': 'Link mechanical forces\nto gene expression at\nsingle-cell resolution'},
        {'name': 'Fluidity-\nGuided\nTherapy', 'x': 13, 'y': 13, 'color': '#56B4E9',
         'desc': 'Target tissue stiffness\nfor improved wound\nhealing outcomes'},
        {'name': 'Temporal\nCell State\nAtlas', 'x': 1.5, 'y': 8, 'color': '#009E73',
         'desc': 'Map cell state transitions\nacross wound phases\nvia scRNA-seq'},
        {'name': 'Predictive\nHealing\nModels', 'x': 14.5, 'y': 8, 'color': '#D55E00',
         'desc': 'ML models predicting\nhealing outcomes from\nearly gene signatures'},
        {'name': 'Spatial\nFluidity\nMapping', 'x': 3, 'y': 3, 'color': '#CC79A7',
         'desc': 'Spatial transcriptomics\nto map fluidity gradients\nacross wound bed'},
        {'name': 'Cross-Tissue\nFluidity\nComparison', 'x': 13, 'y': 3, 'color': '#0072B2',
         'desc': 'Compare fluidity in\nskin, gut, lung, liver\nregeneration models'},
    ]
    
    for p in paradigms:
        ax.add_patch(plt.Circle((p['x'], p['y']), 1.2, facecolor=p['color'], alpha=0.2, 
                                edgecolor=p['color'], lw=2))
        ax.text(p['x'], p['y'] + 0.2, p['name'], ha='center', va='center', 
                fontsize=10, fontweight='bold', color=p['color'])
        
        # Description below
        ax.text(p['x'], p['y'] - 1.8, p['desc'], ha='center', va='top', fontsize=7,
                style='italic', color='#555')
        
        # Arrow from center
        dx, dy = p['x'] - 8, p['y'] - 8
        dist = np.sqrt(dx**2 + dy**2)
        ax.annotate('', xy=(8 + dx * (1 - 2.7/dist), 8 + dy * (1 - 2.7/dist)),
                     xytext=(8 + dx * 1.5/dist, 8 + dy * 1.5/dist),
                     arrowprops=dict(arrowstyle='->', color='#888', lw=1.5, connectionstyle='arc3,rad=0.1'))
    
    ax.set_xlim(-1, 17)
    ax.set_ylim(0, 15)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.title('Emerging Research Paradigms: Tissue Fluidity × scRNA-seq\n', 
              fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIGDIR, 'Fig5_research_paradigms.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(FIGDIR, 'Fig5_research_paradigms.pdf'), bbox_inches='tight')
    plt.close()
    print("    Saved: Fig5_research_paradigms.png/pdf")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 70)
    print("Visualization Suite — Tissue Fluidity in Wound Healing")
    print("Author: Rahul M Sarate")
    print("=" * 70)
    
    data = load_data()
    
    plot_umap_overview(data)
    plot_cell_proportions(data)
    plot_fluidity_scores(data)
    plot_wound_healing_schematic()
    plot_research_paradigm()
    
    print("\n" + "=" * 70)
    print("ALL FIGURES GENERATED")
    print(f"Output directory: {os.path.abspath(FIGDIR)}")
    print("=" * 70)


if __name__ == '__main__':
    main()
