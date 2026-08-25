# EDY SOC Analytics — Continuidade

Atualizado em: 2026-08-25 (America/Sao_Paulo)

## Retomar daqui

Workspace: `D:\EDY-Projects\EDY-SOC-Analytics`

Branch: `codex/portfolio-10-hardening`

Leia primeiro:

1. `PROJECT_STATE.md`;
2. `CHANGELOG.md` na seção `Unreleased`;
3. `docs/REPRODUCIBILITY.md`;
4. `docs/RLS_SECURITY.md`.

## Próximo gate exato

1. Na janela já aberta, clicar em **Apply external changes** e aguardar a carga; não fechar à força a instância existente.
2. Atualizar o modelo e executar modelo vivo, RLS e performance em uma sessão com acesso ao engine local.
3. Inspecionar e recapturar todas as páginas desktop/mobile pós-hardening.
4. Validar teclado e, manualmente, alto contraste/leitor de tela.
5. Corrigir somente falhas demonstradas e repetir os gates; não publicar sem autorização.

## Comandos portáteis

```powershell
python generator/generate_dataset.py
python -m unittest discover -s tests -v
python validation/project_inventory.py
```

Com o Power BI Desktop aberto:

```powershell
powershell -ExecutionPolicy Bypass -File validation/validate_live_model.ps1
powershell -ExecutionPolicy Bypass -File validation/validate_live_rls.ps1
powershell -ExecutionPolicy Bypass -File validation/measure_performance.ps1
powerbi-report-author validate "powerbi/EDY SOC Analytics.Report" --pretty
powerbi-report-author validate "powerbi/EDY SOC Analytics.Report" --no-schema --pretty
```

## Não fazer sem autorização

- não redesenhar o RLS para eventos/alertas;
- não trocar a origem dos três fatos curados;
- não alterar números para melhorar métricas;
- não fechar o Power BI à força nem descartar alterações;
- não fabricar PBIX/PBIT;
- não adicionar licença;
- não executar push, merge ou release.

## Evidência honesta

- resultado esperado de RLS não equivale a execução viva;
- screenshot de Drillthrough sem filtro não prova drillthrough filtrado;
- validação estática não substitui round-trip do Desktop;
- esquema remoto inacessível deve ser registrado como bloqueio de rede, não como warning do relatório;
- alto contraste e leitor de tela continuam manuais até evidência.
- nesta sessão, a árvore acessível confirmou o relatório aberto, mas o controle de captura/input e a autenticação ADOMD foram negados pelo isolamento do host.
