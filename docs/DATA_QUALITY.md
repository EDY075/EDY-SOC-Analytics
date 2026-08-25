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

`data/expected/` tem duas funções no desenho atual:

1. **oracle reproduzível:** hashes, chaves, contagens e `kpi_expected.json` permitem comparar a saída regenerada e o modelo vivo;
2. **camada curada carregada:** `FactIncidentLifecycle`, `FactSLA` e `BridgeIncidentTechnique` são importadas diretamente de seus CSVs em `data/expected/`.

As três fatos principais não são substituídas por esse oracle: `FactSecurityEvents`, `FactAlerts` e `FactIncidents` continuam sendo tipadas, normalizadas, deduplicadas e conformadas por Power Query a partir de `data/raw/`. `DQ_RejectedRows` também deriva da camada raw. Essa distinção deve ser mantida em diagramas e instruções de reprodução.

## Controles automatizados existentes

- seed e SHA-256 determinísticos no manifesto;
- unicidade após deduplicação;
- tratamento de membros desconhecidos;
- integridade referencial de ativo, regra e severidade;
- sequência temporal do lifecycle;
- regras de SLA e chaves MITRE;
- contagens e KPIs esperados;
- classificação `SYNTHETIC_DEMO_DATA` e varredura básica de segredos/PII.

`Registros rejeitados = 0` é o resultado atual do modelo carregado, não prova universal de qualidade. Ele indica apenas que nenhuma linha da amostra atual caiu nas condições não recuperáveis da query de quarentena.
