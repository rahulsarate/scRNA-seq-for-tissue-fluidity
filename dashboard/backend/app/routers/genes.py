"""Gene expression query and search endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.services.data_loader import DataLoader

router = APIRouter(tags=["Genes"])


@router.get("/genes/search")
async def search_genes(
    q: str = Query(..., min_length=1, max_length=50, description="Gene name prefix"),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """Autocomplete search for gene names."""
    loader = DataLoader.get_instance()
    matches = loader.search_genes(q, limit=limit)
    return {"query": q, "matches": matches, "count": len(matches)}


@router.get("/genes/{gene_name}")
async def get_gene_expression(gene_name: str) -> dict:
    """Return per-cell expression values for a gene (for feature plots)."""
    loader = DataLoader.get_instance()
    if loader.adata is None:
        raise HTTPException(status_code=404, detail="No h5ad data loaded")

    expr = loader.get_gene_expression(gene_name)
    if expr is None:
        raise HTTPException(
            status_code=404,
            detail=f"Gene '{gene_name}' not found. Try /genes/search?q={gene_name[:3]}",
        )

    result: dict = {"gene": gene_name, "expression": expr.tolist()}
    coords = loader.get_umap_coords()
    if coords is not None:
        result["x"] = coords[:, 0].tolist()
        result["y"] = coords[:, 1].tolist()

    return result
