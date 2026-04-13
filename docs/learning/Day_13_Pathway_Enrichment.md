# Day 13: Pathway Enrichment Analysis

> **Goal**: Understand how we go from a list of DE genes to biological meaning. Know GO, KEGG, and GSEA.

---

## The Problem: A Gene List Is Not Biology

```
DE result: 500 significantly upregulated genes at wound_7d
    Mmp9, Col1a1, Vim, Fn1, Acta2, Tgfb1, Vegfa, ...

Question: What BIOLOGICAL PROCESSES are activated?

Instead of reading 500 genes one by one:
    → Ask: "Are these genes enriched in known pathways?"
```

---

## Three Types of Enrichment Analysis

### 1. GO (Gene Ontology) — What Functions?

Gene Ontology = a curated database of gene functions organized in a hierarchy.

Three branches:
- **Biological Process (BP)**: "What does this do?" → wound healing, cell migration, ECM organization
- **Molecular Function (MF)**: "What's the molecular activity?" → protease activity, collagen binding
- **Cellular Component (CC)**: "Where in the cell?" → extracellular matrix, cytoskeleton

```
Example:
    Our upregulated genes: Mmp9, Mmp2, Mmp14, Col1a1, Col3a1
    
    GO enrichment result:
    ┌──────────────────────────────────────────────────┐
    │ GO Term                          padj    Genes   │
    │ extracellular matrix organization 2e-8   12/120  │
    │ collagen metabolic process        5e-7   8/45    │
    │ wound healing                     3e-6   15/200  │
    │ cell migration                    1e-5   10/180  │
    └──────────────────────────────────────────────────┘
    
    Interpretation: Wound healing and ECM processes are activated
```

### 2. KEGG — What Pathways?

KEGG = curated metabolic and signaling pathway maps.

```
Example KEGG results:
    Pathway                         padj    Genes
    ECM-receptor interaction        3e-6    8/80
    TGF-beta signaling pathway      5e-5    6/90
    Focal adhesion                  2e-4    7/200
    PI3K-Akt signaling              8e-4    9/350
```

KEGG gives pathway MAPS — visual diagrams showing where your genes fit in signaling cascades.

### 3. GSEA (Gene Set Enrichment Analysis) — Ranked Approach

```
Regular enrichment: Only uses significant genes (top 500)
GSEA: Uses ALL genes ranked by fold change

    ALL genes ranked by log2FC:
    Position 1:   Mmp9     (log2FC = +3.5)  ← most upregulated
    Position 2:   Col1a1   (log2FC = +3.2)
    ...
    Position 500: Gene_X   (log2FC = +0.1)
    ...
    Position 10000: Gene_Y (log2FC = -0.1)
    ...
    Position 20000: Cdh1   (log2FC = -2.1)  ← most downregulated
    
    GSEA asks: Do genes in a pathway cluster at the TOP or BOTTOM?
    If ECM genes are all at the top → ECM pathway is enriched
```

**Advantage of GSEA**: No arbitrary cutoff (padj < 0.05). Uses ALL genes.

---

## The Enrichment Test — Fisher's Exact Test

### The Logic

```
Question: Are ECM genes over-represented in our DE list?

                    DE genes    Not DE    Total
ECM genes              12         108      120
Non-ECM genes         488       19,392   19,880
Total                 500       19,500   20,000

Expected by chance: 500 × (120/20,000) = 3 ECM genes
Observed: 12 ECM genes
p-value: 2e-8  →  Not random!
```

### Multiple Testing

Just like DE: test hundreds of pathways → correct with Benjamini-Hochberg FDR.

---

## Our Enrichment Pipeline

### Using clusterProfiler (R)

```r
# In R — gold standard for enrichment
library(clusterProfiler)
library(org.Mm.eg.db)  # Mouse gene database

# GO enrichment
ego <- enrichGO(
  gene = de_genes,
  OrgDb = org.Mm.eg.db,
  ont = "BP",              # Biological Process
  pAdjustMethod = "BH",
  pvalueCutoff = 0.05
)

# KEGG enrichment  
ekegg <- enrichKEGG(
  gene = entrez_ids,
  organism = "mmu",        # Mouse
  pvalueCutoff = 0.05
)

# GSEA
gsea_result <- gseGO(
  geneList = ranked_genes,  # ALL genes, ranked by log2FC
  OrgDb = org.Mm.eg.db,
  ont = "BP"
)
```

### Using Python (gseapy)

```python
import gseapy as gp

# Enrichr-based analysis
enr = gp.enrichr(
    gene_list=de_genes,
    gene_sets='GO_Biological_Process_2023',
    organism='mouse'
)
```

---

## Expected Enrichment Results for Our Project

### wound_3d vs control (Inflammatory Phase)

```
Top GO Terms:                     Expected?
inflammatory response             ✓ (neutrophils, macrophages)
neutrophil chemotaxis              ✓
cytokine-mediated signaling        ✓ (Il6, Tnf)
phagocytosis                       ✓ (macrophages)
```

### wound_7d vs control (Proliferative Phase — Peak Fluidity)

```
Top GO Terms:                     Expected?
extracellular matrix organization  ✓ (ECM remodeling)
cell migration                     ✓ (tissue fluidity)
wound healing                      ✓
epithelial-mesenchymal transition  ✓ (EMT — core hypothesis)
collagen fibril organization       ✓ (Col1a1, Col3a1)
angiogenesis                       ✓ (Vegfa)
```

### wound_14d vs control (Remodeling Phase)

```
Top GO Terms:                     Expected?
collagen metabolic process         ✓ (remodeling)
ECM-receptor interaction           ✓
cell adhesion                      ✓ (tissue resolidifying)
regulation of cell migration       ✓ (migration slowing)
```

---

## Reading Enrichment Plots

### Dot Plot

```
    Term                          GeneRatio  padj   Count
    ECM organization          ●●●●●         ★★★★   12
    cell migration            ●●●●          ★★★    10
    wound healing             ●●●           ★★★    15
    EMT                       ●●●           ★★     8
    angiogenesis              ●●            ★      6
    
    ● size = number of genes
    ★ color = statistical significance
```

### Bar Plot

```
    ECM organization         ████████████████████  (padj=2e-8)
    cell migration           █████████████████     (padj=1e-6)
    wound healing            ██████████████        (padj=3e-5)
    EMT                      ████████████          (padj=8e-5)
```

---

## Interview Q&A

### Q: "What is pathway enrichment and why do you do it?"

> "Pathway enrichment tests whether our DE genes are statistically over-represented in known biological pathways. Instead of interpreting 500 genes individually, enrichment reveals the higher-level biological processes — like 'ECM organization' or 'EMT' — that are activated. We use GO for functional annotation, KEGG for signaling pathways, and GSEA for a ranked analysis that doesn't require an arbitrary significance cutoff."

### Q: "What enriched pathways support your fluidity hypothesis?"

> "At wound day 7, we see strong enrichment for ECM organization, cell migration, epithelial-mesenchymal transition, and wound healing — exactly the processes that define tissue fluidity. This provides independent pathway-level validation of our gene signature approach. Inflammatory pathways dominate at day 3, and tissue remodeling at day 14, matching the known wound healing trajectory."

---

## Self-Check Questions

1. **What is GO?** → Gene Ontology — curated database of gene functions
2. **Three GO branches?** → Biological Process, Molecular Function, Cellular Component
3. **What is KEGG?** → Curated metabolic/signaling pathway database
4. **How is GSEA different from GO/KEGG enrichment?** → Uses ALL ranked genes, no cutoff
5. **What statistical test does standard enrichment use?** → Fisher's exact test (hypergeometric)
6. **Why correct for multiple testing in enrichment?** → Testing hundreds of pathways, need FDR
7. **What pathways do we expect at wound_7d?** → ECM organization, cell migration, EMT
8. **What R package do we use?** → clusterProfiler
9. **What does GeneRatio mean?** → Fraction of pathway genes found in our DE list
10. **Why is enrichment better than reading individual genes?** → Reveals coordinated biological programs

---

**Next**: [Day 14 — Visualization & Publication Figures](Day_14_Visualization.md)
