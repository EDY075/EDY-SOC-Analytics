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

## Limitações registradas sem sobredeclaração

- O driver de entrada do Windows não conseguiu executar com segurança cliques no Power BI Desktop. Drillthrough, bookmark, navegação por teclado, reset e cross-filter foram confirmados apenas por contrato PBIR, não por interação automatizada nesta sessão.
- As capturas mobile são evidências do hardening já preservado; o editor mobile não foi recapturado ao vivo nesta sessão.
- A página mobile Data Quality elide o timestamp de última atualização na largura estreita.
- A página mobile Methodology mantém contraste secundário mais baixo e espaçamento vertical amplo.
- Alguns nomes técnicos de campos continuam visíveis em slicers e cabeçalhos. Não foram reintroduzidos pela reconciliação; já pertenciam ao commit-base preservado.
- A tabela vazia de registros rejeitados não apresenta mensagem explicativa quando o total é zero.
- RLS no Power BI Service, associação de grupos e comportamento por licença continuam dependentes de um tenant autorizado.

## Próxima decisão

O branch de reconciliação é o candidato recomendado para revisão técnica porque preserva o hardening, resolve o refresh local real e acrescenta gates vivos seguros. Qualquer merge, push, tag, release ou publicação deve ocorrer apenas após autorização explícita e revisão dos commits locais.
