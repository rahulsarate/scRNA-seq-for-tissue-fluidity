# Day 17: Git Workflow & Version Control for Research

> **Goal**: Know Git well enough for interview questions about collaboration, branching, and research code management.

---

## Why Git Matters for This Project

```
Without Git:                       With Git:
script_v1.py                       One file: script.py
script_v2_fixed.py                 Full history of every change
script_v2_fixed_FINAL.py           Can revert any mistake
script_v2_fixed_FINAL_v2.py        Multiple people can work together
script_REALLY_FINAL.py             Every change documented
```

---

## Core Git Concepts

### Repository
Your project folder tracked by Git. Our repo: `scRNA-seq-for-tissue-fluidity`

### Commit
A snapshot of your project at a point in time.
```
commit abc123 — "Add QC filtering with 15% mt threshold"
commit def456 — "Implement Leiden clustering at resolution 0.8"
commit ghi789 — "Add tissue fluidity scoring for all 5 signatures"
```

### Branch
A parallel timeline for developing features without breaking the main code.
```
main ─────○─────○─────○─────○─────── (stable)
               \                  /
feature ────────○────○────○─────── (development)
```

### .gitignore
Files Git should NOT track (already covered in Day 4).

---

## Our Git Workflow

### Day-to-Day Commands

```bash
# See what's changed
git status

# Stage + commit
git add scripts/python/01_scrna_analysis_pipeline.py
git commit -m "Add fluidity scoring to pipeline step 8"

# Push to GitHub
git push origin main

# Pull latest from GitHub
git pull origin main
```

### Commit Message Standards

```
Good:
  "Add pseudobulk DESeq2 for wound_7d vs control"
  "Fix mt% threshold from 10 to 15 for keratinocytes"
  "Add UMAP feature plots for 5 fluidity signatures"

Bad:
  "update"
  "fixed stuff"
  "changes"
```

### What We Commit vs Don't Commit

| Commit ✓ | Don't Commit ✗ |
|----------|----------------|
| Python/R scripts | .h5ad files (>50MB) |
| Config YAML | .rds files |
| Documentation | data/raw/ |
| Dashboard source | .venv/, node_modules/ |
| CI/CD workflows | .env (credentials) |
| requirements.txt | data/counts/ (large) |

---

## GitHub Features We Use

### Issues — Tracking Tasks
```
Issue #1: "Implement QC pipeline with configurable thresholds"
Issue #2: "Add tissue fluidity scoring module"
Issue #3: "Build interactive dashboard"
```

### Actions — CI/CD Automation
On every push, GitHub Actions automatically:
1. Lints Python code (flake8 → syntax/style errors)
2. Lints R code (lintr)
3. Runs smoke tests (imports pass, no crashes)

### README — Project Presentation
First thing anyone sees. Includes:
- Project description, PI name
- Setup instructions
- How to run the pipeline
- How to start the dashboard
- Expected outputs

---

## Branching Strategy for Solo Research

```
main ─────── always works, stable code
  \
  feature/fluidity-scoring ─── develop new feature
  \
  fix/mt-threshold ─── fix a bug
  \
  analysis/new-dataset ─── try new data
```

**Merge back to main** when feature is complete and tested.

---

## Interview Q&A

### Q: "How do you use Git in your project?"

> "I use Git for version control with GitHub as the remote. Every script, config, and documentation file is tracked. Large data files are excluded via .gitignore. I write descriptive commit messages — 'Add pseudobulk DESeq2 for wound_7d vs control' not 'update'. GitHub Actions run automated linting on every push. The project is public at github.com/rahulsarate/scRNA-seq-for-tissue-fluidity."

### Q: "How do you handle large files?"

> "The .gitignore excludes all files >50MB — .h5ad, .rds, FASTQ, count matrices. These are shared via GEO (public datasets) or cloud storage. The repository contains only code, configs, and documentation — everything needed to reproduce the analysis from scratch."

---

## Self-Check Questions

1. **What is a Git commit?** → A snapshot of the project at a point in time
2. **What does .gitignore do?** → Tells Git which files to NOT track
3. **Why not commit .h5ad files?** → Too large (>50MB); Git isn't designed for large binaries
4. **What is a branch?** → A parallel timeline for development
5. **What are GitHub Actions?** → Automated tasks (linting, testing) that run on every push
6. **Good vs bad commit message?** → Good: specific action. Bad: "update" or "fixed stuff"
7. **What's our main branch for?** → Always-stable, working code
8. **Where is our project hosted?** → GitHub: rahulsarate/scRNA-seq-for-tissue-fluidity
9. **What does CI/CD mean?** → Continuous Integration/Continuous Deployment — automated checks
10. **What do we lint?** → Python (flake8) and R (lintr) for syntax and style

---

**Next**: [Day 18 — The AI Agent Architecture](Day_18_AI_Agents.md)
