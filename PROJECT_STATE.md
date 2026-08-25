# EDY SOC Analytics — Estado do Projeto

Atualizado em: 2026-08-24 (America/Sao_Paulo)

## Fase atual

Validação final do relatório — PBIP/PBIR/TMDL, refresh, modelo em memória, 94 visuais nativos, layouts desktop/mobile e interações essenciais foram validados no Power BI Desktop. O próximo gate é concluir bookmarks/reset, desempenho medido, artefatos exportados, documentação e publicação.

## Progresso aproximado

| Fase | Progresso | Estado |
|---|---:|---|
| 1. Pesquisa, auditoria segura e contratos | 100% | VALIDADO |
| 2. Dados sintéticos e qualidade | 100% | VALIDADO |
| 3. Modelo dimensional, Power Query e DAX | 100% | VALIDADO |
| 4. Relatório Power BI e interações | 85% | VALIDADO parcialmente |
| 5. Acessibilidade, RLS, mobile e desempenho | 70% | VALIDADO parcialmente |
| 6. Documentação, auditoria e publicação | 15% | IMPLEMENTADO parcialmente |

## PLANEJADOS

- Pesquisa oficial e benchmark documentado.
- Contrato EDY SIEM, amostras e validador.
- Gerador determinístico e três camadas de dados.
- Modelo estrela, ETL Power Query, medidas DAX e relatório Power BI.
- RLS, acessibilidade, layout mobile e medições de desempenho.
- Documentação acadêmica, PDF, screenshots, CI e publicação GitHub.

## IMPLEMENTADOS

- Escrita em `D:\EDY-Projects` confirmada com arquivo temporário criado e removido.
- Estrutura inicial de diretórios criada exclusivamente em `D:\EDY-Projects\EDY-SOC-Analytics`.
- Auditorias read-only e pesquisa oficial iniciadas em frentes separadas.
- Ferramentas-base detectadas: Python 3.12.10, Node.js 24.17.0, npm 11.13.0, Git 2.55.0 e GitHub CLI 2.97.0.
- Regras reforçadas de checkpoint incorporadas.
- Contrato JSON Schema, adapter e amostras válidas/inválidas implementados.
- Gerador determinístico criou 120.000 eventos, 18.000 alertas e 3.200 incidentes em 18 meses.
- Pesquisa oficial, integração, dicionário, qualidade e linhagem documentados.
- Power Query M, modelo dimensional, catálogo DAX, blueprint e design system implementados em arquivos auditáveis.
- Power BI Desktop x64 2.157.879.0 instalado pela fonte oficial Microsoft; hash do instalador verificado pelo winget.
- Projeto PBIP com dez páginas, modelo TMDL, funções Power Query, 41 medidas DAX e dois papéis RLS gerado em `powerbi/`.
- Schemas PBIR oficiais validados para 16 arquivos JSON.
- Três tentativas reais de abertura no Power BI Desktop executadas; foram corrigidos a sintaxe M da lista de colunas, chave duplicada em `DimAttackTechnique` e o caminho ambíguo entre lifecycle, incidentes e analistas.
- Caminho M portátil corrigido para usar `Character.FromNumber(92)` sem duplicar separadores.
- Duplicação de `DQ_RejectedRows` removida; o modelo possui 21 referências únicas para 21 arquivos de tabela.
- Tratamento de asset ausente alinhado por membro dimensional desconhecido (`AssetKey = 0`) no gerador e no Power Query.
- Analista ausente alinhado por membro desconhecido (`AnalystKey = 0`); bridge MITRE usa filtro bidirecional controlado.
- Validador reproduzível do modelo em memória criado em `validation/validate_live_model.ps1`.
- PBIP salvo, fechado e reaberto pelo Power BI Desktop; modelo pós-round-trip consultado novamente com sucesso.
- Arquivos transitórios `.pbi` locais protegidos no `.gitignore`, incluindo `editorSettings.json`.
- Gerador PBIR auditável em `generator/pbir_visuals.py` com 94 visuais nativos em dez páginas, tema Signal Grid registrado, alt text e ordem de tabulação.
- Layout mobile configurado em todas as dez páginas com 84 estados de visuais; navegadores de página foram omitidos intencionalmente do mobile para preservar legibilidade.
- CLI oficial Microsoft de autoria e bridge do Power BI Desktop instaladas e usadas para validar/recarregar o projeto.

## VALIDADO

- Permissão de escrita na pasta pai: teste real aprovado.
- Pasta raiz resolvida como `D:\EDY-Projects\EDY-SOC-Analytics`.
- Contrato, determinismo, contagens, integridade referencial, lifecycle, SLA, MITRE, hashes, segurança e classificação sintética: 17 testes aprovados.
- Estrutura JSON PBIR: 16 arquivos aprovados contra schemas oficiais Microsoft.
- Abertura limpa do PBIP no Power BI Desktop 2.157.879.0: aprovada, sem diálogo de erro após 15 segundos.
- Refresh Power Query real: aprovado após configuração de privacidade restrita ao arquivo sintético; avisos e erros desapareceram.
- Modelo em memória consultado via ADOMD: 120.000 eventos, 18.000 alertas, 3.200 incidentes, 693 eventos com asset desconhecido, 16 incidentes sem analista e 4.000 linhas MITRE confirmados.
- Filtro MITRE validado em contexto: técnica com 247 linhas filtrou exatamente 247 incidentes, abaixo do total global.
- Medida `Registros rejeitados` validada com resultado numérico zero.
- Round-trip real: PBIP salvo no Desktop, aplicativo fechado, projeto reaberto sem erros e os 13 asserts do validador ADOMD aprovados novamente.
- `powerbi-report-author validate`: 0 erros e 0 avisos após a regeneração final dos visuais.
- Renderização desktop e mobile das dez páginas revisada visualmente; screenshots reais existem em `screenshots/desktop/` e `screenshots/mobile/`.
- Seleção cruzada validada: selecionar a barra Crítico alterou `Incidentes ativos` de 253 para 7 e limpar retornou a 253.
- Drillthrough validado da tabela do Command Center para `9. Incident Drillthrough`, filtrando o detalhe para um incidente e sua timeline.
- Navegação por ação validada do Command Center para `10. Methodology` por foco UIA e `Ctrl+Enter`.
- RLS `SOC_Manager` validado por `Exibir como`: cartão de total permaneceu em 3.200 incidentes. `SOC_Analyst` sem identidade correspondente foi validado como deny-by-default (sem linhas).
- Validador do modelo em memória reexecutado após a última regeneração: 13/13 asserts aprovados.

## BLOQUEADO

- Bookmarks/reset de filtros e tooltips dedicados permanecem `BLOQUEADO` até implementação e teste real.
- Simulação RLS de um analista específico por e-mail fictício permanece `BLOQUEADO` por limitação da caixa `Outro usuário`; o papel, filtro TMDL, acesso gerencial e deny-by-default foram testados.
- PBIX, PBIT e PDF permanecem `BLOQUEADO` até exportação real no Desktop. Screenshots existem, mas o conjunto final deve ser recapturado após o último ajuste tipográfico mobile.
- Desempenho permanece `BLOQUEADO` até medição reproduzível e registro dos tempos.

## Testes realmente executados

1. Criação e remoção de arquivo temporário em `D:\EDY-Projects`: aprovado.
2. Detecção das versões de Python, Node.js, npm, Git e GitHub CLI: aprovado.
3. `python -m unittest discover -s tests -v`: 17 testes aprovados em 38,153 s.
4. Instalação Power BI Desktop 2.157.879.0 e presença do executável oficial: aprovado.
5. Validação JSON PBIR contra schemas oficiais Microsoft: 16 arquivos aprovados.
6. Três aberturas iniciais do PBIP: executadas; cada uma encontrou erro semântico específico, corrigido no gerador.
7. Quarta abertura real após correções: PBIP aberto com título `EDY SOC Analytics`, sem diálogo de erro.
8. `python -m unittest discover -s tests -v`: 18 testes aprovados em 38,119 s após ADRs 009–011.
9. Refresh real do Power BI Desktop: aprovado; 21 tabelas carregadas sem aviso ou erro.
10. Consulta ADOMD no modelo em memória: 13/13 asserts aprovados, incluindo contagens, desconhecidos, rejeitados igual a zero e filtro MITRE.
11. Save/close/reopen no Power BI Desktop: aprovado, sem erro de abertura ou aviso de refresh.
12. Validação ADOMD pós-reabertura: 13/13 asserts aprovados.
13. Validação oficial PBIR após implementação: 0 erros e 0 avisos.
14. Renderização das dez páginas em desktop e mobile: executada e revisada visualmente.
15. Cross-filter Crítico: 253 → 7 → 253, aprovado.
16. Drillthrough para um incidente: aprovado, com detalhe e timeline filtrados.
17. Navegação por botão para Methodology: aprovada por teclado.
18. RLS `SOC_Manager`: 3.200 incidentes; `SOC_Analyst` sem identidade: zero linhas, comportamento deny-by-default aprovado.
19. `validation\validate_live_model.ps1` após regeneração visual: 13/13 asserts aprovados.

## Artefatos existentes

- Estrutura de diretórios do projeto.
- `PROJECT_STATE.md`, `NEXT_SESSION.md`, `DECISIONS.md` e `CHANGELOG.md`.

## Limitações conhecidas

- O último ajuste de callout mobile (18 pt) foi regenerado e recarregado, mas o conjunto de screenshots finais ainda precisa ser recapturado.
- Não houve ainda medição do Performance Analyzer; nenhuma alegação de tempo será feita antes da medição.
- A opção de ignorar níveis de privacidade está limitada ao arquivo atual e só é aceitável enquanto todas as fontes forem CSVs sintéticos locais da mesma origem.

## Dependências pendentes

- Concluir a auditoria pré-Git, inicializar o repositório, publicar no GitHub e validar o workflow de CI.

## Checkpoint final pré-Git — 2026-08-24

### VALIDADO

- Relatório completo com dez páginas, 101 visuais nativos, 91 estados mobile, tema original e navegação acessível.
- Bookmark real `Estado padrão SOC Operations`: seleção alterou alertas de 18 mil para 2 mil e o acionamento restaurou 18 mil. As demais páginas receberam ações nativas `ClearAllSlicers`.
- Screenshots finais das dez páginas em desktop e no editor mobile real, com folhas de contato em `screenshots/desktop-contact-sheet-final.png` e `screenshots/mobile-contact-sheet-final.png`.
- Desempenho automatizado final: maior p95 de consulta igual a 8,16 ms; renderização integral medida em 17.400,69 ms, média de 1.740,07 ms por página.
- PDF real do relatório exportado pelo Power BI, atualizado e revisado: dez páginas sem o aviso de atualização.
- Relatório acadêmico A4 gerado e revisado visualmente: seis páginas.
- Suite final: 18 testes aprovados; modelo vivo 13/13; CLI PBIR 0 erros e 0 avisos; performance aprovada.

### LIMITAÇÕES HONESTAS

- A identidade fictícia específica do papel `SOC_Analyst` não pôde ser digitada de forma confiável em `Outro usuário`; foram validados o acesso integral do gerente e o comportamento deny-by-default do analista sem correspondência.
- O modo de alto contraste do sistema não foi executado nesta estação; contraste, texto alternativo, ordem de tabulação, teclado e layout mobile foram implementados e revisados.
- O fluxo real `Salvar como` do projeto PBIP criou outro projeto PBIP, e não arquivos PBIX/PBIT. A duplicata foi movida para `archive/failed-pbix-export`; nenhum artefato falso será apresentado.

### PRÓXIMO GATE

- Inventário de segredos/PII e arquivos transitórios, inicialização Git, publicação pública em `EDY075/EDY-SOC-Analytics`, execução do CI e release `v1.0.0`.

## Checkpoint pós-publicação — 2026-08-24

- Auditoria pré-Git aprovada: somente identidades fictícias `example.invalid`; nenhum segredo, `.env`, banco, token, caminho pessoal ou arquivo Power BI transitório foi publicado.
- Repositório público criado: `https://github.com/EDY075/EDY-SOC-Analytics`.
- Branch padrão: `main`; commit técnico validado: `4e71a45590b177707208e64ed4bcda77096fa814`.
- CI `Safe validation` aprovado no Linux com regeneração do dataset, 18 testes e árvore reproduzível limpa.
- Portabilidade corrigida com newline explícito e ordenação case-insensitive determinística entre Windows e Linux.
- Nenhuma licença adicionada, conforme requisito.
- Gate restante: validar o commit deste checkpoint e publicar a release `v1.0.0`.
