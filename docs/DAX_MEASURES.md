# Catálogo de medidas DAX

As fórmulas abaixo são a especificação executável do modelo. Percentuais usam `DIVIDE`, tempos usam minutos e bases são reutilizadas. `MTTR` significa exclusivamente criação→resolução.

## Volume e estado

```DAX
Total de eventos = SUM ( FactSecurityEvents[EventCount] )
Total de alertas = SUM ( FactAlerts[AlertCount] )
Total de incidentes = SUM ( FactIncidents[IncidentCount] )

Incidentes novos =
CALCULATE ( [Total de incidentes], KEEPFILTERS ( DimStatus[Status] = "New" ) )

Incidentes ativos =
CALCULATE ( [Total de incidentes], KEEPFILTERS ( DimStatus[IsOpen] = TRUE () ) )

Incidentes fechados =
CALCULATE ( [Total de incidentes], KEEPFILTERS ( DimStatus[IsOpen] = FALSE () ) )

Incidentes críticos ativos =
CALCULATE (
    [Total de incidentes],
    KEEPFILTERS ( DimStatus[IsOpen] = TRUE () ),
    KEEPFILTERS ( DimSeverity[Severity] = "Critical" )
)

Backlog = [Incidentes ativos]

Data de referência = MAX ( FactSecurityEvents[EventTimestampUTC] )

Backlog envelhecido =
VAR Limite = [Data de referência] - 7
RETURN
    CALCULATE (
        [Total de incidentes],
        KEEPFILTERS ( DimStatus[IsOpen] = TRUE () ),
        FactIncidents[CreatedAtUTC] < Limite
    )
```

## Taxas

```DAX
Taxa de fechamento = DIVIDE ( [Incidentes fechados], [Total de incidentes] )

Taxa de escalonamento =
DIVIDE (
    CALCULATE ( [Total de incidentes], FactIncidents[IsEscalated] = TRUE () ),
    [Total de incidentes]
)

Taxa de reabertura =
DIVIDE (
    CALCULATE ( [Total de incidentes], FactIncidents[IsReopened] = TRUE () ),
    [Incidentes fechados]
)

Taxa de falsos positivos =
DIVIDE (
    CALCULATE ( [Total de alertas], FactAlerts[IsFalsePositive] = TRUE () ),
    [Total de alertas]
)

Conversão alerta para incidente =
DIVIDE (
    CALCULATE ( [Total de alertas], FactAlerts[BecameIncident] = TRUE () ),
    [Total de alertas]
)

Incidentes por 1.000 alertas = DIVIDE ( [Total de incidentes] * 1000, [Total de alertas] )

Cumprimento de SLA =
DIVIDE (
    CALCULATE ( COUNTROWS ( FactSLA ), FactSLA[OverallMet] = TRUE () ),
    COUNTROWS ( FactSLA )
)

Violações de SLA = CALCULATE ( COUNTROWS ( FactSLA ), FactSLA[OverallMet] = FALSE () )
```

## Relógios operacionais

```DAX
MTTD (min) = AVERAGE ( FactAlerts[DetectionMinutes] )
MTTA (min) = AVERAGE ( FactIncidents[AcknowledgementMinutes] )
Tempo médio de triagem (min) = AVERAGE ( FactIncidents[TriageMinutes] )
Tempo médio de contenção (min) = AVERAGE ( FactIncidents[ContainmentMinutes] )
MTTR resolução (min) = AVERAGE ( FactIncidents[ResolutionMinutes] )
Tempo médio de recuperação (min) = AVERAGE ( FactIncidents[RecoveryMinutes] )

Idade média do backlog (dias) =
VAR Referencia = [Data de referência]
RETURN
    AVERAGEX (
        FILTER ( FactIncidents, RELATED ( DimStatus[IsOpen] ) = TRUE () ),
        DIVIDE ( DATEDIFF ( FactIncidents[CreatedAtUTC], Referencia, HOUR ), 24 )
    )
```

## Tendência e comparação

```DAX
Incidentes mês anterior =
CALCULATE ( [Total de incidentes], DATEADD ( DimDate[Date], -1, MONTH ) )

Variação mensal de incidentes = [Total de incidentes] - [Incidentes mês anterior]

Variação mensal de incidentes % =
DIVIDE ( [Variação mensal de incidentes], [Incidentes mês anterior] )

MTTR mês anterior =
CALCULATE ( [MTTR resolução (min)], DATEADD ( DimDate[Date], -1, MONTH ) )

Variação MTTR % =
DIVIDE ( [MTTR resolução (min)] - [MTTR mês anterior], [MTTR mês anterior] )

Tendência mensal (índice) =
VAR Atual = [Total de incidentes]
VAR Anterior = [Incidentes mês anterior]
RETURN DIVIDE ( Atual, Anterior, 1 )
```

## MITRE, ativos, regras e fontes

```DAX
Técnicas MITRE observadas = DISTINCTCOUNT ( BridgeIncidentTechnique[AttackTechniqueKey] )

Cobertura MITRE observada =
DIVIDE (
    [Técnicas MITRE observadas],
    CALCULATE ( COUNTROWS ( DimAttackTechnique ), REMOVEFILTERS ( DimAttackTechnique ) )
)

Risco acumulado do ativo = SUM ( FactIncidents[RiskScore] )

Ativos de alto risco =
COUNTROWS (
    FILTER (
        VALUES ( DimAsset[AssetKey] ),
        [Risco acumulado do ativo] >= 250
    )
)

Alertas por regra = [Total de alertas]

Ruído por 1.000 alertas =
DIVIDE (
    CALCULATE ( [Total de alertas], FactAlerts[IsFalsePositive] = TRUE () ) * 1000,
    [Total de alertas]
)

Fidelidade da fonte = 1 - [Taxa de falsos positivos]

Taxa regra para incidente =
DIVIDE (
    CALCULATE ( [Total de alertas], FactAlerts[BecameIncident] = TRUE () ),
    [Total de alertas]
)
```

## Contexto de analistas e qualidade

```DAX
Peso de complexidade resolvida =
SUMX (
    FILTER ( FactIncidents, RELATED ( DimStatus[IsOpen] ) = FALSE () ),
    RELATED ( DimSeverity[RiskWeight] ) * ( 1 + DIVIDE ( FactIncidents[RiskScore], 100 ) )
)

Índice contextual de resolução =
VAR Complexidade = [Peso de complexidade resolvida]
VAR Tempo = [MTTR resolução (min)]
VAR SLA = [Cumprimento de SLA]
RETURN DIVIDE ( Complexidade * ( 0.5 + SLA ), 1 + DIVIDE ( Tempo, 60 ) )

Registros rejeitados = COALESCE ( COUNTROWS ( DQ_RejectedRows ), 0 )

Completude de eventos =
1 - DIVIDE ( [Registros rejeitados], COUNTROWS ( Stg_SecurityEvents ) )

Última atualização UTC = MAX ( FactSecurityEvents[ReceivedAtUTC] )
```

O índice contextual não é um ranking de pessoas. Ele deve ser lido junto com severidade, complexidade, carga, SLA e faixa de experiência.

## Casos limites

- Divisão por zero retorna `BLANK()` ou o alternativo explícito.
- Incidentes ainda abertos não entram em médias que dependem de timestamp futuro.
- A data de referência vem do dataset, não de `NOW()`, preservando reprodutibilidade.
- Filtros sem dados devem mostrar `—` em vez de zero quando zero sugerir atividade medida.
