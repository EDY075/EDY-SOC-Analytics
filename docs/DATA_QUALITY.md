# Regras de qualidade de dados

## Inconsistências controladas na camada raw

| Regra | Injeção | Tratamento esperado no Power Query |
|---|---:|---|
| Eventos duplicados | 720 linhas | `Table.Distinct` por `event_id` após ordenação estável |
| Asset ausente | determinístico, a cada 173 eventos | substituir por `DimAsset[AssetKey] = 0` (`Ativo não informado`) |
| Labels de severidade variantes | módulos determinísticos | trim/lower + mapa canônico |
| Incidentes duplicados | 16 linhas | dedupe por `incident_id` |
| Analista ausente | amostra determinística | `DimAnalyst[AnalystKey] = 0` (`Não atribuído`) |
| Status variantes pt-BR | módulos determinísticos | mapa canônico |

## Dimensões de qualidade

- Completude: proporção de campos obrigatórios preenchidos.
- Validade: proporção que respeita tipo, domínio e formato.
- Unicidade: chave de negócio sem duplicação após limpeza.
- Integridade: chaves estrangeiras resolvidas.
- Pontualidade: atraso entre evento e recebimento dentro do limite escolhido.
- Consistência: timestamps do ciclo de vida em ordem não decrescente.

## Quarentena

Linhas com chave de evento, timestamp ou severidade inválidos não entram nas fatos. Asset ausente é uma falha recuperável e entra com o membro desconhecido, preservando o volume. A query `DQ_RejectedRows` mantém somente falhas não recuperáveis, com motivo seguro e sem payload ou texto operacional.

## Valores esperados

`data/expected/` funciona como oracle de testes e não como substituto do Power Query. `data/expected/kpi_expected.json` contém baselines reproduzíveis para conferir medidas.
