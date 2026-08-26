# EDY SOC Analytics — Estado do projeto

Atualizado em: 2026-08-26 (America/Sao_Paulo)

## Estado executivo

- Repositório público: `EDY075/EDY-SOC-Analytics`.
- Release pública atual: `v1.1.0` no commit de merge `c5e52b3`.
- Branch reconciliada: `codex/portfolio-10-reconcile`, incorporada à `main` por merge normal.
- CI pós-merge aprovado em Linux e Windows.
- Esta preparação altera somente documentação e materiais do LinkedIn; nenhuma release existente foi modificada e nenhuma publicação foi realizada.
- O repositório permanece sem arquivo de licença.

## Inventário validado

| Item | Quantidade |
|---|---:|
| Páginas | 10 |
| Visuais nativos | 101 |
| Estados mobile | 91 |
| Tabelas TMDL | 21 |
| Medidas DAX | 41 |
| Relacionamentos | 27 |
| Papéis RLS | 2 |
| Eventos / alertas / incidentes | 120.000 / 18.000 / 3.200 |

## Validações concluídas

- 28/28 testes portáteis aprovados.
- Inventário PBIR/TMDL aprovado sem divergências.
- Refresh vivo de 20/20 tabelas aprovado em 29,07 s.
- Modelo vivo aprovado em 13/13 asserts.
- RLS vivo aprovado para três equipes, gerente e identidade sem mapeamento.
- PBIR estrutural e schemas oficiais aprovados com 0 erros e 0 avisos.
- Nove interações manuais aprovadas, incluindo navegação, cross-filter, drillthrough, bookmark de limpeza e foco por teclado no escopo testado.
- 101/101 visuais com texto alternativo e ordem de tabulação válida.
- Scanner de segredos, PII, caminhos pessoais e arquivos proibidos aprovado.
- CI pós-merge da `main` concluído com sucesso.

Resultados estruturados: `validation/results/`. Evidências visuais finais: `screenshots/reconcile-final-2026-08-25/`.

## Limitações confirmadas

- dados sintéticos demonstram comportamento plausível; não estimam risco real;
- RLS de analista restringe incidentes, lifecycle, SLA e MITRE por equipe, mas eventos e alertas permanecem globais;
- lifecycle, SLA e bridge MITRE usam atualmente tabelas curadas de `data/expected`;
- Power BI Service, associação de grupos aos papéis e comportamento por licença não foram validados;
- alto contraste e leitor de tela não foram executados interativamente;
- a captura pública principal de Drillthrough mostra o estado completo; a evidência filtrada está registrada no resultado de validação manual;
- `pProjectRoot` precisa ser ajustado após clone em outro caminho.

## Estado para portfólio

A release pública `v1.1.0` está aprovada para apresentação como projeto independente de portfólio, desde que as limitações acima sejam preservadas e não se alegue experiência profissional como analista SOC.
