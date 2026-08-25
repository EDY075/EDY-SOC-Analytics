# EDY SOC Analytics — Estado do projeto

Atualizado em: 2026-08-25 (America/Sao_Paulo)

## Estado executivo

- Repositório público existente: `EDY075/EDY-SOC-Analytics`.
- Release imutável existente: `v1.0.0` no commit `53386f3`.
- Branch local de trabalho: `codex/portfolio-10-hardening`.
- Main local e remota não foram reescritas.
- Nenhum push, merge, release ou publicação foi realizado nesta revisão.
- Nenhum arquivo de licença foi adicionado.
- Cinco commits funcionais e um ajuste de checkpoint foram criados somente na branch local.

## Inventário atual

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

## Implementado nesta branch

- documentação realinhada ao PBIR/TMDL executável;
- guia funcional das dez páginas e reprodução desde clone limpo;
- arquitetura e modelo dimensional em Mermaid, SVG e PNG;
- capa profissional e roteiro de demonstração;
- relatório acadêmico ampliado e gerador PDF reprodutível;
- suíte expandida para inventário, alt text, tab order, links e segurança;
- CI Windows/Linux com verificação de tracked e untracked;
- validador RLS vivo por identidade;
- parse seguro de timestamps inválidos;
- ordenação semântica, rótulos amigáveis e ajustes mobile de legibilidade.

## Validações concluídas

- 23/23 testes Python aprovados na execução da frente de CI.
- Inventário 10/101/91/21/41/2 aprovado.
- Alt text 101/101 e tab order sem duplicidade aprovados.
- Links Markdown locais e scanner de segurança aprovados.
- As 10 capturas desktop e as 10 mobile da release-base foram abertas e revisadas.
- Diagramas e capa foram inspecionados em resolução original.
- PBIR aprovado offline com 0 erros e 0 avisos; a tentativa com schemas remotos terminou com 0 erros e 10 avisos de rede.
- PDF acadêmico de 9 páginas renderizado e revisado página a página após correção das referências.
- O Power BI Desktop aberto foi confirmado pela árvore de acessibilidade, incluindo 10 páginas, dados carregados e aviso de alterações externas.

## Validações pendentes

- aplicar as alterações externas no Desktop e concluir refresh/round-trip;
- repetir `validate_live_model.ps1`, `validate_live_rls.ps1` e performance em uma sessão com autenticação local ao engine ADOMD;
- validar PBIR com schemas oficiais quando a rede permitir;
- recapturar e reinspecionar as 10 páginas desktop/mobile pós-hardening;
- validar teclado novamente e executar alto contraste/leitor de tela manualmente.

## Limitações confirmadas

- RLS de analista protege incidentes/lifecycle/SLA/MITRE por equipe, mas não eventos/alertas;
- lifecycle, SLA e bridge carregam tabelas curadas de `data/expected`;
- `pProjectRoot` precisa ser ajustado após clone em outro caminho;
- a captura pública de Drillthrough não mostra um único incidente filtrado;
- a medição de 8,16 ms é maior valor observado em cinco amostras, não p95 robusto;
- alto contraste, leitor de tela e Service não foram validados nesta branch.

## Decisões que exigem autorização

1. Redesigned RLS para isolamento integral de eventos, alertas e incidentes.
2. Nova origem raw para lifecycle, SLA e bridge MITRE.
3. Qualquer push, merge, release, publicação ou reescrita de histórico.

## Power BI Desktop

Versão instalada: `2.157.879.0`. A janela `EDY SOC Analytics` está aberta e foi lida pela árvore acessível. A sessão automatizada não conseguiu capturar a janela (`SetIsBorderRequired`/`Access denied`), clicar em **Apply external changes** nem autenticar no engine ADOMD iniciado fora do sandbox. Nenhum processo foi encerrado e nenhum estado foi salvo ou descartado.
