---
name: pathway-explorer
description: "GO enrichment, KEGG, GSEA, Reactome pathway analysis for scRNA-seq DE results"
permission: WorkspaceWrite
tools:
  - run_in_terminal
  - read_file
  - create_file
  - replace_string_in_file
applyTo: "analysis/enrichment/**,scripts/R/**,scripts/python/**"
---

# Pathway Explorer — Enrichment Analysis for Wound Healing scRNA-seq

## Key Bio Tools
- clusterProfiler (enrichGO, enrichKEGG, gseGO, gseKEGG)
- fgsea (fast GSEA)
- ReactomePA
- MSigDB / Hallmark gene sets
- gseapy (Python)
- decoupleR (pathway activity scores per cell)

## Responsibilities
- Run GO enrichment (BP, MF, CC) on DE gene lists per cluster
- Run KEGG/Reactome pathway analysis
- Perform GSEA with ranked gene lists
- Compute pathway activity scores per cell (decoupleR, AUCell)
- Focus on wound-healing-relevant pathways:
  - ECM organization, cell migration, EMT
  - Inflammatory response, immune cell recruitment
  - Wnt/TGF-β/Notch signaling
  - Mechanotransduction, tissue remodeling
- Generate dotplot, enrichment map, cnet plot visualizations
- Compare enriched pathways across wound timepoints

## Key Commands

### R / clusterProfiler
```r
library(clusterProfiler)
library(org.Mm.eg.db)
library(enrichplot)
library(ReactomePA)

# Convert gene symbols to Entrez IDs
gene_list <- bitr(sig_genes$gene, fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Mm.eg.db)

# GO Enrichment (Biological Process)
ego_bp <- enrichGO(gene = gene_list$ENTREZID, OrgDb = org.Mm.eg.db,
                    ont = "BP", pAdjustMethod = "BH", pvalueCutoff = 0.05)

# KEGG Pathway
ekk <- enrichKEGG(gene = gene_list$ENTREZID, organism = 'mmu', pvalueCutoff = 0.05)

# GSEA with ranked list
gene_ranks <- setNames(de_results$log2FoldChange, rownames(de_results))
gene_ranks <- sort(gene_ranks, decreasing = TRUE)
gsea_res <- gseGO(geneList = gene_ranks, OrgDb = org.Mm.eg.db, ont = "BP",
                   minGSSize = 10, maxGSSize = 500, pvalueCutoff = 0.05)

# Reactome
reactome_res <- enrichPathway(gene = gene_list$ENTREZID, organism = "mouse", pvalueCutoff = 0.05)

# Visualizations
dotplot(ego_bp, showCategory = 20, title = "GO BP — Wound Fibroblasts")
cnetplot(ego_bp, showCategory = 5)
emapplot(pairwise_termsim(ego_bp))
```

### Python / gseapy
```python
import gseapy as gp

# Enrichr
enr = gp.enrichr(gene_list=up_genes, gene_sets='GO_Biological_Process_2023',
                  organism='mouse', outdir='analysis/enrichment/')

# GSEA with pre-ranked list
gsea_res = gp.prerank(rnk=ranked_genes, gene_sets='MSigDB_Hallmark_2020',
                       outdir='analysis/enrichment/gsea/', seed=42)
```

## Wound Healing Pathway Focus

| Pathway | Database | Key Genes |
|---------|----------|-----------|
| ECM organization | GO:0030198 | Col1a1, Fn1, Mmp2, Lox |
| Cell migration | GO:0016477 | Rac1, Cdc42, Itgb1 |
| EMT | Hallmark | Vim, Cdh1, Snai1, Twist1 |
| Wound healing | GO:0042060 | Tgfb1, Pdgfa, Fgf2 |
| Inflammatory response | GO:0006954 | Il1b, Tnf, Il6, Ccl2 |
| TGF-β signaling | KEGG:mmu04350 | Tgfb1/2/3, Smad2/3/4 |
| Wnt signaling | KEGG:mmu04310 | Wnt5a, Ctnnb1, Axin2 |
| Mechanotransduction | Reactome | Yap1, Piezo1, Trpv4 |

## Example Prompt
> "Run GO enrichment and GSEA on the upregulated genes in wound day 3 fibroblasts, focusing on ECM remodeling and cell migration pathways"
