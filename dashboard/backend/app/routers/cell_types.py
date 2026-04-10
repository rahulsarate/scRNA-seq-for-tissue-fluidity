"""Cell type annotations and proportion endpoints."""

from fastapi import APIRouter, HTTPException

from app.config import CELL_TYPE_COLORS, CONDITION_COLORS
from app.services.data_loader import DataLoader

router = APIRouter(tags=["Cell Types"])


@router.get("/cell-types")
async def get_cell_types() -> dict:
    """Return cell type annotations and counts."""
    loader = DataLoader.get_instance()
    if loader.adata is None:
        raise HTTPException(status_code=404, detail="No h5ad data loaded")

    obs = loader.adata.obs
    ct_col = next(
        (c for c in ["cell_type", "cell_type_annotation", "celltype"] if c in obs.columns),
        None,
    )
    if ct_col is None:
        return {"cell_types": [], "message": "No cell type column found"}

    counts = obs[ct_col].value_counts().to_dict()
    return {
        "column": ct_col,
        "cell_types": [
            {"name": k, "count": int(v), "color": CELL_TYPE_COLORS.get(str(k), "#999999")}
            for k, v in counts.items()
        ],
        "total_cells": int(obs.shape[0]),
    }


@router.get("/proportions")
async def get_proportions() -> dict:
    """Return cell type proportions per condition (stacked bar data)."""
    loader = DataLoader.get_instance()
    if loader.adata is None:
        raise HTTPException(status_code=404, detail="No h5ad data loaded")

    obs = loader.adata.obs
    ct_col = next(
        (c for c in ["cell_type", "cell_type_annotation", "celltype"] if c in obs.columns),
        None,
    )
    cond_col = next(
        (c for c in ["condition", "sample_condition", "group"] if c in obs.columns),
        None,
    )
    if ct_col is None or cond_col is None:
        raise HTTPException(
            status_code=404,
            detail=f"Need cell_type and condition columns. Found: {list(obs.columns)}",
        )

    crosstab = obs.groupby([cond_col, ct_col]).size().unstack(fill_value=0)
    proportions = crosstab.div(crosstab.sum(axis=1), axis=0)

    return {
        "conditions": list(proportions.index),
        "cell_types": list(proportions.columns),
        "proportions": proportions.to_dict(orient="index"),
        "counts": crosstab.to_dict(orient="index"),
        "condition_colors": CONDITION_COLORS,
        "cell_type_colors": CELL_TYPE_COLORS,
    }
