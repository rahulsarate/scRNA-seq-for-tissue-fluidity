#!/usr/bin/env python3
"""
Download Public scRNA-seq Datasets from GEO
=============================================
Author: Rahul M Sarate
Project: Tissue fluidity in wound healing

Curated datasets specifically relevant to skin wound healing scRNA-seq.
Downloads metadata and provides instructions for full data retrieval.

Usage:
    python scripts/python/00_download_geo_data.py
"""

import os
import json

OUTPUT_DIR = os.path.join('data', 'references')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# CURATED DATASETS FOR WOUND HEALING scRNA-seq
# ============================================================================
DATASETS = {
    "GSE234269": {
        "title": "Itgbl1-mediated regulation of fibrogenesis — skin wound healing scRNA-seq",
        "organism": "Mus musculus",
        "timepoints": ["Day 3", "Day 7", "Day 14"],
        "cell_types": "Wound bed cells",
        "platform": "10X Chromium",
        "relevance": "HIGH — Direct wound healing timepoints matching our study design",
        "data_format": "CSV",
        "n_samples": 3,
        "paper": "Wang et al., Novel integrated multiomics analysis reveals Itgbl1",
        "download_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE234269",
        "sra_url": None,
        "notes": "scRNA-seq of murine skin wound tissues at 3 different time points after injury (3d, 7d, 14d). Investigates fibrogenesis through TGFβ1 and IL1β signaling."
    },
    "GSE159827": {
        "title": "Symmetry breaking of tissue mechanics in wound-induced hair follicle regeneration",
        "organism": "Mus musculus",
        "timepoints": ["Post-wound"],
        "cell_types": "Wound bed + hair follicle cells",
        "platform": "10X Chromium",
        "relevance": "VERY HIGH — Tissue mechanics + wound healing + scRNA-seq",
        "data_format": "TXT",
        "n_samples": 1,
        "paper": "Tissue mechanics in WIHN model (Mus vs Acomys)",
        "download_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE159827",
        "sra_url": "https://www.ncbi.nlm.nih.gov/Traces/study/?acc=PRJNA670657",
        "notes": "Investigates mechanical and molecular responses of wound-induced hair neogenesis. Wound stiffness gradient predicts pattern of hair formation. DIRECTLY RELEVANT to tissue fluidity."
    },
    "GSE188432": {
        "title": "Wound healing in aged skin — systems-level cellular composition changes",
        "organism": "Mus musculus",
        "timepoints": ["Homeostasis", "Wound day 4", "Wound day 7"],
        "cell_types": "Epithelial, fibroblast, immune",
        "platform": "10X Chromium (NovaSeq + HiSeq)",
        "relevance": "HIGH — Young vs aged wound healing scRNA-seq",
        "data_format": "MTX, TSV",
        "n_samples": 11,
        "paper": "Wound healing in aged skin — cell-cell communication changes",
        "download_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE188432",
        "sra_url": None,
        "notes": "Defines baseline differences across epithelial/fibroblast/immune cells in young and aged skin. Cell-cell communication analysis."
    },
    "GSE203244": {
        "title": "Monocyte/macrophage heterogeneity during skin wound healing",
        "organism": "Mus musculus",
        "timepoints": ["Day 3", "Day 6", "Day 10"],
        "cell_types": "Monocytes, macrophages",
        "platform": "10X Chromium (HiSeq)",
        "relevance": "HIGH — Macrophage dynamics in wound healing",
        "data_format": "MTX, TSV",
        "n_samples": 3,
        "paper": "Monocyte/macrophage heterogeneity during skin wound healing in mice",
        "download_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE203244",
        "sra_url": None,
        "notes": "CD45+ cells from skin wounds at 3 timepoints. Macrophage polarization relevant to tissue remodeling."
    },
    "GSE186821": {
        "title": "scRNA-seq of diabetic wound CD45+ immune cells",
        "organism": "Mus musculus",
        "timepoints": ["Diabetic wound"],
        "cell_types": "CD45+ immune cells (17 clusters, 4 macrophage types)",
        "platform": "10X Chromium",
        "relevance": "MEDIUM — Impaired wound healing model",
        "data_format": "TSV",
        "n_samples": 8,
        "paper": "Immune cell heterogeneity in chronic wound model",
        "download_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE186821",
        "sra_url": "https://www.ncbi.nlm.nih.gov/Traces/study/?acc=PRJNA776242",
        "notes": "Chronic diabetic wound immune cell analysis. Can compare normal vs impaired wound healing."
    },
    "GSE197588": {
        "title": "Wound memory of epidermal stem cells [scRNAseq]",
        "organism": "Mus musculus",
        "timepoints": ["40 weeks post-wound"],
        "cell_types": "Lrig1 epidermal stem cell progeny",
        "platform": "Smart-seq",
        "relevance": "HIGH — Epigenetic wound memory in stem cells",
        "data_format": "TXT",
        "n_samples": 310,
        "paper": "Wound priming in epidermal Lrig1 stem cell progeny",
        "download_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE197588",
        "sra_url": None,
        "notes": "Primed progenitors maintain transcriptional program acquired during wound healing in young age. 310 individual cells."
    },
    "GSE270438": {
        "title": "scRNA-seq reveals immune cell heterogeneity in keloid",
        "organism": "Homo sapiens",
        "timepoints": ["Keloid vs normal scar"],
        "cell_types": "CD45+ immune cells from keloid and normal scar dermis",
        "platform": "10X Chromium",
        "relevance": "MEDIUM — Pathological wound healing (keloid/excess scarring)",
        "data_format": "MTX, TSV",
        "n_samples": 6,
        "paper": "Increased Th17 cells in keloid",
        "download_url": "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE270438",
        "sra_url": None,
        "notes": "Human keloid vs normal scar. Pathological wound healing → excess tissue fluidity/stiffness."
    },
}


def main():
    print("=" * 70)
    print("Public scRNA-seq Datasets for Wound Healing Research")
    print("Curated for: Tissue Fluidity Project (Sarate Lab)")
    print("=" * 70)
    
    # Save dataset catalog
    catalog_path = os.path.join(OUTPUT_DIR, 'geo_dataset_catalog.json')
    with open(catalog_path, 'w') as f:
        json.dump(DATASETS, f, indent=2)
    print(f"\nSaved dataset catalog: {catalog_path}")
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"{'GEO ID':<12} {'Organism':<15} {'Samples':<8} {'Relevance':<12} Title")
    print(f"{'='*70}")
    
    for gse_id, info in DATASETS.items():
        print(f"{gse_id:<12} {info['organism'][:14]:<15} {info['n_samples']:<8} "
              f"{info['relevance'].split(' — ')[0]:<12} {info['title'][:50]}")
    
    print(f"\n{'='*70}")
    print("\nTo download a dataset, use one of these methods:\n")
    
    print("METHOD 1: R / GEOquery")
    print("```r")
    print('library(GEOquery)')
    print('getGEOSuppFiles("GSE234269", baseDir = "data/raw/")')
    print("```\n")
    
    print("METHOD 2: wget (supplementary files)")
    print("```bash")
    for gse_id in DATASETS:
        print(f'wget -r -np -nd -P data/raw/{gse_id}/ "{DATASETS[gse_id]["download_url"]}"')
    print("```\n")
    
    print("METHOD 3: SRA Toolkit (raw FASTQ)")
    print("```bash")
    print("prefetch SRR_ACCESSION")
    print("fasterq-dump SRR_ACCESSION --outdir data/raw/ --threads 8")
    print("```\n")
    
    # Generate download script
    script_path = os.path.join('scripts', 'bash', 'download_geo_data.sh')
    os.makedirs(os.path.dirname(script_path), exist_ok=True)
    
    with open(script_path, 'w', newline='\n') as f:
        f.write("#!/bin/bash\n")
        f.write("# Download scRNA-seq datasets from GEO\n")
        f.write("# Project: Tissue Fluidity in Wound Healing (Sarate Lab)\n\n")
        f.write("set -euo pipefail\n\n")
        
        for gse_id, info in DATASETS.items():
            f.write(f"# {gse_id}: {info['title'][:60]}\n")
            f.write(f"mkdir -p data/raw/{gse_id}\n")
            f.write(f"echo \"Downloading {gse_id}...\"\n")
            f.write(f"# wget -r -np -nd -P data/raw/{gse_id}/ \"{info['download_url']}\"\n\n")
        
        f.write("echo \"Done. Check data/raw/ for downloaded files.\"\n")
    
    print(f"Generated download script: {script_path}")
    print("\nRECOMMENDED STARTING DATASETS:")
    print("  1. GSE234269 — Direct wound timepoints (3d, 7d, 14d)")
    print("  2. GSE159827 — Tissue mechanics + wound healing (MOST RELEVANT)")
    print("  3. GSE188432 — Comprehensive young vs aged wound scRNA-seq")


if __name__ == '__main__':
    main()
