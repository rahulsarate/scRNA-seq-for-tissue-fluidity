---
name: frontend-dashboard
description: "Build and run the interactive scRNA-seq dashboard. Use when creating, updating, or debugging the FastAPI + React dashboard for UMAP exploration, gene search, DE volcano plots, and fluidity scoring."
---

# Frontend Dashboard Skill

## When to Use
- Setting up or running the dashboard
- Adding new visualization panels
- Debugging API endpoints or React components
- Connecting new analysis outputs to the dashboard

## Quick Start
```bash
# Terminal 1: Backend
cd dashboard/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend (dev mode)
cd dashboard/frontend
npm install
npm run dev
```
Open http://localhost:5173

## API Endpoints
| Method | Path | Returns |
|--------|------|---------|
| GET | /api/v1/datasets | Available h5ad/CSV files |
| GET | /api/v1/umap?color_by=leiden | UMAP coords + metadata |
| GET | /api/v1/genes/{name} | Per-cell expression |
| GET | /api/v1/genes/search?q=Krt | Gene autocomplete |
| GET | /api/v1/de/{comparison} | DE table for volcano |
| GET | /api/v1/cell-types | Cell type counts |
| GET | /api/v1/proportions | Stacked bar data |
| GET | /api/v1/fluidity/scores | Fluidity module scores |
| GET | /api/v1/qc/summary | QC metrics per sample |
| GET | /api/v1/config | Project config + palettes |

## Color Palettes (from config)
```python
CONDITION_COLORS = {"control": "#2166AC", "wound_3d": "#F4A582", "wound_7d": "#D6604D", "wound_14d": "#B2182B"}
CELL_TYPE_COLORS = {"Basal_Keratinocyte": "#E69F00", "Diff_Keratinocyte": "#F0E442", "Fibroblast": "#56B4E9", ...}
```

## Frontend Components
- `UMAPPlot` — Plotly scattergl (WebGL, handles 50K+ points)
- `VolcanoPlot` — Interactive with hover labels, threshold lines
- `ProportionChart` — Stacked bar by condition
- `GeneSearch` — Debounced autocomplete
- `FluidityPanel` — Box plots per module per condition
