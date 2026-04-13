# Day 2: Single-Cell RNA-seq Technology — How It Works

> **Series**: 30-Day Interview Preparation Guide for scRNA-seq Wound Healing Project
> **Time**: ~2.5 hours of focused reading
> **Prerequisites**: Day 1 (Project Overview & Big Picture)
> **Goal**: After today, you can explain the entire journey from a piece of mouse skin to the count matrix on your computer — and why every step matters for your analysis.

---

## Why This Day Matters

In interviews, you will be asked: "Walk me through how scRNA-seq works." This is not an abstract question — interviewers want to know that you understand the **data you analyse**. If you built a pipeline that processes count matrices but cannot explain where those matrices come from, it raises red flags.

Today we trace the **complete path** of data in our project:

```
MOUSE SKIN TISSUE
       │
       ▼
 1. Tissue Dissociation  ──── separate cells from tissue
       │
       ▼
 2. 10X Chromium          ──── barcode each cell
       │
       ▼
 3. Library Prep           ──── prepare DNA for sequencing
       │
       ▼
 4. Illumina Sequencing    ──── read the DNA sequences
       │
       ▼
 5. Cell Ranger            ──── align reads, produce count matrix
       │
       ▼
 COUNT MATRIX (.h5ad)     ──── OUR STARTING POINT (analysis begins here)
```

You (the bioinformatician) work from step 5 onwards. Steps 1–4 are done by the wet lab team. But understanding all five steps is absolutely essential — the quality of upstream steps directly affects everything you do in your code.

---

## From Tissue to Data: The Wet Lab Journey

### Step 1: Tissue Dissociation — Separating Cells from Tissue

#### What happens

We start with a piece of mouse skin. In our project, this comes from C57BL/6J mice (a common laboratory strain with black fur). The tissue is from one of four conditions:

| Condition   | What it is                        | Phase of healing       |
|-------------|-----------------------------------|------------------------|
| `control`   | Healthy, unwounded skin           | Homeostasis            |
| `wound_3d`  | Skin 3 days after a punch biopsy  | Inflammatory phase     |
| `wound_7d`  | Skin 7 days after wounding        | Proliferative phase    |
| `wound_14d` | Skin 14 days after wounding       | Remodelling phase      |

Each condition has **2 biological replicates** (2 separate mice), giving us **8 samples** total.

The tissue sample is a small disc of skin, roughly 4–6 mm in diameter. Skin is a complex organ with multiple layers:

```
SKIN CROSS-SECTION
┌─────────────────────────────────────────────────────────┐
│   EPIDERMIS (top layer)                                 │
│   ┌───────────────────────────────────────────────────┐ │
│   │  Differentiated Keratinocytes (Krt10, Krt1)       │ │
│   │  Basal Keratinocytes (Krt14, Krt5) ── stem cells  │ │
│   └───────────────────────────────────────────────────┘ │
│                                                         │
│   DERMIS (middle layer)                                 │
│   ┌───────────────────────────────────────────────────┐ │
│   │  Fibroblasts (Col1a1, Dcn) ── make collagen       │ │
│   │  Blood vessels ── Endothelial cells (Pecam1)       │ │
│   │  Immune cells ── Macrophages (Cd68), T cells (Cd3d)│ │
│   │  Hair follicles ── HFSCs (Sox9, Lgr5)             │ │
│   │  Melanocytes (Dct, Tyrp1)                          │ │
│   └───────────────────────────────────────────────────┘ │
│                                                         │
│   HYPODERMIS (bottom layer)                             │
│   ┌───────────────────────────────────────────────────┐ │
│   │  Fat cells (adipocytes), connective tissue         │ │
│   └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

All the cell types listed above — keratinocytes, fibroblasts, macrophages, endothelial cells, etc. — are the **10 cell types** we expect to find in our data.

To analyse these cells individually, we first need to **separate them from each other**. Cells in tissue are glued together by proteins (like E-cadherin, encoded by the *Cdh1* gene — one of our EMT markers!). We use enzymes to dissolve this glue:

1. **Collagenase** — breaks down collagen (the main structural protein in skin)
2. **Trypsin** or **Dispase** — breaks cell-cell adhesion proteins
3. **DNase I** — prevents liberated DNA from making the solution sticky

The result: a **cell suspension** — millions of individual cells floating freely in a tube of liquid.

#### Why this matters for YOUR analysis

Dissociation is not perfect. Several problems can occur, and **you will see them in your data**:

**Problem 1: Doublets**
Sometimes two cells stick together and are treated as one. Your pipeline will see a "cell" expressing both keratinocyte markers (*Krt14*) AND macrophage markers (*Cd68*). That is biologically impossible — a single cell cannot be both. It is a doublet.

- Our expected doublet rate: **~5%** (configured in `configs/analysis_config.yaml` as `doublet_rate: 0.05`)
- We detect and remove doublets during QC using tools like Scrublet (Python) or DoubletFinder (R)
- If you see a mysterious cluster expressing markers from two unrelated cell types, doublets are the first suspect

**Problem 2: Dead cells**
Enzymes can damage cells. A dying cell's membrane breaks down, releasing mitochondrial mRNA. This is why we measure **percent mitochondrial genes** (`percent_mt`) — it is our "cell death detector."

- Healthy cells: ~2–8% mitochondrial reads
- Damaged cells: >15% mitochondrial reads
- Our threshold: **max 15%** (slightly higher than the 10% standard because skin keratinocytes are metabolically active and naturally have more mitochondria)

**Problem 3: Ambient RNA**
When cells die during dissociation, they spill their mRNA into the surrounding liquid. This "ambient RNA" gets captured alongside healthy cells, adding noise. Tools like SoupX or CellBender can estimate and remove ambient RNA contamination.

**Problem 4: Dissociation-induced gene changes**
The enzymatic digestion itself can trigger stress responses. Some genes (particularly heat-shock genes like *Hspa1a*, *Hspa1b*, and immediate-early genes like *Fos*, *Jun*) get artificially activated during dissociation. Experienced analysts know to be cautious about these genes — if *Fos* appears as a top marker for a cluster, it is more likely a dissociation artefact than real biology.

```
DISSOCIATION SUMMARY

  Skin tissue    ──[enzymes]──►    Cell suspension
  ┌──────────┐                     ┌──────────────────────┐
  │ ■■■■■■■■ │                     │ ○  ○  ○  ○  ○  ○    │ ← single cells (good!)
  │ ■■■■■■■■ │        ──►         │ ○○ ○  ○  ○  ○       │ ← doublet (bad!)
  │ ■■■■■■■■ │                     │ ○  ✕  ○  ○  ○  ○    │ ← dead cell (remove in QC)
  └──────────┘                     │ ~  ~  ~  ~  ~  ~    │ ← ambient RNA (noise)
                                   └──────────────────────┘
```

---

### Step 2: 10X Chromium — The Magic Bead Machine

This is the most ingenious step. The 10X Chromium system solves a fundamental problem: **how do you sequence millions of mRNA molecules and know which cell each molecule came from?**

#### The problem

Imagine you have 10,000 cells, each containing thousands of mRNA molecules. If you just mixed all the mRNA together and sequenced it, you would get 20 million sequences — but you would have no idea which cell produced which sequence. You would be back to bulk RNA-seq.

#### The solution: Barcodes in droplets

10X Genomics uses a technology called **GEM** — Gel Bead-in-Emulsion. Here is how it works:

```
THE 10X CHROMIUM WORKFLOW

 STEP A: Prepare gel beads (pre-made by 10X Genomics)
 ┌──────────────────────────────────────────────────────┐
 │                                                      │
 │   Each gel bead carries MILLIONS of identical        │
 │   oligonucleotide primers:                           │
 │                                                      │
 │   ┌──────────────────────────────────────────────┐   │
 │   │  [Illumina adapter]──[Cell Barcode]──[UMI]──[poly(dT)]  │
 │   │       (for sequencer)   (16 bp)    (12 bp)  (captures mRNA) │
 │   └──────────────────────────────────────────────┘   │
 │                                                      │
 │   • Cell Barcode: 16 bases long → 4^16 = 4 billion  │
 │     possible barcodes (each bead gets a unique one)  │
 │   • UMI: 12 bases long → 4^12 = 16 million possible │
 │     (each PRIMER on a bead gets a unique UMI)        │
 │   • poly(dT): a string of T nucleotides that binds   │
 │     to the poly(A) tail on mRNA                      │
 │                                                      │
 └──────────────────────────────────────────────────────┘

 STEP B: Microfluidic chip combines three ingredients
 ┌──────────────────────────────────────────────────────┐
 │                                                      │
 │    Gel beads ──────►  ╔════════════════╗              │
 │                       ║                ║              │
 │    Cells in liquid ──►║  JUNCTION      ║──► Oil + GEMs│
 │                       ║  (tiny cross)  ║    (droplets)│
 │    Oil ──────────────►╚════════════════╝              │
 │                                                      │
 │    The chip has microscopic channels. Fluids flow     │
 │    at precisely controlled rates so that MOST         │
 │    droplets contain exactly:                          │
 │      • 1 gel bead                                    │
 │      • 1 cell (or 0 cells — some droplets are empty) │
 │      • Lysis reagents                                │
 │                                                      │
 └──────────────────────────────────────────────────────┘

 STEP C: Inside each droplet (GEM = Gel Bead-in-Emulsion)
 ┌──────────────────────────────────────────────────────┐
 │                                                      │
 │     ┌─── Oil shell (keeps everything contained) ───┐ │
 │     │                                               │ │
 │     │    ┌──────────┐    ┌──────────┐               │ │
 │     │    │ GEL BEAD │    │   CELL   │               │ │
 │     │    │          │    │          │               │ │
 │     │    │ Barcode: │    │ Contains │               │ │
 │     │    │ ACGT...  │    │ mRNA     │               │ │
 │     │    └──────────┘    └─────┬────┘               │ │
 │     │                         │                     │ │
 │     │    1. Cell lyses (membrane breaks open)       │ │
 │     │    2. mRNA spills out                         │ │
 │     │    3. poly(A) tails on mRNA bind to           │ │
 │     │       poly(dT) on bead primers                │ │
 │     │    4. Reverse transcription: mRNA → cDNA      │ │
 │     │       Each cDNA molecule now carries the      │ │
 │     │       bead's barcode + a unique UMI           │ │
 │     │                                               │ │
 │     └───────────────────────────────────────────────┘ │
 │                                                      │
 └──────────────────────────────────────────────────────┘
```

#### The student ID analogy

Think of it like a university exam:

| Concept | Analogy | What it means |
|---------|---------|---------------|
| **Cell** | A student | One biological cell in our sample |
| **Cell barcode** | Student ID number | A unique 16-base-pair tag identifying which cell this molecule came from |
| **mRNA molecule** | One exam answer | One copy of a gene's transcript |
| **UMI** | Answer number on the exam sheet | A unique 12-base-pair tag identifying each *individual molecule* (not just the gene, but this specific copy) |
| **GEM (droplet)** | An exam room with one student | A tiny oil droplet containing one cell + one bead |
| **Gel bead** | Exam sheet with pre-printed student ID | The capture bead carrying the barcode + primers |

After the exam is done, you collect all answer sheets from all students. Even though they are shuffled together, you can reconstruct who answered what because every answer has the student ID (cell barcode) and the answer number (UMI) printed on it.

#### Why 10X Chromium specifically?

There are several single-cell platforms. Here is how they compare:

| Feature | 10X Chromium (our choice) | Smart-seq2 | Drop-seq | inDrop |
|---------|--------------------------|------------|----------|--------|
| Cells per run | ~1,000–10,000 | ~96–384 | ~5,000 | ~3,000 |
| Gene coverage | 3' end only | Full-length transcript | 3' end | 3' end |
| Cost per cell | Low (~$0.10) | High (~$5.00) | Low | Low |
| Sensitivity | Moderate | Very high | Moderate | Moderate |
| Best for | Large surveys, cell type discovery | Deep profiling of few cells, isoform analysis | Budget-friendly large screens | Budget-friendly |
| UMI? | Yes | No | Yes | Yes |
| Commercial kit? | Yes (standardised) | Manual protocol | Manual protocol | Kit available |

**Why we chose 10X**: We need to profile ~10,000 cells per sample to capture rare cell types (like melanocytes or hair follicle stem cells). Smart-seq2 would give better sensitivity but only ~384 cells — we would miss rare populations. 10X is the **industry standard** for cell type discovery at scale, with well-supported software (Cell Ranger) and broad community support for troubleshooting.

**Trade-off we accept**: 10X only captures the **3' end** of mRNA (because the poly(dT) primer binds the poly(A) tail at the 3' end). This means we cannot study alternative splicing or isoforms. For tissue fluidity, this is fine — we care about *which genes* are expressed, not *which isoforms*.

---

### Step 3: Library Preparation and Sequencing

#### From mRNA to something a sequencer can read

After the GEM reactions, we have cDNA molecules tagged with cell barcodes and UMIs. But we need to **amplify** this material (there is not enough for sequencing) and **format** it for the Illumina platform.

```
LIBRARY PREPARATION STEPS

 1. GEM-RT (already done in droplets)
    mRNA ──[reverse transcriptase]──► cDNA with barcode + UMI

 2. Break the emulsion
    Pool all the cDNA from all droplets together
    (this is okay — every molecule has its barcode)

 3. cDNA amplification (PCR)
    Make many copies of each cDNA molecule
    Problem: PCR doubles molecules each cycle ── can't tell if
    a gene has 8 copies because the cell had 8 mRNAs, or
    because PCR duplicated 1 mRNA three times (1→2→4→8)
    Solution: UMIs! (explained below)

 4. Fragmentation and size selection
    Break long cDNA into ~300 bp fragments
    Select fragments from the 3' end (near the barcode)

 5. Add sequencing adapters
    Attach Illumina-specific sequences to fragment ends

 6. Quality check
    Run on Bioanalyzer/TapeStation to verify library size (~400 bp)
    Quantify by qPCR
```

#### Illumina NovaSeq 6000 sequencing

Our project uses the **Illumina NovaSeq 6000**, one of the highest-throughput sequencers available. Here is what happens:

1. Libraries are loaded onto a **flow cell** — a glass slide with billions of tiny wells
2. Each cDNA fragment binds to the flow cell surface and is **clonally amplified** (bridge amplification) creating a "cluster" of identical fragments
3. **Sequencing by synthesis**: fluorescently-labelled nucleotides are added one at a time. A camera photographs which colour lights up at each position, reading the sequence base by base

Our sequencing configuration: **28 + 90 bp paired-end reads**

```
WHAT EACH READ CONTAINS

 Read 1 (28 bp):   Contains the cell identity information
 ┌────────────────────────────────────────┐
 │  Cell Barcode (16 bp)  │  UMI (12 bp) │
 │  ACGTACGTACGTACGT       │  NNNNNNNNNNNN │
 │  "Which cell?"          │  "Which molecule?" │
 └────────────────────────────────────────┘

 Read 2 (90 bp):   Contains the gene sequence
 ┌──────────────────────────────────────────────────────────────────┐
 │  cDNA sequence from the mRNA ──────────────────────────────────  │
 │  (this gets aligned to the genome to identify the gene)          │
 └──────────────────────────────────────────────────────────────────┘

 Index read (8 bp): Sample index — identifies which sample in a
                    multiplexed run (multiple samples on one flow cell)
```

So every sequencing read gives us THREE pieces of information:
1. **Which cell** (cell barcode in Read 1)
2. **Which molecule** (UMI in Read 1)
3. **Which gene** (sequence in Read 2, after alignment)

#### Output: FASTQ files

The sequencer outputs **FASTQ files** — text files where each read is stored as four lines:

```
@SRR12345678.1                    ← Read name (unique identifier)
ACGTACGTACGTACGTNNNNNNNNNNNN      ← DNA sequence (the actual bases)
+                                  ← Separator line
FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF  ← Quality scores (how confident the machine
                                     is about each base call)
```

These FASTQ files live in our `data/raw/` directory. They are **READ-ONLY** — we never modify them. They are the ultimate source of truth. If anything goes wrong downstream, we can always reprocess from the raw FASTQs.

**File sizes**: A single sample generates ~20–50 GB of FASTQ data. This is why our `.gitignore` prevents committing files over 50 MB — FASTQ files would overwhelm a git repository.

---

### Step 4: Cell Ranger — From Reads to Count Matrix

Cell Ranger is **10X Genomics' official software** for processing 10X Chromium data. It is the bridge between raw sequencing reads and the count matrix that our pipeline analyses.

#### What Cell Ranger does

```
CELL RANGER PIPELINE

 FASTQ files (raw reads)
       │
       ▼
 ┌─────────────────────────────────────────────────────────┐
 │  cellranger count                                       │
 │                                                          │
 │  1. DEMULTIPLEXING                                       │
 │     Read the cell barcode from Read 1                    │
 │     Match it to the list of known 10X barcodes           │
 │     (~737,000 possible barcodes in the whitelist)        │
 │                                                          │
 │  2. ALIGNMENT                                            │
 │     Align Read 2 to the reference genome                 │
 │     Our genome: GRCm39 (mm39) with GENCODE vM33          │
 │     Aligner: STAR (Spliced Transcripts Alignment to a    │
 │              Reference) — handles intron-spanning reads   │
 │                                                          │
 │  3. UMI COUNTING                                         │
 │     For each cell barcode × gene combination:            │
 │     Count the number of UNIQUE UMIs                      │
 │     (not reads — UMIs! This is the deduplication step)    │
 │                                                          │
 │  4. CELL CALLING                                         │
 │     Distinguish real cells from empty droplets            │
 │     Uses the "knee plot" — sharp drop in UMI counts      │
 │     marks the boundary between cells and background       │
 │                                                          │
 └─────────────────────────────────────────────────────────┘
       │
       ▼
 COUNT MATRIX + BAM files + QC report (web_summary.html)
```

#### Why GRCm39 (mm39) and not mm10?

You will see many older papers and tutorials use mm10 (GRCm38) as the mouse reference genome. Our project uses **mm39 (GRCm39)**, the latest assembly:

- **mm39** was released in 2020 and fixes hundreds of errors in mm10
- Better representation of repetitive regions and structural variants
- We use **GENCODE vM33** gene annotations, which are updated to work with mm39
- Using the latest genome means our gene coordinates are more accurate
- Fewer reads will be incorrectly mapped or unmapped

This is configured in our `configs/analysis_config.yaml`:
```yaml
project:
  genome_build: "GRCm39 (mm39)"
  annotation: "GENCODE vM33"
```

#### UMI deduplication — Why this is critical

This concept is so important that it deserves a detailed explanation.

**The PCR duplication problem:**

During library preparation, PCR amplification copies molecules. If one cell had 5 copies of *Krt14* mRNA, but PCR happened to amplify one of them more efficiently, you might end up with:

```
BEFORE PCR (truth):        AFTER PCR (inflated):
Krt14 molecule A (UMI_01)  → 8 copies of UMI_01
Krt14 molecule B (UMI_02)  → 4 copies of UMI_02
Krt14 molecule C (UMI_03)  → 16 copies of UMI_03
Krt14 molecule D (UMI_04)  → 2 copies of UMI_04
Krt14 molecule E (UMI_05)  → 6 copies of UMI_05

If we count READS:    8 + 4 + 16 + 2 + 6 = 36   ← wrong!
If we count UMIs:     5 unique UMIs               ← correct!
```

Without UMIs, we would think this cell has 36 copies of *Krt14* when it really has 5. UMI deduplication removes PCR bias and gives us **true molecular counts**.

**This is why the count matrix values are called "UMI counts" not "read counts."**

#### Cell Ranger output files

Cell Ranger produces several output files in a directory called `outs/`:

| File | What it contains |
|------|-----------------|
| `filtered_feature_bc_matrix/` | Count matrix (only real cells, no empty droplets) |
| `raw_feature_bc_matrix/` | Full matrix including empty droplets |
| `possorted_genome_bam.bam` | Aligned reads (very large file, ~50 GB) |
| `web_summary.html` | QC report with plots (estimated cells, reads per cell, etc.) |
| `metrics_summary.csv` | Key QC metrics in tabular form |

The `filtered_feature_bc_matrix/` directory contains three files in **MTX format**:
- `matrix.mtx.gz` — the sparse count matrix
- `barcodes.tsv.gz` — list of cell barcodes (one per row)
- `features.tsv.gz` — list of genes (one per row)

Our pipeline reads these directly into an AnnData object (Python) or Seurat object (R).

---

## The Count Matrix — Our Starting Point

Everything in our `scripts/python/01_scrna_analysis_pipeline.py` and `scripts/R/01_seurat_analysis.R` starts from the count matrix. Let us understand it deeply.

### What is actually in the data

The count matrix is a giant table:

```
REAL COUNT MATRIX (simplified)

                Krt14  Krt10  Col1a1  Cd68  Vim  Pecam1  mt-Co1  ...  (20,000+ genes)
Cell_0001        25      0      0      0     1     0       12     ...
Cell_0002         0     18      3      0     0     0        8     ...
Cell_0003         0      0     45      0    22     0        5     ...
Cell_0004         0      0      0     38     8     0       15     ...
Cell_0005         0      0      0      0     0    29        3     ...
Cell_0006        30      0      0      0     2     0       95     ...  ← high mt! (dying cell)
...
Cell_8000        12      0      0      0     4     0        7     ...

                    ↑                   ↑                   ↑
              Keratinocyte          Macrophage          Mitochondrial
               markers              marker              gene (QC)
```

**Key observations:**

1. **Most values are zero.** A typical cell expresses ~2,000–3,000 out of ~20,000 genes. That means ~85% of entries are zero. This is called a **sparse matrix**.

2. **Zeros do not mean the gene is absent from the cell's genome.** Every cell has every gene. A zero means the gene is not being *transcribed* (read) in that cell — or that the mRNA was present but was not captured (this is called **dropout**, a technical limitation).

3. **The values are small integers.** The count of 25 for *Krt14* in Cell_0001 means 25 unique mRNA molecules of *Krt14* were captured from that cell.

4. **You can already see cell types.** Cell_0001 has high *Krt14* → likely a basal keratinocyte. Cell_0004 has high *Cd68* → likely a macrophage. This is the foundation of cell type annotation.

#### Why is the matrix sparse? The restaurant analogy

Imagine a spreadsheet listing every item on every restaurant's menu in a city. Most restaurants only serve a fraction of all possible dishes. A sushi restaurant does not serve pizza; a pizzeria does not serve sashimi. If you listed ALL possible dishes as columns, most cells would be zero.

Similarly, a keratinocyte does not need macrophage genes, and a macrophage does not need keratinocyte genes. Each cell type activates only the genes relevant to its function.

### Our synthetic data vs. real data

| Property | Our synthetic data | Real 10X data |
|----------|-------------------|---------------|
| Cells | ~8,000 | ~5,000–15,000 per sample |
| Genes | ~2,000 | ~20,000–30,000 |
| Location | `data/synthetic/` | `data/counts/` |
| Purpose | Test the pipeline quickly | Actual biological analysis |
| Generated by | `scripts/python/generate_synthetic_data.py` | Cell Ranger from FASTQ files |

We use synthetic data (stored in `data/synthetic/synthetic_counts.h5ad`) to test our pipeline without waiting for real data processing. The synthetic data mimics the structure and sparsity patterns of real data, with known cell types and conditions.

### File formats we use

| Format | Extension | Software | Use in our project | Example path |
|--------|-----------|----------|---------------------|-------------|
| AnnData | `.h5ad` | Scanpy (Python) | Primary analysis format | `analysis/clustering/wound_adata.h5ad` |
| Seurat Object | `.rds` | Seurat (R) | R alternative pipeline | `analysis/clustering/wound_sobj.rds` |
| CSV | `.csv` | Any | DE results, metadata, QC summaries | `analysis/de/wound_3d_vs_control.csv` |
| FASTQ | `.fastq.gz` | Cell Ranger | Raw sequencing reads (READ-ONLY!) | `data/raw/*.fastq.gz` |
| MTX | `.mtx` + `.tsv` | 10X | Sparse matrix from Cell Ranger | `data/counts/*/filtered_feature_bc_matrix/` |
| H5 | `.h5` | 10X / HDF5 | Combined matrix format from Cell Ranger | `data/counts/*/*.h5` |

### AnnData structure — What our code actually uses

AnnData is the core data structure in Scanpy. Understanding it is like understanding a spreadsheet application — everything revolves around it.

```
AnnData Object (adata)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 adata.X ─────────────── The count matrix (cells × genes)
 │                        Shape: (8000, 2000) or (8000, 20000)
 │                        Values: UMI counts (integers) or
 │                                normalized values (floats)
 │
 adata.obs ───────────── Cell metadata (one row per cell)
 │                        Columns: cell_type, condition, sample,
 │                                 n_genes, n_counts, percent_mt,
 │                                 leiden (cluster ID)
 │
 adata.var ───────────── Gene metadata (one row per gene)
 │                        Columns: gene_name, gene_id,
 │                                 highly_variable (bool),
 │                                 mean, dispersion
 │
 adata.obsm ──────────── Cell embeddings (dimensionality reduction)
 │                        Keys: 'X_pca' (PCA coordinates),
 │                              'X_umap' (UMAP coordinates)
 │                        These are the numbers behind UMAP plots
 │
 adata.uns ───────────── Unstructured data (anything else)
 │                        Keys: 'leiden_colors', 'pca_variance_ratio',
 │                              'rank_genes_groups' (DE results)
 │
 adata.layers ─────────── Alternative matrices (same shape as X)
                          Keys: 'raw_counts' (original UMI counts),
                                'log_normalized' (after normalization)
```

#### Real examples from our code

When your script runs `adata.obs['condition']`, it returns something like:

```
Cell_0001    control
Cell_0002    control
Cell_0003    wound_3d
Cell_0004    wound_3d
Cell_0005    wound_7d
...
Name: condition, dtype: category
```

When your script runs `adata[adata.obs['cell_type'] == 'Fibroblast']`, it creates a new AnnData containing only fibroblast cells — used in our differential expression analysis to compare fibroblasts between conditions.

When your script runs `adata.obsm['X_umap']`, it returns a matrix of shape (n_cells, 2) — the UMAP coordinates that produce the colourful scatter plots in our dashboard.

#### Seurat object (R equivalent)

If you work in R, the Seurat object has a parallel structure:

```
Seurat Object (wound_sobj)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 wound_sobj[["RNA"]]@counts ──── Raw count matrix
 wound_sobj[["RNA"]]@data ──── Normalized data
 wound_sobj@meta.data ──── Cell metadata (like adata.obs)
 Embeddings(wound_sobj, "umap") ── UMAP coordinates
 Embeddings(wound_sobj, "pca") ─── PCA coordinates
```

The information is the same — just accessed with different syntax.

---

## Quality Metrics: What Makes a Good Cell?

Quality control is your **first line of defense** against bad data. Before any biological analysis, we filter out cells that are not trustworthy.

### The three QC filters we apply

These thresholds are configured in `configs/analysis_config.yaml` and applied in our pipeline scripts:

```yaml
qc_thresholds:
  min_genes_per_cell: 200
  max_genes_per_cell: 5000
  min_counts_per_cell: 500
  max_percent_mt: 15
  min_cells_per_gene: 3
  doublet_rate: 0.05
```

#### Filter 1: Number of genes detected (200–5,000)

```
n_genes DISTRIBUTION (what it looks like)

 Number
 of cells
   │
   │     ▓▓▓▓
   │    ▓▓▓▓▓▓▓
   │   ▓▓▓▓▓▓▓▓▓▓
   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓
   │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
   │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
   └──┬────────────────┬───── n_genes
     200             5000
      ↑               ↑
   Remove below    Remove above
   (empty drops)   (doublets)
```

- **Below 200 genes**: The "cell" is likely an **empty droplet** that captured some ambient RNA but no actual cell. Or it is a **dead cell** with severely degraded RNA.
- **Above 5,000 genes**: Suspiciously high. A normal cell expresses 2,000–3,000 genes. If something appears to express 6,000+ genes, it might be a **doublet** (two cells in one droplet) combining their gene profiles.
- **The sweet spot**: Most real, healthy cells fall between 500 and 4,000 genes.

#### Filter 2: Total UMI counts (minimum 500)

This is the total number of mRNA molecules captured from a cell. Low counts indicate:
- The cell was not efficiently captured
- The cell was dead or dying before capture
- The droplet had very little reagent

We set a minimum of **500 UMI counts**. Cells below this are unreliable — with only a few hundred molecules, you cannot confidently determine cell type or gene expression patterns.

#### Filter 3: Percentage of mitochondrial genes (maximum 15%)

This is the most important filter for detecting **dying cells**.

**Why mitochondrial percentage indicates cell death:**

```
HEALTHY CELL                              DYING CELL
┌───────────────────────┐                ┌───────────────────────┐
│                       │                │         ╳ ╳           │
│   Nucleus             │                │   Nucleus             │
│   ┌─────────┐         │                │   ┌─────────┐         │
│   │ nuclear │         │                │   │ nuclear │  LEAKED! │
│   │ mRNA    │         │                │   │ mRNA    │──►out   │
│   └─────────┘         │                │   └─────────┘         │
│                       │                │         ╳ ╳           │
│   [mito] ── small     │                │   [mito] ── still     │
│   organelles with     │                │   intact! Their mRNA  │
│   their own mRNA      │                │   is captured but     │
│                       │                │   nuclear mRNA has    │
│   ___membrane intact__│                │   leaked out ╳ ╳ ╳    │
└───────────────────────┘                └───────────────────────┘

mt% = mt mRNA / total mRNA               mt% = mt mRNA / (less total)
    = low (normal ~5%)                        = HIGH (dying! >15%)
```

When a cell dies, its **outer membrane** breaks down. Nuclear mRNA leaks out and degrades. But mitochondria, being small organelles with their own membranes, stay intact longer. So a dying cell retains its mitochondrial mRNA while losing nuclear mRNA — making the *proportion* of mitochondrial reads artificially high.

**Why 15% instead of the standard 10%?**

Our tissue is **skin**. Keratinocytes (the most abundant cell type in skin) are metabolically active cells with naturally higher mitochondrial content than, say, lymphocytes. If we used 10%, we would discard many healthy keratinocytes. The 15% threshold is a compromise — strict enough to catch dying cells but lenient enough to retain healthy skin cells.

#### Additional filter: Minimum cells per gene (3)

We also filter from the **gene side**: any gene detected in fewer than 3 cells is removed. Why? A gene found in only 1 or 2 cells out of 8,000 is likely noise — perhaps a sequencing error or ambient RNA contamination. Removing these genes reduces the matrix size without losing meaningful signal.

### Putting it all together: QC in code

In our Scanpy pipeline, QC filtering looks like this:

```python
# Calculate QC metrics
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

# Filter cells
adata = adata[adata.obs['n_genes_by_counts'] >= 200]
adata = adata[adata.obs['n_genes_by_counts'] <= 5000]
adata = adata[adata.obs['total_counts'] >= 500]
adata = adata[adata.obs['pct_counts_mt'] <= 15]

# Filter genes
sc.pp.filter_genes(adata, min_cells=3)
```

After filtering, the QC summary is saved to `analysis/qc/qc_summary.csv`.

---

## Interview Deep Dive: Common Questions

### "Why single-cell instead of bulk RNA-seq?"

**Full answer you should give:**

> "Bulk RNA-seq averages gene expression across all cells in a sample. In wound healing, this is misleading because different cell types respond differently at each time point. For example, at 3 days post-wounding, macrophages are highly active while fibroblasts are still quiescent. If I did bulk RNA-seq, the macrophage signal would dominate and hide the fibroblast response. With scRNA-seq, I can separate cell types computationally and ask precise questions like: 'In fibroblasts specifically, which EMT genes are upregulated at day 7?'
>
> There's a classic analogy: bulk RNA-seq is like making a fruit smoothie — you know what fruits went in, but you can't tell apple from banana in the final mix. Single-cell is like keeping each piece of fruit separate — you can characterise every piece individually."

**Follow-up they might ask:** "But bulk is cheaper and has better sensitivity per cell — when would you still use it?"

> "Bulk RNA-seq is great when your sample is homogeneous — like a pure cell line, or when you only care about one cell type that you can sort beforehand. It's also better for detecting lowly-expressed genes because you have more reads per gene. For pseudobulk differential expression, we actually aggregate our single-cell data back to pseudo-bulk — we get the best of both worlds: cell-type resolution from scRNA-seq, and statistical power from pseudobulk DESeq2."

### "What are UMIs and why do they matter?"

**Answer:**

> "UMIs — Unique Molecular Identifiers — are random 12-nucleotide sequences attached to each mRNA molecule before PCR amplification. They solve the PCR duplication problem.
>
> Without UMIs: if PCR amplifies one mRNA molecule 10 times, you would count it as 10 molecules — a 10× overestimate. With UMIs, all 10 copies have the same UMI tag, so you collapse them into one count. UMIs let us measure the true number of mRNA molecules in each cell.
>
> In our pipeline, the count matrix contains UMI counts, not read counts. This is critical — the values in `adata.X` represent actual molecules, not amplification artefacts. That's why we call them 'counts' and not 'reads'."

### "What's the difference between reads and UMIs?"

**Answer:**

> "A **read** is a raw sequencing output — one fragment of DNA sequenced by the machine. A **UMI** represents one original mRNA molecule. The relationship is: many reads can come from the same UMI, because PCR copies molecules.
>
> Example: If a cell had 5 molecules of *Col1a1* (5 UMIs), but PCR amplified them to 40 total copies, the sequencer would produce 40 reads. After UMI deduplication, we correctly count 5.
>
> In our data, a typical cell has ~50,000 reads but only ~2,000–5,000 UMI counts. The difference is PCR duplicates, which UMI deduplication removes.
>
> Key point: when we report gene expression values, we report UMI counts. When we report sequencing depth, we report reads per cell. Both numbers matter but measure different things."

### "Why 10X Chromium and not other platforms?"

**Answer:**

> "We chose 10X Chromium for three practical reasons:
>
> 1. **Throughput**: We need ~10,000 cells per sample to discover rare populations like hair follicle stem cells and melanocytes. Smart-seq2 only does ~384 cells.
> 2. **Standardisation**: 10X provides Cell Ranger software and a well-supported analysis ecosystem. This is important for reproducibility and troubleshooting.
> 3. **UMIs**: 10X includes UMIs for accurate quantification. Smart-seq2 does not use UMIs.
>
> The trade-off is that 10X only captures the 3' end of transcripts, so we lose splice-isoform information. But for our tissue fluidity analysis — where we're scoring signature gene expression — 3' capture is sufficient.
>
> If the research question were about alternative splicing in wound healing, I would recommend Smart-seq2 or 10X 5' chemistry instead."

### "How many cells do you need per sample?"

**Answer:**

> "It depends on the number of expected cell types and how rare the rarest type is. A rule of thumb is: you need at least 50–100 cells of each type for reliable analysis.
>
> In our project, we expect 10 cell types. The rarest — melanocytes and hair follicle stem cells — might be only ~2–3% of total cells. At 10,000 total cells, we expect ~200–300 of the rarest type, which is sufficient.
>
> For differential expression (our DESeq2 analysis), we're comparing the same cell type across conditions. If fibroblasts are ~15% of cells and we have ~10,000 cells per sample, we get ~1,500 fibroblasts per sample — plenty for pseudobulk analysis.
>
> Under-sampling (too few cells) means rare cell types disappear. Over-sampling (too many cells) wastes money and increases computational cost without much statistical benefit. Saturation typically occurs around 5,000–10,000 cells for skin tissue with standard complexity."

### "What could go wrong with the data?"

**Answer (showing depth of understanding):**

> "Several things, and we check for all of them in QC:
>
> 1. **Batch effects**: Different sequencing runs produce systematic differences. We use integration methods like Harmony to correct this.
> 2. **Doublets (~5%)**: Two cells captured in one droplet. Detected by Scrublet/DoubletFinder — they appear as cells expressing markers from two unrelated types.
> 3. **Ambient RNA**: mRNA from lysed cells contaminates all droplets. Corrected with SoupX or CellBender.
> 4. **Low capture efficiency**: Not all mRNA in a cell gets captured. 10X typically captures 10–15% of mRNA molecules — 'dropout' of lowly-expressed genes is common.
> 5. **Cell type bias**: Dissociation can kill fragile cells (like neurons), so cell proportions in the data may not match proportions in tissue. For skin, this is less of an issue.
> 6. **Dissociation artefacts**: Stress-response genes (*Fos*, *Jun*, *Hspa1a*) can be artificially elevated."

---

## Technical Vocabulary Cheat Sheet

| Term | Simple Definition | Why You Need to Know It |
|------|-------------------|------------------------|
| **scRNA-seq** | Sequencing RNA from individual cells | The core technology of our project |
| **UMI** | Unique molecular barcode for each mRNA molecule | Removes PCR bias; our count matrix uses UMI counts |
| **Cell barcode** | 16-bp tag identifying which cell a molecule came from | How we assign reads to specific cells |
| **GEM** | Gel Bead-in-Emulsion — a droplet containing one cell + one bead | 10X Chromium's core technology |
| **Doublet** | Two cells captured in one droplet | We filter ~5% of these in QC |
| **Dropout** | A gene is expressed but not detected (reads as zero) | Why our matrix has so many zeros |
| **Sparse matrix** | A matrix where most values are zero | Describes scRNA-seq count matrices; stored efficiently |
| **Count matrix** | Table of cells × genes with UMI counts | The starting point of all our analysis |
| **AnnData** | Python data structure (Scanpy) holding counts + metadata | Our primary analysis object (`.h5ad` files) |
| **Seurat object** | R data structure holding counts + metadata | Our R pipeline's data structure (`.rds` files) |
| **FASTQ** | Text file format for raw sequencing reads | Lives in `data/raw/`, never modified |
| **Cell Ranger** | 10X Genomics' alignment + counting software | Converts FASTQs to count matrices |
| **GRCm39 / mm39** | Latest mouse reference genome assembly | What we align reads against |
| **GENCODE vM33** | Gene annotation database for mouse | Tells Cell Ranger where genes are on the genome |
| **Poly(A) tail** | String of adenines at the 3' end of mRNA | How 10X captures mRNA (poly(dT) primer binds it) |
| **Poly(dT) primer** | String of thymines on gel bead primers | Binds poly(A) tail to capture mRNA |
| **PCR amplification** | Making copies of DNA molecules | Necessary for sequencing but introduces bias (solved by UMIs) |
| **Ambient RNA** | Free-floating mRNA from dead cells | Background noise; corrected by SoupX/CellBender |
| **Percent mitochondrial** | Fraction of reads from mitochondrial genes | High values indicate dying cells (our threshold: 15%) |
| **STAR aligner** | Software that maps reads to the genome | Used inside Cell Ranger; handles spliced reads |
| **Knee plot** | Graph used to distinguish real cells from empty droplets | Cell Ranger uses this for cell calling |
| **Library** | Prepared DNA fragments ready for sequencing | Final product of library preparation step |
| **Flow cell** | Glass slide where sequencing happens | Part of the Illumina NovaSeq 6000 |
| **Paired-end** | Both ends of a DNA fragment are sequenced | Our config: 28 bp (Read 1) + 90 bp (Read 2) |

---

## How This Connects to Our Analysis Pipeline

Now you can see how everything fits together:

```
DAY 2 KNOWLEDGE MAP — How wet lab connects to your code

WET LAB (not your job, but you must understand it)
──────────────────────────────────────────────────
Tissue dissociation → 10X Chromium → Library prep → Sequencing → Cell Ranger
                                                                      │
────────────────────────────────────────────────────────────────────────
YOUR JOB (computational analysis — Days 3-30)                         │
                                                                      ▼
     ┌──────────────────────── COUNT MATRIX ─────────────────────────┐
     │                                                                │
     │  ┌─── QC & Filtering (Day 3) ───────────────────────────────┐  │
     │  │  Remove dead cells, doublets, low-quality cells           │  │
     │  │  Script: 01_scrna_analysis_pipeline.py                    │  │
     │  │  Config: configs/analysis_config.yaml                     │  │
     │  └──────────────────────────────────────────────────────────┘  │
     │                        │                                       │
     │  ┌─── Normalization & Clustering (Days 4-5) ────────────────┐  │
     │  │  PCA → UMAP → Leiden clustering → cell type annotation    │  │
     │  └──────────────────────────────────────────────────────────┘  │
     │                        │                                       │
     │  ┌─── Differential Expression (Days 6-7) ───────────────────┐  │
     │  │  Pseudobulk DESeq2: wound_3d vs control, etc.             │  │
     │  │  Output: analysis/de/*.csv                                │  │
     │  └──────────────────────────────────────────────────────────┘  │
     │                        │                                       │
     │  ┌─── Tissue Fluidity Scoring (Days 8-9) ───────────────────┐  │
     │  │  Score EMT, ECM, migration, mechanotransduction, wound    │  │
     │  │  signals across cell types and conditions                 │  │
     │  └──────────────────────────────────────────────────────────┘  │
     │                        │                                       │
     │  ┌─── Visualization & Reporting (Days 10+) ─────────────────┐  │
     │  │  UMAP plots, volcano plots, heatmaps                     │  │
     │  │  Dashboard: dashboard/                                    │  │
     │  └──────────────────────────────────────────────────────────┘  │
     └────────────────────────────────────────────────────────────────┘
```

---

## Self-Check Questions

Test your understanding. Try answering each question before looking at the answer.

---

**Q1: Why do we use enzymatic digestion to dissociate tissue, and what problems can it cause?**

<details>
<summary>Answer</summary>

Cells in tissue are held together by adhesion proteins (like E-cadherin/Cdh1) and extracellular matrix (collagen). Enzymes like collagenase and trypsin break these connections to free individual cells. Problems include: (1) creating doublets when cells are not fully separated, (2) killing fragile cells which increases mitochondrial percentage, (3) releasing ambient RNA from dead cells, and (4) inducing stress-response genes like *Fos* and *Jun* as dissociation artefacts.
</details>

---

**Q2: A cell barcode is 16 bp long. How many possible unique barcodes does that give? Is that enough?**

<details>
<summary>Answer</summary>

4^16 = 4,294,967,296 (about 4.3 billion) possible barcodes. Since we capture ~10,000 cells per sample, this is vastly more than needed — the chance of two cells accidentally getting the same barcode (a "barcode collision") is negligible. 10X uses a whitelist of ~737,000 validated barcodes, which is still far more than the number of cells we capture.
</details>

---

**Q3: You see a "cell" in your data expressing both Krt14 (keratinocyte marker) and Cd68 (macrophage marker) at high levels. What is the most likely explanation?**

<details>
<summary>Answer</summary>

This is most likely a **doublet** — two cells (one keratinocyte, one macrophage) captured in the same droplet. No single cell should express both keratinocyte and macrophage markers. We detect and remove these during QC.
</details>

---

**Q4: Why do we use UMI counts in the count matrix rather than raw read counts?**

<details>
<summary>Answer</summary>

PCR amplification introduces bias — some molecules get copied more than others. If we counted reads, we would conflate biological signal with PCR artefacts. UMIs tag each original molecule before PCR, so after sequencing, we collapse all reads with the same cell barcode + UMI + gene into a single count. This gives us the true number of original mRNA molecules.
</details>

---

**Q5: Why is our mitochondrial percentage threshold (15%) higher than the typical 10%?**

<details>
<summary>Answer</summary>

Our tissue is skin, and keratinocytes (the most abundant cell type in skin) are metabolically active cells with naturally higher mitochondrial gene expression than many other cell types. Using a 10% threshold would incorrectly remove healthy keratinocytes. The 15% threshold balances sensitivity (removing dying cells) with specificity (keeping healthy skin cells). This is documented in `configs/analysis_config.yaml`.
</details>

---

**Q6: What is the difference between `adata.X`, `adata.obs`, and `adata.obsm`?**

<details>
<summary>Answer</summary>

- `adata.X`: The main data matrix (cells × genes) — contains UMI counts or normalized values
- `adata.obs`: Cell-level metadata — a DataFrame where each row is a cell and columns include cell_type, condition, sample, QC metrics, etc.
- `adata.obsm`: Cell-level multi-dimensional annotations — matrices like PCA coordinates (`X_pca`) and UMAP coordinates (`X_umap`) that are used for dimensionality reduction plots

Think of it as: `.X` is the data, `.obs` is the labels, `.obsm` is the embeddings.
</details>

---

**Q7: You are reviewing a Cell Ranger web summary and see that only 500 cells were detected from a sample where you expected 5,000. What might have gone wrong?**

<details>
<summary>Answer</summary>

Several possibilities: (1) Poor tissue dissociation — cells were not properly separated and most were lost. (2) Cell death during preparation — most cells died, producing high ambient RNA and few viable cells. (3) Clogging in the microfluidic chip — beads or cells blocked the channels. (4) Incorrect cell loading concentration — too few cells were loaded. (5) Sequencing was too shallow — not enough reads to detect all cells (unlikely with NovaSeq). You would check the knee plot in the web summary to see if cell calling was appropriate.
</details>

---

**Q8: Why do we use GRCm39 (mm39) instead of the older mm10 genome?**

<details>
<summary>Answer</summary>

GRCm39 is the latest mouse reference genome (released 2020), fixing hundreds of assembly errors in mm10 (GRCm38). It has better resolved repetitive regions and structural variants, leading to more accurate read alignment and gene quantification. Combined with GENCODE vM33 annotations, it gives us the most up-to-date gene models. Using the latest genome improves mapping rates and reduces artefacts from incorrect genome coordinates.
</details>

---

**Q9: What three pieces of information does a single sequencing read from a 10X Chromium library give you?**

<details>
<summary>Answer</summary>

1. **Which cell** the molecule came from (cell barcode, 16 bp, in Read 1)
2. **Which molecule** it is (UMI, 12 bp, in Read 1) — for PCR deduplication
3. **Which gene** it represents (cDNA sequence, 90 bp, in Read 2) — identified by aligning to the reference genome
</details>

---

**Q10: An interviewer asks: "If scRNA-seq only captures ~10-15% of mRNA molecules in each cell, how can you trust the data?" How do you respond?**

<details>
<summary>Answer</summary>

"That's a great question. The ~10-15% capture efficiency means we have 'dropout' — some genes that are expressed will show zero counts in our data, especially lowly-expressed genes. However, three factors make the data reliable despite this:

1. **Highly-expressed genes are consistently detected.** Marker genes like *Krt14* for keratinocytes or *Col1a1* for fibroblasts are expressed at high enough levels that they are almost always captured. These are the genes that define cell types.

2. **We analyse thousands of cells.** Even if one cell drops out a gene, across 1,000 cells of the same type, we get a reliable average. This is the power of large cell numbers.

3. **Statistical methods account for dropout.** Methods like ZINB (zero-inflated negative binomial) models and imputation tools are designed to handle the excess zeros. Our pseudobulk DESeq2 approach aggregates cells before testing, which largely eliminates the dropout issue.

The key insight is that scRNA-seq trades depth (per-cell sensitivity) for breadth (thousands of cells). For cell type discovery and differential expression between conditions — our main use cases — this trade-off is well worth it."
</details>

---

## Summary: What You Learned Today

| Topic | Key Takeaway |
|-------|-------------|
| Tissue dissociation | Enzymes free cells from tissue; causes doublets, death, ambient RNA |
| 10X Chromium | Barcodes each cell in a droplet; ~10,000 cells per run |
| Cell barcode + UMI | 16 bp barcode = cell identity; 12 bp UMI = molecule identity |
| Library prep | cDNA amplified by PCR; UMIs solve PCR duplication bias |
| Sequencing | NovaSeq 6000; Read 1 = barcode+UMI, Read 2 = gene sequence |
| Cell Ranger | FASTQ → aligned reads → count matrix; uses STAR + mm39 |
| Count matrix | Sparse table of cells × genes; values are UMI counts |
| AnnData | Python object: .X (matrix), .obs (metadata), .obsm (embeddings) |
| QC thresholds | 200–5000 genes, 500 min counts, 15% max mt |
| File formats | .h5ad (Scanpy), .rds (Seurat), .csv (tables), .fastq.gz (raw) |

---

## Tomorrow: Day 3 — Quality Control Deep Dive

We will walk through the entire QC pipeline step by step, running actual code on our synthetic data. You will learn to interpret QC plots (violin plots, scatter plots, knee plots) and understand exactly what happens when we filter cells.

---

*Last updated: 2025-07-15 | Part of the 30-Day scRNA-seq Interview Preparation Guide*