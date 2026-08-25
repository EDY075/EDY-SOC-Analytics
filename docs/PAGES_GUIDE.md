# Guia funcional das páginas

Este guia vincula cada página ao PBIR versionado. Nomes de medidas, dimensões, slicers e ações correspondem aos visuais existentes. Sob `SOC_Analyst`, métricas de incidentes são filtradas por equipe, enquanto eventos e alertas permanecem globais; cada seção explicita quando esse escopo misto afeta a leitura.

## 1. Command Center

- **Objetivo:** oferecer triagem executiva do backlog e das prioridades operacionais.
- **Pergunta respondida:** quais incidentes exigem atenção agora e como volume, SLA e tempo estão evoluindo?
- **Indicadores:** `Incidentes ativos`, `Incidentes críticos ativos`, `Backlog`, `Cumprimento de SLA`, `MTTD (min)`, `MTTR resolução (min)`, `Variação mensal de incidentes %` e `Total de incidentes` na tendência/tabela.
- **Filtros e interações:** slicer Ano; linha por `YearMonth`; barras por severidade; seleção cruzada; botão `Limpar filtros`; tabela de prioridades com `IncidentId`, severidade, status, ativo e risco; drillthrough pela linha do incidente; navegação para Methodology e page navigator.
- **Uso no SOC:** iniciar o turno pelos críticos ativos, verificar backlog e SLA e abrir o detalhe do incidente com maior risco.
- **Decisão apoiada:** priorizar contenção de um incidente crítico em ativo de maior `RiskScore` antes de itens informativos, registrando o impacto esperado no backlog.

**Nota de RLS:** MTTD vem de alertas e permanece global; MTTR, backlog, SLA e incidentes respeitam a equipe do analista.

## 2. SOC Operations

- **Objetivo:** mostrar o funil operacional entre telemetria, alertas e incidentes e localizar fontes/regras de maior volume.
- **Pergunta respondida:** o volume recebido está produzindo sinal útil ou ruído excessivo?
- **Indicadores:** `Total de eventos`, `Total de alertas`, `Total de incidentes`, `Conversão alerta para incidente`, `Taxa de falsos positivos` e `Fidelidade da fonte`.
- **Filtros e interações:** slicers Ano e Severidade; linha mensal com alertas e incidentes; barras por produto-fonte e regra; tabela de fidelidade por fonte; cross-filter; bookmark real `Estado padrão SOC Operations`; page navigator.
- **Uso no SOC:** comparar uma elevação de alertas com incidentes gerados, identificar a origem dominante e inspecionar regras que aumentaram o volume.
- **Decisão apoiada:** abrir atividade de tuning para uma regra de alto volume quando a conversão não acompanha o crescimento de alertas e a taxa de falso positivo permanece alta.

**Nota de RLS:** eventos e alertas são globais; incidentes são restritos por equipe. A relação entre eles é um indicador de escopo misto para `SOC_Analyst`, não uma taxa exclusiva da equipe.

## 3. Incident Lifecycle

- **Objetivo:** decompor o tempo de resposta e evidenciar aging e violações de SLA.
- **Pergunta respondida:** em qual etapa do ciclo de vida os incidentes ficam mais tempo e onde o SLA falha?
- **Indicadores:** `MTTA (min)`, `Tempo médio de triagem (min)`, `Tempo médio de contenção (min)`, `MTTR resolução (min)`, `Cumprimento de SLA`, `Backlog`, `Backlog envelhecido`, `Violações de SLA` e `Idade média do backlog (dias)`.
- **Filtros e interações:** barras por estágio usando `MinutesFromPreviousStage`; barras de MTTR e SLA por severidade; tabela de backlog/violações; seleção cruzada e page navigator. Não há slicer local nem botão de reset nesta página.
- **Uso no SOC:** comparar reconhecimento, triagem, contenção e resolução, depois selecionar uma severidade para localizar o gargalo operacional.
- **Decisão apoiada:** reforçar a etapa de contenção quando ela concentra o maior tempo e severidades altas acumulam violações.

## 4. Threat & MITRE

- **Objetivo:** contextualizar incidentes com táticas e técnicas MITRE ATT&CK observadas.
- **Pergunta respondida:** quais comportamentos adversários aparecem com maior frequência e risco?
- **Indicadores:** `Técnicas MITRE observadas`, `Cobertura MITRE observada`, `Incidentes críticos ativos`, `Total de incidentes` e `Risco acumulado do ativo`.
- **Filtros e interações:** slicer Tática; barras por tática e técnica; tabela acessível com tática, `TechniqueId`, nome, incidentes e risco; cross-filter; `Limpar filtros`; page navigator.
- **Uso no SOC:** selecionar uma tática, comparar técnicas recorrentes e verificar se frequência e risco justificam nova detecção ou playbook.
- **Decisão apoiada:** priorizar cobertura de uma técnica recorrente com alto risco acumulado, mesmo que outra técnica tenha volume ligeiramente maior.

## 5. Assets & Exposure

- **Objetivo:** localizar concentração de risco por ativo e contexto de negócio.
- **Pergunta respondida:** quais ativos, unidades e ambientes concentram incidentes e risco?
- **Indicadores:** `Ativos de alto risco`, `Risco acumulado do ativo`, `Incidentes ativos` e `Total de incidentes`.
- **Filtros e interações:** slicers Ambiente e Unidade; barras de risco por ativo e incidentes por unidade; tabela com ativo, tipo, criticidade, ambiente, incidentes e risco; cross-filter; `Limpar filtros`; page navigator.
- **Uso no SOC:** restringir a Produção ou a uma unidade, comparar criticidade com risco observado e selecionar o ativo para ver a contribuição ao total.
- **Decisão apoiada:** escalar tratamento de um ativo crítico de Produção quando ele combina risco acumulado alto e incidentes ativos.

## 6. Detection Engineering

- **Objetivo:** apoiar tuning de regras com volume, falso positivo, fidelidade e conversão.
- **Pergunta respondida:** quais regras geram sinal útil e quais consomem capacidade sem converter em incidente?
- **Indicadores:** `Total de alertas`, `Taxa de falsos positivos`, `Taxa regra para incidente`, `Fidelidade da fonte` e `Ruído por 1.000 alertas`.
- **Filtros e interações:** slicer Família de regra; barras de volume e falso positivo por regra; tabela com nome, família, alertas, conversão, falso positivo e fidelidade; cross-filter; `Limpar filtros`; page navigator.
- **Uso no SOC:** filtrar uma família, comparar regras de volume semelhante e priorizar a combinação de alto ruído e baixa fidelidade.
- **Decisão apoiada:** revisar limiar ou enriquecimento de uma regra antes de desativá-la, preservando cobertura e medindo conversão após o ajuste.

**Nota de RLS:** todos os indicadores desta página derivam de alertas e permanecem globais no papel `SOC_Analyst`.

## 7. Analyst & SLA

- **Objetivo:** contextualizar carga e desempenho por equipe sem transformar a página em ranking de pessoas.
- **Pergunta respondida:** como carga, complexidade, SLA e tempo de resolução variam entre equipes e faixas de experiência?
- **Indicadores:** `Cumprimento de SLA`, `Índice contextual de resolução`, `Peso de complexidade resolvida`, `MTTR resolução (min)` e `Total de incidentes`.
- **Filtros e interações:** slicer Equipe; barras de carga e SLA por equipe; tabela por `AnalystLabel`, equipe e `ExperienceBand`; cross-filter; `Limpar filtros`; page navigator.
- **Uso no SOC:** comparar SLA junto com complexidade e carga, evitando interpretar volume isolado como produtividade individual.
- **Decisão apoiada:** redistribuir casos ou oferecer apoio a uma equipe quando carga e complexidade sobem simultaneamente e o SLA cai.

Os nomes de analista são rótulos sintéticos. O índice contextual é uma medida demonstrativa, não avaliação de pessoa.

## 8. Data Quality

- **Objetivo:** tornar visíveis classificação, atualização, rejeições e fidelidade por fonte.
- **Pergunta respondida:** os dados carregados são rastreáveis e adequados para interpretar os indicadores?
- **Indicadores:** `Registros rejeitados`, `Total de eventos`, `Última atualização UTC` e `Fidelidade da fonte`.
- **Filtros e interações:** slicer Produto-fonte; barras de eventos e fidelidade por fonte; tabela de rejeições com motivo seguro; tabela de classificação/origem; cross-filter; `Limpar filtros`; page navigator.
- **Uso no SOC:** verificar atualização e classificação antes de usar o relatório, filtrar uma fonte e conferir se volume ou fidelidade explicam uma anomalia.
- **Decisão apoiada:** suspender uma conclusão operacional quando a fonte relevante estiver desatualizada ou apresentar queda de fidelidade, mesmo com zero rejeições.

**Nota de RLS:** eventos, origem e qualidade são globais no desenho atual. `Registros rejeitados = 0` descreve a amostra carregada, não garante ausência de falhas futuras.

## 9. Incident Drillthrough

- **Objetivo:** reunir o contexto investigativo de um incidente selecionado sem perder o filtro de origem.
- **Pergunta respondida:** o que ocorreu, em qual ativo, por qual regra, em que sequência e com quais técnicas MITRE?
- **Indicadores:** `Total de incidentes`, `MTTA (min)`, `Tempo médio de contenção (min)`, `MTTR resolução (min)` e `Cumprimento de SLA`.
- **Filtros e interações:** página declarada como Drillthrough; filtro `FactIncidents[IncidentId]`; tabela de identificação/contexto; timeline com estágio, data, minutos e ação segura; tabela MITRE; botão de retorno ao Command Center; page navigator.
- **Uso no SOC:** abrir a partir da tabela de prioridades, confirmar que existe um único incidente no contexto e percorrer timeline, ativo, regra, risco e técnicas.
- **Decisão apoiada:** manter a investigação aberta ou escalá-la quando timeline, risco do ativo e técnica observada indicarem contenção insuficiente.

## 10. Methodology

- **Objetivo:** explicar escopo, leitura, segurança, limitações e fontes do produto analítico.
- **Pergunta respondida:** como interpretar os números sem extrapolar o que o dataset sintético demonstra?
- **Indicadores:** não possui medidas; contém seis caixas de texto sobre escopo/ética, relógios, segurança, fontes, limitações e uso.
- **Filtros e interações:** page navigator; não há slicer, bookmark ou botão local.
- **Uso no SOC:** consultar definições antes de comparar tempos, entender a fronteira de RLS e conferir fontes metodológicas.
- **Decisão apoiada:** rejeitar uma comparação ou publicação quando ela tratar os dados sintéticos como risco real ou ignorar a diferença entre métricas globais e restritas.

## Interpretação transversal

- A seleção cruzada é uma ferramenta de investigação, não um controle de acesso.
- Tooltips são os tooltips enriquecidos padrão do Power BI; não existem páginas customizadas de tooltip.
- O único bookmark versionado é `Estado padrão SOC Operations`.
- Tabelas oferecem alternativa textual aos gráficos e ajudam a verificar o contexto de filtro.
- Valores são sintéticos e reproduzíveis; não representam desempenho de pessoas, risco de ativos reais nem operação de um SOC específico.
