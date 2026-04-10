"""UMAP coordinates and cell metadata endpoint."""

from fastapi import APIRouter, HTTPException, Query

from app.config import CELL_TYPE_COLORS, CONDITION_COLORS
from app.services.data_loader import DataLoader

router = APIRouter(tags=["UMAP"])


@router.get("/umap")
async def get_umap(
    color_by: str = Query("cell_type", description="Column to color by"),
) -> dict:
    """Return UMAP coordinates with cell metadata for interactive scatter plot."""
    loader = DataLoader.get_instance()
    if loader.adata is None:
        raise HTTPException(status_code=404, detail="No h5ad data loaded")

    coords = loader.get_umap_coords()
    if coords is None:
        raise HTTPException(status_code=404, detail="No UMAP coordinates found in obsm")

    obs = loader.adata.obs
    result: dict = {
        "x": coords[:, 0].tolist(),
        "y": coords[:, 1].tolist(),
        "n_cells": len(coords),
    }

    if color_by in obs.columns:
        result["labels"] = obs[color_by].astype(str).tolist()
        result["color_by"] = color_by

        if color_by in ("cell_type", "cell_type_annotation"):
            result["color_map"] = CELL_TYPE_COLORS
        elif color_by == "condition":
            result["color_map"] = CONDITION_COLORS
    else:
        available = [
            c for c in obs.columns if obs[c].dtype.name in ("category", "object")
        ]
        raise HTTPException(
            status_code=400,
            detail=f"Column '{color_by}' not found. Available: {available}",
        )

    # Hover metadata
    hover_cols = ["cell_type", "condition", "sample", "leiden"]
    hover_data: dict[str, list] = {}
    for col in hover_cols:
        if col in obs.columns:
            hover_data[col] = obs[col].astype(str).tolist()
    result["hover"] = hover_data

    return result
