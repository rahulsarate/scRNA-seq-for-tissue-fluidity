# Day 12: Tissue Fluidity Scoring — The Core Research Question

> **Goal**: Master the fluidity scoring methodology — this is YOUR research contribution and the #1 thing interviewers will ask about.

---

## What Makes This Project Unique

Every scRNA-seq study does QC → clustering → DE. That's standard.

**What makes our project stand out**: We go further with a **hypothesis-driven fluidity scoring framework** using 5 biologically-curated gene signatures.

---

## The 5 Fluidity Gene Signatures — Deep Dive

### 1. EMT (Epithelial-Mesenchymal Transition)

```
Cdh1 (E-cadherin) DOWN + Vim (Vimentin) UP = EMT happening

    Epithelial (stuck):              Mesenchymal (mobile):
    ┌────┐┌────┐┌────┐              ┌────┐
    │cell││cell││cell│              │cell│→
    │ E  ││ E  ││ E  │              │ M  │   → migrating
    └────┘└────┘└────┘              └────┘→
    ^^^^^^^^^^^^^^^^^^^
    Tight junctions (E-cadherin)     Lost junctions, gained motility
```

**Genes**: Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2

| Gene | Role | Expected in Wound |
|------|------|-------------------|
| Vim | Mesenchymal cytoskeleton | ↑ UP at wound_7d |
| Cdh1 | Cell-cell adhesion ("glue") | ↓ DOWN at wound_7d |
| Snai1/2 | EMT transcription factors | ↑ UP at wound_3d–7d |
| Twist1 | EMT inducer | ↑ UP during migration |
| Zeb1/2 | EMT master regulators | ↑ UP in migrating cells |

### 2. ECM Remodeling

```
Old tissue → Break down (MMPs) → Build new (Collagens)

    ████████████          ░░░░░░░░░░          ████████████
    Old ECM     →  MMPs destroy  →  New ECM deposited
    (rigid)        old scaffold      (initially softer)
```

**Genes**: Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2

| Gene | Role | Expected |
|------|------|----------|
| Mmp2/9/14 | "Bulldozers" cutting old ECM | ↑ wound_3d–7d |
| Col1a1/3a1 | Building new collagen scaffold | ↑ wound_7d–14d |
| Fn1 | Fibronectin (migration highway) | ↑ wound_7d |
| Timp1 | MMP inhibitor (stop destruction) | ↑ wound_14d |
| Lox/Loxl2 | Cross-linking collagen (stiffening) | ↑ wound_14d |

### 3. Cell Migration

**Genes**: Rac1, Cdc42, Itgb1, RhoA, Rock1, Rock2

These are the cell's **motor and wheels**:
- **Rac1/Cdc42**: Push the cell forward (leading edge)
- **RhoA/Rock**: Contract the rear (squeeze forward)
- **Itgb1**: Integrins — "feet" that grip the ECM

### 4. Mechanotransduction

**Genes**: Yap1, Wwtr1 (TAZ), Piezo1, Trpv4, Lats1, Lats2

How cells **sense** physical forces:
- **Piezo1**: Ion channel that opens when membrane is stretched
- **YAP/TAZ**: Transcription factors activated by stiff/stretched environment
- **Lats1/2**: Kinases that regulate YAP/TAZ (part of Hippo pathway)

### 5. Wound Signals

**Genes**: Tgfb1, Tgfb2, Tgfb3, Pdgfa, Vegfa, Wnt5a, Il6, Tnf

Chemical **messengers** coordinating the response:
- **TGF-β**: Master regulator — drives EMT, fibrosis, and immune response
- **VEGFA**: "Build blood vessels here" signal
- **IL-6/TNF**: Inflammatory signals (peak at wound_3d)

---

## How Gene Set Scoring Works

### The Algorithm (sc.tl.score_genes)

```python
for name, genes in FLUIDITY_GENE_SETS.items():
    available = [g for g in genes if g in adata.var_names]
    sc.tl.score_genes(adata, gene_list=available, score_name=f'fluidity_{name}')
```

**What happens inside `sc.tl.score_genes`**:

```
For each cell:
  1. Calculate mean expression of signature genes
     → mean(Vim, Cdh1, Snai1, ...) = 2.1
     
  2. Select random "control" genes with similar expression levels
     → mean(Gene_0042, Gene_0187, ...) = 1.4
     
  3. Score = signature_mean - control_mean
     → score = 2.1 - 1.4 = 0.7
     
  Score > 0: signature is ACTIVE (above background)
  Score < 0: signature is INACTIVE (below background)
  Score ~ 0: signature at background level
```

**Why subtract random controls?** To account for global expression differences between cells. A cell with generally high expression would score high for EVERYTHING without this correction.

---

## Expected Results: Fluidity Across Conditions

```
           Fluidity Score
    HIGH   │               ╭─╮
           │             ╭─╯ │
           │           ╭─╯   │
           │         ╭─╯     ╰─╮
           │       ╭─╯         ╰─╮
           │     ╭─╯             ╰─╮
    LOW    │   ╭─╯                 ╰──
           │ ──╯
           └─────────────────────────────
            ctrl   wound_3d   wound_7d   wound_14d
                                 ▲
                                 │
                          PEAK FLUIDITY
                      (max EMT + ECM + migration)
```

### Expected Pattern Per Signature

| Signature | control | wound_3d | wound_7d | wound_14d |
|-----------|---------|----------|----------|-----------|
| EMT | Low | Medium | **HIGH** | Medium |
| ECM Remodeling | Low | Low-Med | **HIGH** | Medium |
| Cell Migration | Low | **HIGH** | HIGH | Low |
| Mechanotransduction | Low | Medium | **HIGH** | High |
| Wound Signals | Low | **HIGH** | Medium | Low |

**Key biology**: 
- Migration and wound signals peak EARLY (day 3) — "sound the alarm and start moving"
- EMT and ECM peak at day 7 — "restructure the tissue"
- Mechanotransduction stays elevated — tissue senses ongoing changes
- Everything trends back toward control by day 14 — "healing complete"

---

## Visualizing Fluidity Scores

### UMAP Feature Plots

```python
# Each UMAP colored by a different fluidity score:
fluidity_scores = [c for c in adata.obs.columns if c.startswith('fluidity_')]

for score in fluidity_scores:
    sc.pl.umap(adata, color=score, cmap='RdBu_r',
               title=score.replace('fluidity_', ''))
```

**What these show**: 
- Blue cells = low fluidity score
- Red cells = high fluidity score
- You can see which CLUSTERS and CONDITIONS have the highest fluidity

### Box Plots by Condition

```python
# For each fluidity signature, compare scores across conditions:
import seaborn as sns

for score in fluidity_scores:
    sns.boxplot(data=adata.obs, x='condition', y=score,
                order=['control', 'wound_3d', 'wound_7d', 'wound_14d'])
```

---

## Cell-Type-Specific Fluidity (Advanced)

### Why Cell Type Matters

Not all cells become equally "fluid":
- **Fibroblasts**: HIGH EMT and ECM scores (they remodel the matrix)
- **Keratinocytes**: HIGH migration scores (they re-epithelialize)
- **Macrophages**: HIGH wound signal scores (they direct the response)
- **T cells**: LOW fluidity overall (not their role)

```
Fluidity Heatmap (cell_type × signature):

                 EMT    ECM    Migration  Mechano.  Signals
Fibroblast       ████   █████  ███        ████      ██
Myofibroblast    █████  █████  ██         █████     ███
Keratinocyte     ███    ██     █████      ████      ██
Macrophage       ██     ██     ████       ██        █████
Neutrophil       █      █      ████       █         ████
T Cell           █      █      ██         █         ██
Endothelial      ██     ███    ███        ███       ███

███ = High score
█   = Low score
```

---

## Composite Fluidity Score

### Combining All 5 Signatures

```python
# Average all 5 fluidity scores into one composite:
fluidity_cols = [c for c in adata.obs.columns if c.startswith('fluidity_')]
adata.obs['fluidity_composite'] = adata.obs[fluidity_cols].mean(axis=1)
```

This gives one number per cell representing **overall tissue fluidity**. Useful for:
- Quick comparison across conditions
- Correlation with other variables
- Dashboard visualization

---

## Interview Q&A

### Q: "What is tissue fluidity and how do you measure it?"

> "Tissue fluidity describes the ability of tissue to transition from a solid-like, rigid state to a fluid-like, mobile state during wound healing. I measure it computationally using 5 curated gene signatures — EMT, ECM remodeling, cell migration, mechanotransduction, and wound signals — totaling about 40 genes. For each cell, I calculate a per-signature score using Scanpy's gene scoring function, which compares signature gene expression to random background genes. Higher scores indicate more active fluidity programs. We see peak fluidity at wound day 7 during the proliferative phase, consistent with maximum cell migration and ECM restructuring."

### Q: "Why these specific 5 gene categories?"

> "They represent the 5 biological processes that physically enable tissue fluidity. EMT allows cells to break free from neighbors. ECM remodeling softens the structural scaffold. Migration machinery actually moves cells. Mechanotransduction senses the physical environment. Wound signals coordinate everything. Together they capture the full picture of how tissue transitions from solid to fluid and back."

### Q: "Can you walk me through the scoring algorithm?"

> "For each cell, the algorithm: (1) calculates mean expression of the signature genes, (2) selects a set of random control genes with similar expression distributions, (3) subtracts the control mean from the signature mean. This background subtraction is critical — without it, cells with generally high expression would falsely score high for every signature. A positive score means the signature is more active than expected by chance."

### Q: "What was your most interesting finding about fluidity?"

> "The most striking finding is that fluidity is cell-type-specific. Fibroblasts and myofibroblasts show the highest EMT and ECM remodeling scores at wound day 7, while macrophages lead in wound signaling at day 3. This means different cell types contribute different aspects of fluidity at different timepoints — it's a coordinated multi-cell-type program, not a global tissue-wide switch."

---

## Self-Check Questions

1. **Name all 5 fluidity signature categories** → EMT, ECM remodeling, Cell migration, Mechanotransduction, Wound signals
2. **What does EMT stand for?** → Epithelial-Mesenchymal Transition
3. **Which gene is the "cell glue" that goes DOWN during EMT?** → Cdh1 (E-cadherin)
4. **What are MMPs?** → Matrix Metalloproteinases — enzymes that break down ECM
5. **When does fluidity peak?** → wound_7d (proliferative phase)
6. **How does sc.tl.score_genes calculate a score?** → Signature mean minus random control mean
7. **Why subtract control genes?** → To correct for global expression differences between cells
8. **Which cell type has highest ECM remodeling score?** → Fibroblasts/Myofibroblasts
9. **What does a negative fluidity score mean?** → Signature less active than background
10. **What is the composite fluidity score?** → Average of all 5 individual signature scores

---

**Next**: [Day 13 — Pathway Enrichment Analysis](Day_13_Pathway_Enrichment.md)
