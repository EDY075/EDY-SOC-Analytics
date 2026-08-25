# Changeset — hardening de portfólio

Data: 2026-08-25 (America/Sao_Paulo)

Base: `main` em `8b5deb5`

Branch local: `codex/portfolio-10-hardening`

Este manifesto lista exatamente os arquivos adicionados e modificados em relação à base. Nenhum arquivo foi removido.

## Adicionados (18)

- `docs/CHANGESET_2026-08-25.md`
- `docs/DEMO_SCRIPT.md`
- `docs/PAGES_GUIDE.md`
- `docs/REPRODUCIBILITY.md`
- `docs/architecture/README.md`
- `docs/architecture/architecture-overview.mmd`
- `docs/architecture/architecture-overview.png`
- `docs/architecture/architecture-overview.svg`
- `docs/architecture/dimensional-model.mmd`
- `docs/architecture/dimensional-model.png`
- `docs/architecture/dimensional-model.svg`
- `docs/assets/README.md`
- `docs/assets/edy-soc-analytics-hero.png`
- `tests/test_project_quality.py`
- `validation/project_inventory.py`
- `validation/resolve_powerbi_workspace.ps1`
- `validation/validate_live_rls.ps1`
- `validation/verify_clean_tree.py`

## Modificados (69)

- `.github/workflows/ci.yml`
- `CHANGELOG.md`
- `DECISIONS.md`
- `NEXT_SESSION.md`
- `PROJECT_STATE.md`
- `README.md`
- `docs/ACCESSIBILITY_CHECKLIST.md`
- `docs/DATA_LINEAGE.md`
- `docs/DATA_QUALITY.md`
- `docs/DAX_MEASURES.md`
- `docs/DIMENSIONAL_MODEL.md`
- `docs/RELATORIO_ACADEMICO.md`
- `docs/REPORT_BLUEPRINT.md`
- `docs/RLS_SECURITY.md`
- `generator/generate_academic_pdf.py`
- `generator/generate_pbip.py`
- `generator/pbir_visuals.py`
- `output/pdf/RELATORIO_ACADEMICO.pdf`
- `powerbi/EDY SOC Analytics.Report/definition/pages/AnalystSLA/visuals/5ea07ea5ab8055f980f6/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/AssetsExposure/visuals/01b68afad051511b86b8/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/AssetsExposure/visuals/127a25ad26e2566987b8/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/AssetsExposure/visuals/3dd19b1d77385792b6e5/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/AssetsExposure/visuals/54f6b8d1b55959358767/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/AssetsExposure/visuals/870cd92fbac856288d34/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/CommandCenter/visuals/8da278ae90b759138da8/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/CommandCenter/visuals/f6e0e767fc605a12b2e9/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DataQuality/visuals/0c7d38abfab751528574/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DataQuality/visuals/152ab76accc65fc18e31/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DataQuality/visuals/8482f4be411957b99c19/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DataQuality/visuals/8986127f3fb05d49a473/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DataQuality/visuals/bcca1a763ae15118af49/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DataQuality/visuals/e28667afd71f5261b652/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DetectionEngineering/visuals/083917e6e7a55a07b45d/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DetectionEngineering/visuals/08df7dafce1a59288baa/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DetectionEngineering/visuals/8089b7fb1bb357aca61c/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/DetectionEngineering/visuals/adbcf8433f4c53259219/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/IncidentDrillthrough/visuals/79afd4494ff055d6b23b/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/IncidentDrillthrough/visuals/97bd7668e28c527895c6/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/IncidentDrillthrough/visuals/c7897990bbdf538c9ffa/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/IncidentLifecycle/visuals/048ba27e87c659e98f5f/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/IncidentLifecycle/visuals/232bb6d27b8b59669539/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/IncidentLifecycle/visuals/491e4f3b6883520e8662/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/IncidentLifecycle/visuals/89d3f0129f895e8dbd49/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/Methodology/visuals/2c72cf03734e50968672/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/Methodology/visuals/47be0e0c85ed543d9254/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/Methodology/visuals/8de983b2fd82555e9ce7/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/Methodology/visuals/97ecd27dbd74543ea6d3/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/Methodology/visuals/b4598a123b645edb90bc/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/Methodology/visuals/b8f77960180256659146/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/SOCOperations/visuals/6f9865d0a6c159b6be3f/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/SOCOperations/visuals/9c45d1ac5cd05dd4a797/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/SOCOperations/visuals/bde3f12b14945d49946e/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/SOCOperations/visuals/f2130585b9905c1b9fc3/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/ThreatMITRE/visuals/42f5b4718a2d5535a699/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/ThreatMITRE/visuals/87aa61a904a9506ab0ce/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/ThreatMITRE/visuals/a590f6c403ae50ebafad/visual.json`
- `powerbi/EDY SOC Analytics.Report/definition/pages/ThreatMITRE/visuals/de42583e8cfe5cf2a7cb/visual.json`
- `powerbi/EDY SOC Analytics.SemanticModel/definition/tables/DQ_RejectedRows.tmdl`
- `powerbi/EDY SOC Analytics.SemanticModel/definition/tables/DimDate.tmdl`
- `powerbi/EDY SOC Analytics.SemanticModel/definition/tables/DimSeverity.tmdl`
- `powerbi/EDY SOC Analytics.SemanticModel/definition/tables/DimStatus.tmdl`
- `powerbi/EDY SOC Analytics.SemanticModel/definition/tables/DimTime.tmdl`
- `powerbi/EDY SOC Analytics.SemanticModel/definition/tables/FactIncidentLifecycle.tmdl`
- `powerbi/EDY SOC Analytics.SemanticModel/definition/tables/FactSecurityEvents.tmdl`
- `powerbi/power-query/FactSecurityEvents.m`
- `powerbi/power-query/Quality.m`
- `tests/test_security.py`
- `validation/measure_performance.ps1`
- `validation/validate_live_model.ps1`

