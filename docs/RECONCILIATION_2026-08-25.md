# Reconciliação segura de 25/08/2026

## Escopo

Esta entrega foi construída no worktree isolado `EDY-SOC-Analytics-RECONCILE`, no branch `codex/portfolio-10-reconcile`, a partir do commit `a846a2a8ff21d4ed4c1907c67487c53ec1d9582f`. O projeto original e os backups externos permaneceram fora do fluxo de edição.

## Decisões de reconciliação

- O hardening do commit-base foi preservado: 10 páginas, 101 visuais, 91 estados mobile, 21 tabelas, 41 medidas, 2 roles e 27 relacionamentos.
- As 46 melhorias geradas do hardening e os quatro arquivos-fonte correspondentes permaneceram presentes.
- Três alterações automáticas do Desktop foram analisadas separadamente: atualização de schema `visualContainer` de `2.9.0` para `2.12.0` e inclusão de `active: true` em slicers de `DimAnalyst[Team]` ou `DimDate[Year]`.
- Essas três alterações não foram incorporadas. O schema oficial `2.9.0` validou com zero erros/avisos; o endereço oficial `2.12.0` não estava publicado e tornava o gate de schema não reproduzível. `active: true` não demonstrou mudança funcional.
- A única correção funcional incorporada foi a leitura dos CSVs por uma fronteira única `Folder.Files(data)`, necessária para o refresh real não colidir com o firewall de privacidade do Power Query.
- Os validadores vivos passaram a exigir PID explícito quando duas instâncias do mesmo relatório estiverem abertas, impedindo validar ou atualizar a janela errada.

## Evidências executadas

- regeneração controlada: 276 arquivos antes/depois, zero hashes alterados na segunda execução;
- refresh vivo: 20/20 tabelas, 26,69 s;
- modelo vivo: 13/13 asserts;
- RLS vivo: cinco identidades aprovadas; paridade do filtro de produção aprovada; duas roles restantes após limpeza;
- desempenho: cinco consultas, cinco execuções aquecidas cada, maior p95 de 7,02 ms para orçamento de 2.000 ms;
- PBIR: validação estrutural e schema oficial com zero erros e zero avisos;
- desktop: dez páginas capturadas após refresh e revisadas visualmente;
- mobile: dez capturas existentes revisadas e 91 estados `mobile.json` validados estruturalmente;
- acessibilidade estrutural: 101 `altText` não vazios e `tabOrder` sem duplicidade por página.

Os resultados estruturados estão em `validation/results/`; as capturas desktop desta execução estão em `screenshots/reconcile-live-2026-08-25/`.

## Acabamentos finais

- Os nove slicers agora escondem o cabeçalho técnico redundante do campo e preservam o título amigável e o `altText` em português. Os aliases PBIR de `Year`, `YearMonth` e `Team` foram corrigidos para `Ano`, `Ano/mês` e `Equipe`.
- O valor de `Última atualização UTC` agora usa o formato curto e inequívoco `dd/MM/yy HH:mm "UTC"` e fonte de 10 pontos no card de Data Quality. O layout mobile permanece com 320 pontos de largura e 176 de altura, sem reticências e com o fuso explícito.
- O subtítulo e os seis painéis de Methodology passaram a usar cores secundárias mais claras (`#B8C6DA` e `#F1F5FA`), preservando o tema Signal Grid.
- A tabela vazia informa `Registros rejeitados — nenhum no período selecionado`; a mensagem foi confirmada na instância limpa.
- O inventário permaneceu em 10 páginas, 101 visuais e 91 estados mobile. Apenas o `formatString` de apresentação da medida de atualização foi alterado; expressão DAX, roles, relacionamentos e dados permaneceram intactos.

Uma nova instância limpa foi aberta no PBIP desta reconciliação, confirmada pelo bridge com `hasUnsavedChanges: false`, e recarregou somente os arquivos externos desta branch. Não houve novo refresh. Oito páginas afetadas foram recapturadas em `screenshots/reconcile-final-2026-08-25/`; a ausência de dados na instância limpa é indicada pelos banners do Desktop e não foi interpretada como regressão visual.

O acabamento de rótulos foi concluído no PBIR sem alterar o modelo semântico. O gerador agora usa `displayName`, propriedade específica de apresentação do schema, em todas as projeções de coluna e agregação. A recaptura viva confirmou cabeçalhos como `Incidente`, `Severidade`, `Status`, `Ativo`, `Risco`, `Analista`, `Equipe`, `Experiência`, `Produto-fonte`, `Sistema-fonte`, `Classificação`, `Etapa`, `Data/hora UTC` e `ID da técnica`. Um teste independente contém o mapa esperado em português e impede a volta das captions técnicas.

## Evidência interativa final

Os testes manuais com dados carregados produziram a seguinte evidência real:

- **navegação — aprovada:** Command Center → Methodology → Command Center;
- **cross-filter — aprovado:** a seleção de `2025-06` reduziu `Incidentes ativos` e `Backlog` de 253 para 22 e atualizou tabela e demais visuais;
- **drillthrough — aprovado:** `INC-00000001` abriu a página 9 com total 1, ativo sintético 067, risco 285, timeline e MITRE filtrados;
- **estado vazio — aprovado:** `Registros rejeitados — nenhum no período selecionado` foi exibido corretamente;
- **Methodology mobile — aprovado:** conteúdo legível, sem cortes ou sobreposição;
- **reset/bookmark — aguardando reteste após correção:** antes da correção, `Limpar filtros` não removia a seleção do gráfico nem restaurava os cartões de 22 para 253, inclusive com Ctrl+clique;
- **timestamp mobile — aguardando reteste após correção:** antes da correção, o valor aparecia truncado como `31/07/2026 23:...`;
- **teclado — inconclusivo:** após clicar no canvas e pressionar Tab três vezes, não surgiu foco visível.

A causa do reset foi confirmada no PBIR: o botão usava `ClearAllSlicers`, ação que não restaura seleções de pontos de dados em gráficos. Ele agora aponta para o bookmark determinístico `Estado padrão Command Center`, com `Data` representado pelo estado sem seleção de todos os visuais de dados, página ativa `CommandCenter`, slicer e projeções capturados. O teste regressivo verifica ação habilitada, tipo, referência existente, registro no catálogo, cobertura dos visuais e ausência de referência quebrada. A posição de teclado do botão permanece `tabOrder: 3`; o navegador de páginas e os botões essenciais continuam presentes na ordem estrutural, mas o foco visível ainda requer novo teste manual.

Gates finais desta correção: `tests.test_project_quality` aprovou 9/9; `tests.test_security` aprovou 5/5; PBIR estrutural e schema oficial retornaram 0 erros/0 avisos; a suíte completa conclusiva aprovou 28/28 em 38,721 s. A primeira chamada da suíte perdeu a cauda do resultado no transporte do PTY e foi repetida uma vez para obter exit code verificável; o resultado estruturado registra as duas tentativas sem ocultá-las. O inventário permaneceu em 10 páginas, 101 visuais, 91 estados mobile, 21 tabelas, 41 medidas, 2 roles e 27 relacionamentos. Os testes de manifesto e seed confirmaram novamente os dados e hashes determinísticos.

## Limitações registradas sem sobredeclaração

- O reset por bookmark e o timestamp mobile corrigidos ainda exigem reteste manual com dados carregados; não há captura pós-correção inventada.
- A navegação básica por teclado continua inconclusiva: o contrato de `tabOrder` está válido, mas o foco visível não foi demonstrado manualmente.
- RLS no Power BI Service, associação de grupos e comportamento por licença continuam dependentes de um tenant autorizado.

## Próxima decisão

O branch de reconciliação é o candidato recomendado para revisão técnica porque preserva o hardening, resolve o refresh local real e acrescenta gates vivos seguros. Qualquer merge, push, tag, release ou publicação deve ocorrer apenas após autorização explícita e revisão dos commits locais.
