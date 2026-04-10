# scRNA-seq Wound Healing Dashboard

Interactive visualization dashboard for the tissue fluidity scRNA-seq project.

## Quick Start

### Backend (FastAPI)
```bash
cd dashboard/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (React + Vite)
```bash
cd dashboard/frontend
npm install
npm run dev
```

Open http://localhost:5173 — Vite proxies `/api` requests to the backend.

## Pages

| Page | Path | Description |
|------|------|-------------|
| Overview | `/` | UMAP plot (color by cell type/condition/cluster) + cell-type proportion chart |
| Gene Explorer | `/genes` | Search any gene → feature plot overlay + per-cell-type stats |
| DE Results | `/de` | Volcano plot for wound_3d/7d/14d vs control + top-gene table |
| Fluidity | `/fluidity` | Tissue fluidity signature scores (EMT, ECM, migration, mechanotransduction, wound signals) |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/umap?color_by=cell_type` | GET | UMAP coordinates + labels |
| `/api/v1/genes/search?q=Krt` | GET | Autocomplete gene search |
| `/api/v1/genes/{gene}` | GET | Per-cell expression + stats |
| `/api/v1/de` | GET | List available DE comparisons |
| `/api/v1/de/{comparison}` | GET | Volcano data for a comparison |
| `/api/v1/cell-types` | GET | Cell type counts |
| `/api/v1/proportions` | GET | Cell proportions by condition |
| `/api/v1/fluidity/signatures` | GET | Gene signature lists |
| `/api/v1/fluidity/scores` | GET | Per-cell fluidity scores |
| `/api/v1/qc/summary` | GET | QC metrics summary |
| `/config` | GET | Analysis config |
| `/datasets` | GET | Available datasets |

## Data Sources
- **h5ad**: `analysis/clustering/`, `data/synthetic/`, `data/counts/` (first found)
- **DE CSVs**: `analysis/de/`
- **QC CSVs**: `analysis/qc/`
- **Config**: `configs/analysis_config.yaml`

## Production Build
```bash
cd dashboard/frontend
npm run build          # outputs to dashboard/frontend/dist/
```
The FastAPI backend serves the built frontend as static files in production.

## Architecture
```
Browser → Vite dev server (5173) → proxy /api → FastAPI (8000) → h5ad/CSV files
```
