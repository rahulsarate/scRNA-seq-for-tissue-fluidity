# Day 20: Config-Driven Design & analysis_config.yaml

> **Goal**: Understand why and how we centralize all parameters in one config file.

---

## The Anti-Pattern: Hardcoded Parameters

```python
# BAD — parameters scattered across scripts
# In script_1.py:
adata = adata[adata.obs['n_genes'] > 200]

# In script_2.py:
sc.pp.filter_cells(adata, min_genes=200)  # Same number, different place

# In script_3.py:
min_g = 200  # Is this the same threshold? Who knows?
```

Problem: Change a threshold → hunt through every script → miss one → inconsistent results.

---

## Our Solution: analysis_config.yaml

One source of truth for every parameter in the project.

```
configs/analysis_config.yaml
       │
       ├──▶ scripts/python/01_scrna_analysis_pipeline.py
       ├──▶ scripts/python/02_visualization_suite.py
       ├──▶ scripts/python/generate_synthetic_data.py
       ├──▶ scripts/R/01_seurat_analysis.R
       └──▶ dashboard/backend/app/config.py
```

---

## Config File Structure

```yaml
# ═══════════════════════════════════════
# Project Identity
# ═══════════════════════════════════════
project:
  name: "tissue-fluidity-scrna"
  pi: "Rahul M Sarate"
  organism: "Mus musculus"
  genome: "GRCm39"

# ═══════════════════════════════════════
# Experimental Design
# ═══════════════════════════════════════
experiment:
  conditions:
    - control
    - wound_3d
    - wound_7d
    - wound_14d
  replicates_per_condition: 2
  total_samples: 8
  platform: "10X Chromium v3"
  sequencer: "NovaSeq 6000"

# ═══════════════════════════════════════
# QC Thresholds
# ═══════════════════════════════════════
qc:
  min_genes: 200
  max_genes: 5000
  min_counts: 500
  max_percent_mt: 15
  min_cells_per_gene: 3

# ═══════════════════════════════════════
# Clustering
# ═══════════════════════════════════════
clustering:
  algorithm: "leiden"
  resolution: 0.8
  n_pcs: 30
  n_neighbors: 15

# ═══════════════════════════════════════
# Differential Expression
# ═══════════════════════════════════════
de:
  method: "pseudobulk_deseq2"
  shrinkage: "ashr"
  padj_threshold: 0.05
  log2fc_threshold: 1.0
  reference: "control"

# ═══════════════════════════════════════
# Tissue Fluidity Signatures
# ═══════════════════════════════════════
tissue_fluidity:
  emt:
    - Vim
    - Cdh1
    - Cdh2
    - Snai1
    - ...
  ecm_remodeling:
    - Fn1
    - Col1a1
    - Col3a1
    - Mmp2
    - ...
```

---

## How Scripts Load Config

### Python
```python
import yaml

def load_config(path="configs/analysis_config.yaml"):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Use config values — never hardcode
min_genes = config['qc']['min_genes']        # 200
resolution = config['clustering']['resolution']  # 0.8
padj_thresh = config['de']['padj_threshold']     # 0.05
```

### R
```r
library(yaml)

config <- yaml::read_yaml("configs/analysis_config.yaml")

min_genes <- config$qc$min_genes        # 200
resolution <- config$clustering$resolution  # 0.8
```

---

## Benefits of Config-Driven Design

| Benefit | Without Config | With Config |
|---------|---------------|-------------|
| Change threshold | Edit 5 files | Edit 1 line |
| Reproducibility | "What params did I use?" | Check config file |
| Documentation | Parameters in comments | Parameters in structured YAML |
| Sharing | "Use min_genes=200 everywhere" | Share config file |
| Version control | Diff scattered changes | Diff one file |
| Error risk | Different values in different scripts | Single source of truth |

---

## Config Sections Map to Pipeline Steps

```
analysis_config.yaml          Pipeline Step
─────────────────────         ────────────────────
project:                  →   Metadata, logging
experiment:               →   Sample organization
qc:                       →   Step 2: QC filtering
normalization:            →   Step 3: Normalize
clustering:               →   Step 5: Leiden clustering
cell_type_markers:        →   Step 6: Annotation
de:                       →   Step 7: Differential expression
tissue_fluidity:          →   Step 8: Fluidity scoring
output:                   →   File saving (format, DPI)
```

---

## Interview Q&A

### Q: "How do you manage analysis parameters?"

> "Everything is centralized in `configs/analysis_config.yaml`. QC thresholds, clustering resolution, DE settings, tissue fluidity gene lists — all in one YAML file. Every script loads this config at startup. If I need to change the mitochondrial percentage threshold from 15% to 20%, I change one line in the config, and every script picks it up. This ensures consistency, reproducibility, and easy parameter tracking across the project."

### Q: "Why YAML instead of JSON or Python dictionaries?"

> "YAML is human-readable — biologists can review parameters without knowing code. It supports comments for documenting why specific values were chosen. It's natively supported in both Python (PyYAML) and R (yaml package), keeping our dual-language project consistent."

### Q: "How does config-driven design help reproducibility?"

> "Three ways: (1) All parameters are in one version-controlled file — git log shows exactly when/what changed. (2) No risk of one script using min_genes=200 while another uses 300 — single source of truth. (3) Anyone can reproduce the analysis by cloning the repo — the config file contains every parameter needed."

---

## Self-Check Questions

1. **Where is the config file?** → `configs/analysis_config.yaml`
2. **Why not hardcode parameters?** → Risk of inconsistency across scripts, hard to track changes
3. **How does Python load the config?** → `yaml.safe_load()` from PyYAML
4. **How does R load the config?** → `yaml::read_yaml()`
5. **What QC thresholds are in the config?** → min_genes=200, max_genes=5000, min_counts=500, max_mt=15%
6. **What clustering settings?** → Leiden, resolution=0.8, 30 PCs, 15 neighbors
7. **What DE method is configured?** → Pseudobulk DESeq2 with ashr shrinkage
8. **How many config sections are there?** → ~8 (project, experiment, qc, normalization, clustering, de, fluidity, output)
9. **What fluidity signature categories?** → EMT, ECM remodeling, cell migration, mechanotransduction, wound signals
10. **How does config help with collaboration?** → Single file to review, structured format, version-controlled, language-agnostic

---

**Next**: [Day 21 — Python Best Practices for Bioinformatics](Day_21_Python_Practices.md)
