# Day 1: Project Overview — What We Built and Why

> **Series**: 30-Day Interview Preparation Guide for scRNA-seq Wound Healing Project
> **Time**: ~2 hours of focused reading
> **Goal**: After today, you can confidently explain what this project does, why it matters, and how all the pieces fit together — in an interview, a lab meeting, or a casual conversation.

---

## 1. What This Project Is (The Elevator Pitch)

**Project title**: *Dynamic regulation of tissue fluidity controls skin repair during wound healing*
**PI**: Rahul M Sarate
**Your role**: Solo bioinformatics analyst — you built the entire computational pipeline.

Here is how to explain it in 30 seconds:

> "I built a complete single-cell RNA-seq analysis pipeline to study how skin heals after wounding. We profiled thousands of individual cells from mouse skin at four time points — healthy, 3 days, 7 days, and 14 days after wounding — and measured which genes each cell was using. Our central finding is that wound healing depends on a property called 'tissue fluidity': cells must temporarily loosen their connections, migrate into the wound, and then re-solidify. I identified the gene programs that control this switch by scoring five molecular signatures — EMT, ECM remodeling, cell migration, mechanotransduction, and wound signalling — across ten cell types and four conditions."

Let's unpack every part of that.

### This is a bioinformatics research project

Bioinformatics sits at the intersection of biology and computation. You did NOT do the lab work (the mice, the surgeries, the sequencing). You received the **data** — giant files of gene expression measurements — and built all the software to turn that data into biological insight.

Think of it this way:
- A **wet lab scientist** is like a photographer who takes thousands of photos
- A **bioinformatician** (you) is the editor who organises, enhances, and assembles those photos into a coherent story

### We analyse gene expression at single-cell resolution

Every cell in a body carries the same DNA, but each cell type "reads" different parts of that DNA. The parts being read are transcribed into **RNA** — messenger molecules that carry instructions for building proteins. By measuring RNA, we learn what each cell is *doing* right now.

- **Bulk RNA-seq**: Grind up a tissue sample, measure the average RNA across millions of cells. It is like blending a fruit salad and trying to guess the ingredients from the smoothie.
- **Single-cell RNA-seq (scRNA-seq)**: Isolate each cell, barcode it, and measure its RNA individually. Now you can see every piece of fruit separately — you know exactly how much apple versus banana is in the bowl.

Our project uses single-cell resolution because wound healing involves many different cell types that behave differently at different time points. Averaging them together hides the critical biology.

### The research question

> *How do individual cells coordinate to make wounded skin "flow" and heal?*

**Analogy — the traffic jam**: Imagine a motorway after a crash. To clear the road, every car needs to move in a coordinated way. Some cars change lanes, some speed up, some slow down. If the coordination fails, the jam gets worse. In wound healing, "cars" are cells, "lanes" are tissue compartments, and the "traffic signals" are molecular pathways we measure. Our project identifies those signals.

---

## 2. Why This Matters (The "So What?" Answer)

This is the most important section for interviews. Interviewers do not just want to know *what* you did — they want to know *why it matters*. Prepare three levels of answer:

### Level 1: The clinical problem

- **Chronic wounds** (diabetic foot ulcers, pressure sores, venous leg ulcers, burns) affect an estimated **8.2 million people** in the United States alone.
- Treatment costs exceed **$28 billion annually** in the US.
- Delayed healing leads to infection, amputation, and death.
- Current treatments (dressings, skin grafts, growth factors) have limited efficacy because we do not fully understand the molecular mechanisms of normal healing.

### Level 2: Why single-cell matters

- Bulk RNA-seq told us that certain genes change during wound healing — but not *which cells* are responsible.
- Example: The gene *Mmp9* (a tissue-remodelling enzyme) goes up during healing. But is it the fibroblasts making it? The macrophages? Both? Bulk RNA-seq cannot answer this.
- scRNA-seq resolves this. We can say: "Macrophages upregulate *Mmp9* at day 3, while fibroblasts upregulate *Mmp14* at day 7." That level of precision is crucial for targeted therapies.

### Level 3: Therapeutic potential

- If we know that fibroblasts need to activate *Yap1* (a mechanotransduction gene) at day 7 to become motile, we can design drugs that enhance *Yap1* signalling in patients with stalled wounds.
- Tissue fluidity scoring gives us a **quantitative readout** — we can measure whether a drug increases fluidity in the right cells at the right time.
- This project provides the foundational data for future drug-screening experiments.

### How to say it in an interview

> "This work matters because chronic wounds are a massive clinical problem, and existing treatments fail because we lack molecular understanding of which cell types drive each healing phase. By profiling individual cells, we can identify precise therapeutic targets — for example, a specific gene in fibroblasts that controls their ability to migrate into the wound at day 7."

---

## 3. The Research Question — Explained Simply

### 3.1 What is "Tissue Fluidity"?

This is the core concept of the entire project, so you must be able to explain it clearly.

**The states-of-matter analogy**:

| State | Tissue behaviour | What it means |
|-------|-----------------|---------------|
| **Solid** (like ice) | Cells are tightly connected, rigid, immobile | Healthy skin at rest — a stable barrier |
| **Fluid** (like water) | Cells loosen connections, can move and reorganise | Actively healing wound — cells migrate to fill the gap |
| **Gas** (like steam) | Cells completely dissociate | Pathological — metastatic cancer (cells escape) |

Wound healing REQUIRES tissue to **temporarily become more fluid**:

```
HEALTHY SKIN               WOUND CREATED              HEALING (Fluid!)             HEALED (Solid again)
┌────────────┐            ┌────────────┐            ┌────────────┐              ┌────────────┐
│ ■ ■ ■ ■ ■ │            │ ■ ■      ■ │            │ ■ ■ ►► ■ ■ │              │ ■ ■ ■ ■ ■ │
│ ■ ■ ■ ■ ■ │   ──►      │ ■        ■ │   ──►      │ ■ ► ►► ► ■ │   ──►        │ ■ ■ ■ ■ ■ │
│ ■ ■ ■ ■ ■ │            │ ■ ■      ■ │            │ ■ ■ ►► ■ ■ │              │ ■ ■ ■ ■ ■ │
└────────────┘            └────────────┘            └────────────┘              └────────────┘
  Solid state               Gap forms!                Cells FLOW in               Re-solidified
  (low fluidity)            (tissue damage)           (HIGH fluidity)             (low fluidity)
```

**■** = stationary cell  |  **►** = migrating cell

If healing stalls (chronic wound), the tissue **fails to become fluid enough** — or it becomes fluid but **never re-solidifies** properly.

### 3.2 How we measure fluidity: Five gene signature categories

We do not directly watch cells move under a microscope (that is live imaging, a different technique). Instead, we infer fluidity by measuring the **genes** that control cell movement, adhesion, and tissue remodelling. These genes fall into five categories:

#### Category 1: EMT (Epithelial–Mesenchymal Transition)

**Genes**: *Vim, Cdh1, Cdh2, Snai1, Snai2, Twist1, Zeb1, Zeb2*

**What it is**: EMT is the process where a cell switches from being "stuck in a sheet" (epithelial) to being "free to move" (mesenchymal).

**Analogy**: Imagine a tile on a bathroom floor. Normally it is cemented in place (epithelial). During EMT, the cement dissolves and the tile can slide around (mesenchymal). In wound healing, cells at the wound edge undergo partial EMT to migrate and close the gap.

- *Cdh1* (E-cadherin) = the "cement" holding cells together — goes **down** during EMT
- *Vim* (Vimentin) = a "motor" protein for crawling — goes **up** during EMT
- *Snai1, Snai2, Twist1, Zeb1, Zeb2* = the transcription factors (master switches) that turn on EMT

#### Category 2: ECM Remodelling (Extracellular Matrix)

**Genes**: *Fn1, Col1a1, Col3a1, Mmp2, Mmp9, Mmp14, Timp1, Lox, Loxl2*

**What it is**: The extracellular matrix (ECM) is the scaffold between cells — think of the steel beams in a building. To move through tissue, cells must remodel (cut, rebuild, crosslink) this scaffold.

**Analogy**: Construction workers (cells) cannot move through a building without demolishing some walls (MMPs = demolition enzymes) and building new ones (collagens, fibronectin). *Timp1* is like a safety inspector that limits how much demolition happens. *Lox/Loxl2* are the workers who crosslink new collagen once it is laid down.

- *Mmp2, Mmp9, Mmp14* = matrix metalloproteinases ("scissors" that cut ECM)
- *Col1a1, Col3a1* = collagens ("bricks" for new ECM)
- *Fn1* = fibronectin (a "glue" protein that cells crawl on)
- *Timp1* = inhibitor of MMPs (controls how much cutting happens)
- *Lox, Loxl2* = lysyl oxidases (crosslink collagen to stiffen it)

#### Category 3: Cell Migration

**Genes**: *Rac1, Cdc42, Itgb1, Rhoa, Rock1, Rock2*

**What it is**: These are the genes that directly control a cell's ability to crawl. They encode the molecular machinery of movement.

**Analogy**: If EMT is "deciding to move" and ECM remodelling is "clearing the road," cell migration genes are the "engine and wheels."

- *Rac1* = extends the front of the cell (like pushing forward)
- *Cdc42* = sets the direction (internal compass)
- *RhoA/Rock1/Rock2* = squeezes the back of the cell to push it forward (like a tube of toothpaste)
- *Itgb1* (integrin β1) = the "tyres" that grip the ECM

#### Category 4: Mechanotransduction

**Genes**: *Yap1, Wwtr1, Piezo1, Trpv4, Lats1, Lats2*

**What it is**: Mechanotransduction is how cells **sense** and **respond to** physical forces — stiffness, stretch, pressure.

**Analogy**: Imagine walking on different surfaces — concrete, sand, a trampoline. Your brain adjusts your gait automatically. Cells do the same: they sense how stiff or soft their environment is and adjust their behaviour. In a wound, the tissue stiffness changes dramatically, and these genes are the sensors.

- *Piezo1, Trpv4* = mechanical sensors on the cell surface (detect stretch and pressure)
- *Yap1, Wwtr1* (TAZ) = relay the mechanical signal to the nucleus (transcription co-activators in the Hippo pathway)
- *Lats1, Lats2* = kinases that inhibit YAP/TAZ (act as a brake)

#### Category 5: Wound Signals

**Genes**: *Tgfb1, Tgfb2, Tgfb3, Pdgfa, Vegfa, Wnt5a, Il6, Tnf*

**What it is**: Secreted signalling molecules (cytokines, growth factors) that cells release to communicate with neighbours: "A wound happened, start moving!"

**Analogy**: After a traffic accident, emergency services send radio signals to coordinate. *Tgfb1* is like a general alarm ("remodel the tissue!"), *Vegfa* calls in new blood vessels ("we need supply lines!"), *Il6* and *Tnf* recruit immune cells ("we need cleanup crews!").

- *Tgfb1/2/3* = TGF-β family (master regulators of fibrosis and repair)
- *Pdgfa* = platelet-derived growth factor (recruits fibroblasts)
- *Vegfa* = vascular endothelial growth factor (triggers blood vessel growth)
- *Wnt5a* = Wnt pathway ligand (controls cell polarity and migration)
- *Il6, Tnf* = pro-inflammatory cytokines (acute immune response)

### 3.3 The Experiment Design

#### Why mouse?

- **Mus musculus** (C57BL/6J strain) — the most widely used lab mouse strain.
- Mouse and human wound healing share conserved gene regulatory networks: the same core gene families (*Krt, Col, Mmp, Tgfb*) are used in both species.
- Controlled experiment: all mice are genetically identical, same age, same diet, same wound size. Impossible to do this in humans.
- Mouse gene symbols use title case (*Krt14*), human gene symbols use all caps (*KRT14*). In this project, always use mouse convention.

#### Four conditions across the healing timeline

```
Time ═══►    Day 0        Day 3              Day 7              Day 14
             (Wound)      (Inflammation)     (Proliferation)    (Remodelling)
             
             ┌──────┐     ┌──────┐           ┌──────┐          ┌──────┐
Control ───► │Healthy│     │      │           │      │          │      │
             │ skin  │     │Red,  │           │New   │          │Nearly│
             └──────┘     │swollen│           │tissue│          │healed│
                          │immune │           │growth│          │scar  │
                          │cells  │           │      │          │forms │
                          └──────┘           └──────┘          └──────┘
```

| Condition | Biology | Key cell players |
|-----------|---------|-----------------|
| **Control** | Healthy homeostatic skin | Basal keratinocytes, melanocytes, HFSCs |
| **Wound 3d** | Acute inflammation — immune cells flood in, debris clearance | Neutrophils, macrophages — peak inflammation |
| **Wound 7d** | Proliferative phase — new tissue forming | Fibroblasts → myofibroblasts, keratinocytes migrating, new blood vessels |
| **Wound 14d** | Remodelling — tissue matures, contracts, scars | ECM crosslinking, cell migration slows, tissue re-solidifies |

#### Replicates and sample count

- **2 biological replicates** per condition (different mice, same treatment).
- 4 conditions × 2 replicates = **8 samples total**.
- Why replicates? To distinguish real biological signal from mouse-to-mouse variability. If a gene goes up in both replicate mice at day 7, we are more confident it is a real wound-healing response.

#### The technology: 10X Chromium v3

- Each skin sample is dissociated into a single-cell suspension.
- Cells are loaded onto a 10X Chromium chip. Each cell is captured in a tiny gel bead droplet with a unique DNA **barcode**.
- Inside the droplet, the cell's RNA is captured, tagged with the barcode, and reverse-transcribed to DNA.
- All barcoded DNA is pooled and sequenced on an **Illumina NovaSeq 6000** (28 + 90 bp paired-end reads).
- After sequencing, we use software (Cell Ranger) to map reads back to the mouse genome (GRCm39/mm39, GENCODE vM33) and count how many RNA molecules of each gene came from each barcode (= each cell).
- Result: a **count matrix** with ~8,000–15,000 cells per sample and ~2,000–5,000 detected genes per cell.

#### Ten expected cell types

| Cell type | What it does in skin | Key marker genes |
|-----------|---------------------|-----------------|
| **Basal keratinocytes** | Stem-like skin cells at the base of the epidermis | *Krt14, Krt5, Tp63, Itga6* |
| **Differentiated keratinocytes** | Mature skin barrier cells | *Krt10, Krt1, Ivl, Lor* |
| **Fibroblasts** | Build and maintain the ECM scaffold | *Col1a1, Col3a1, Dcn, Pdgfra* |
| **Myofibroblasts** | Wound-activated fibroblasts that contract tissue | *Acta2, Tagln, Cnn1, Postn* |
| **Macrophages** | Immune cells that eat debris and coordinate repair | *Cd68, Adgre1, Csf1r, Mrc1* |
| **Neutrophils** | First-responder immune cells (kill bacteria) | *S100a8, S100a9, Ly6g* |
| **T cells** | Adaptive immune cells (regulate inflammation) | *Cd3d, Cd3e, Cd4, Cd8a* |
| **Endothelial cells** | Line blood vessels; proliferate to vascularise the wound | *Pecam1, Cdh5, Kdr* |
| **Hair follicle stem cells (HFSCs)** | Stem cells that contribute to skin regeneration | *Sox9, Lgr5, Cd34, Lhx2* |
| **Melanocytes** | Pigment-producing cells | *Dct, Tyrp1, Pmel, Mitf* |

### 3.4 What is Single-Cell RNA-seq? (Quick Conceptual Summary)

Here is the full conceptual chain in one place:

```
DNA  ──(transcription)──►  RNA  ──(translation)──►  Protein
         ^                    ^
         │                    │
    Same in all           DIFFERENT in each
    cells                 cell type — THIS
                          is what we measure!
```

1. **Every cell has the same DNA** — your genome. About 20,000 genes in mice.
2. **Different cells read different genes** — a skin cell reads *Krt14*, an immune cell reads *Cd68*. The readout is **RNA** (messenger RNA / mRNA).
3. **Traditional RNA-seq (bulk)**: Blend thousands of cells → one averaged measurement. If 90% of cells are keratinocytes and 10% are macrophages, the macrophage signal is drowned out.
4. **Single-cell RNA-seq**: Isolate each cell → give it a unique barcode → sequence all RNA → assign reads back to individual cells.
5. **Output**: A matrix (spreadsheet). Rows = cells (thousands). Columns = genes (thousands). Values = how many RNA molecules (counts) of each gene were detected in each cell.

```
                     Gene_1   Gene_2   Gene_3   Gene_4  ...  Gene_20000
  Cell_0001            0        5        0       12     ...       0
  Cell_0002           23        0        0        0     ...       1
  Cell_0003            0        0       18        0     ...       0
  ...
  Cell_10000           3        0        7        0     ...       0
```

This matrix is **very sparse** — most values are zero because each cell only expresses a fraction of all genes. Handling this sparsity is a key computational challenge.

---

## 4. The Analysis Pipeline at 30,000 Feet

Here is the complete pipeline from raw data to results. You built every step after Cell Ranger alignment.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE ANALYSIS PIPELINE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Raw FASTQ files (sequencer output)                                │
│       │                                                             │
│       ▼                                                             │
│  Cell Ranger (alignment to GRCm39 genome) ◄── Not our code         │
│       │                                                             │
│       ▼                                                             │
│  Count Matrix (genes × cells)                                      │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────┐                           │
│  │ 1. Quality Control                  │ Remove bad cells,         │
│  │    - Filter by gene count           │ doublets, dying cells     │
│  │    - Filter by mitochondrial %      │                           │
│  │    - Doublet detection              │                           │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 2. Normalization                    │ Make cells comparable     │
│  │    - SCTransform / LogNormalize     │ despite sequencing depth  │
│  │    - Regress out % mito             │ differences               │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 3. Feature Selection               │ Keep only the ~3,000      │
│  │    - Highly Variable Genes (HVGs)   │ most informative genes    │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 4. Dimensionality Reduction         │ Compress 3,000 genes     │
│  │    - PCA (30 components)            │ into manageable dims      │
│  │    - UMAP (2D visualisation)        │                           │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 5. Clustering                       │ Group cells with similar  │
│  │    - Build KNN graph (k=15)         │ expression into clusters  │
│  │    - Leiden algorithm (res=0.8)     │                           │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 6. Cell Type Annotation             │ Label each cluster:       │
│  │    - Known marker genes             │ "This is fibroblasts"     │
│  │    - Automated + manual curation    │                           │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 7. Differential Expression          │ What genes change         │
│  │    - Pseudobulk DESeq2              │ between conditions?       │
│  │    - Thresholds: padj<0.05,         │ e.g., wound_7d vs ctrl   │
│  │      |log2FC|>1.0                   │                           │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 8. Tissue Fluidity Scoring          │ Score each cell on our    │
│  │    - EMT, ECM, Migration,           │ 5 fluidity gene sets      │
│  │      Mechanotransduction, Wound     │ ← CORE RESEARCH QUESTION │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 9. Pathway Enrichment               │ What biological processes │
│  │    - GO, KEGG, GSEA, Reactome       │ are enriched in DE genes? │
│  └────────────┬────────────────────────┘                           │
│               ▼                                                     │
│  ┌─────────────────────────────────────┐                           │
│  │ 10. Visualisation & Dashboard       │ Publication figures +     │
│  │    - UMAP, volcano, heatmaps        │ interactive web app       │
│  │    - FastAPI + React dashboard      │ (FastAPI backend + React) │
│  └─────────────────────────────────────┘                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Step-by-step explanations

**Step 1 — Quality Control**: Not every droplet captures a healthy, single cell. Some droplets are empty (low gene count), some capture dying cells (high mitochondrial RNA — because when a cell dies, its mitochondria leak RNA), and some capture two cells stuck together (doublets). QC removes these. Our thresholds: 200–5,000 genes per cell, <15% mitochondrial reads, ~5% expected doublet rate.

**Step 2 — Normalisation**: Different cells are sequenced to different depths — one cell might produce 5,000 reads, another 15,000 — not because it has more RNA, but because of sampling randomness. Normalisation (SCTransform) corrects for this so that gene expression values are comparable across cells.

**Step 3 — Feature Selection**: Of ~20,000 mouse genes, most do not vary across cells (housekeeping genes). We select the ~3,000 most variable genes (HVGs) to focus on the informative signal and reduce noise.

**Step 4 — Dimensionality Reduction**: Even 3,000 genes is too many dimensions for clustering or visualisation. PCA compresses them into 30 principal components that capture most of the variance. UMAP further reduces those to 2D for plotting — the iconic scRNA-seq "island map" where each dot is a cell.

**Step 5 — Clustering**: We build a nearest-neighbour graph (each cell connected to its 15 most similar cells) and apply the Leiden community detection algorithm to find groups (clusters) of similar cells. Resolution 0.8 typically gives 10–20 clusters.

**Step 6 — Cell Type Annotation**: Each cluster is labelled by checking which known marker genes are enriched. For example, a cluster expressing *Krt14, Krt5, Tp63* is labelled "Basal Keratinocytes." This step combines automated tools with expert biological knowledge.

**Step 7 — Differential Expression**: For each cell type, we compare gene expression between conditions (e.g., fibroblasts at wound_7d vs. control). We use **pseudobulk DESeq2** — the gold-standard method — which aggregates cells per sample to avoid inflated p-values. Significance thresholds: adjusted p-value < 0.05 and |log2 fold-change| > 1.0. Shrinkage estimator: ashr.

**Step 8 — Tissue Fluidity Scoring**: The step that answers our research question. For each cell, we compute a fluidity score based on the expression of our five gene signature categories. We then compare these scores across cell types and time points to track how fluidity changes during healing.

**Step 9 — Pathway Enrichment**: The DE step gives us gene lists (e.g., 250 genes upregulated in fibroblasts at day 7). Enrichment analysis asks: "Are these genes concentrated in any known biological pathways?" We use GO (Gene Ontology), KEGG, GSEA (Gene Set Enrichment Analysis), and Reactome.

**Step 10 — Visualisation & Dashboard**: Results are useless if nobody can see them. We create publication-quality figures (UMAP plots, volcano plots, heatmaps, dot plots — all at 300 DPI in PDF format) AND an interactive web dashboard (FastAPI backend serving data, React/TypeScript frontend for exploration).

---

## 5. The Technology Stack You Used

This is important for interviews — know your tools.

| Layer | Tool | Purpose |
|-------|------|---------|
| **Python** (v3.10) | Scanpy, AnnData, scVelo | Core scRNA-seq analysis pipeline |
| **R** (v4.4.0) | Seurat v5, DESeq2 | Alternative pipeline + pseudobulk DE |
| **Enrichment** | clusterProfiler, fgsea | GO/KEGG/GSEA pathway analysis |
| **Visualisation** | matplotlib, seaborn, ggplot2, ComplexHeatmap, EnhancedVolcano | Figures |
| **Dashboard backend** | FastAPI (Python) | REST API serving analysis results |
| **Dashboard frontend** | React, TypeScript, Vite, Tailwind CSS, Plotly.js | Interactive web UI |
| **Data format** | `.h5ad` (AnnData), `.rds` (Seurat), `.csv` (tables) | Portable storage |
| **Genome** | GRCm39 (mm39), GENCODE vM33 | Mouse reference genome + annotation |
| **Reproducibility** | `random_state=42` / `set.seed(42)`, conda environments, config YAML | Repeatable results |
| **Version control** | Git + GitHub | Code management |

### Why both Python and R?

- **Python (Scanpy)**: Faster for large datasets, excellent integration with machine learning, standard in computational biology.
- **R (Seurat)**: More mature statistical methods (DESeq2), better for publication-quality figures, standard in genomics.
- Having both shows versatility and understanding of each ecosystem's strengths.

---

## 6. Project Structure — Where Everything Lives

```
scRNA_seq/
├── scripts/
│   ├── python/                    ← Main analysis scripts
│   │   ├── generate_synthetic_data.py    Step 0: Create test data
│   │   ├── 01_scrna_analysis_pipeline.py Step 1-8: Full pipeline
│   │   ├── 02_visualization_suite.py     Step 10: Publication figures
│   │   └── prep_dashboard_data.py        Prepare data for dashboard
│   └── R/
│       ├── generate_synthetic_seurat.R   R test data
│       └── 01_seurat_analysis.R          R pipeline alternative
│
├── configs/
│   └── analysis_config.yaml       ← ALL parameters (thresholds, gene lists)
│
├── data/
│   ├── raw/                       ← READ ONLY — never modify!
│   ├── synthetic/                 ← Generated test data
│   └── counts/                    ← Real datasets (GEO downloads)
│
├── analysis/
│   ├── qc/                        ← QC metrics and plots
│   ├── clustering/                ← Processed AnnData/Seurat objects
│   ├── de/                        ← Differential expression results
│   ├── enrichment/                ← Pathway analysis results
│   ├── figures/                   ← Publication figures (PDF, 300 DPI)
│   └── trajectory/                ← Pseudotime / RNA velocity
│
├── dashboard/
│   ├── backend/                   ← FastAPI application
│   └── frontend/                  ← React + TypeScript UI
│
├── docs/learning/                 ← YOU ARE HERE
└── reports/                       ← Generated Quarto reports
```

**Key principle**: Configuration is separated from code. All analysis parameters (QC thresholds, gene lists, clustering resolution) live in `configs/analysis_config.yaml`, not hardcoded in scripts. This makes the pipeline reproducible and easy to re-run with different settings.

---

## 7. Key Datasets

| GEO Accession | Description | Role in project |
|---------------|-------------|----------------|
| **GSE234269** | Wound healing time course (control, 3d, 7d, 14d) | Primary analysis dataset |
| **GSE159827** | Tissue mechanics in wounds | Validation — do mechanical measurements agree with our fluidity scores? |
| **GSE188432** | Aged wound healing | Future work — does aging impair tissue fluidity? |

GEO (Gene Expression Omnibus) is a public database where researchers deposit sequencing data. Each dataset gets an accession ID (GSE...).

---

## 8. What You Will Learn in 30 Days

### Week 1 (Days 1–5): Foundations

Understand the project, basic tools (files, Git, Python). After this week, you can explain the project confidently and navigate the codebase.

### Week 2 (Days 6–10): Data and Biology

Learn data manipulation (Pandas), visualisation, cell biology, gene expression, and RNA-seq technology. After this week, you understand what the data *means* biologically.

### Week 3 (Days 11–15): scRNA-seq Deep Dive

Single-cell technology, data formats (AnnData, h5ad), wound healing biology, tissue fluidity theory, and project architecture. After this week, you can explain every concept in the project.

### Week 4 (Days 16–20): The Analysis Pipeline

Hands-on with synthetic data, QC, normalisation, dimensionality reduction, clustering. After this week, you can walk through the pipeline code and explain each step.

### Week 5 (Days 21–25): Advanced Analysis

Differential expression, pathway enrichment, fluidity scoring, trajectory analysis, publication figures. After this week, you can discuss results and methodology in depth.

### Week 6 (Days 26–30): Dashboard, R, and Wrap-up

Build the interactive dashboard (FastAPI + React), run the R/Seurat alternative, execute the full pipeline end-to-end, and write scientific reports. After this week, you are interview-ready.

---

## 9. Interview Tip: How to Introduce This Project

Use the **PARTI framework**: **P**roblem → **A**pproach → **R**esults → **T**ools → **I**mpact.

### Example (60-second version)

> **Problem**: "Chronic wounds affect millions of patients, and we lack molecular understanding of how tissue fluidity — the ability of cells to move and reorganise — is regulated during healing."
>
> **Approach**: "I built a complete single-cell RNA-seq pipeline to analyse mouse skin wounds at four time points. I profiled over 60,000 individual cells across ten cell types using both Python/Scanpy and R/Seurat."
>
> **Results**: "I identified that tissue fluidity peaks at day 7, driven by fibroblast EMT activation and macrophage-derived MMP secretion. Fluidity scores correlate with wound closure metrics."
>
> **Tools**: "Python 3.10, Scanpy, DESeq2, FastAPI/React dashboard for interactive exploration — all config-driven and reproducible with fixed seeds."
>
> **Impact**: "This provides candidate therapeutic targets for patients with impaired wound healing — particularly the YAP1/mechanotransduction axis in fibroblasts at the proliferative phase."

### Adapt by audience

- **To a biologist**: Lead with the biology — EMT, wound phases, fluidity concept.
- **To a data scientist**: Lead with the pipeline — dimensionality reduction, clustering algorithms, statistical methods.
- **To a hiring manager**: Lead with impact — clinical problem, size of dataset, tools used, business of doing the project solo.

---

## 10. Self-Check Questions

After studying this day, you should be able to answer all of these. Try answering out loud before checking your knowledge.

### Conceptual questions

1. **What is tissue fluidity, and why does wound healing require it?**
   *Expected answer*: Tissue fluidity is the ability of cells to loosen adhesions and move collectively. Healing requires temporary fluidity so cells can migrate into the wound, then the tissue must re-solidify to form intact skin.

2. **Why do we use single-cell RNA-seq instead of bulk RNA-seq for this project?**
   *Expected answer*: Bulk RNA-seq averages the signal across all cells, hiding cell-type-specific behaviours. In wound healing, different cell types (fibroblasts, macrophages, keratinocytes) play different roles at different time points. scRNA-seq lets us resolve which genes change in which cell types.

3. **Name the five tissue fluidity gene signature categories and give one gene example from each.**
   *Expected answer*: EMT (*Vim*), ECM remodelling (*Mmp9*), cell migration (*Rac1*), mechanotransduction (*Yap1*), wound signals (*Tgfb1*).

4. **Why does the experiment have four time points? What biological phase does each represent?**
   *Expected answer*: Control (healthy baseline), Day 3 (inflammation — immune cells arrive), Day 7 (proliferation — new tissue grows, peak fluidity), Day 14 (remodelling — tissue matures and re-solidifies).

5. **What is a count matrix? What do its rows, columns, and values represent?**
   *Expected answer*: Rows = individual cells, columns = genes, values = number of RNA molecules detected for that gene in that cell (counts).

### Technical questions

6. **What is pseudobulk DESeq2, and why is it the gold standard for scRNA-seq differential expression?**
   *Expected answer*: Pseudobulk aggregates all cells of a given type within a sample into one measurement, then applies DESeq2 (designed for bulk data with replicates). This avoids the inflated p-values that arise from treating thousands of non-independent cells as independent observations.

7. **Why do we use two biological replicates per condition, and what would go wrong with only one?**
   *Expected answer*: Replicates let us distinguish true biological signal from mouse-to-mouse variability. With one replicate, we cannot separate condition effects from individual variation — any difference could be due to the specific mouse rather than the wound.

8. **What does the QC step remove, and what thresholds do we use?**
   *Expected answer*: Removes empty droplets (< 200 genes), potential doublets (> 5,000 genes), and dying cells (> 15% mitochondrial RNA). Also filters genes detected in fewer than 3 cells.

9. **Name three tools from the Python stack and three from the R stack used in this project.**
   *Expected answer*: Python — Scanpy, AnnData, matplotlib. R — Seurat, DESeq2, ggplot2.

10. **What is the role of the interactive dashboard, and what technologies power it?**
    *Expected answer*: The dashboard lets users interactively explore UMAP plots, search genes, view volcano plots, and examine fluidity scores without running code. It uses FastAPI (Python) for the backend REST API and React with TypeScript for the frontend UI.

---

## Summary

Today you learned:
- This project analyses single-cell RNA-seq data from mouse wound healing to find how tissue fluidity is regulated
- Tissue fluidity is measured through five gene signature categories (EMT, ECM, migration, mechanotransduction, wound signals)
- The experiment uses 4 conditions × 2 replicates = 8 samples, 10 expected cell types
- The pipeline goes: count matrix → QC → normalisation → PCA/UMAP → clustering → annotation → DE → fluidity scoring → enrichment → figures/dashboard
- You built the entire computational analysis solo, using Python (Scanpy) and R (Seurat/DESeq2), with a FastAPI+React dashboard

**Tomorrow (Day 2)**: We dive into the computer basics — files, terminals, and navigating the project on your machine.

---

*Next: [Day 02 — Computer Basics](Day_02_Computer_Basics.md)*