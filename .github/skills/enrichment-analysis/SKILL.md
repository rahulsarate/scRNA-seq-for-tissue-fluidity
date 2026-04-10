---
name: enrichment-analysis
description: "GO, KEGG, GSEA, and Reactome pathway enrichment analysis. Use when running functional enrichment on DE gene lists."
---

# Pathway Enrichment Skill

## When to Use
- GO enrichment on DE results
- KEGG pathway analysis
- Gene Set Enrichment Analysis (GSEA)
- Reactome pathway analysis

## Python (gseapy)
```python
import gseapy as gp

# Over-representation analysis
enr = gp.enrichr(
    gene_list=upregulated_genes,
    gene_sets='GO_Biological_Process_2023',
    organism='mouse',
    outdir='analysis/enrichment/',
    cutoff=0.05
)

# GSEA with ranked gene list
ranked = de_results.sort_values('log2FC', ascending=False)
ranked_list = ranked.set_index('gene')['log2FC']

gs = gp.prerank(
    rnk=ranked_list,
    gene_sets='KEGG_2021_Mouse',
    outdir='analysis/enrichment/',
    seed=42,
    min_size=15,
    max_size=500
)
```

## R (clusterProfiler)
```r
library(clusterProfiler)
library(org.Mm.eg.db)

# Convert symbols to Entrez IDs
gene_ids <- bitr(gene_list, fromType = "SYMBOL", toType = "ENTREZID",
                 OrgDb = org.Mm.eg.db)

# GO enrichment
ego <- enrichGO(gene = gene_ids$ENTREZID,
                OrgDb = org.Mm.eg.db,
                ont = "BP", pAdjustMethod = "BH",
                pvalueCutoff = 0.05)

# KEGG
ekegg <- enrichKEGG(gene = gene_ids$ENTREZID,
                    organism = "mmu", pvalueCutoff = 0.05)

# GSEA
gse <- gseGO(geneList = ranked_gene_list,
             OrgDb = org.Mm.eg.db,
             ont = "BP", pvalueCutoff = 0.05)
```

## Expected Pathways (wound healing)
- **wound_3d**: Inflammatory response, neutrophil chemotaxis, cytokine signaling
- **wound_7d**: ECM organization, collagen fibril organization, cell migration
- **wound_14d**: Wound healing, tissue remodeling, angiogenesis
- **Fluidity-related**: EMT, focal adhesion, TGF-beta signaling, Hippo signaling

## Output
- Save enrichment tables: `analysis/enrichment/<comparison>_GO_BP.csv`
- Save dot plots: `analysis/figures/<comparison>_enrichment_dotplot.pdf`
