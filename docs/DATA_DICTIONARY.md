# Dicionário e catálogo de dados

Todos os dados têm classificação `SYNTHETIC_DEMO_DATA`.

## Granularidade das fatos

| Tabela | Grão | Chave | Medidas aditivas/semiaditivas |
|---|---|---|---|
| FactSecurityEvents | um evento canônico | EventKey / EventId | EventCount, IngestionDelaySeconds |
| FactAlerts | um alerta derivado | AlertKey / AlertId | AlertCount, DetectionMinutes |
| FactIncidents | estado analítico atual de um incidente | IncidentKey / IncidentId | IncidentCount, tempos, RiskScore |
| FactIncidentLifecycle | uma transição de estágio | LifecycleKey | MinutesFromPreviousStage |
| FactSLA | avaliação de SLA por incidente | SLAFactKey | metas, reais e flags |
| BridgeIncidentTechnique | vínculo incidente↔técnica | IncidentTechniqueKey | IsPrimary |

## Dimensões

| Tabela | Finalidade | Chave principal | Atributos relevantes |
|---|---|---|---|
| DimDate | inteligência de tempo | DateKey | ano, trimestre, mês, dia, dia da semana |
| DimTime | heatmap intradiário | TimeKey | hora, minuto, período |
| DimAsset | exposição e criticidade | AssetKey | tipo, unidade, ambiente, criticidade |
| DimSourceProduct | origem e fidelidade | SourceProductKey | produto, sistema, fidelidade, volume |
| DimSeverity | semântica e sort-by | SeverityKey | label EN/PT, ordem, peso, cor |
| DimStatus | estado e sort-by | StatusKey | label EN/PT, ordem, aberto/fechado |
| DimDetectionRule | qualidade de detecção | DetectionRuleKey | família, severidade, fidelidade, ruído |
| DimAttackTactic | matriz MITRE | AttackTacticKey | ID, nome, versão e domínio |
| DimAttackTechnique | técnica MITRE | AttackTechniqueKey | ID, nome, tática, versão e depreciação |
| DimAnalyst | carga contextualizada | AnalystKey | rótulo fictício, equipe, região, experiência |
| DimClassification | encerramento | ClassificationKey | label e flag falso positivo |
| DimSLA | metas por severidade | SLAKey | reconhecimento, contenção, resolução |

## Relógios

| Métrica | Início | Fim | Unidade |
|---|---|---|---|
| MTTD | EventTimestampUTC | DetectedAtUTC | minutos |
| MTTA | CreatedAtUTC | AcknowledgedAtUTC | minutos |
| Triagem | CreatedAtUTC | TriagedAtUTC | minutos |
| Contenção | CreatedAtUTC | ContainedAtUTC | minutos |
| MTTR — resolução | CreatedAtUTC | ResolvedAtUTC | minutos |
| Recuperação | ResolvedAtUTC | ClosedAtUTC | minutos |

MTTR sempre significa tempo até resolução neste projeto. Tempo até fechamento é uma medida distinta.

## Campos sensíveis deliberadamente ausentes

Não há nome real, e-mail, telefone, credencial, domínio real, IP público, hostname pessoal, comando, payload, exploit, hash operacional ou texto livre de evidência.

