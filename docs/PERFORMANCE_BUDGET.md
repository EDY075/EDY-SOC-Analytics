# Orçamento e medição de desempenho

## Metas internas EDY

- p95 de consulta + renderização por visual após cache aquecido: <2.000 ms.
- Página inicial: até 8 visuais analíticos principais.
- Nenhum visual individual: >3.000 ms após otimização sem justificativa.
- Refresh local dos CSVs: <120 s no host de validação.
- Modelo: apenas colunas necessárias; IDs de alta cardinalidade ocultos e usados somente em detalhe.

Essas metas não são SLAs da Microsoft.

## Estratégias já implementadas

- Star schema e filtros unidirecionais.
- Separação Date/Time.
- CSV selecionado/tipado cedo no Power Query.
- Queries de staging previstas sem carga.
- Medidas explícitas com bases reutilizáveis, `VAR` e `DIVIDE`.
- Limite de densidade por página.

## Medições reais - 24/08/2026

| Consulta | Cold (ms) | P50 warm (ms) | P95 warm (ms) | Estado |
|---|---:|---:|---:|---|
| Command Center | 7,98 | 5,07 | 5,66 | VALIDADO |
| Tendência mensal | 3,98 | 2,80 | 3,19 | VALIDADO |
| Cobertura MITRE | 3,36 | 3,24 | 3,93 | VALIDADO |
| Regras de detecção | 3,81 | 3,98 | 8,16 | VALIDADO |
| Detalhe de incidente | 6,98 | 5,92 | 6,39 | VALIDADO |

A captura das dez páginas pelo Desktop Bridge, incluindo navegação, settle e PNG, levou 17.400,69 ms: média de 1.740,07 ms/página. O teste mede o host local e não substitui o Performance Analyzer do serviço.

Evidências: `validation/results/performance.json`, `validation/results/render-performance.json` e `validation/measure_performance.ps1`.
