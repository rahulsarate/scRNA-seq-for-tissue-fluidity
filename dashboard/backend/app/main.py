"""FastAPI application — scRNA-seq Wound Healing Dashboard."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import cell_types, de, fluidity, genes, qc, umap
from app.services.data_loader import DataLoader

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_DIST = PROJECT_ROOT / "dashboard" / "frontend" / "dist"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Pre-load data on startup."""
    loader = DataLoader.get_instance()
    loader.load_all()
    logger.info("Data loaded — ready to serve")
    yield


app = FastAPI(
    title="scRNA-seq Wound Healing Dashboard",
    description="Interactive visualization for tissue fluidity analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(umap.router, prefix="/api/v1")
app.include_router(genes.router, prefix="/api/v1")
app.include_router(de.router, prefix="/api/v1")
app.include_router(cell_types.router, prefix="/api/v1")
app.include_router(fluidity.router, prefix="/api/v1")
app.include_router(qc.router, prefix="/api/v1")


@app.get("/api/v1/config")
async def get_config() -> dict:
    """Return project configuration (palettes, thresholds, signatures)."""
    from app.config import CELL_TYPE_COLORS, CONDITION_COLORS, CONFIG

    return {
        "condition_colors": CONDITION_COLORS,
        "cell_type_colors": CELL_TYPE_COLORS,
        "conditions": CONFIG.get("experimental_design", {}).get("conditions", []),
        "qc_thresholds": CONFIG.get("qc_thresholds", {}),
        "tissue_fluidity_signatures": CONFIG.get("tissue_fluidity_signatures", {}),
    }


@app.get("/api/v1/datasets")
async def list_datasets() -> dict:
    """List available h5ad and CSV files in analysis/."""
    analysis_dir = PROJECT_ROOT / "analysis"
    datasets: list[dict] = []
    if analysis_dir.exists():
        for ext in ["*.h5ad", "*.csv"]:
            for p in analysis_dir.rglob(ext):
                datasets.append(
                    {
                        "name": p.name,
                        "path": str(p.relative_to(PROJECT_ROOT)),
                        "size_mb": round(p.stat().st_size / 1e6, 1),
                        "directory": p.parent.name,
                    }
                )
    return {"datasets": datasets}


# Serve built React frontend in production
if FRONTEND_DIST.exists():
    app.mount(
        "/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend"
    )
