# Day 24: Trajectory Analysis & RNA Velocity

> **Goal**: Understand how cells transition between states during wound healing — pseudotime and RNA velocity.

---

## Why Trajectory Analysis?

scRNA-seq captures a snapshot. But wound healing is a **process** — cells change over time.

```
Snapshot (what we capture):        Process (what actually happens):
  ○ ○ ○ ●● ■ ■ ■                    ○ → ○ → ● → ● → ■ → ■ → ■
  All cells at one moment            Cells transitioning over days

Trajectory analysis reconstructs the process from the snapshot.
```

### Wound Healing Example
```
Fibroblast → Myofibroblast (wound contraction)
  When? Peaks at wound_7d
  Driven by: TGF-β1, mechanical tension

Keratinocyte migration (re-epithelialization)
  EMT-like programs activate at wound edges
  Driven by: Vim↑, Cdh1↓, Snai1↑
```

---

## Pseudotime Analysis

### Concept
Assign each cell a "pseudotime" value = where it is in a biological process.

```
Real time:  Day 0 ───── Day 3 ───── Day 7 ───── Day 14
                        (wound)

Pseudotime: 0.0 ──── 0.3 ──── 0.6 ──── 1.0
             start              end of transition
```

### Why "Pseudo"?
We don't know the real time for each cell. We **infer** an ordering from gene expression patterns.

### Diffusion Pseudotime (DPT)

```python
import scanpy as sc

# 1. Compute diffusion map
sc.tl.diffmap(adata)

# 2. Set root cell (a control fibroblast)
adata.uns['iroot'] = find_root_cell(adata, condition='control', 
                                      cell_type='Fibroblast')

# 3. Compute pseudotime
sc.tl.dpt(adata)

# 4. Visualize
sc.pl.umap(adata, color='dpt_pseudotime', cmap='viridis')
```

### What Pseudotime Shows for Our Project

```
Expected result:

Pseudotime 0.0 ───── 0.5 ───── 1.0
(control)         (wound_7d)     (wound_14d)

Fibroblasts:
  dpt=0.0  Quiescent fibroblasts (control)
  dpt=0.3  Activated fibroblasts (wound_3d)
  dpt=0.7  Myofibroblasts (wound_7d, peak contraction)
  dpt=1.0  Resolving fibroblasts (wound_14d)
```

---

## RNA Velocity

### The Big Idea

RNA velocity goes BEYOND pseudotime — it predicts the **future state** of each cell.

```
Pseudotime:  Where is this cell in the process?
RNA Velocity: Where is this cell GOING?
```

### How It Works: Spliced vs Unspliced RNA

```
DNA → pre-mRNA (unspliced, has introns) → mRNA (spliced, mature)

If a gene is being UPREGULATED:
  Unspliced RNA ↑ (just transcribed, not yet processed)
  Ratio: high unspliced / low spliced
  → Cell is MOVING TOWARD that gene's expression

If a gene is being DOWNREGULATED:
  Unspliced RNA ↓ (transcription stopped)
  Ratio: low unspliced / high spliced
  → Cell is MOVING AWAY from that gene's expression
```

### Velocity Arrows on UMAP

```
UMAP with velocity arrows:

  ○ → → → ● → → → ■
  ↗                  ↘
  ○ → → ●            ■
  
  Arrows show direction of state transition
  Length = speed of change
```

### scVelo Implementation

```python
import scvelo as scv

# Load with spliced/unspliced counts
adata = scv.read("wound_velocity.h5ad")

# Standard preprocessing
scv.pp.filter_and_normalize(adata)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)

# Compute velocity
scv.tl.velocity(adata, mode='stochastic')
scv.tl.velocity_graph(adata)

# Visualize velocity arrows on UMAP
scv.pl.velocity_embedding_stream(adata, basis='umap',
    color='cell_type', smooth=0.8)
```

---

## Trajectory Methods in Our Project

### What's Configured

```yaml
# From analysis_config.yaml
trajectory:
  methods:
    - diffusion_pseudotime  # Scanpy
    - rna_velocity          # scVelo
  root_condition: "control"
  root_cell_type: "Fibroblast"
```

### Expected Trajectories

| Trajectory | Start | End | Key Genes |
|-----------|-------|-----|-----------|
| Fibroblast → Myofibroblast | Quiescent fib | Contractile myo | Acta2↑, Col1a1↑, Fn1↑ |
| EMT activation | Epithelial kerat | Mesenchymal-like | Vim↑, Cdh1↓, Snai1↑ |
| Immune resolution | Inflamm. macro | Resolving macro | Il6↓, Arg1↑, Mrc1↑ |
| Re-epithelialization | Wound edge kerat | Migrating kerat | Krt14↑, Itgb1↑, Mmp9↑ |

---

## Choosing Root Cells

Pseudotime needs a starting point — the "root" cell.

```python
# Strategy: Pick a control fibroblast with highest quiescence score
control_fibs = adata.obs[
    (adata.obs['condition'] == 'control') & 
    (adata.obs['cell_type'] == 'Fibroblast')
]

# Find cell closest to centroid (most "average" control fibroblast)
centroid = adata[control_fibs.index].obsm['X_pca'].mean(axis=0)
distances = np.linalg.norm(
    adata[control_fibs.index].obsm['X_pca'] - centroid, axis=1
)
root_idx = control_fibs.index[np.argmin(distances)]
adata.uns['iroot'] = np.where(adata.obs_names == root_idx)[0][0]
```

---

## Interview Q&A

### Q: "What is trajectory analysis?"

> "Trajectory analysis reconstructs biological processes from snapshot data. Each cell gets a pseudotime value representing its position along a transition — for example, fibroblast-to-myofibroblast during wound healing. We use diffusion pseudotime (Scanpy) to order cells and RNA velocity (scVelo) to predict future cell states by comparing spliced vs unspliced RNA ratios."

### Q: "How does RNA velocity work?"

> "RNA velocity exploits the kinetics of mRNA processing. Newly transcribed pre-mRNA contains introns (unspliced); mature mRNA has introns removed (spliced). If a gene has high unspliced-to-spliced ratio, it's being actively upregulated — the cell is moving toward that gene's expression state. scVelo fits a dynamical model to all genes simultaneously, producing velocity vectors that show the direction and speed of state change on the UMAP."

### Q: "What trajectories do you expect in wound healing?"

> "Four main trajectories: (1) fibroblast → myofibroblast activation for wound contraction, (2) EMT-like programs in keratinocytes at wound edges for migration, (3) inflammatory → resolving macrophage transition, and (4) keratinocyte migration for re-epithelialization. These connect directly to our tissue fluidity hypothesis — fluid tissue states enable cell migration during repair."

---

## Self-Check Questions

1. **What does trajectory analysis do?** → Reconstructs dynamic processes from snapshot data
2. **What is pseudotime?** → Computed ordering of cells along a biological process
3. **Why "pseudo"?** → We infer temporal ordering from expression, not actual time
4. **What two trajectory methods do we use?** → Diffusion pseudotime (Scanpy) and RNA velocity (scVelo)
5. **What is RNA velocity based on?** → Ratio of unspliced (pre-mRNA) to spliced (mature mRNA)
6. **High unspliced/spliced ratio means?** → Gene is being upregulated; cell is transitioning
7. **What are velocity arrows?** → Vectors on UMAP showing direction and speed of state change
8. **What is our root condition?** → Control (quiescent state before wounding)
9. **Name 2 expected trajectories** → Fibroblast → myofibroblast; EMT activation in keratinocytes
10. **Why is trajectory relevant to tissue fluidity?** → Fluid states enable cell migration during repair transitions

---

**Next**: [Day 25 — Cell Communication & Signaling](Day_25_Cell_Communication.md)
