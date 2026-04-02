# New Research Paradigms: Tissue Fluidity × scRNA-seq in Wound Healing
# =====================================================================
# Author: Rahul M Sarate
# Based on: "Dynamic regulation of tissue fluidity controls skin repair
#            during wound healing" (Sarate et al.)
# Date: 2026-04-02
# =====================================================================

## Executive Summary

This document brainstorms emerging research paradigms at the intersection of
**tissue fluidity**, **single-cell transcriptomics**, and **wound healing biology**.
These represent high-impact directions building on the Sarate Lab's foundational
work on how tissue mechanical properties regulate skin repair.

---

## Paradigm 1: Mechano-Transcriptomics — Linking Forces to Gene Expression

### Core Idea
Single-cell resolution mapping of how mechanical forces (stiffness, viscosity,
tissue fluidity) directly regulate gene expression programs during wound healing.

### Key Questions
1. Which gene programs activate in response to changes in tissue stiffness?
2. Are mechanosensitive transcription factors (YAP/TAZ) the primary transducers,
   or are there novel mechano-responsive pathways?
3. Can we identify "mechano-responsive cell states" that exist only under
   specific tissue fluidity conditions?

### Approach
- Combine atomic force microscopy (AFM) of wound tissue with paired scRNA-seq
- Use Piezo1/TRPV4 channel expression as proxy for force-sensing state
- Correlate YAP target gene scores with tissue stiffness measurements
- Time-resolved scRNA-seq at multiple wound phases (0h, 6h, 12h, 24h, 3d, 7d, 14d)

### Expected Outcomes
- A "mechano-transcriptomic atlas" of wound healing
- Discovery of novel mechano-responsive genes beyond YAP/TAZ
- Cell-type-specific mechano-sensitivity rankings

### Novelty Score: ★★★★★ (No one has done this at single-cell resolution)

---

## Paradigm 2: Fluidity-Guided Therapeutic Targeting

### Core Idea
Identify druggable targets that modulate tissue fluidity to accelerate wound
healing or prevent pathological scarring.

### Key Questions
1. Can we pharmacologically increase tissue fluidity in early wounds to improve healing?
2. Which MMPs/LOXs are the most impactful modulators of tissue fluidity?
3. Can we prevent keloid/hypertrophic scars by maintaining appropriate fluidity?

### Approach
- Screen small molecules that modulate tissue stiffness in vitro (collagen gels)
- Test top candidates in mouse wound models with scRNA-seq readout
- Drug targets: MMP inhibitors (selective), LOX inhibitors, ROCK inhibitors,
  YAP/TAZ modulators (verteporfin)
- Compare fibroblast gene programs: drug-treated vs untreated wounds

### Drug Target Candidates
| Target | Effect on Fluidity | Drug | Status |
|--------|-------------------|------|--------|
| ROCK1/2 | ↑ Fluidity | Y-27632, Fasudil | FDA-approved (fasudil) |
| LOX | ↑ Fluidity | BAPN | Preclinical |
| MMPs | Depends on context | Marimastat | Clinical trials (failed for cancer) |
| Piezo1 | Modulate sensing | Yoda1 (agonist) | Research tool |
| YAP | ↓ ECM production | Verteporfin | FDA-approved (other indication) |

### Novelty Score: ★★★★☆ (Translational, high clinical impact)

---

## Paradigm 3: Temporal Cell State Atlas of Wound Healing

### Core Idea
Create the definitive single-cell atlas of mouse skin wound healing with
ultra-high temporal resolution, focusing on transient cell states that
control tissue fluidity transitions.

### Key Innovation
Most wound healing scRNA-seq studies have 3-4 timepoints. We propose
**12+ timepoints** (0h, 6h, 12h, 1d, 2d, 3d, 5d, 7d, 10d, 14d, 21d, 28d)
to capture:
- Transient "fluidity activator" cell states
- EMT/MET transition intermediates
- Myofibroblast emergence and resolution kinetics

### Approach
- 10X Multiome (paired scRNA-seq + scATAC-seq) at each timepoint
- Trajectory analysis with RNA velocity + chromatin accessibility dynamics
- Identify "regulatory switches" — transcription factors that flip cell states
- Focus on fibroblast heterogeneity: resting → activated → myofibroblast → resolved

### Deliverables
- Interactive web atlas (cellxgene / UCSC Cell Browser)
- Gene regulatory networks for each cell state transition
- "Fluidity clock" — gene signature that predicts healing progress

### Novelty Score: ★★★★★ (No atlas with this temporal resolution exists)

---

## Paradigm 4: Spatial Fluidity Mapping

### Core Idea
Use spatial transcriptomics (Visium, MERFISH, Slide-seq) to map tissue fluidity
gene signatures in 2D/3D across the wound bed, creating a spatial "fluidity map".

### Key Questions
1. Is there a fluidity gradient from wound center to edge?
2. Do high-fluidity zones correlate with faster re-epithelialization?
3. Is there spatial compartmentalization of fluidity-promoting cell types?

### Approach
- 10X Visium on wound sections at 3d, 7d, 14d (thin vs thick sections)
- MERFISH (500-gene panel targeting fluidity + cell type markers)
- Integrate with scRNA-seq reference for deconvolution (RCTD/cell2location)
- Compute per-spot fluidity scores → generate spatial heatmaps
- Correlate with histological features (collagen density, cellularity)

### Predicted Findings
- Wound edge: highest EMT signature, high fluidity
- Wound center: highest inflammatory signature, moderate fluidity
- Peri-wound: intermediate states → gradual transition zone
- Granulation tissue: highest ECM remodeling, myofibroblast-dense

### Novelty Score: ★★★★★ (Spatial fluidity mapping is completely new)

---

## Paradigm 5: Predictive Healing Models (ML/AI)

### Core Idea
Build machine learning models that predict wound healing outcomes
from early (day 1-3) scRNA-seq signatures.

### Key Questions
1. Can we predict at day 3 whether a wound will heal normally or scar excessively?
2. Which early gene signatures are most predictive of outcome?
3. Can we transfer learning from mouse to human wound models?

### Approach
- Training data: scRNA-seq from wounds that heal normally vs pathologically
  (diabetic wounds, aged wounds, keloids)
- Features: cell type proportions, fluidity scores, pathway activities,
  cell-cell communication strengths
- Models: Random forest, gradient boosting, graph neural networks on
  cell-cell interaction graphs
- Validate on held-out datasets (GSE188432 aged wounds, GSE186821 diabetic)

### Model Architecture Ideas
```
Input: Day 3 scRNA-seq → 
  Feature extraction:
    - Cell type fractions (10 dim)
    - Fluidity signature scores (5 dim)
    - Top 50 DE genes (50 dim)
    - Pathway activity scores (14 dim)
  → 
  Gradient Boosting / Neural Network →
  Output: Healing score (0-1), Scar risk (0-1)
```

### Novelty Score: ★★★★☆ (Growing field, but no fluidity-focused models exist)

---

## Paradigm 6: Cross-Tissue Fluidity Comparison

### Core Idea
Compare tissue fluidity signatures across different regenerating tissues
(skin, gut, liver, lung) to identify universal vs tissue-specific
fluidity mechanisms.

### Key Questions
1. Is the EMT → fluidity → ECM remodeling cascade conserved across tissues?
2. Are there "universal fluidity genes" vs "tissue-specific fluidity genes"?
3. Why does skin scar but liver regenerates? Is fluidity the difference?

### Approach
- Curate published scRNA-seq datasets from wound/injury in:
  - Skin (our data + GSE234269, GSE188432)
  - Gut (DSS colitis models, Crohn's)
  - Liver (partial hepatectomy, CCl4 injury)
  - Lung (bleomycin fibrosis, COVID ARDS)
- Compute standardized fluidity scores in each tissue
- Cross-tissue comparison using Harmony integration
- Identify conserved "fluidity regulons" (SCENIC+)

### Hypothesis
Tissues that regenerate (gut, liver) maintain high fluidity longer,
while tissues that scar (skin, lung) lose fluidity too quickly due to
premature crosslinking and myofibroblast persistence.

### Novelty Score: ★★★★★ (Highly novel cross-tissue mechanobiology comparison)

---

## Paradigm 7: Epigenetic Memory of Tissue Fluidity

### Core Idea
Investigate whether wounds "remember" previous fluidity states through
epigenetic modifications, and how this affects subsequent wound healing.

### Supporting Evidence
- GSE197588: Wound memory in epidermal stem cells (Lrig1+)
- Previous work showing epigenetic "priming" after first wound
- Chromatin accessibility changes persist long after wound closure

### Key Questions
1. Do cells that experienced high fluidity retain epigenetic marks?
2. Does prior wound experience improve future wound healing through fluidity memory?
3. Which epigenetic mechanisms (histone marks, DNA methylation, chromatin accessibility)
   carry fluidity memory?

### Approach
- Paired scRNA-seq + scATAC-seq (10X Multiome) on:
  - First wound (naive skin)
  - Second wound (same location, 4 weeks later)
  - Control (uninjured skin)
- Compare chromatin accessibility at fluidity gene loci
- Focus on fibroblasts and hair follicle stem cells
- Use CUT&Tag for H3K27ac (active enhancers) at EMT/ECM gene loci

### Novelty Score: ★★★★★ (Wound epigenetic memory × fluidity is unexplored)

---

## Paradigm 8: Single-Cell Mechanical Phenotyping + Transcriptomics

### Core Idea
Develop methods to measure single-cell mechanical properties (stiffness,
deformability) and pair with transcriptomes from the same cells.

### Technology Ideas
- Real-time deformability cytometry (RT-DC) → sort by stiffness → scRNA-seq
- Microfluidic squeeze-flow + cell capture → single-cell RT-PCR
- Optical stretcher + droplet-based scRNA-seq
- Integrate AFM force maps with Slide-seq spatial transcriptomics

### Key Questions
1. Are "soft" (high fluidity) cells transcriptionally distinct from "stiff" cells?
2. Is there a continuous spectrum of mechanical ↔ transcriptional states?
3. Do mechanical properties predict cell fate during wound healing?

### Novelty Score: ★★★★★ (Technology development + biology, high risk/high reward)

---

## Priority Matrix

| Paradigm | Novelty | Feasibility | Impact | Priority |
|----------|---------|-------------|--------|----------|
| 1. Mechano-Transcriptomics | ★★★★★ | ★★★☆☆ | ★★★★★ | **HIGH** |
| 2. Fluidity-Guided Therapy | ★★★★☆ | ★★★★☆ | ★★★★★ | **HIGH** |
| 3. Temporal Cell State Atlas | ★★★★★ | ★★★★☆ | ★★★★☆ | **HIGH** |
| 4. Spatial Fluidity Mapping | ★★★★★ | ★★★☆☆ | ★★★★★ | **HIGH** |
| 5. Predictive ML Models | ★★★★☆ | ★★★★★ | ★★★★☆ | **MEDIUM** |
| 6. Cross-Tissue Comparison | ★★★★★ | ★★★★☆ | ★★★★★ | **HIGH** |
| 7. Epigenetic Fluidity Memory | ★★★★★ | ★★★☆☆ | ★★★★☆ | **MEDIUM** |
| 8. Mechanical Phenotyping | ★★★★★ | ★★☆☆☆ | ★★★★★ | **EXPLORATORY** |

---

## Recommended 3-Year Research Plan

### Year 1: Foundation
- Complete temporal cell state atlas (Paradigm 3) with 12 timepoints
- Generate synthetic + real data analysis pipeline (current project)
- Publish atlas paper + launch web portal

### Year 2: Spatial + Cross-Tissue
- Spatial fluidity mapping (Paradigm 4) on key timepoints
- Cross-tissue comparison (Paradigm 6) using published datasets
- Begin drug screening collaboration (Paradigm 2)

### Year 3: Translation + Innovation
- Predictive ML models (Paradigm 5) with clinical validation
- Mechano-transcriptomics pilot (Paradigm 1)
- File provisional patent on fluidity-modulating therapeutics

---

## Key Collaborations Needed

| Expertise | For Paradigm | Role |
|-----------|-------------|------|
| Biophysics / AFM | 1, 8 | Force measurements, mechanical phenotyping |
| Spatial TX core | 4 | Visium/MERFISH experiments |
| Clinical dermatology | 2, 5 | Human wound samples, clinical data |
| Machine learning | 5 | Model development, validation |
| Comparative biology | 6 | Multi-organ injury models |
| Epigenetics | 7 | CUT&Tag, ATAC-seq expertise |
| Drug discovery | 2 | HTS screening, medicinal chemistry |
