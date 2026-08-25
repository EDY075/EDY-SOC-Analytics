# Diagramas de arquitetura

Esta pasta contém fontes editáveis em Mermaid e exports SVG portáteis, sem dependências externas em runtime.

| Diagrama | Fonte | Export vetorial | PNG 2× |
|---|---|---|---|
| Arquitetura completa | `architecture-overview.mmd` | `architecture-overview.svg` | `architecture-overview.png` (3600×2240) |
| Modelo dimensional | `dimensional-model.mmd` | `dimensional-model.svg` | `dimensional-model.png` (3600×2520) |

Os diagramas refletem o estado real do repositório em 24/08/2026. Em particular:

- `FactIncidentLifecycle`, `FactSLA` e `BridgeIncidentTechnique` são carregadas de `data/expected`;
- `SOC_Analyst` restringe `DimAnalyst`/`FactIncidents`, mas não os fatos de eventos e alertas;
- a ponte incidente–técnica é a única relação bidirecional;
- as 27 relações físicas são representadas no diagrama dimensional;
- linhas tracejadas indicam dependências lógicas, não relacionamentos físicos.

Para regenerar os SVGs em uma ferramenta Mermaid compatível, use os arquivos `.mmd` como fonte e preserve o tema escuro e a legenda semântica. Os PNGs foram rasterizados dos SVGs com o conversor `sharp` já disponível no runtime do workspace; nenhuma dependência foi instalada no projeto.
