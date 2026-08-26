# EDY SOC Analytics — Próxima sessão

Atualizado em: 2026-08-26 (America/Sao_Paulo)

## Estado atual

A release pública `v1.1.0` foi reconciliada, validada e incorporada à `main`. O material técnico de evidência está em `validation/results/`, `screenshots/reconcile-final-2026-08-25/` e `docs/RECONCILIATION_2026-08-25.md`.

## Próximas evoluções possíveis

1. Executar auditoria completa com leitor de tela e alto contraste.
2. Validar publicação, associação de grupos e RLS em um tenant autorizado do Power BI Service.
3. Projetar isolamento integral de eventos e alertas por equipe, caso o escopo futuro exija essa fronteira.
4. Derivar lifecycle, SLA e bridge MITRE de fontes brutas independentes.
5. Capturar uma evidência pública dedicada do drillthrough filtrado em um único incidente.

## Gates de regressão

```powershell
python generator/generate_dataset.py
python validation/project_inventory.py
python -m unittest discover -s tests -v
```

Com o relatório aberto no Power BI Desktop, quando houver alteração no modelo ou no PBIR:

```powershell
powershell -ExecutionPolicy Bypass -File validation/validate_live_model.ps1
powershell -ExecutionPolicy Bypass -File validation/validate_live_rls.ps1
powershell -ExecutionPolicy Bypass -File validation/measure_performance.ps1
powerbi-report-author validate "powerbi/EDY SOC Analytics.Report" --pretty
```

## Restrições

- não publicar dados reais, credenciais, UPNs reais ou endereços fora das faixas reservadas;
- não declarar isolamento integral no RLS atual;
- não substituir validação viva por resultado apenas estático;
- não executar push, merge, release ou publicação sem autorização explícita.
