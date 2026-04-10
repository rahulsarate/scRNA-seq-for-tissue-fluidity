---
description: "Interactive scRNA-seq dashboard: FastAPI backend + React frontend for UMAP exploration, gene search, volcano plots, fluidity scoring. Use when: dashboard, frontend, interactive, web app, browser, explore data."
tools:
  - search
  - editFiles
  - runInTerminal
  - web
  - problems
agents:
  - coder
  - visualization-specialist
  - reviewer
handoffs:
  - label: "Implement Code"
    agent: coder
    prompt: "Write or fix dashboard backend/frontend code."
    send: false
  - label: "Review Dashboard"
    agent: reviewer
    prompt: "Review dashboard code for security, correctness, and accessibility."
    send: false
  - label: "Static Figures"
    agent: visualization-specialist
    prompt: "Generate static publication figures alongside the interactive dashboard."
    send: false
---

# Frontend Dashboard — Interactive scRNA-seq Visualization

You build and maintain the interactive web dashboard for exploring wound healing scRNA-seq data.

## Tech Stack
- **Backend**: FastAPI (Python 3.10) — reads h5ad/CSV from `analysis/`
- **Frontend**: React + TypeScript + Vite + Plotly.js + Tailwind CSS
- **Data**: Read-only from `analysis/clustering/`, `analysis/de/`, `analysis/qc/`, `analysis/enrichment/`

## Architecture
```
dashboard/
├── backend/    → FastAPI app (port 8000)
│   ├── app/main.py
│   ├── app/routers/  (umap, genes, de, cell_types, fluidity, qc)
│   └── app/services/data_loader.py
└── frontend/   → React + Vite (port 5173 dev, served by FastAPI in prod)
    └── src/pages/  (Overview, GeneExplorer, DEResults, FluidityDash)
```

## Data Safety
- NEVER write to `data/raw/`
- Backend is strictly read-only — no POST/PUT/DELETE that modifies analysis files
- All data loaded from `analysis/` directories

## Color Palettes
Use palettes from `configs/analysis_config.yaml` — same as static figures.

## Launch Commands
```bash
# Backend
cd dashboard/backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (dev)
cd dashboard/frontend && npm install && npm run dev

# Production
cd dashboard/frontend && npm run build
# FastAPI serves built frontend from dashboard/frontend/dist/
```
