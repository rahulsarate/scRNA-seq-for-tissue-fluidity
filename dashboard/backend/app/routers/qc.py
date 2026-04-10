"""QC summary metrics endpoint."""

from fastapi import APIRouter, HTTPException

from app.services.data_loader import DataLoader

router = APIRouter(tags=["Quality Control"])


@router.get("/qc/summary")
async def get_qc_summary() -> dict:
    """Return QC metrics summary."""
    loader = DataLoader.get_instance()

    # Try pre-computed CSV summary first
    if loader.qc_summary is not None:
        return {
            "source": "csv",
            "data": loader.qc_summary.to_dict(orient="records"),
            "columns": list(loader.qc_summary.columns),
        }

    # Fall back to computing from the loaded h5ad
    if loader.adata is None:
        raise HTTPException(status_code=404, detail="No data loaded")

    obs = loader.adata.obs
    metrics: dict = {}

    for col in ["n_genes_by_counts", "nFeature_RNA", "n_genes"]:
        if col in obs.columns:
            metrics["genes_per_cell"] = {
                "mean": float(obs[col].mean()),
                "median": float(obs[col].median()),
                "min": int(obs[col].min()),
                "max": int(obs[col].max()),
            }
            break

    for col in ["total_counts", "nCount_RNA", "n_counts"]:
        if col in obs.columns:
            metrics["counts_per_cell"] = {
                "mean": float(obs[col].mean()),
                "median": float(obs[col].median()),
                "min": int(obs[col].min()),
                "max": int(obs[col].max()),
            }
            break

    for col in ["pct_counts_mt", "percent.mt", "percent_mt"]:
        if col in obs.columns:
            metrics["percent_mt"] = {
                "mean": float(obs[col].mean()),
                "median": float(obs[col].median()),
                "max": float(obs[col].max()),
            }
            break

    metrics["n_cells"] = int(obs.shape[0])
    metrics["n_genes"] = int(loader.adata.n_vars)

    sample_col = next(
        (c for c in ["sample", "sample_id", "orig.ident"] if c in obs.columns), None
    )
    if sample_col:
        per_sample = obs.groupby(sample_col).size().to_dict()
        metrics["cells_per_sample"] = {str(k): int(v) for k, v in per_sample.items()}

    return {"source": "h5ad", "metrics": metrics}
