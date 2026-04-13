# Day 18: The AI Agent Architecture

> **Goal**: Explain how 12 AI agents power this project — what they do, how they're configured, and why.

---

## Why AI Agents?

Traditional approach: one developer writes everything manually.
Our approach: 12 specialized AI agents, each expert in one domain, coordinated by an orchestrator.

```
                    ┌─────────────┐
                    │ orchestrator │ ← Entry point for every task
                    └──────┬──────┘
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
      ┌───────────┐ ┌───────────┐ ┌───────────┐
      │data-wrangler│ │  coder    │ │pipeline-  │
      └─────┬─────┘ └───────────┘ │ builder   │
            ▼                      └───────────┘
      ┌───────────┐
      │qc-analyst │
      └─────┬─────┘
            ▼
      ┌───────────┐
      │scrna-analyst│
      └─────┬─────┘
        ┌───┴───┐
        ▼       ▼
  ┌─────────┐ ┌──────────────────┐
  │de-analyst│ │visualization-    │
  └────┬────┘ │specialist        │
       ▼      └──────────────────┘
  ┌─────────────┐
  │pathway-     │
  │explorer     │
  └──────┬──────┘
         ▼
  ┌─────────────┐     ┌──────────┐
  │report-writer│ ──▶ │ reviewer │
  └─────────────┘     └──────────┘
```

---

## The 12 Agents

| # | Agent | Domain | Example Task |
|---|-------|--------|-------------|
| 1 | orchestrator | Plan & route | "Plan the full analysis for GSE234269" |
| 2 | coder | Implementation | Write/edit/debug/run any script |
| 3 | data-wrangler | Data import | Download GEO data, parse sample sheets |
| 4 | qc-analyst | Quality control | Filter cells, detect doublets |
| 5 | scrna-analyst | Clustering | Normalize, UMAP, annotate cell types |
| 6 | de-analyst | Diff expression | Pseudobulk DESeq2 comparisons |
| 7 | pathway-explorer | Pathways | GO, KEGG, GSEA enrichment |
| 8 | visualization-specialist | Plotting | UMAP, volcano, heatmaps |
| 9 | report-writer | Documentation | Methods sections, figure legends |
| 10 | reviewer | Code review | Statistical validation |
| 11 | pipeline-builder | Automation | Snakemake workflows, environments |
| 12 | frontend-dashboard | Dashboard | React + FastAPI interactive app |

---

## How Agents Are Configured

### Three Configuration Files

```
.github/
├── agents/              ← Agent definition files
│   ├── orchestrator.agent.md
│   ├── coder.agent.md
│   ├── qc-analyst.agent.md
│   └── ... (12 total)
├── instructions/        ← Rules applied to all/specific files
│   ├── data-safety.instructions.md     ← All files
│   ├── python-standards.instructions.md ← *.py only
│   └── r-standards.instructions.md      ← *.R only
├── skills/              ← Domain knowledge packages
│   ├── scrna-pipeline/SKILL.md
│   ├── tissue-fluidity/SKILL.md
│   └── ... (12 total)
└── copilot-instructions.md  ← Global project context
```

### Agent File Structure (YAML Frontmatter)
```yaml
---
name: "qc-analyst"
description: "Quality control for scRNA-seq"
tools:
  - run_in_terminal    # Can run code
  - read_file          # Can read files
  - create_file        # Can create files
---

# QC Analyst

You are a QC specialist for scRNA-seq data...
## Your responsibilities:
- Filter cells by gene count, UMI count, mt%
- Detect doublets with Scrublet
- Generate QC reports
```

### Instructions vs Skills

| Feature | Instructions | Skills |
|---------|-------------|--------|
| File | `.instructions.md` | `SKILL.md` |
| Loaded | Automatically by `applyTo` pattern | On demand when relevant |
| Scope | File-type rules | Domain knowledge |
| Example | "Python files must use snake_case" | "How to run DESeq2 analysis" |

---

## The Handoff System

Agents don't work in isolation — they hand off tasks to each other.

```
User: "Run the full analysis pipeline"
  │
  ▼
orchestrator: "I'll coordinate this. First, data."
  │ send: true (automatic)
  ▼
data-wrangler: "Data loaded. Handing to QC."
  │ send: true
  ▼
qc-analyst: "Cells filtered. Handing to clustering."
  │ send: true
  ▼
scrna-analyst: "10 cell types found. Handing to DE."
  │ send: true
  ▼
de-analyst: "3,247 DE genes found. Handing to pathways."
  │ send: true
  ▼
pathway-explorer: "Enrichment done. Results saved."
```

### Handoff Types
- **`send: true`** — Automatic: agent starts immediately
- **`send: false`** — Manual: user reviews prompt before sending

---

## AGENTS.md — The Master Reference

The root `AGENTS.md` file serves as:
1. **Agent registry** — Lists all 12 agents with roles
2. **Invocation guide** — How to call each agent
3. **Handoff map** — Who passes to whom
4. **Skill registry** — Available knowledge packages
5. **Rules** — Universal rules all agents follow

### Universal Rules
```
1. Mouse genes: Krt14 not KRT14
2. Reproducibility: set seeds (42), log versions
3. Data safety: Never modify data/raw/
4. Save outputs: R→.rds, Python→.h5ad
5. Tissue fluidity focus: Always consider 5 gene signatures
6. Config-driven: Read from analysis_config.yaml
```

---

## Why This Architecture?

### Single Agent vs Multi-Agent

```
Single Agent (bad for complex projects):
  - One agent tries to know everything
  - Gets confused switching contexts
  - Mistakes QC advice for DE advice

Multi-Agent (our approach):
  - Each agent is an expert
  - Clear responsibilities
  - Orchestrator coordinates
  - Skills loaded only when needed
```

### Real-World Analogy
```
Hospital:                          Our Project:
  Receptionist → orchestrator      (routes patients/tasks)
  Lab Tech → data-wrangler         (processes samples/data)
  Pathologist → qc-analyst         (quality checks)
  Specialist → scrna-analyst       (diagnosis/annotation)
  Surgeon → de-analyst             (precise operations)
  Pharmacist → pathway-explorer    (drug/pathway targets)
  Radiologist → viz-specialist     (images/visualizations)
  Admin → report-writer            (documentation)
  Peer Review → reviewer           (validation)
```

---

## Interview Q&A

### Q: "How do you use AI in your project?"

> "I built a multi-agent AI architecture with 12 specialized agents using VS Code Copilot. Each agent has a specific domain — one for QC, one for clustering, one for DE analysis, etc. They're configured via YAML frontmatter in .agent.md files, with shared skills (domain knowledge packages) and instructions (coding standards). An orchestrator agent coordinates the pipeline. This lets me invoke the right expert for each task — @de-analyst for differential expression, @qc-analyst for quality control — rather than relying on a generic AI."

### Q: "What are 'skills' in your agent system?"

> "Skills are packaged domain knowledge in SKILL.md files. For example, the tissue-fluidity skill contains our 5 gene signatures (EMT, ECM, migration, mechanotransduction, wound signals) and how to score them. Skills are loaded on demand — the DE analyst loads the DESeq2 skill, the pathway explorer loads the enrichment skill. This keeps each agent focused and reduces context pollution."

### Q: "How do agents communicate?"

> "Through a handoff system defined in AGENTS.md. Each agent has a 'Hands Off To' list. The orchestrator can delegate to any agent. After completing work, agents hand off to the next in the pipeline — qc-analyst → scrna-analyst → de-analyst. Handoffs can be automatic (send: true) or manual (send: false, user reviews first)."

---

## Self-Check Questions

1. **How many agents does this project use?** → 12 specialized agents
2. **What is the orchestrator's role?** → Plan, triage, and delegate tasks to specialist agents
3. **Where are agent definitions stored?** → `.github/agents/*.agent.md`
4. **What's the difference between instructions and skills?** → Instructions auto-apply by file pattern; skills load on demand for domain knowledge
5. **What is AGENTS.md?** → Root-level master reference with agent registry, handoff map, rules
6. **Name the pipeline handoff order** → orchestrator → data-wrangler → qc-analyst → scrna-analyst → de-analyst → pathway-explorer → visualization → report-writer → reviewer
7. **What does `send: true` mean?** → Automatic handoff — target agent starts immediately
8. **Where are skills stored?** → `.github/skills/<name>/SKILL.md`
9. **What are the 6 universal rules?** → Mouse gene case, seeds, data safety, save format, fluidity focus, config-driven
10. **Why multi-agent over single agent?** → Specialization, clear responsibilities, reduced confusion, right domain knowledge loaded per task

---

**Next**: [Day 19 — CI/CD & GitHub Actions](Day_19_CICD.md)
