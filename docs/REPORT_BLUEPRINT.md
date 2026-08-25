# Blueprint funcional do relatório

## Narrativa e páginas

| Página | Pergunta | Visuais nativos principais | Interações |
|---|---|---|---|
| 1. Command Center | O que exige atenção agora? | KPIs, linha 12 meses, barras críticas, tabela de prioridades | slicers sincronizados, reset, drillthrough |
| 2. SOC Operations | O volume e a conversão estão saudáveis? | combo chart, severidade/status, heatmap dia×hora, top fontes/regras | cross-filter, tooltip, foco |
| 3. Incident Lifecycle | Onde o fluxo desacelera? | funil, barras por etapa, aging bands, SLA por severidade | seleção por severidade, drillthrough |
| 4. Threat & MITRE | Quais comportamentos se repetem? | matriz tática×técnica, barras, dispersão risco×frequência | drillthrough e tabela acessível |
| 5. Assets & Exposure | Onde o risco se concentra? | Pareto, treemap moderado, linha, tabela de ativos | filtro por unidade/ambiente |
| 6. Detection Engineering | Quais regras geram sinal ou ruído? | quadrante volume×fidelidade, barras, tabela de ações | tooltip e filtro por família |
| 7. Analyst & SLA | A carga está equilibrada no contexto? | distribuição, severidade, SLA, small multiples | sem ranking ordinal simplista |
| 8. Data Quality | Os dados são confiáveis? | completude, rejeições, duplicidade, qualidade por fonte, atualização | tabela de motivos segura |
| 9. Incident Drillthrough | O que ocorreu neste incidente sintético? | resumo, timeline, ativo/regra/MITRE/SLA | voltar; filtro IncidentId mantido |
| 10. Methodology | Como interpretar o relatório? | cartões textuais, tabela de definições e fontes | navegação e links seguros |

## Slicers sincronizados

Período, produto-fonte, severidade, status e ambiente. A página de drillthrough não sincroniza `IncidentId` para evitar estado inesperado.

## Bookmarks funcionais

- `Reset_Global`: limpa filtros permitidos e retorna ao estado padrão.
- `View_Executive`: reduz detalhes operacionais no Command Center.
- `View_Operational`: expande a fila de prioridades.
- `Show_Definitions`: exibe/oculta painel metodológico contextual.

## Tooltips

- `Tooltip_KPI`: definição, relógio, unidade e período anterior.
- `Tooltip_Rule`: volume, conversão, falso positivo e última atividade.
- `Tooltip_Asset`: criticidade, incidentes, risco e fontes.

Informação essencial nunca depende somente de tooltip, pois leitores de tela não leem todos os report tooltips.

## Estados

- Carregamento: skeleton não existe nativamente; usar título “Atualizando…” somente quando medido via estado de refresh.
- Vazio: medida retorna mensagem “Nenhum registro para os filtros selecionados”.
- Erro: queries de qualidade expõem contagem e razão segura; não mostram payload.
- Sucesso: verde reservado para SLA cumprido, qualidade aprovada ou redução confirmada.

