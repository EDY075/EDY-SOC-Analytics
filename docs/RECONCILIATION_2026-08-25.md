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
- O valor de `Última atualização UTC` foi reduzido de 14 para 12 pontos para caber no card mobile de Data Quality sem alterar o layout de 320 pontos.
- O subtítulo e os seis painéis de Methodology passaram a usar cores secundárias mais claras (`#B8C6DA` e `#F1F5FA`), preservando o tema Signal Grid.
- A tabela vazia informa `Registros rejeitados — nenhum no período selecionado`; a mensagem foi confirmada na instância limpa.
- O inventário permaneceu em 10 páginas, 101 visuais e 91 estados mobile. Nenhum TMDL, medida DAX, role, relacionamento ou dado foi alterado.

Uma nova instância limpa foi aberta no PBIP desta reconciliação, confirmada pelo bridge com `hasUnsavedChanges: false`, e recarregou somente os arquivos externos desta branch. Não houve novo refresh. Oito páginas afetadas foram recapturadas em `screenshots/reconcile-final-2026-08-25/`; a ausência de dados na instância limpa é indicada pelos banners do Desktop e não foi interpretada como regressão visual.

O acabamento de rótulos permanece parcialmente pendente: títulos de slicer e aliases PBIR estão amigáveis, porém o Desktop continua renderizando captions técnicas em alguns cabeçalhos de tabelas (`AnalystLabel`, `ExperienceBand`, `SourceProduct` etc.). Corrigi-los integralmente exigiria alterar captions do modelo semântico ou reconstruir as tabelas; isso excede o escopo visual seguro desta etapa e acionaria nova validação live.

## Evidência interativa final

O arquivo `validation/results/interaction-validation.json` registra origem, ação, resultado esperado, observado, evidência e status das seis interações. A navegação real entre páginas foi aprovada pelo Desktop bridge e pelas capturas correspondentes. Drillthrough, cross-filter, bookmark, reset de filtros e foco visível por teclado ficaram inconclusivos: a instância limpa não possuía linhas carregadas e o driver de entrada atingiu o limite combinado de uma abordagem por acessibilidade e uma alternativa por captura. Nenhuma interação foi aprovada apenas pelo contrato estático.

Gates finais: `tests.test_project_quality` aprovou 7/7; `tests.test_security` aprovou 5/5; PBIR estrutural e schema oficial retornaram 0 erros/0 avisos; a suíte completa aprovou 26/26 em 41,388 s. Após o último ajuste de cabeçalho de slicer, o teste afetado e os dois gates PBIR foram repetidos e permaneceram aprovados; a suíte completa não foi executada uma segunda vez.

## Limitações registradas sem sobredeclaração

- O driver de entrada do Windows não conseguiu executar com segurança cliques no Power BI Desktop. Drillthrough, bookmark, navegação por teclado, reset e cross-filter foram confirmados apenas por contrato PBIR, não por interação automatizada nesta sessão.
- As capturas mobile são evidências do hardening já preservado; o editor mobile não foi recapturado ao vivo nesta sessão.
- A correção de tamanho do timestamp de Data Quality mobile foi validada estruturalmente, mas não recapturada com um valor vivo porque a instância limpa não foi atualizada.
- Methodology desktop foi recapturada com o contraste novo; a confirmação mobile viva permanece manual.
- Alguns nomes técnicos continuam visíveis somente em cabeçalhos de tabelas; os cabeçalhos técnicos dos slicers foram removidos.
- RLS no Power BI Service, associação de grupos e comportamento por licença continuam dependentes de um tenant autorizado.

## Próxima decisão

O branch de reconciliação é o candidato recomendado para revisão técnica porque preserva o hardening, resolve o refresh local real e acrescenta gates vivos seguros. Qualquer merge, push, tag, release ou publicação deve ocorrer apenas após autorização explícita e revisão dos commits locais.
