# Blueprint funcional do relatório

Este documento descreve o PBIR versionado, não um backlog de visuais planejados. O detalhamento operacional das dez páginas está em `docs/PAGES_GUIDE.md`.

## Narrativa e páginas implementadas

| Página | Pergunta | Visuais nativos existentes | Filtros e ações existentes |
|---|---|---|---|
| 1. Command Center | O que exige atenção agora? | 3 cards, linha mensal, barras por severidade, tabela de prioridades | slicer Ano, `Limpar filtros`, navegação para Methodology, page navigator, cross-filter e drillthrough pela linha de incidente |
| 2. SOC Operations | Qual é o fluxo de eventos, alertas e incidentes? | 2 cards, linha temporal, 2 barras, tabela por fonte | slicers Ano e Severidade, bookmark `Estado padrão`, page navigator e cross-filter |
| 3. Incident Lifecycle | Onde o ciclo desacelera e viola SLA? | 2 cards, 3 barras e tabela de backlog/SLA | page navigator e cross-filter por estágio/severidade |
| 4. Threat & MITRE | Quais táticas e técnicas aparecem nos incidentes? | card, 2 barras e tabela MITRE acessível | slicer Tática, `Limpar filtros`, page navigator e cross-filter |
| 5. Assets & Exposure | Em quais ativos, unidades e ambientes o risco se concentra? | card, 2 barras e tabela de exposição | slicers Ambiente e Unidade, `Limpar filtros`, page navigator e cross-filter |
| 6. Detection Engineering | Quais regras geram volume, sinal e falso positivo? | 2 cards, 2 barras e matriz de ajuste em tabela | slicer Família de regra, `Limpar filtros`, page navigator e cross-filter |
| 7. Analyst & SLA | Como carga, SLA, complexidade e tempo variam por equipe? | 2 cards, 2 barras e tabela contextual | slicer Equipe, `Limpar filtros`, page navigator e cross-filter |
| 8. Data Quality | A camada analítica está completa, classificada e atualizada? | 2 cards, 2 barras e 2 tabelas | slicer Produto-fonte, `Limpar filtros`, page navigator e cross-filter |
| 9. Incident Drillthrough | O que ocorreu no incidente selecionado? | 2 cards e 3 tabelas de contexto, timeline e MITRE | filtro drillthrough por `IncidentId`, botão de retorno ao Command Center e page navigator |
| 10. Methodology | Como ler, limitar e reproduzir a análise? | 8 caixas de texto | page navigator |

Todos os 101 visuais são nativos. Não existem heatmap, funil, dispersão, Pareto, treemap, small multiples ou páginas dedicadas de tooltip no PBIR atual.

## Filtros e sincronização

Os slicers existentes são locais às páginas:

- Command Center: Ano;
- SOC Operations: Ano e Severidade;
- Threat & MITRE: Tática;
- Assets & Exposure: Ambiente e Unidade;
- Detection Engineering: Família de regra;
- Analyst & SLA: Equipe;
- Data Quality: Produto-fonte.

O PBIR não declara uma coleção de slicers sincronizados globalmente. O page navigator permite deslocamento entre as dez páginas, mas cada página conserva apenas seu próprio contexto compatível. `IncidentId` é um filtro de drillthrough da página 9, não um slicer global.

## Bookmark e reset implementados

Existe um bookmark real: `Estado padrão SOC Operations`. O botão `Estado padrão` da página 2 aponta para esse bookmark e restaura o estado registrado. A evidência funcional anterior reduziu alertas de 18 mil para 2 mil por seleção e restaurou 18 mil pelo bookmark.

Os botões `Limpar filtros` usam a ação nativa `ClearAllSlicers` nas páginas 1, 4, 5, 6, 7 e 8. O Command Center também possui navegação por ação para Methodology; a página de drillthrough possui retorno por navegação para Command Center. Incident Lifecycle e Methodology não têm botão de reset porque não possuem slicer local.

Não existem os bookmarks `Reset_Global`, `View_Executive`, `View_Operational` ou `Show_Definitions` descritos em versões preliminares deste documento.

## Tooltips implementados

O relatório habilita `useEnhancedTooltips` e utiliza os tooltips padrão/enriquecidos dos visuais nativos. Não existem páginas de report tooltip ou artefatos chamados `Tooltip_KPI`, `Tooltip_Rule` ou `Tooltip_Asset`.

Informação essencial está nos títulos, rótulos, cards e tabelas; nenhum fluxo depende exclusivamente de hover. Isso preserva acesso por teclado e evita que uma definição crítica exista apenas em tooltip.

## Interações verificadas

- cross-filter no Command Center: incidentes ativos variaram de 253 para 7 e voltaram a 253 após limpeza;
- drillthrough: uma linha de incidente abriu a página 9 filtrada para um único `IncidentId`;
- bookmark: uma seleção reduziu alertas de 18 mil para 2 mil e `Estado padrão` restaurou 18 mil;
- navegação por ação e teclado: Command Center → Methodology.

As demais interações seguem o comportamento nativo de seleção cruzada; elas não devem ser anunciadas como testes manuais individuais sem nova evidência.

## Estados e comunicação

- carregamento é o estado nativo do Power BI; não há skeleton customizado;
- filtros sem correspondência produzem cards em branco/zero conforme a semântica da medida e visuais sem linhas;
- `DQ_RejectedRows` expõe somente motivo seguro e classificação, nunca payload bruto;
- verde é reservado para cumprimento/resultado favorável, âmbar para atenção e vermelho para criticidade;
- a cobertura de RLS é parcial por desenho: incidentes respeitam equipe, eventos e alertas permanecem globais. Consulte `docs/RLS_SECURITY.md`.
