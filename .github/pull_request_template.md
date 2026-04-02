## Summary
<!-- Briefly describe what this PR does -->

## Type of Change
- [ ] New analysis script / pipeline step
- [ ] Bug fix in existing script
- [ ] New figure / visualization
- [ ] Configuration change (conda env, analysis params)
- [ ] Documentation update
- [ ] Agent / skill definition update
- [ ] CI/CD workflow change

## Analysis Context
<!-- Fill in what's relevant -->
- **Dataset(s)**: <!-- e.g. GSE234269, synthetic -->
- **Script(s) changed**: <!-- e.g. scripts/python/01_scrna_analysis_pipeline.py -->
- **Output directory**: <!-- e.g. analysis/clustering/ -->

## Reproducibility Checklist
- [ ] I ran the script locally and it completed without errors
- [ ] New dependencies are added to `configs/conda_envs/scrna_wound_healing.yml`
- [ ] Large output files (`.h5ad`, `.rds`, `.bam`) are excluded by `.gitignore`
- [ ] No patient/clinical/PHI data is included in this PR
- [ ] Analysis parameters are documented in `configs/analysis_config.yaml`

## Figures / Results
<!-- Paste key plots or describe key findings if applicable -->
N/A

## Notes for Reviewer
<!-- Any context that helps review, e.g. known limitations, next steps -->
