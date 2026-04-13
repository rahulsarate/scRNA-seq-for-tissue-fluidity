"""Differential expression results endpoints."""

from fastapi import APIRouter, HTTPException, Query

from app.services.data_loader import DataLoader

router = APIRouter(tags=["Differential Expression"])


@router.get("/de")
async def list_comparisons() -> dict:
    """List available DE comparison result files."""
    loader = DataLoader.get_instance()
    comparisons = []
    for name, df in loader.de_results.items():
        comparisons.append(
            {"name": name, "n_genes": len(df), "columns": list(df.columns)}
        )
    return {"comparisons": comparisons}


@router.get("/de/{comparison}")
async def get_de_results(
    comparison: str,
    padj_threshold: float = Query(0.05, ge=0, le=1),
    log2fc_threshold: float = Query(1.0, ge=0),
) -> dict:
    """Return DE results for a specific comparison (volcano plot data)."""
    loader = DataLoader.get_instance()
    if comparison not in loader.de_results:
        available = list(loader.de_results.keys())
        raise HTTPException(
            status_code=404,
            detail=f"Comparison '{comparison}' not found. Available: {available}",
        )

    df = loader.de_results[comparison].copy()

    # Normalize column names to consistent schema
    col_map: dict[str, str] = {}
    for col in df.columns:
        cl = col.lower()
        if "log2" in cl and ("fc" in cl or "fold" in cl):
            col_map[col] = "log2FC"
        elif cl in ("padj", "p_val_adj", "padjusted", "fdr", "qvalue"):
            col_map[col] = "padj"
        elif cl in ("basemean", "base_mean", "avgexpr"):
            col_map[col] = "baseMean"
    df = df.rename(columns=col_map)

    if "log2FC" not in df.columns or "padj" not in df.columns:
        return {
            "comparison": comparison,
            "genes": df.reset_index().to_dict(orient="records"),
            "n_total": len(df),
        }

    # Use existing 'gene' column, or fall back to index
    if "gene" not in df.columns:
        df["gene"] = df.index
    df["significant"] = "ns"
    up_mask = (df["padj"] < padj_threshold) & (df["log2FC"] > log2fc_threshold)
    down_mask = (df["padj"] < padj_threshold) & (df["log2FC"] < -log2fc_threshold)
    df.loc[up_mask, "significant"] = "up"
    df.loc[down_mask, "significant"] = "down"

    return {
        "comparison": comparison,
        "genes": df[["gene", "log2FC", "padj", "significant"]].to_dict(
            orient="records"
        ),
        "n_total": len(df),
        "n_up": int(up_mask.sum()),
        "n_down": int(down_mask.sum()),
        "thresholds": {"padj": padj_threshold, "log2fc": log2fc_threshold},
    }
