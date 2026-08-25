# Checklist de acessibilidade

Estado da revisão: validação estrutural aprovada; inspeção das evidências da release-base concluída; alto contraste, leitor de tela e recaptura pós-hardening permanecem manuais.

## Evidência automatizada

- [x] 101/101 visuais possuem `altText` não vazio.
- [x] `tabOrder` é inteiro, não negativo e sem duplicidade em cada página.
- [x] As dez páginas e os 91 estados mobile são JSON válido e pertencem ao inventário declarado.
- [x] Links e imagens locais da documentação resolvem dentro do repositório.
- [x] Largura mobile de 320 pontos e espaçamento vertical de oito pontos são determinísticos.

Comando:

```powershell
python -m unittest tests.test_project_quality -v
```

## Contraste calculado do tema

Relações calculadas conforme luminância relativa WCAG para pares usados no Signal Grid:

| Uso | Primeiro plano | Fundo | Relação |
|---|---|---|---:|
| Texto primário | `#E8EEF7` | `#0D1118` | 16,21:1 |
| Texto secundário | `#AEBBD0` | `#141B25` | 8,92:1 |
| Subtítulo | `#8FA0B8` | `#0D1118` | 7,10:1 |
| Ciano interativo | `#39C6E6` | `#0D1118` | 9,36:1 |
| Callout | `#F5F8FC` | `#111823` | 16,73:1 |
| Crítico textual | `#E5484D` | `#0D1118` | 4,83:1 |
| Atenção | `#F2B84B` | `#0D1118` | 10,57:1 |

Todos superam 4,5:1 para texto normal. O cálculo de cor não substitui inspeção de opacidade, antialiasing e estado real do Power BI.

## Evidência visual revisada

- [x] As dez capturas desktop da release-base foram abertas individualmente.
- [x] As dez capturas mobile da release-base foram abertas individualmente.
- [x] Severidade aparece em texto, não apenas por cor.
- [x] Gráficos principais possuem tabelas ou valores textuais equivalentes.
- [x] Conteúdo essencial não depende de tooltip customizado.
- [x] Ações principais de navegação, voltar, limpar e bookmark possuem rótulo e alt text.
- [x] Não há sobreposição nos layouts mobile versionados.
- [x] Oito páginas afetadas foram recapturadas após os acabamentos finais; os slicers exibem apenas títulos amigáveis e Data Quality/Methodology preservam o layout desktop.
- [ ] Recapturar e reinspecionar as dez páginas após as alterações de ordenação, rótulos e Methodology mobile.

Problemas encontrados na evidência-base:

- o valor de `Última atualização UTC` estava truncado no mobile de Data Quality;
- Methodology mobile tinha texto denso sobre fundo sem painel;
- a captura de Incident Drillthrough estava sem um único incidente filtrado;
- as capturas desktop mantinham uma faixa estreita do painel lateral do Desktop.

Os três primeiros receberam correção de definição. As páginas desktop afetadas foram recapturadas em `screenshots/reconcile-final-2026-08-25/`; a aprovação mobile final ainda depende de recaptura real no editor com dados carregados.

## Checklist manual exato

### Teclado

1. Abrir cada página no modo de consumo.
2. Pressionar `Tab` e confirmar ordem: título → ações/filtros → KPIs → gráficos → tabelas.
3. Acionar page navigator, `Limpar filtros`, `Estado padrão`, `Command Center` e `Metodologia` com `Enter` ou `Ctrl+Enter`, conforme o controle.
4. Confirmar foco visível em todas as ações.
5. Abrir o drillthrough por teclado a partir de um `IncidentId` e confirmar retorno.

### Alto contraste do Windows

1. Salvar o PBIP antes do teste; não descartar alterações existentes.
2. Ativar um tema de contraste do Windows manualmente em **Configurações → Acessibilidade → Temas de contraste**.
3. Reabrir ou atualizar o Power BI Desktop se necessário.
4. Percorrer as dez páginas e confirmar texto, foco, eixos, barras, seleção e estados de botão.
5. Registrar screenshots de pelo menos Command Center, Threat & MITRE, Data Quality e Methodology.
6. Desativar o tema manualmente ao terminar.

Esta revisão não altera configurações globais do Windows automaticamente e não declara esse gate aprovado.

### Leitor de tela

1. Usar Narrator ou NVDA em ambiente autorizado.
2. Percorrer todos os visuais de Command Center e Incident Drillthrough.
3. Confirmar anúncio de título, tipo do visual e alt text sem repetição inútil.
4. Abrir a tabela acessível de MITRE e conferir cabeçalhos/ordem.
5. Registrar diferenças entre Desktop e Service, caso publicado.

### Mobile real

1. Abrir o editor de layout mobile.
2. Revisar as dez páginas em 100% de zoom.
3. Confirmar timestamp completo em Data Quality e leitura confortável em Methodology.
4. Confirmar ausência de scroll interno evitável e espaço mínimo entre visuais.
5. Testar no aplicativo móvel após publicação autorizada.

## Critério de conclusão

O projeto só pode afirmar acessibilidade manual completa quando teclado, alto contraste, leitor de tela e recaptura pós-hardening tiverem data, versão do Desktop, evidência visual e resultado registrado. Até lá, a afirmação correta é: **acessibilidade estrutural aprovada; validações assistivas finais pendentes**.
