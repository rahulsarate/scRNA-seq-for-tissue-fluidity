# Day 25: Cell Communication & Signaling

> **Goal**: Understand how cells talk to each other during wound healing and how we analyze those interactions.

---

## Why Cell Communication Matters

Wound healing isn't individual cells acting alone — it's a **coordinated response**.

```
Platelet → releases PDGF → recruits Fibroblasts
Macrophage → releases TGF-β → activates Myofibroblasts
Keratinocyte → releases VEGF → stimulates Endothelial cells (angiogenesis)
Fibroblast → deposits ECM → provides migration scaffold
```

---

## Ligand-Receptor Interactions

Cells communicate through ligand-receptor pairs:

```
Sending Cell                      Receiving Cell
┌─────────────┐                  ┌─────────────┐
│             │   Ligand         │   Receptor  │
│  Fibroblast │ ──Tgfb1──────▶ │──Tgfbr2──── │ Keratinocyte
│             │                  │             │
└─────────────┘                  └─────────────┘

The sending cell EXPRESSES the ligand gene
The receiving cell EXPRESSES the receptor gene
If BOTH are expressed → interaction is likely active
```

### Key Wound Healing Signaling

| Pathway | Ligand | Receptor | Sender → Receiver | Function |
|---------|--------|----------|-------------------|----------|
| TGF-β | Tgfb1/2/3 | Tgfbr1/2 | Macro → Fibro | Myofibroblast activation |
| PDGF | Pdgfa/b | Pdgfra/b | Platelet → Fibro | Fibroblast recruitment |
| VEGF | Vegfa | Kdr/Flt1 | Kerat → Endo | Angiogenesis |
| Wnt | Wnt5a | Fzd | Multiple | Migration, polarity |
| TNF-α | Tnf | Tnfrsf1a | Macro → Multiple | Inflammation |
| IL-6 | Il6 | Il6ra | Macro → Fibro | Acute phase response |

---

## CellChat: Our Communication Analysis Tool

### What CellChat Does

```
Input:                           Output:
  scRNA-seq expression data        Which cell types talk?
  Cell type annotations            Through which pathways?
  Curated L-R database             How strong are interactions?
                                   How do they change across conditions?
```

### CellChat Workflow

```r
library(CellChat)

# 1. Create CellChat object
cellchat <- createCellChat(object = seurat_obj, group.by = "cell_type")

# 2. Set ligand-receptor database
CellChatDB <- CellChatDB.mouse    # Mouse-specific database
cellchat@DB <- CellChatDB

# 3. Identify overexpressed ligands/receptors
cellchat <- identifyOverExpressedGenes(cellchat)
cellchat <- identifyOverExpressedInteractions(cellchat)

# 4. Compute communication probability
cellchat <- computeCommunicProb(cellchat)
cellchat <- computeCommunicProbPathway(cellchat)
cellchat <- aggregateNet(cellchat)

# 5. Visualize
netVisual_circle(cellchat@net$count)          # Network diagram
netVisual_heatmap(cellchat)                    # Heatmap
netVisual_bubble(cellchat, signaling = "TGFb") # Bubble plot
```

### Python Alternative (via rpy2)

```python
# CellChat is R-native; we call it from Python using rpy2
import rpy2.robjects as ro
from rpy2.robjects import r

r('library(CellChat)')
# ... R code executed from Python
```

---

## Comparing Communication Across Conditions

### The Key Question

How does cell-cell communication change during wound healing?

```
Control:                    Wound_7d:
  Macro ──(low)──▶ Fibro      Macro ──(HIGH)──▶ Fibro
  Kerat ──(low)──▶ Endo       Kerat ──(HIGH)──▶ Endo

Peak signaling at wound_7d:
  TGF-β pathway: 5x increase
  PDGF pathway: 3x increase
  VEGF pathway: 4x increase

Resolution at wound_14d:
  Inflammatory signals decrease
  Pro-resolution signals increase
```

### Differential Communication Analysis

```r
# Compare wound_7d vs control
cellchat_merged <- mergeCellChat(
    list(control = cellchat_ctrl, wound_7d = cellchat_w7d)
)

# Find changed interactions
netVisual_diffInteraction(cellchat_merged)

# Identify signaling changes
rankNet(cellchat_merged, mode = "comparison")
```

---

## Connection to Tissue Fluidity

Cell communication drives tissue fluidity changes:

```
Signal              →  Fluidity Effect
TGF-β from macrophages →  Activates EMT in keratinocytes
                         →  Vim↑, Cdh1↓ → cells become motile
                         →  ↑ Tissue Fluidity

ECM remodeling signals  →  MMPs degrade matrix
                         →  Cells can move through tissue
                         →  ↑ Tissue Fluidity

Mechanical signals      →  YAP/TAZ activation
(Piezo1, Trpv4)         →  Cells sense stiffness
                         →  Modulates migration
```

---

## Interview Q&A

### Q: "How do you analyze cell-cell communication?"

> "We use CellChat with the mouse ligand-receptor database. For each condition (control, wound_3d, wound_7d, wound_14d), we compute communication probabilities between all cell-type pairs across all signaling pathways. Then we compare conditions to identify which interactions are upregulated during wound healing — particularly TGF-β (fibroblast activation), PDGF (recruitment), and VEGF (angiogenesis) pathways."

### Q: "What ligand-receptor interactions are most important in your project?"

> "Three key pathways: (1) TGF-β from macrophages to fibroblasts — drives myofibroblast activation and wound contraction. (2) PDGF from platelets/macrophages to fibroblasts — recruits fibroblasts to the wound. (3) Wnt5a — controls cell polarity and directional migration, directly relevant to tissue fluidity. These peak at wound_7d and resolve by wound_14d."

### Q: "How does cell communication relate to tissue fluidity?"

> "Our central hypothesis is that wound healing requires a transient increase in tissue fluidity — cells becoming more motile. This is driven by cell-cell signaling: TGF-β activates EMT programs (cells loosen junctions), MMPs from fibroblasts degrade ECM (clearing migration paths), and mechanical signals through Piezo1/YAP/TAZ let cells sense and respond to tissue stiffness. CellChat quantifies these signaling changes across wound healing phases."

---

## Self-Check Questions

1. **What is a ligand-receptor pair?** → A signaling molecule (ligand) and its cell-surface binding partner (receptor)
2. **What tool do we use for communication analysis?** → CellChat (R-based)
3. **What does CellChat need as input?** → scRNA-seq expression + cell type annotations + L-R database
4. **Name 3 key wound healing signaling pathways** → TGF-β, PDGF, VEGF
5. **What does TGF-β do in wounds?** → Activates fibroblasts → myofibroblasts; induces EMT
6. **When is signaling highest in wound healing?** → wound_7d (active repair phase)
7. **How do we compare across conditions?** → mergeCellChat + differential interaction analysis
8. **What is the CellChat database for mouse?** → `CellChatDB.mouse` — curated L-R pairs for Mus musculus
9. **How does communication affect fluidity?** → Signals activate EMT, ECM degradation, migration → increased fluidity
10. **Can we run CellChat from Python?** → Yes, via rpy2 (R-in-Python bridge)

---

**Next**: [Day 26 — Interview Prep: Project Walkthrough](Day_26_Interview_Walkthrough.md)
