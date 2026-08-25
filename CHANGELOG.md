# Changelog

Todas as mudanças relevantes do EDY SOC Analytics serão registradas neste arquivo.

## [Unreleased]

### Added — 2026-08-24

- Estrutura inicial do projeto em pasta isolada.
- Checkpoints `PROJECT_STATE.md`, `NEXT_SESSION.md`, `DECISIONS.md` e `CHANGELOG.md`.
- Registro das primeiras decisões de isolamento, privacidade, modelagem e validação.
- Pesquisa oficial, integração EDY, dicionário, qualidade e linhagem.
- Contrato JSON Schema, validador local, amostras e CI.
- Gerador determinístico e dataset sintético em três camadas.

### Validated — 2026-08-24

- Escrita em `D:\EDY-Projects`.
- Disponibilidade local de Python, Node.js, npm, Git e GitHub CLI.
- 17 testes automatizados do contrato, dataset e segurança.

### Pre-execution checkpoint — 2026-08-24

- Power BI Desktop ausente; pacote oficial Microsoft 2.157.879.0 verificado no catálogo winget.
- Instalação oficial 64-bit autorizada pelo requisito do projeto e ainda não executada neste checkpoint.

### Added — 2026-08-24 (Power BI preparation)

- Power BI Desktop x64 2.157.879.0 instalado com hash oficial verificado.
- Expressões Power Query M, documentação dimensional, catálogo DAX, blueprint de páginas, acessibilidade, RLS e orçamento de desempenho.
- Tema, tokens, logo e capa originais Signal Grid.

### Not yet validated

- Abertura, refresh, round-trip, renderização e interações no Power BI Desktop.

### Power BI compatibility iteration — 2026-08-24

- PBIP, PBIR e TMDL gerados com dez páginas, 41 medidas, relações e papéis RLS.
- 16 arquivos JSON PBIR aprovados contra os schemas oficiais Microsoft.
- Três aberturas reais do PBIP executadas; corrigidos sintaxe M de listas, chave duplicada em `DimAttackTechnique` e caminho de filtro ambíguo do lifecycle.
- Construção de caminhos Power Query corrigida com separador Windows explícito por código de caractere.
- Referência duplicada de `DQ_RejectedRows` eliminada; 21 tabelas únicas confirmadas.
- Quarta abertura real do PBIP concluída sem diálogo de erro no Power BI Desktop.
- Suíte de 17 testes reexecutada e aprovada em 39,242 s.
- Refresh, round-trip, visuais e interações permanecem `BLOQUEADO` até os próximos testes no Desktop.

### Pre-execution data quality alignment — 2026-08-24

- Divergência estática entre o oracle e o Power Query encontrada antes do refresh.
- Decidido e implementado membro desconhecido `AssetKey = 0` para assets ausentes.
- Gerador, Power Query, teste automatizado e regra de qualidade atualizados; dataset e PBIP ainda precisam ser regenerados e retestados.
- Chaves de eventos, alertas e incidentes corrigidas para derivação determinística pelo ID, eliminando drift causado pela ordem embaralhada do raw.
- Analista ausente alinhado com membro desconhecido; filtro MITRE corrigido pela bridge controlada.

### Power BI refresh validation — 2026-08-24

- Refresh real concluído no Power BI Desktop sem avisos após configuração de privacy firewall limitada ao arquivo sintético.
- Modelo em memória validado por ADOMD: eventos, alertas, incidentes, unknown members, bridge MITRE e filtro por técnica conferidos.
- Medida `Registros rejeitados` corrigida para retornar zero em tabela vazia; segundo refresh ainda pendente.

### Power BI semantic-model round-trip — 2026-08-24

- PBIP salvo, fechado e reaberto no Power BI Desktop sem diálogo de erro ou aviso de refresh.
- Validador ADOMD executado novamente após a reabertura: 13/13 asserts aprovados.
- Confirmados 120.000 eventos, 18.000 alertas, 3.200 incidentes, zero rejeitados e propagação de filtro MITRE.
- Arquivos transitórios `.pbi`, incluindo `editorSettings.json`, mantidos fora do inventário Git.
- Próximo gate: implementação e renderização dos visuais PBIR e das interações.

### Pending

- Visuais, interações, RLS via `View as`, mobile, acessibilidade, desempenho, artefatos exportados, documentação final, auditoria e publicação.

### Report visual and mobile milestone — 2026-08-24

- Adicionado gerador PBIR auditável com 94 visuais nativos, tema registrado e dez páginas completas.
- Configurados 84 estados de layout mobile; cartões foram divididos para manter até três medidas por grupo e melhorar leitura em telas estreitas.
- CLI oficial Microsoft validou o PBIR com 0 erros e 0 avisos; bridge oficial recarregou o relatório no Desktop.
- Renderização desktop/mobile das dez páginas revisada visualmente e registrada em screenshots reais.
- Seleção cruzada, drillthrough filtrado e navegação por ação/teclado testados com sucesso.
- RLS `SOC_Manager` validado com visão integral; `SOC_Analyst` sem identidade correspondente validado como deny-by-default.
- Modelo em memória revalidado após regeneração: 13/13 asserts aprovados.
- Pendências reais: bookmark/reset, desempenho medido, recaptura final de screenshots, PBIX/PBIT/PDF, documentação final, auditoria e publicação.

### Final report validation — 2026-08-24

- Relatório ampliado para 101 visuais nativos e 91 estados mobile, com botões de restauração e ajuste tipográfico final.
- Bookmark real `Estado padrão SOC Operations` criado e validado; ações `ClearAllSlicers` adicionadas às páginas aplicáveis.
- Evidências finais desktop/mobile recapturadas e folhas de contato geradas.
- Medições finais aprovadas: maior p95 de consulta 8,16 ms; renderização total 17.400,69 ms e média 1.740,07 ms por página.
- PDF do relatório exportado novamente após atualização das tabelas calculadas: dez páginas limpas e revisadas.
- Relatório acadêmico A4 gerado em PDF com seis páginas e verificação visual completa.
- Documentação final atualizada, incluindo desempenho, acessibilidade, RLS e decisões arquiteturais.
- Tentativa real de exportação PBIX/PBIT documentada como não suportada pelo fluxo `Salvar como` do PBIP; nenhum artefato falso foi criado.
- Suite final aprovada: 18 testes automatizados, 13/13 asserts do modelo vivo e PBIR com 0 erros/0 avisos.

### Pre-Git checkpoint — 2026-08-24

- Construção, testes, evidências e documentação concluídos.
- Git ainda não inicializado; próximo gate é a auditoria de segredos/PII e do inventário staged antes da publicação.

### CI portability fix — 2026-08-24

- Geração JSON alterada para bytes UTF-8 com LF explícito, eliminando tradução de newline dependente do sistema operacional.
- Ordenação dos hashes do manifesto normalizada por `casefold`, preservando a mesma ordem em Windows e Linux.
- CSVs declarados com CRLF explícito no Git para corresponder ao `csv.DictWriter` em todos os runners.
- Actions oficiais atualizadas para `checkout@v7` e `setup-python@v7`, removendo o aviso de runtime Node.js obsoleto.
