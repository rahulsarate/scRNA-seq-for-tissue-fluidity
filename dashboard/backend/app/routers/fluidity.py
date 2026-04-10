"""Tissue fluidity gene signature endpoints."""

import numpy as np
from fastapi import APIRouter, HTTPException

from app.config import CONFIG
from app.services.data_loader import DataLoader

router = APIRouter(tags=["Tissue Fluidity"])


@router.get("/fluidity/signatures")
async def get_fluidity_signatures() -> dict:
    """Return tissue fluidity gene signatures from config."""
    sigs = CONFIG.get("tissue_fluidity_signatures", {})
    return {"signatures": sigs}


@router.get("/fluidity/scores")
async def get_fluidity_scores() -> dict:
    """Compute per-cell fluidity scores for each signature category."""
    loader = DataLoader.get_instance()
    if loader.adata is None:
        raise HTTPException(status_code=404, detail="No h5ad data loaded")

    sigs = CONFIG.get("tissue_fluidity_signatures", {})
    if not sigs:
        raise HTTPException(status_code=404, detail="No fluidity signatures in config")

    scores: dict[str, list[float]] = {}
    for category, sig_data in sigs.items():
        genes = sig_data.get("genes", [])
        present = [g for g in genes if g in loader.adata.var_names]
        if not present:
            scores[category] = [0.0] * loader.adata.n_obs
            continue

        gene_indices = [list(loader.adata.var_names).index(g) for g in present]
        subset = loader.adata.X[:, gene_indices]
        if hasattr(subset, "toarray"):
            subset = subset.toarray()
        scores[category] = np.mean(np.asarray(subset), axis=1).tolist()

    obs = loader.adata.obs
    result: dict = {"scores": scores, "n_cells": loader.adata.n_obs}

    for col in ["condition", "cell_type", "cell_type_annotation"]:
        if col in obs.columns:
            result[col] = obs[col].astype(str).tolist()

    coords = loader.get_umap_coords()
    if coords is not None:
        result["x"] = coords[:, 0].tolist()
        result["y"] = coords[:, 1].tolist()

    return result


@router.get("/fluidity/genes")
async def get_fluidity_gene_expression() -> dict:
    """Return expression matrix for all fluidity signature genes."""
    loader = DataLoader.get_instance()
    if loader.adata is None:
        raise HTTPException(status_code=404, detail="No h5ad data loaded")

    sigs = CONFIG.get("tissue_fluidity_signatures", {})
    all_genes: list[str] = []
    gene_categories: dict[str, str] = {}
    for category, sig_data in sigs.items():
        for gene in sig_data.get("genes", []):
            if gene in loader.adata.var_names and gene not in all_genes:
                all_genes.append(gene)
                gene_categories[gene] = category

    expression: dict[str, list[float]] = {}
    for gene in all_genes:
        expr = loader.get_gene_expression(gene)
        if expr is not None:
            expression[gene] = expr.tolist()

    return {
        "genes": all_genes,
        "categories": gene_categories,
        "expression": expression,
        "n_cells": loader.adata.n_obs,
    }
