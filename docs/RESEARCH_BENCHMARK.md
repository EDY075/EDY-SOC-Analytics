# Pesquisa e benchmark — EDY SOC Analytics

Pesquisa verificada em 24/08/2026. Foram usadas somente fontes oficiais e primárias; produtos correlatos serviram para identificar princípios e lacunas, nunca para copiar layout, dados ou textos.

## PL-300 e competências demonstradas

O guia vigente desde 20/04/2026 divide o exame em preparação de dados (25–30%), modelagem (25–30%), visualização e análise (25–30%) e gerenciamento/segurança (15–20%). O projeto cobre parâmetros e profiling, limpeza, fatos/dimensões, relacionamentos, DAX, narrativa visual, bookmarks, tooltips, drillthrough, mobile, acessibilidade e RLS.

Fonte: [Microsoft Learn — PL-300 Study Guide](https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/pl-300).

## Padrões observados

| Fonte | Padrão útil | Limitação observada | Decisão EDY |
|---|---|---|---|
| Microsoft Sentinel | Estado, severidade, classificação, tempos de triagem/fechamento e tendências | Cada atualização gera uma linha em `SecurityIncident`; contar linhas superestima incidentes | Separar estado atual de histórico de ciclo de vida e deduplicar por chave/última atualização |
| Sentinel Overview | Correlação alerta→incidente, saúde das fontes e regras | Foco operacional imediato; workbooks têm limites de resultado | Usar Power BI para histórico, modelo dimensional e análise comparativa |
| MITRE ATT&CK | Táticas, técnicas, versionamento e domínio | Sentinel está alinhado a v18; site ATT&CK está em v19.2 e bundle STIX versionado verificado em v19.1 | Fixar `AttackVersion=19.1` no dataset e nunca misturar versões sem rótulo |
| NIST CSF 2.0 | Govern, Identify, Protect, Detect, Respond, Recover | Framework não define um score universal | Não apresentar “conformidade NIST”; qualquer score futuro será metodologia interna explícita |
| NIST SP 800-61 Rev. 3 | Preparação, resposta e melhoria contínua integradas ao CSF 2.0 | Não prescreve MTTD/MTTR específicos | Usar os KPIs como indicadores operacionais locais, com relógios documentados |

Fontes: [métricas de incidentes Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/manage-soc-with-incident-metrics), [visibilidade Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/get-visibility), [MITRE ATT&CK Enterprise](https://attack.mitre.org/matrices/enterprise/), [histórico de versões ATT&CK](https://attack.mitre.org/resources/versions/), [NIST CSF 2.0](https://www.nist.gov/cyberframework), [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final).

## Modelagem, ETL e desempenho

- Fatos mantêm granularidade uniforme; dimensões filtram e agrupam. Esse desenho segue a [orientação oficial de star schema](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema).
- CSV não fornece query folding. Portanto, o projeto filtra arquivos e seleciona colunas cedo, usa staging sem carga e documenta que as transformações são executadas pelo engine do Power Query. Referências: [Power Query folding](https://learn.microsoft.com/en-us/power-query/power-query-folding) e [data profiling](https://learn.microsoft.com/en-us/power-query/data-profiling-tools).
- O orçamento interno é p95 abaixo de 2 s por visual após cache aquecido e até 8 visuais analíticos principais por página. É uma meta EDY, não um SLA Microsoft.
- O [Performance Analyzer](https://learn.microsoft.com/en-us/power-bi/create-reports/performance-analyzer) separa consulta DAX, DirectQuery, renderização visual e “Other”. Ele não mede capacidade/PPU; os resultados só serão registrados após execução real.
- Medidas usam bases explícitas, `VAR`, `DIVIDE`, filtros booleanos e granularidade apropriada.

## PBIP, PBIR e TMDL

PBIP, armazenamento PBIR e armazenamento TMDL no Desktop continuam em preview em 24/08/2026. O projeto os utiliza para versionabilidade, mas exige round-trip real no Power BI Desktop antes de considerá-los validados. Conversão PBIX↔PBIP só é oficialmente suportada pela interface do Desktop.

Fontes: [PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview), [pasta PBIR](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report), [modelo e TMDL](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset), [TMDL](https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview) e [schemas oficiais Microsoft](https://github.com/microsoft/json-schemas/tree/main/fabric/item).

## RLS e acessibilidade

- RLS será aplicado por tabela de autorização e relações ativas. No serviço, restringe consumidores Viewer; Admin, Member e Contributor não são restringidos. Fonte: [RLS no Power BI](https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security).
- Alt text, ordem de tabulação, títulos descritivos, teclado, tabelas de dados, contraste e redundância além da cor seguem a [orientação de acessibilidade do Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports).
- Meta interna: WCAG 2.2 AA. Texto normal ≥4,5:1 e texto grande/elementos gráficos relevantes ≥3:1. Fonte: [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/).
- Mobile terá hierarquia curta e visuais essenciais; detalhes permanecem no desktop. Fonte: [mobile-optimized reports](https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-create-mobile-optimized-report-best-practices).

## Decisões rejeitadas

- Copiar a página Overview do Sentinel: rejeitado por identidade e narrativa próprias.
- Usar visuais externos apenas por estética: rejeitado por segurança, manutenção e acessibilidade.
- Exibir ranking simples de analistas: rejeitado por incentivar comparação injusta sem complexidade/contexto.
- Chamar frequência observada de “cobertura MITRE”: rejeitado; cobertura é tratada como técnicas observadas versus universo explicitamente selecionado/versionado.
- Afirmar desempenho sem medição: rejeitado.
- Gerar arquivo PBIX por renomeação ou compactação: rejeitado; seria artefato falso.

## Diferenciação: Signal Grid

O EDY SOC Analytics organiza o relatório como uma grade de sinais: panorama executivo, fila operacional, relógios do incidente, padrões de ameaça, exposição, engenharia de detecção, capacidade contextualizada e qualidade dos dados. A identidade usa grafite, ciano técnico moderado, âmbar para atenção, vermelho apenas para crítico e verde apenas para sucesso. Não replica Sentinel nem os produtos EDY existentes.

