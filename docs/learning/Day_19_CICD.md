# Day 19: CI/CD & GitHub Actions

> **Goal**: Understand automated testing and quality checks that run on every code push.

---

## What Is CI/CD?

```
CI = Continuous Integration
     → Automatically test code when you push

CD = Continuous Deployment
     → Automatically deploy (not used here — we're research, not a product)
```

### Why CI for Research Code?

```
Without CI:                          With CI:
Push broken code → nobody knows      Push code → GitHub catches errors
Colleague runs your script → crash   Linting runs automatically
"It works on my machine"             Standards enforced for everyone
```

---

## Our CI Pipeline

When you `git push`, GitHub Actions automatically runs:

```
git push
  │
  ▼
┌───────────────────────────────┐
│ GitHub Actions Workflow       │
│                               │
│ 1. Checkout code              │
│ 2. Set up Python 3.10         │
│ 3. Install dependencies       │
│ 4. Run flake8 (Python lint)   │
│ 5. Run lintr (R lint)         │
│ 6. Run smoke tests            │
│ 7. ✅ Pass or ❌ Fail         │
└───────────────────────────────┘
```

---

## GitHub Actions Workflow File

Located at `.github/workflows/ci.yml`:

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install flake8
      - run: flake8 scripts/python/ --max-line-length=120

  lint-r:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: r-lib/actions/setup-r@v2
      - run: Rscript -e "install.packages('lintr')"
      - run: Rscript -e "lintr::lint_dir('scripts/R/')"

  smoke-test:
    runs-on: ubuntu-latest
    needs: [lint-python]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python -c "import scanpy; import anndata; print('OK')"
```

---

## What Does Each Check Do?

### 1. Flake8 — Python Linter
Catches syntax errors, undefined variables, style issues.
```python
# Flake8 would flag:
x=1          # E225: missing whitespace around operator
import os    # F401: imported but unused
def f( x ):  # E211: whitespace before parenthesis
```

### 2. Lintr — R Linter
Same idea for R code.
```r
# lintr would flag:
x=1          # Use <- not = for assignment
T            # Use TRUE not T
```

### 3. Smoke Tests
Quick check that critical imports work:
```python
import scanpy        # Core analysis
import anndata       # Data format
import pandas        # Data manipulation
import numpy         # Numerics
print("All imports OK")
```

---

## Reading CI Results

### On GitHub
```
✅ All checks passed     → Your code is clean
❌ lint-python failed    → Python syntax/style issues
❌ smoke-test failed     → Import or environment problem
```

### In the Actions Tab
```
GitHub → Repository → Actions tab → Click workflow run
  → See logs for each step
  → Find exact line with error
```

---

## CI for Research: What We Check vs Don't

| We Check ✓ | We Don't Check ✗ |
|-----------|-----------------|
| Syntax errors | Biological correctness |
| Import availability | Statistical interpretation |
| Code style | Analysis results |
| File structure | Figure aesthetics |
| Config validity | Publication readiness |

CI ensures **code quality**, not **scientific quality** — that's the reviewer agent's job.

---

## Interview Q&A

### Q: "Do you have automated testing?"

> "Yes, GitHub Actions runs CI on every push. It lints Python with flake8, lints R with lintr, and runs smoke tests to verify all dependencies import correctly. This catches syntax errors, undefined variables, and broken imports before they reach the main branch."

### Q: "What testing frameworks do you use?"

> "For a research project, we focus on linting and integration smoke tests rather than unit tests — the 'units' are biological analyses that require data context. Flake8 enforces Python style (PEP 8), lintr enforces R conventions, and smoke tests verify the computational environment. For future work, I'd add pytest for utility functions and validate expected outputs against reference data."

### Q: "How do you ensure code quality as a solo developer?"

> "Three layers: (1) CI/CD with flake8/lintr on every push, (2) the reviewer AI agent that checks statistical validity and reproducibility, (3) config-driven design so parameters are in YAML rather than hardcoded across scripts."

---

## Self-Check Questions

1. **What does CI stand for?** → Continuous Integration
2. **When does CI run?** → On every git push to main (or pull request)
3. **What is flake8?** → A Python linter that checks syntax and style
4. **What is lintr?** → An R linter that checks coding conventions
5. **What's a smoke test?** → A quick check that critical imports/features work
6. **Where is the workflow file?** → `.github/workflows/ci.yml`
7. **What triggers the workflow?** → `on: push` and `on: pull_request` to main branch
8. **Does CI check biological correctness?** → No — only code quality
9. **What does a ❌ in GitHub mean?** → One or more CI checks failed
10. **How do you find the error?** → GitHub Actions tab → click the failed workflow → read logs

---

**Next**: [Day 20 — Config-Driven Design](Day_20_Config_Design.md)
