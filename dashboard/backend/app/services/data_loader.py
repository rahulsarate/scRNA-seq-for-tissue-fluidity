"""Singleton data loader — reads h5ad and CSV files, caches in memory."""

import logging
from pathlib import Path
from threading import Lock
from typing import Optional

import anndata as ad
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[4]


class DataLoader:
    """Thread-safe singleton that loads and caches analysis data."""

    _instance: Optional["DataLoader"] = None
    _lock = Lock()

    def __init__(self) -> None:
        self.adata: Optional[ad.AnnData] = None
        self.de_results: dict[str, pd.DataFrame] = {}
        self.qc_summary: Optional[pd.DataFrame] = None
        self._loaded = False

    @classmethod
    def get_instance(cls) -> "DataLoader":
        """Return the singleton DataLoader instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load_all(self) -> None:
        """Load all available analysis data."""
        if self._loaded:
            return

        self._load_h5ad()
        self._load_de_results()
        self._load_qc_summary()
        self._loaded = True

    def _load_h5ad(self) -> None:
        """Load the first available h5ad file from known locations."""
        h5ad_candidates = [
            PROJECT_ROOT / "analysis" / "clustering" / "wound_adata.h5ad",
            PROJECT_ROOT / "analysis" / "clustering" / "processed_adata.h5ad",
            PROJECT_ROOT / "data" / "synthetic" / "synthetic_wound_adata.h5ad",
            PROJECT_ROOT / "data" / "counts" / "integrated.h5ad",
        ]
        for path in h5ad_candidates:
            if path.exists():
                logger.info("Loading AnnData from %s", path)
                self.adata = ad.read_h5ad(path)
                logger.info(
                    "Loaded %d cells x %d genes", self.adata.n_obs, self.adata.n_vars
                )
                return

        # Fallback: search for any h5ad in analysis/ then data/ (skip data/raw/)
        for search_dir in [PROJECT_ROOT / "analysis", PROJECT_ROOT / "data"]:
            if not search_dir.exists():
                continue
            for p in search_dir.rglob("*.h5ad"):
                if "raw" in p.parts:
                    continue
                logger.info("Loading AnnData from %s", p)
                self.adata = ad.read_h5ad(p)
                return

        logger.warning("No h5ad files found — dashboard will run with limited data")

    def _load_de_results(self) -> None:
        """Load all DE CSV files from analysis/de/."""
        de_dir = PROJECT_ROOT / "analysis" / "de"
        if not de_dir.exists():
            return
        for csv_path in de_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_path, index_col=0)
                self.de_results[csv_path.stem] = df
                logger.info("Loaded DE: %s (%d genes)", csv_path.stem, len(df))
            except Exception as exc:
                logger.warning("Failed to load %s: %s", csv_path, exc)

    def _load_qc_summary(self) -> None:
        """Load QC summary CSV if available."""
        qc_dir = PROJECT_ROOT / "analysis" / "qc"
        if not qc_dir.exists():
            return
        for csv_path in qc_dir.glob("*summary*.csv"):
            try:
                self.qc_summary = pd.read_csv(csv_path)
                logger.info("Loaded QC summary: %s", csv_path.name)
                return
            except Exception as exc:
                logger.warning("Failed to load QC: %s", exc)

    # ------------------------------------------------------------------
    # Data access helpers
    # ------------------------------------------------------------------

    def get_umap_coords(self) -> Optional[np.ndarray]:
        """Return UMAP coordinates array (n_cells, 2) if available."""
        if self.adata is None:
            return None
        if "X_umap" in self.adata.obsm:
            return self.adata.obsm["X_umap"]
        return None

    def get_gene_expression(self, gene: str) -> Optional[np.ndarray]:
        """Return expression vector for a single gene."""
        if self.adata is None or gene not in self.adata.var_names:
            return None
        idx = list(self.adata.var_names).index(gene)
        x = self.adata.X[:, idx]
        if hasattr(x, "toarray"):
            return x.toarray().flatten()
        return np.asarray(x).flatten()

    def search_genes(self, query: str, limit: int = 20) -> list[str]:
        """Search gene names by prefix (case-insensitive)."""
        if self.adata is None:
            return []
        query_lower = query.lower()
        matches = [
            g for g in self.adata.var_names if g.lower().startswith(query_lower)
        ]
        return sorted(matches)[:limit]
