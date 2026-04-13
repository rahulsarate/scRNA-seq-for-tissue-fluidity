# Day 15: The Interactive Dashboard

> **Goal**: Understand the full-stack dashboard architecture, how backend serves data, and how frontend renders interactive plots.

---

## Why Build a Dashboard?

```
Static figures:  Generate → Share PDF → Collaborator has a question → Re-generate
Dashboard:       Collaborator opens browser → Explores data themselves → Real-time answers
```

| Static Figures | Interactive Dashboard |
|---------------|----------------------|
| Fixed views | Hover, zoom, filter |
| Regenerate for each question | Self-service exploration |
| Good for publications | Good for collaboration |
| PDF files | Web browser |
| Our `02_visualization_suite.py` | Our `dashboard/` |

---

## Architecture: Client-Server Model

```
┌─────────────────┐          ┌──────────────────┐
│    Frontend      │  HTTP    │     Backend       │
│  (React + TS)    │ ◄──────► │  (FastAPI + Python)│
│                  │  JSON    │                    │
│  Browser-based   │          │  Loads .h5ad data  │
│  Interactive     │          │  Serves REST API   │
│  Plotly charts   │          │  Runs on port 8000 │
└─────────────────┘          └──────────────────┘
   Port 5173 (dev)              Port 8000
```

**How it works**:
1. Backend starts → loads the processed AnnData from `analysis/clustering/wound_adata.h5ad`
2. Frontend starts → shows the UI in browser
3. User clicks "show gene Krt14" → frontend calls `GET /api/v1/genes/Krt14`
4. Backend extracts Krt14 expression from AnnData → returns JSON
5. Frontend receives JSON → renders interactive Plotly scatter plot

---

## Backend Deep Dive (FastAPI)

### Entry Point: `dashboard/backend/app/main.py`

```python
app = FastAPI(
    title="scRNA-seq Wound Healing Dashboard",
    version="1.0.0",
)

# CORS: allow frontend (port 5173) to call backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],       # Read-only — no POST/PUT/DELETE
)

# Register API routes
app.include_router(umap.router, prefix="/api/v1")
app.include_router(genes.router, prefix="/api/v1")
app.include_router(de.router, prefix="/api/v1")
app.include_router(fluidity.router, prefix="/api/v1")
```

### API Endpoints

| Endpoint | Returns | Used For |
|----------|---------|----------|
| `GET /api/v1/umap` | UMAP x,y coordinates + cell metadata | UMAP scatter plot |
| `GET /api/v1/genes/{gene}` | Expression values per cell | Gene feature UMAP |
| `GET /api/v1/de/{comparison}` | DE table (gene, log2FC, padj) | Volcano plot |
| `GET /api/v1/cell-types` | Cell type counts per condition | Proportion chart |
| `GET /api/v1/fluidity` | Fluidity scores per cell | Fluidity dashboard |
| `GET /api/v1/qc` | QC metrics summary | QC overview |
| `GET /api/v1/config` | Colors, thresholds, gene signatures | App configuration |

### Data Loader Service

```python
# dashboard/backend/app/services/data_loader.py
class DataLoader:
    """Singleton — loads data once, serves it for all requests."""
    
    def load_all(self):
        self.adata = sc.read_h5ad('analysis/clustering/wound_adata.h5ad')
        self.de_results = {}
        for f in Path('analysis/de/').glob('*.csv'):
            self.de_results[f.stem] = pd.read_csv(f)
```

**Key design**: Data is loaded ONCE at startup. Every API call reads from memory — no disk I/O per request.

### Security Notes

- **Read-only API**: Only `GET` methods — no one can modify data through the dashboard
- **CORS restricted**: Only frontend origin (`localhost:5173`) can call the API
- **No authentication needed**: It's a local tool, not public-facing

---

## Frontend Deep Dive (React + TypeScript)

### App Structure

```
dashboard/frontend/src/
├── App.tsx              ← Routing: which page to show
├── main.tsx             ← React entry point
├── index.css            ← Global styles (Tailwind)
│
├── pages/               ← Full page views
│   ├── Overview.tsx     ← UMAP + QC + proportions
│   ├── GeneExplorer.tsx ← Search genes, see expression
│   ├── DEResults.tsx    ← Volcano plots, DE tables
│   └── FluidityDash.tsx ← Fluidity scores explorer
│
├── components/          ← Reusable plot components
│   ├── UMAPPlot.tsx     ← Interactive UMAP (Plotly)
│   ├── VolcanoPlot.tsx  ← Interactive volcano (Plotly)
│   ├── GeneSearch.tsx   ← Search input for genes
│   ├── ProportionChart.tsx  ← Cell type proportions
│   └── FluidityPanel.tsx    ← Fluidity score vis
│
├── hooks/
│   └── useApi.ts        ← React hook for API calls
│
└── lib/
    ├── api.ts           ← API client (fetch wrapper)
    └── colors.ts        ← Color palettes
```

### The Navigation

```tsx
// App.tsx — sidebar navigation
const navItems = [
  { to: "/", label: "Overview" },        // UMAP + QC
  { to: "/genes", label: "Gene Explorer" },// Search any gene
  { to: "/de", label: "DE Results" },      // Volcano plots
  { to: "/fluidity", label: "Fluidity" },  // Fluidity scores
];
```

### How a Component Fetches Data

```typescript
// hooks/useApi.ts
function useApi<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch(`http://localhost:8000${url}`)
      .then(res => res.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [url]);
  
  return { data, loading };
}

// Usage in a component:
const { data, loading } = useApi('/api/v1/umap');
```

---

## Running the Dashboard

```bash
# Terminal 1: Start backend
cd dashboard/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start frontend
cd dashboard/frontend
npm install
npm run dev                    # → opens http://localhost:5173
```

---

## Key Technologies Explained

| Tech | Role | Why Chosen |
|------|------|------------|
| **FastAPI** | REST API framework | Auto-docs, type validation, async, Python-native |
| **React** | UI framework | Component-based, huge ecosystem |
| **TypeScript** | Type-safe JavaScript | Catches errors at compile time |
| **Plotly** | Interactive charts | Hover, zoom, pan, download |
| **Tailwind CSS** | Styling | Utility classes, no external CSS files |
| **Vite** | Build tool | Fast dev server, hot module reload |

---

## Interview Q&A

### Q: "Tell me about your dashboard."

> "I built a full-stack interactive dashboard for the scRNA-seq data. The backend is FastAPI serving a read-only REST API from the processed AnnData object — endpoints for UMAP coordinates, gene expression, DE results, and fluidity scores. The frontend is React with TypeScript, using Plotly for interactive plots. Collaborators can explore the data in a browser — search any gene, see its expression on UMAP, view volcano plots, and compare fluidity scores across conditions — all without writing code."

### Q: "Why build a dashboard when you have static figures?"

> "Static figures answer predetermined questions. The dashboard lets collaborators ask their OWN questions — 'What does gene Fn1 look like on UMAP?' or 'Which genes are significant in wound_3d?' — without coming to me. It accelerates collaborative iterations and makes the project more accessible to lab biologists who don't write code."

---

## Self-Check Questions

1. **What's the client-server model?** → Frontend (React in browser) ↔ Backend (FastAPI serving data)
2. **What port does the backend run on?** → 8000
3. **What data format does the API return?** → JSON
4. **Why read-only API?** → Dashboard is for exploration, not data modification
5. **What's CORS?** → Cross-Origin Resource Sharing — controls which origins can call the API
6. **What is a React component?** → Reusable UI building block (e.g., UMAPPlot)
7. **Why Plotly over matplotlib in the dashboard?** → Plotly is interactive (hover, zoom); matplotlib is static
8. **What is the DataLoader singleton?** → Loads data once at startup, serves from memory
9. **Name 4 dashboard pages** → Overview, Gene Explorer, DE Results, Fluidity
10. **What is Tailwind CSS?** → Utility-first CSS framework for styling with class names

---

**Next**: [Day 16 — Reproducibility & Environment Management](Day_16_Reproducibility.md)
