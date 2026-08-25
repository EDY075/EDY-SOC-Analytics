# Signal Grid — Design system

## Princípios

1. Informação antes de decoração.
2. Alta densidade com alinhamento rigoroso em grade de 8 px.
3. Estado sempre expresso por texto e forma, não só por cor.
4. Ciano guia a navegação; vermelho é reservado a crítico; verde a resultado positivo.
5. Superfícies sólidas substituem glassmorphism e brilho excessivo.

## Tokens

| Token | Valor | Uso |
|---|---|---|
| Canvas | `#0D1118` | fundo principal |
| Surface | `#141B25` | cards e visuais |
| Surface raised | `#1A2330` | painel ativo/tooltips |
| Border | `#273244` | divisão estrutural |
| Text primary | `#E8EEF7` | títulos e valores |
| Text secondary | `#AEBBD0` | labels e apoio |
| Cyan | `#39C6E6` | navegação e seleção |
| Violet | `#7D8CFF` | comparação secundária |
| Amber | `#F2B84B` | atenção/SLA em risco |
| Critical | `#E5484D` | incidente crítico |
| Positive | `#46C78C` | cumprimento/redução |

## Tipografia e espaçamento

- Segoe UI; fallback nativo do Power BI.
- Callout 26 px, título 14 px, cabeçalho 12 px, label 11 px.
- Escala espacial: 4, 8, 12, 16, 24 e 32 px.
- Raio de 6 px; borda 1 px; sombras desativadas por padrão.

## Componentes

- KPI compacto: label, valor, variação textual e sparkline quando útil.
- Cabeçalho: título da página, pergunta respondida, atualização e filtros ativos.
- Slicer: estado padrão, hover/foco e seleção visíveis.
- Tabela operacional: densidade média, cabeçalho fixo, zebra discreta e ícone textual de severidade.
- Botão: verbo claro; nenhum botão decorativo.

## Arsenal de referência

- shadcn/ui e Base UI: estados, acessibilidade e espaçamento.
- OriginKit/Origin UI e Skiper UI: composição e hierarquia.
- React Bits, Aceternity, Magic UI, Motion, 21st.dev e UIverse: microdetalhes moderados e sensação de produto.
- Lucide: coerência iconográfica como referência; o relatório prioriza ícones nativos.
- Recharts: legibilidade de eixos, legendas e tooltips.
- GSAP, Three.js e React Three Fiber foram rejeitados porque não agregam valor no Power BI e aumentariam peso/risco.

Nenhum componente de terceiros foi copiado e nenhuma dependência web foi adicionada ao Power BI.

