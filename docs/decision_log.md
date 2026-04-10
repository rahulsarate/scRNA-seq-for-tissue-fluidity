# Analysis Decision Log

Track key analysis decisions, parameter choices, and their rationale.

## Format
```
### YYYY-MM-DD — Decision Title
**Context**: What prompted this decision
**Decision**: What was chosen
**Rationale**: Why
**Alternatives considered**: What else was evaluated
**Impact**: What this affects downstream
```

---

### 2026-04-02 — Project Initialization
**Context**: Setting up scRNA-seq analysis infrastructure for tissue fluidity study
**Decision**: Use VS Code Copilot agents with .github/agents/ structure + AGENTS.md
**Rationale**: Native VS Code discovery, proper YAML frontmatter, handoff chains between agents
**Alternatives considered**: .agent_config/ custom directory (not auto-discovered by VS Code)
**Impact**: All 10 agents now available in VS Code agent dropdown with full tool/handoff support

### 2026-04-02 — Pseudobulk DESeq2 as primary DE method
**Context**: Need robust differential expression for scRNA-seq condition comparisons
**Decision**: Pseudobulk DESeq2 with ashr shrinkage (not per-cell Wilcoxon)
**Rationale**: Muscat/Squire benchmarks show pseudobulk outperforms per-cell methods for between-condition comparisons. Aggregating by sample respects biological replicates.
**Alternatives considered**: MAST (good for cell-level but inflates p-values for conditions), edgeR (comparable but less common in scRNA-seq)
**Impact**: All DE results across cell types use consistent methodology

### 2026-04-02 — Harmony for integration
**Context**: 8 samples across 4 conditions need batch correction
**Decision**: Harmony integration (group.by = "sample")
**Rationale**: Fast, good preservation of biological variation, widely used in scRNA-seq
**Alternatives considered**: RPCA (Seurat native, good but slower), scVI (deep learning, overkill for 8 samples)
**Impact**: All downstream analyses (clustering, DE, trajectory) use Harmony-corrected embeddings

### 2026-04-02 — 4-Phase Roadmap Adopted
**Context**: Need a structured plan to move from infrastructure to publication
**Decision**: Phase 1 (synthetic validation) → Phase 2 (GSE234269 real data) → Phase 3 (cross-dataset) → Phase 4 (publication)
**Rationale**: Synthetic-first catches pipeline bugs cheaply; staged approach lets each agent validate its step before real data
**Alternatives considered**: Jump straight to real data (risky if pipeline has bugs), all datasets at once (too scattered)
**Impact**: All analysis work follows phase gates in PROJECT.md

### 2026-04-02 — Visualization stays Python/R (no React/FastAPI)
**Context**: Evaluated whether web framework needed for visualization
**Decision**: Use matplotlib/seaborn/scanpy (Python) + ggplot2/ComplexHeatmap (R) for static figures; cellxgene for interactive exploration
**Rationale**: scRNA-seq publication figures are static PDFs. Interactive exploration is handled by cellxgene (zero-code). A React/FastAPI dashboard adds complexity with no benefit for this project scope
**Alternatives considered**: React + FastAPI dashboard (overkill), Streamlit/Dash (decent but not needed when cellxgene exists), plotly (good for supplementary interactive plots)
**Impact**: No frontend/backend web development needed; visualization-specialist agent focuses on matplotlib/ggplot2
