#!/usr/bin/env python3
"""
Download, Import & Validate scRNA-seq Datasets from GEO
========================================================
Author: Rahul M Sarate
Project: Dynamic regulation of tissue fluidity controls skin repair

Downloads supplementary count matrices from GEO, parses into AnnData,
validates data integrity, and saves to data/counts/.

Key Datasets:
  GSE234269   91.6 MB  Wound healing 3d/7d/14d      PRIMARY
  GSE159827   12.1 MB  Tissue mechanics (unwounded)  VALIDATION
  GSE188432  ~558  MB  Young vs aged wound healing   COMPARISON

Config: configs/analysis_config.yaml

Usage:
    python scripts/python/00_download_geo_data.py                    # All 3
    python scripts/python/00_download_geo_data.py --dataset GSE234269
    python scripts/python/00_download_geo_data.py --skip-download    # Parse only
"""

import argparse
import gzip
import json
import logging
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve

import anndata as ad
import numpy as np
import pandas as pd
import scanpy as sc
import yaml
from scipy.io import mmread
from scipy.sparse import csr_matrix

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.info("scanpy==%s, anndata==%s, numpy==%s", sc.__version__, ad.__version__, np.__version__)

np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "configs" / "analysis_config.yaml"
COUNTS_DIR = PROJECT_ROOT / "data" / "counts"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"
REFERENCES_DIR = PROJECT_ROOT / "data" / "references"

GEO_FTP = "https://ftp.ncbi.nlm.nih.gov/geo/series"


def _ftp_base(gse_id: str) -> str:
    """Build FTP suppl directory URL for a GEO series."""
    prefix = gse_id[: len(gse_id) - 3] + "nnn"
    return f"{GEO_FTP}/{prefix}/{gse_id}/suppl"


# ============================================================================
# DATASET DEFINITIONS
# ============================================================================
DATASETS = {
    "GSE234269": {
        "title": "Wound healing timepoints 3d/7d/14d (Itgbl1 fibrogenesis)",
        "organism": "Mus musculus",
        "relevance": "PRIMARY — wound healing timepoints matching study design",
        "size_mb": 91.6,
        "format": "tar_csv",
        "url": f"{_ftp_base('GSE234269')}/GSE234269_RAW.tar",
        "samples": {
            "GSM7461430": {"name": "wound_3d", "condition": "wound_3d", "timepoint": "3d"},
            "GSM7461431": {"name": "wound_7d", "condition": "wound_7d", "timepoint": "7d"},
            "GSM7461432": {"name": "wound_14d", "condition": "wound_14d", "timepoint": "14d"},
        },
    },
    "GSE159827": {
        "title": "Tissue mechanics — unwounded dorsal skin (Drop-Seq)",
        "organism": "Mus musculus",
        "relevance": "VALIDATION — tissue mechanics + wound healing",
        "size_mb": 12.1,
        "format": "tar_txt",
        "url": f"{_ftp_base('GSE159827')}/GSE159827_RAW.tar",
        "samples": {
            "GSM4848109": {"name": "unwounded_skin", "condition": "control", "timepoint": "0d"},
        },
    },
    "GSE188432": {
        "title": "Aged wound healing — young vs aged skin (10X MTX)",
        "organism": "Mus musculus",
        "relevance": "COMPARISON — age effects on wound healing",
        "size_mb": 558,
        "format": "10x_mtx",
        "files": {
            "aged_v3_batch1": {
                "barcodes": f"{_ftp_base('GSE188432')}/GSE188432_aged_v3_batch1_barcodes.tsv.gz",
                "features": f"{_ftp_base('GSE188432')}/GSE188432_aged_v3_batch1_features.tsv.gz",
                "matrix": f"{_ftp_base('GSE188432')}/GSE188432_aged_v3_batch1_matrix.mtx.gz",
            },
            "young_aged_v3_batch2": {
                "barcodes": f"{_ftp_base('GSE188432')}/GSE188432_young%2Baged_v3_batch2_barcodes.tsv.gz",
                "features": f"{_ftp_base('GSE188432')}/GSE188432_young%2Baged_v3_batch2_features.tsv.gz",
                "matrix": f"{_ftp_base('GSE188432')}/GSE188432_young%2Baged_v3_batch2_matrix.mtx.gz",
            },
            "young_v2": {
                "barcodes": f"{_ftp_base('GSE188432')}/GSE188432_young_v2_barcodes.tsv.gz",
                "features": f"{_ftp_base('GSE188432')}/GSE188432_young_v2_genes.tsv.gz",
                "matrix": f"{_ftp_base('GSE188432')}/GSE188432_young_v2_matrix.mtx.gz",
            },
        },
        "batches": {
            "aged_v3_batch1": {"age_group": "aged", "chemistry": "v3"},
            "young_aged_v3_batch2": {"age_group": "young+aged", "chemistry": "v3"},
            "young_v2": {"age_group": "young", "chemistry": "v2"},
        },
        "samples": {},  # populated from barcodes
    },
}


# ============================================================================
# DOWNLOAD HELPERS
# ============================================================================
def _progress_hook(block_num: int, block_size: int, total_size: int) -> None:
    """Print download progress."""
    if total_size > 0:
        downloaded = block_num * block_size
        pct = min(100, downloaded * 100 / total_size)
        mb = downloaded / 1e6
        total_mb = total_size / 1e6
        print(f"\r  {pct:5.1f}% ({mb:.1f}/{total_mb:.1f} MB)", end="", flush=True)


def download_file(url: str, dest: Path, desc: str = "") -> bool:
    """Download a file from URL. Skips if dest already exists."""
    if dest.exists() and dest.stat().st_size > 0:
        logger.info("  Already downloaded: %s", dest.name)
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    label = desc or dest.name
    logger.info("  Downloading %s ...", label)
    logger.info("  URL: %s", url)
    try:
        urlretrieve(url, str(dest), reporthook=_progress_hook)
        print()  # newline after progress
        logger.info("  Saved: %s (%.1f MB)", dest.name, dest.stat().st_size / 1e6)
        return True
    except (URLError, HTTPError) as exc:
        logger.error("  Download failed: %s", exc)
        if dest.exists():
            dest.unlink()
        return False


# ============================================================================
# READ HELPERS
# ============================================================================
def read_10x_from_files(
    matrix_path: Path, features_path: Path, barcodes_path: Path
) -> ad.AnnData:
    """Read 10X data from individual (possibly gzipped) MTX/TSV files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Decompress into standard-named files
        _decompress(matrix_path, tmp / "matrix.mtx")
        _decompress(features_path, tmp / "features.tsv")
        _decompress(barcodes_path, tmp / "barcodes.tsv")
        # Check if features has 2 or 3 columns (v2 genes.tsv vs v3 features.tsv)
        first_line = (tmp / "features.tsv").read_text().split("\n")[0]
        n_cols = len(first_line.split("\t"))
        if n_cols < 3:
            # v2 format: genes.tsv has 2 columns — rename
            shutil.move(str(tmp / "features.tsv"), str(tmp / "genes.tsv"))
            adata = sc.read_10x_mtx(str(tmp), var_names="gene_symbols", make_unique=True)
        else:
            adata = sc.read_10x_mtx(str(tmp), var_names="gene_symbols", make_unique=True)
    return adata


def _decompress(src: Path, dest: Path) -> None:
    """Decompress gzipped file, or copy if not gzipped."""
    if str(src).endswith(".gz"):
        with gzip.open(src, "rb") as fin, open(dest, "wb") as fout:
            shutil.copyfileobj(fin, fout)
    else:
        shutil.copy2(src, dest)


def _detect_matrix_orientation(df: pd.DataFrame) -> str:
    """Detect whether a CSV/TSV is genes-x-cells or cells-x-genes."""
    # Heuristic: if first column has gene-like names, it's genes x cells
    first_col = df.iloc[:, 0].astype(str) if df.index.dtype == object else df.index.astype(str)
    sample_vals = first_col[:20].tolist()
    # Gene names typically: Krt14, Col1a1, mt-Co1, A2m, etc.
    # Barcodes: ATCGATCG-1, AAACCTGAGAAACCAT-1
    barcode_like = sum(1 for v in sample_vals if "-" in v and len(v) > 10)
    if barcode_like > len(sample_vals) * 0.5:
        return "cells_x_genes"
    return "genes_x_cells"


# ============================================================================
# PER-DATASET IMPORTERS
# ============================================================================
def import_gse234269(skip_download: bool = False) -> Optional[ad.AnnData]:
    """Import GSE234269: wound healing 3d/7d/14d (CSV in tar)."""
    gse = "GSE234269"
    info = DATASETS[gse]
    out_dir = COUNTS_DIR / gse
    out_dir.mkdir(parents=True, exist_ok=True)
    h5ad_path = out_dir / f"{gse}.h5ad"

    if h5ad_path.exists():
        logger.info("[%s] h5ad already exists, loading: %s", gse, h5ad_path)
        return sc.read_h5ad(str(h5ad_path))

    # Download
    tar_path = out_dir / f"{gse}_RAW.tar"
    if not skip_download:
        if not download_file(info["url"], tar_path, f"{gse} RAW tar (91.6 MB)"):
            return None

    if not tar_path.exists():
        logger.error("[%s] Tar file not found: %s", gse, tar_path)
        return None

    # Extract
    logger.info("[%s] Extracting tar...", gse)
    extract_dir = out_dir / "extracted"
    extract_dir.mkdir(exist_ok=True)
    with tarfile.open(str(tar_path), "r") as tar:
        # Security: validate member paths
        for member in tar.getmembers():
            if member.name.startswith("/") or ".." in member.name:
                raise ValueError(f"Unsafe tar member: {member.name}")
        tar.extractall(str(extract_dir))

    # Parse CSV files — each GSM sample is a CSV
    adatas = []
    sample_info = info["samples"]
    # Deduplicate: glob("*.csv*") and glob("*.gz") can overlap for .csv.gz files
    csv_set: set[str] = set()
    csv_files: list[Path] = []
    for pattern in ["*.csv", "*.csv.gz"]:
        for p in sorted(extract_dir.glob(pattern)):
            if p.name not in csv_set:
                csv_set.add(p.name)
                csv_files.append(p)

    if not csv_files:
        csv_files = sorted(extract_dir.rglob("*.csv*"))

    logger.info("[%s] Found %d CSV files in tar", gse, len(csv_files))

    for csv_path in csv_files:
        fname = csv_path.name
        logger.info("  Parsing: %s", fname)

        # Match GSM ID from filename
        gsm_id = None
        for gid in sample_info:
            if gid in fname:
                gsm_id = gid
                break

        try:
            # Memory-efficient chunked reading for large CSV files.
            # These CSVs are genes-x-cells (32k genes x 5k-23k cells),
            # so we read in chunks of 2000 genes (rows), convert each
            # chunk to sparse immediately, then stack vertically.
            from scipy.sparse import vstack as sparse_vstack

            compression = "gzip" if fname.endswith(".gz") else None
            chunk_iter = pd.read_csv(
                csv_path, index_col=0, compression=compression, chunksize=2000,
            )

            sparse_chunks: list[csr_matrix] = []
            gene_names: list[str] = []
            barcodes: list[str] | None = None

            for i, chunk_df in enumerate(chunk_iter):
                if barcodes is None:
                    barcodes = chunk_df.columns.tolist()
                gene_names.extend(chunk_df.index.astype(str).tolist())
                sparse_chunks.append(csr_matrix(chunk_df.values.astype(np.float32)))
                if (i + 1) % 5 == 0:
                    logger.info("    ... processed %d genes", len(gene_names))

            # Stack all chunks (genes x cells), then transpose to cells x genes
            genes_x_cells = sparse_vstack(sparse_chunks, format="csr")
            X = genes_x_cells.T.tocsr()
            del sparse_chunks, genes_x_cells  # free memory

            logger.info("    Parsed: %d cells x %d genes", X.shape[0], X.shape[1])

            adata = ad.AnnData(
                X=X,
                obs=pd.DataFrame(index=barcodes),
                var=pd.DataFrame(index=gene_names),
            )
            adata.var_names_make_unique()
            adata.obs_names_make_unique()

            # Add metadata
            if gsm_id and gsm_id in sample_info:
                si = sample_info[gsm_id]
                adata.obs["sample"] = si["name"]
                adata.obs["condition"] = si["condition"]
                adata.obs["timepoint"] = si["timepoint"]
                adata.obs["gsm_id"] = gsm_id
            else:
                # Infer from filename
                adata.obs["sample"] = fname.split(".")[0]
                adata.obs["gsm_id"] = fname.split("_")[0] if "GSM" in fname else "unknown"

            adata.obs["dataset"] = gse
            adata.obs["organism"] = "Mus musculus"
            logger.info("    AnnData: %d cells x %d genes", adata.n_obs, adata.n_vars)
            adatas.append(adata)

        except Exception as exc:
            logger.warning("    Failed to parse %s: %s", fname, exc)
            continue

    if not adatas:
        logger.error("[%s] No data files parsed successfully", gse)
        return None

    # Concatenate samples
    if len(adatas) == 1:
        combined = adatas[0]
    else:
        combined = ad.concat(adatas, join="outer", fill_value=0)
        combined.obs_names_make_unique()

    combined.uns["dataset"] = gse
    combined.uns["title"] = info["title"]

    logger.info("[%s] Combined: %d cells x %d genes", gse, combined.n_obs, combined.n_vars)
    combined.write_h5ad(str(h5ad_path))
    logger.info("[%s] Saved: %s", gse, h5ad_path)
    return combined


def import_gse159827(skip_download: bool = False) -> Optional[ad.AnnData]:
    """Import GSE159827: tissue mechanics — unwounded skin (Drop-Seq DGE)."""
    gse = "GSE159827"
    info = DATASETS[gse]
    out_dir = COUNTS_DIR / gse
    out_dir.mkdir(parents=True, exist_ok=True)
    h5ad_path = out_dir / f"{gse}.h5ad"

    if h5ad_path.exists():
        logger.info("[%s] h5ad already exists, loading: %s", gse, h5ad_path)
        return sc.read_h5ad(str(h5ad_path))

    # Download
    tar_path = out_dir / f"{gse}_RAW.tar"
    if not skip_download:
        if not download_file(info["url"], tar_path, f"{gse} RAW tar (12.1 MB)"):
            return None

    if not tar_path.exists():
        logger.error("[%s] Tar file not found: %s", gse, tar_path)
        return None

    # Extract
    logger.info("[%s] Extracting tar...", gse)
    extract_dir = out_dir / "extracted"
    extract_dir.mkdir(exist_ok=True)
    with tarfile.open(str(tar_path), "r") as tar:
        for member in tar.getmembers():
            if member.name.startswith("/") or ".." in member.name:
                raise ValueError(f"Unsafe tar member: {member.name}")
        tar.extractall(str(extract_dir))

    # Parse TXT/TSV files (Drop-Seq DGE: genes x cells)
    txt_files = sorted(extract_dir.glob("*.txt*")) + sorted(extract_dir.glob("*.tsv*"))
    if not txt_files:
        txt_files = sorted(extract_dir.rglob("*.txt*")) + sorted(extract_dir.rglob("*.tsv*"))

    logger.info("[%s] Found %d text files", gse, len(txt_files))

    adatas = []
    sample_info = info["samples"]

    for txt_path in txt_files:
        fname = txt_path.name
        logger.info("  Parsing: %s", fname)

        try:
            if fname.endswith(".gz"):
                df = pd.read_csv(txt_path, sep="\t", index_col=0, compression="gzip")
            else:
                df = pd.read_csv(txt_path, sep="\t", index_col=0)

            logger.info("    Shape: %s", df.shape)

            # Drop-Seq DGE is genes x cells
            orient = _detect_matrix_orientation(df)
            if orient == "genes_x_cells":
                adata = ad.AnnData(
                    X=csr_matrix(df.values.T.astype(np.float32)),
                    obs=pd.DataFrame(index=df.columns),
                    var=pd.DataFrame(index=df.index),
                )
            else:
                adata = ad.AnnData(
                    X=csr_matrix(df.values.astype(np.float32)),
                    obs=pd.DataFrame(index=df.index),
                    var=pd.DataFrame(index=df.columns),
                )

            adata.var_names_make_unique()
            adata.obs_names_make_unique()

            # Match GSM ID
            gsm_id = None
            for gid in sample_info:
                if gid in fname:
                    gsm_id = gid
                    break

            if gsm_id and gsm_id in sample_info:
                si = sample_info[gsm_id]
                adata.obs["sample"] = si["name"]
                adata.obs["condition"] = si["condition"]
                adata.obs["timepoint"] = si["timepoint"]
                adata.obs["gsm_id"] = gsm_id
            else:
                adata.obs["sample"] = fname.split(".")[0]

            adata.obs["dataset"] = gse
            adata.obs["organism"] = "Mus musculus"
            logger.info("    AnnData: %d cells x %d genes", adata.n_obs, adata.n_vars)
            adatas.append(adata)

        except Exception as exc:
            logger.warning("    Failed to parse %s: %s", fname, exc)
            continue

    if not adatas:
        logger.error("[%s] No data files parsed successfully", gse)
        return None

    combined = ad.concat(adatas, join="outer", fill_value=0) if len(adatas) > 1 else adatas[0]
    combined.obs_names_make_unique()
    combined.uns["dataset"] = gse
    combined.uns["title"] = info["title"]

    logger.info("[%s] Combined: %d cells x %d genes", gse, combined.n_obs, combined.n_vars)
    combined.write_h5ad(str(h5ad_path))
    logger.info("[%s] Saved: %s", gse, h5ad_path)
    return combined


def import_gse188432(skip_download: bool = False) -> Optional[ad.AnnData]:
    """Import GSE188432: aged wound healing (10X MTX batches, ~558 MB)."""
    gse = "GSE188432"
    info = DATASETS[gse]
    out_dir = COUNTS_DIR / gse
    dl_dir = out_dir / "download"
    out_dir.mkdir(parents=True, exist_ok=True)
    dl_dir.mkdir(parents=True, exist_ok=True)
    h5ad_path = out_dir / f"{gse}.h5ad"

    if h5ad_path.exists():
        logger.info("[%s] h5ad already exists, loading: %s", gse, h5ad_path)
        return sc.read_h5ad(str(h5ad_path))

    # Download all batch files
    batch_files = info["files"]
    if not skip_download:
        for batch_name, urls in batch_files.items():
            for file_type, url in urls.items():
                fname = url.split("/")[-1].replace("%2B", "+")
                dest = dl_dir / fname
                if not download_file(url, dest, f"{batch_name}/{file_type}"):
                    logger.error("[%s] Failed to download %s — skipping batch", gse, fname)
                    break

    # Parse each batch
    adatas = []
    batch_meta = info["batches"]

    for batch_name, urls in batch_files.items():
        logger.info("[%s] Parsing batch: %s", gse, batch_name)

        # Find downloaded files for this batch
        matrix_file = None
        features_file = None
        barcodes_file = None

        for fpath in dl_dir.iterdir():
            fname_lower = fpath.name.lower().replace("+", "_").replace("%2b", "_")
            batch_key = batch_name.lower().replace("+", "_")
            if batch_key not in fname_lower and batch_name.replace("_", "") not in fname_lower:
                # Try a more relaxed match
                parts = batch_name.split("_")
                if not all(p.lower() in fname_lower for p in parts if len(p) > 2):
                    continue

            if "matrix" in fpath.name.lower():
                matrix_file = fpath
            elif "features" in fpath.name.lower() or "genes" in fpath.name.lower():
                features_file = fpath
            elif "barcodes" in fpath.name.lower():
                barcodes_file = fpath

        if not all([matrix_file, features_file, barcodes_file]):
            logger.warning(
                "  Missing files for batch %s (matrix=%s, features=%s, barcodes=%s)",
                batch_name, matrix_file, features_file, barcodes_file,
            )
            continue

        try:
            adata = read_10x_from_files(matrix_file, features_file, barcodes_file)
            meta = batch_meta.get(batch_name, {})
            adata.obs["batch"] = batch_name
            adata.obs["age_group"] = meta.get("age_group", "unknown")
            adata.obs["chemistry"] = meta.get("chemistry", "unknown")
            adata.obs["dataset"] = gse
            adata.obs["organism"] = "Mus musculus"
            logger.info("  Batch %s: %d cells x %d genes", batch_name, adata.n_obs, adata.n_vars)
            adatas.append(adata)
        except Exception as exc:
            logger.warning("  Failed to parse batch %s: %s", batch_name, exc)
            continue

    if not adatas:
        logger.error("[%s] No batches parsed successfully", gse)
        return None

    # Concatenate
    combined = ad.concat(adatas, join="outer", fill_value=0)
    combined.obs_names_make_unique()
    combined.uns["dataset"] = gse
    combined.uns["title"] = info["title"]

    logger.info("[%s] Combined: %d cells x %d genes", gse, combined.n_obs, combined.n_vars)
    combined.write_h5ad(str(h5ad_path))
    logger.info("[%s] Saved: %s", gse, h5ad_path)
    return combined


# ============================================================================
# VALIDATION
# ============================================================================
def validate_adata(adata: ad.AnnData, gse_id: str) -> dict:
    """Run validation checks on an imported AnnData object."""
    report = {
        "dataset": gse_id,
        "n_cells": adata.n_obs,
        "n_genes": adata.n_vars,
        "sparsity_pct": 0.0,
        "median_genes_per_cell": 0.0,
        "median_counts_per_cell": 0.0,
        "has_mt_genes": False,
        "n_mt_genes": 0,
        "obs_columns": list(adata.obs.columns),
        "issues": [],
        "status": "PASS",
    }

    # Sparsity
    from scipy.sparse import issparse
    if issparse(adata.X):
        nnz = adata.X.nnz
        total = adata.n_obs * adata.n_vars
        report["sparsity_pct"] = round((1 - nnz / total) * 100, 1) if total > 0 else 0
    else:
        report["sparsity_pct"] = round((np.asarray(adata.X) == 0).sum() / adata.X.size * 100, 1)

    # Per-cell QC
    genes_per_cell = np.diff(adata.X.indptr) if issparse(adata.X) else (np.asarray(adata.X) > 0).sum(axis=1)
    counts_per_cell = np.asarray(adata.X.sum(axis=1)).flatten()
    report["median_genes_per_cell"] = float(np.median(genes_per_cell))
    report["median_counts_per_cell"] = float(np.median(counts_per_cell))

    # Mitochondrial genes (mouse: mt- prefix)
    mt_mask = adata.var_names.str.startswith("mt-") | adata.var_names.str.startswith("MT-")
    report["has_mt_genes"] = bool(mt_mask.any())
    report["n_mt_genes"] = int(mt_mask.sum())

    # Validation checks
    if adata.n_obs == 0:
        report["issues"].append("CRITICAL: No cells in dataset")
        report["status"] = "FAIL"
    if adata.n_vars < 100:
        report["issues"].append(f"WARNING: Very few genes ({adata.n_vars})")
    if report["median_genes_per_cell"] < 50:
        report["issues"].append(f"WARNING: Low median genes/cell ({report['median_genes_per_cell']:.0f})")
    if report["sparsity_pct"] < 80:
        report["issues"].append(f"NOTE: Unusually low sparsity ({report['sparsity_pct']}%)")
    if not report["has_mt_genes"]:
        report["issues"].append("NOTE: No mitochondrial genes found (mt- prefix)")

    if not report["issues"]:
        report["issues"] = ["None"]

    return report


def print_validation(report: dict) -> None:
    """Print formatted validation report."""
    gse = report["dataset"]
    status = report["status"]
    print(f"\n{'='*60}")
    print(f"  VALIDATION: {gse} — {status}")
    print(f"{'='*60}")
    print(f"  Cells:              {report['n_cells']:,}")
    print(f"  Genes:              {report['n_genes']:,}")
    print(f"  Sparsity:           {report['sparsity_pct']}%")
    print(f"  Median genes/cell:  {report['median_genes_per_cell']:.0f}")
    print(f"  Median counts/cell: {report['median_counts_per_cell']:.0f}")
    print(f"  MT genes:           {report['n_mt_genes']} ({'yes' if report['has_mt_genes'] else 'no'})")
    print(f"  Obs columns:        {', '.join(report['obs_columns'])}")
    if report["issues"] != ["None"]:
        print(f"  Issues:")
        for iss in report["issues"]:
            print(f"    - {iss}")
    print(f"{'='*60}")


# ============================================================================
# SAMPLE METADATA
# ============================================================================
def create_sample_metadata(results: dict[str, ad.AnnData]) -> pd.DataFrame:
    """Create a combined sample metadata CSV from all imported datasets."""
    rows = []
    for gse_id, adata in results.items():
        if adata is None:
            continue
        info = DATASETS[gse_id]
        if "sample" in adata.obs.columns:
            for sample_name in adata.obs["sample"].unique():
                mask = adata.obs["sample"] == sample_name
                cond = adata.obs.loc[mask, "condition"].iloc[0] if "condition" in adata.obs else "unknown"
                tp = adata.obs.loc[mask, "timepoint"].iloc[0] if "timepoint" in adata.obs else "unknown"
                rows.append({
                    "dataset": gse_id,
                    "sample_id": sample_name,
                    "condition": cond,
                    "timepoint": tp,
                    "n_cells": int(mask.sum()),
                    "organism": "Mus musculus",
                    "relevance": info["relevance"],
                })
        elif "batch" in adata.obs.columns:
            for batch_name in adata.obs["batch"].unique():
                mask = adata.obs["batch"] == batch_name
                age = adata.obs.loc[mask, "age_group"].iloc[0] if "age_group" in adata.obs else "unknown"
                rows.append({
                    "dataset": gse_id,
                    "sample_id": batch_name,
                    "condition": f"batch_{batch_name}",
                    "timepoint": age,
                    "n_cells": int(mask.sum()),
                    "organism": "Mus musculus",
                    "relevance": info["relevance"],
                })
        else:
            rows.append({
                "dataset": gse_id,
                "sample_id": gse_id,
                "condition": "unknown",
                "timepoint": "unknown",
                "n_cells": adata.n_obs,
                "organism": "Mus musculus",
                "relevance": info["relevance"],
            })

    df = pd.DataFrame(rows)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = METADATA_DIR / "geo_sample_metadata.csv"
    df.to_csv(out_path, index=False)
    logger.info("Sample metadata saved: %s (%d samples)", out_path, len(df))
    return df


# ============================================================================
# CATALOG (backward compat)
# ============================================================================
def save_catalog() -> None:
    """Save dataset catalog JSON (reference info)."""
    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    catalog = {}
    for gse_id, info in DATASETS.items():
        catalog[gse_id] = {
            "title": info["title"],
            "organism": info["organism"],
            "relevance": info["relevance"],
            "size_mb": info["size_mb"],
            "format": info["format"],
        }
    path = REFERENCES_DIR / "geo_dataset_catalog.json"
    with open(path, "w") as f:
        json.dump(catalog, f, indent=2)
    logger.info("Dataset catalog saved: %s", path)


# ============================================================================
# MAIN
# ============================================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download, import & validate GEO scRNA-seq datasets"
    )
    parser.add_argument(
        "--dataset", type=str, default=None,
        choices=list(DATASETS.keys()),
        help="Download a single dataset (default: all 3)",
    )
    parser.add_argument(
        "--skip-download", action="store_true",
        help="Skip downloads, parse already-downloaded files only",
    )
    args = parser.parse_args()

    # Load project config
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)
        logger.info("Loaded config: %s", CONFIG_PATH)
    else:
        logger.warning("Config not found: %s", CONFIG_PATH)
        config = {}

    print("=" * 70)
    print("  scRNA-seq GEO Data Import & Validation")
    print(f"  Project: {config.get('project', {}).get('name', 'Tissue Fluidity')}")
    print(f"  Output:  {COUNTS_DIR}")
    print("=" * 70)

    # Save catalog
    save_catalog()

    # Determine which datasets to import
    if args.dataset:
        targets = [args.dataset]
    else:
        targets = list(DATASETS.keys())

    # Print download plan
    total_mb = sum(DATASETS[gse]["size_mb"] for gse in targets)
    print(f"\nDatasets to import: {', '.join(targets)}")
    print(f"Estimated download: ~{total_mb:.0f} MB\n")

    # Import each dataset
    importers = {
        "GSE234269": import_gse234269,
        "GSE159827": import_gse159827,
        "GSE188432": import_gse188432,
    }

    results: dict[str, Optional[ad.AnnData]] = {}
    reports: list[dict] = []

    for gse_id in targets:
        print(f"\n{'─'*60}")
        print(f"  Importing {gse_id}: {DATASETS[gse_id]['title']}")
        print(f"{'─'*60}")
        importer = importers.get(gse_id)
        if importer is None:
            logger.error("No importer for %s", gse_id)
            continue

        adata = importer(skip_download=args.skip_download)
        results[gse_id] = adata

        if adata is not None:
            report = validate_adata(adata, gse_id)
            print_validation(report)
            reports.append(report)

    # Save validation report
    if reports:
        report_df = pd.DataFrame(reports)
        report_path = COUNTS_DIR / "import_validation_report.csv"
        report_df.to_csv(report_path, index=False)
        logger.info("Validation report saved: %s", report_path)

    # Create sample metadata
    valid_results = {k: v for k, v in results.items() if v is not None}
    if valid_results:
        meta_df = create_sample_metadata(valid_results)
        print(f"\n{'─'*60}")
        print("  Sample Metadata Summary")
        print(f"{'─'*60}")
        print(meta_df.to_string(index=False))

    # Final summary
    print(f"\n{'='*70}")
    print("  IMPORT SUMMARY")
    print(f"{'='*70}")
    for gse_id in targets:
        adata = results.get(gse_id)
        if adata is not None:
            print(f"  ✓ {gse_id}: {adata.n_obs:,} cells x {adata.n_vars:,} genes")
        else:
            print(f"  ✗ {gse_id}: FAILED")
    print(f"\n  Output directory: {COUNTS_DIR}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
