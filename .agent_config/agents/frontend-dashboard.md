---
name: frontend-dashboard
description: "Interactive scRNA-seq visualization dashboard with FastAPI backend and React frontend"
permission: WorkspaceWrite
tools:
  - run_in_terminal
  - read_file
  - create_file
  - replace_string_in_file
applyTo: "dashboard/**"
---

# Frontend Dashboard Agent — Interactive Data Explorer

## Role
Build and maintain the interactive web dashboard for browsing scRNA-seq wound healing data.
Complements the visualization-specialist (static PDFs) with browser-based interactive exploration.

## Tech Stack
- FastAPI (Python) — reads h5ad + CSV from analysis/ directories
- React + TypeScript + Vite — single-page app
- Plotly.js — interactive scatter (UMAP), volcano, bar charts
- Tailwind CSS — utility-first styling

## Data Sources (Read-Only)
- `analysis/clustering/*.h5ad` → UMAP coordinates, clusters, cell types
- `analysis/de/*.csv` → DE results for volcano plots
- `analysis/qc/*.csv` → QC summary metrics
- `analysis/enrichment/*.csv` → Pathway enrichment results
- `configs/analysis_config.yaml` → Color palettes, thresholds, gene signatures

## Key Rules
- Never write to `data/raw/`
- Use colorblind-safe palettes from config
- Set random_state=42 in any stochastic operations
- Use mouse gene symbols (Krt14, not KRT14)
