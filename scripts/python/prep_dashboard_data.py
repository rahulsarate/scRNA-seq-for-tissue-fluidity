"""Quick preprocessing of synthetic data to prepare for dashboard."""
import scanpy as sc
import numpy as np
import pandas as pd
import os
import warnings

warnings.filterwarnings("ignore")
np.random.seed(42)

print("Loading synthetic data...")
adata = sc.read_h5ad("data/synthetic/synthetic_counts.h5ad")
print(f"  {adata.n_obs} cells x {adata.n_vars} genes")

print("Preprocessing...")
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata
sc.pp.highly_variable_genes(adata, n_top_genes=1500)
sc.pp.pca(adata, n_comps=30, random_state=42)
sc.pp.neighbors(adata, n_pcs=30, random_state=42)
sc.tl.umap(adata, random_state=42)
sc.tl.leiden(adata, random_state=42, resolution=0.8)
print(f"  UMAP computed, {adata.obs['leiden'].nunique()} clusters")

adata.obs["sample_id"] = adata.obs["condition"].astype(str) + "_rep1"

out_dir = "analysis/clustering"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "wound_adata.h5ad")
adata.write_h5ad(out_path)
print(f"  Saved: {out_path}")

print("Generating DE results...")
de_dir = "analysis/de"
os.makedirs(de_dir, exist_ok=True)

for cond in ["wound_3d", "wound_7d", "wound_14d"]:
    comp_name = f"{cond}_vs_control"
    mask_cond = adata.obs["condition"] == cond
    mask_ctrl = adata.obs["condition"] == "control"
    if mask_cond.sum() == 0 or mask_ctrl.sum() == 0:
        continue
    sub = adata[mask_cond | mask_ctrl].copy()
    sc.tl.rank_genes_groups(
        sub, groupby="condition", groups=[cond], reference="control", method="wilcoxon"
    )
    result = sc.get.rank_genes_groups_df(sub, group=cond)
    result = result.rename(
        columns={
            "names": "gene",
            "logfoldchanges": "log2FoldChange",
            "pvals_adj": "padj",
            "pvals": "pvalue",
        }
    )
    result["baseMean"] = np.random.uniform(50, 5000, len(result))
    result.to_csv(os.path.join(de_dir, f"{comp_name}.csv"))
    n_sig = (result["padj"] < 0.05).sum()
    print(f"  {comp_name}: {len(result)} genes, {n_sig} significant")

print("Generating QC summary...")
qc_dir = "analysis/qc"
os.makedirs(qc_dir, exist_ok=True)
qc_data = []
for sample in adata.obs["sample_id"].unique():
    mask = adata.obs["sample_id"] == sample
    qc_data.append(
        {
            "sample": sample,
            "n_cells": int(mask.sum()),
            "median_genes": float(adata.obs.loc[mask, "nFeature_RNA"].median()),
            "median_counts": float(adata.obs.loc[mask, "nCount_RNA"].median()),
            "median_mt_pct": float(adata.obs.loc[mask, "percent_mt"].median()),
        }
    )
pd.DataFrame(qc_data).to_csv(os.path.join(qc_dir, "qc_summary.csv"), index=False)
print("  Saved QC summary")

print("DONE - all data ready for dashboard")
