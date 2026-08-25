# Guia de reprodução e validação

Este procedimento parte de uma cópia nova do repositório e separa abertura do artefato versionado, regeneração determinística e validações que dependem do Power BI Desktop. Não exige credenciais nem Power BI Service.

## Versões e pré-requisitos

| Componente | Requisito |
|---|---|
| Sistema para geração/testes | Windows, Linux ou macOS com Python 3.11+ |
| Versão usada no CI | Python 3.12 |
| Dependências Python | biblioteca padrão; o projeto não requer pacote externo para dataset e testes |
| Power BI | Power BI Desktop para Windows com suporte a PBIP, PBIR e TMDL |
| Versão registrada no modelo | `2.157.879.0 (26.08)` |
| PBIP/PBIR/modelo | PBIP 1.0, report definition 4.0 e semantic model definition 4.2 |
| Validador PBIR | comando opcional `powerbi-report-author`, quando já disponível no ambiente |

O Power BI Service é necessário somente para publicar, atribuir grupos aos papéis e testar RLS no tenant. Essas operações não fazem parte da reprodução local.

## 1. Obter uma cópia limpa

Via Git:

```powershell
git clone https://github.com/EDY075/EDY-SOC-Analytics.git
cd EDY-SOC-Analytics
git status --short
```

Ou baixe o ZIP do repositório, extraia-o e abra um terminal na pasta que contém `pyproject.toml`. O caminho pode ser escolhido pelo usuário; nenhum arquivo deve depender de uma cópia antiga em outro volume.

Confirme o ambiente:

```powershell
python --version
python -c "import pathlib; print(pathlib.Path.cwd().resolve())"
```

## 2. Entender as fontes

```text
generator/config.json        seed, período, volumes e classificação
data/raw/                    inconsistências controladas
data/reference/              dimensões e autorização fictícia
data/expected/               oracle e tabelas curadas auxiliares
powerbi/*.pbip               ponto de entrada do Desktop
powerbi/*.SemanticModel/     TMDL, Power Query, medidas e roles
powerbi/*.Report/            PBIR, páginas, visuais, bookmark e mobile
tests/                       testes portáteis
validation/                  consultas ao modelo vivo e desempenho
```

`FactSecurityEvents`, `FactAlerts` e `FactIncidents` são transformadas de `data/raw/` pelo Power Query. `FactIncidentLifecycle`, `FactSLA` e `BridgeIncidentTechnique` carregam os CSVs curados de `data/expected/`. Consulte `docs/DATA_LINEAGE.md`.

## 3. Regenerar somente o dataset

O gerador usa seed fixa `75075`, timezone `America/Sao_Paulo` e parâmetros de `generator/config.json`.

```powershell
python generator/generate_dataset.py
git diff -- data
```

Uma execução correta reproduz contagens e hashes do manifesto. Em uma árvore limpa, `git diff -- data` deve ficar vazio. Se houver diferença, não a descarte automaticamente: registre Python, sistema, arquivo divergente e hash antes de investigar.

## 4. Executar testes portáteis

```powershell
python -m unittest discover -s tests -v
```

A suíte verifica determinismo, contagens, deduplicação, membros desconhecidos, integridade referencial, lifecycle, SLA, MITRE, manifesto, KPIs, contrato, links e controles básicos de segurança. Ela não substitui validação viva de DAX, RLS, PBIR ou inspeção visual.

Para reproduzir o mesmo gate do CI:

```powershell
python validation/project_inventory.py
python generator/generate_dataset.py
python -m unittest discover -s tests -v
python validation/verify_clean_tree.py
```

## 5. Abrir o PBIP versionado

Abra no Power BI Desktop:

```text
powerbi/EDY SOC Analytics.pbip
```

O relatório referencia o modelo por caminho relativo (`../EDY SOC Analytics.SemanticModel`). As fontes CSV usam o parâmetro de texto `pProjectRoot`.

Em uma pasta diferente daquela gravada no parâmetro:

1. abra **Transformar dados → Gerenciar parâmetros**;
2. defina `pProjectRoot` como a raiz atual do clone, isto é, a pasta que contém `data/`;
3. aplique as alterações e atualize;
4. não grave caminhos de perfil pessoal em documentação ou screenshots;
5. revise o diff TMDL antes de versionar qualquer alteração.

`fxCsv` enumera uma única fronteira de privacidade com `Folder.Files(pProjectRoot & "\\data")` e então resolve o caminho completo esperado com comparação exata e guarda de unicidade. Isso evita combinar várias fontes dinâmicas `File.Contents` no firewall de privacidade, sem aceitar arquivos fora de `data/`.

## 6. Reconstruir PBIP/PBIR por código, quando necessário

`generator/generate_pbip.py` reescreve artefatos gerados do relatório e do modelo, inclusive o parâmetro de raiz. Use-o apenas em worktree limpa, sem alterações não salvas no Desktop, e sempre revise o diff.

```powershell
git status --short
python generator/generate_dataset.py
python generator/generate_pbip.py
git diff --stat
git diff -- powerbi
```

Esse fluxo serve para testar a capacidade de reconstrução. Ele não deve ser usado para apagar ajustes manuais aprovados, e diferenças não devem ser aceitas sem validar bookmark, mobile, interações, tema e modelo.

## 7. Validar PBIR estaticamente

Quando `powerbi-report-author` estiver instalado no ambiente:

```powershell
powerbi-report-author validate "powerbi/EDY SOC Analytics.Report" --no-schema --pretty
powerbi-report-author validate "powerbi/EDY SOC Analytics.Report" --pretty
```

O primeiro comando é o gate estrutural offline e deve retornar zero erros e zero avisos. O segundo consulta os schemas oficiais: o critério ideal também é zero/zero, mas falha de resolução ou bloqueio de rede deve ser registrado separadamente como `PBIR_SCHEMA_UNREACHABLE`, sem atribuí-lo ao relatório. Sem a ferramenta, registre o gate como pendente; abrir o relatório sem erro não equivale a validar todos os schemas PBIR.

## 8. Validar o modelo vivo

Com o relatório aberto e atualizado no Power BI Desktop, execute no Windows:

```powershell
powershell -ExecutionPolicy Bypass -File validation/refresh_live_model.ps1
powershell -ExecutionPolicy Bypass -File validation/validate_live_model.ps1
powershell -ExecutionPolicy Bypass -File validation/validate_live_rls.ps1 -IdentityMode EphemeralCustomData
```

Os scripts localizam a instância e o workspace Analysis Services sem registrar PID ou porta na documentação. Quando houver duas instâncias com o mesmo título, use `-DesktopPid <PID>` em cada comando; sem esse parâmetro, a ambiguidade falha de forma fechada. Quando título de janela ou WMI não estão acessíveis, o fallback só é aceito se houver exatamente uma instância e um workspace recentes.

`refresh_live_model.ps1` processa as tabelas sequencialmente, registra tempo e falha na primeira tabela problemática. `validate_live_model.ps1` compara eventos, alertas, incidentes, lifecycle, ponte, SLA, membros desconhecidos, rejeições e propagação MITRE. `validate_live_rls.ps1` testa gerente, três equipes e identidade sem mapeamento, incluindo o escopo parcial esperado: incidentes/lifecycle/MITRE/SLA por equipe e eventos/alertas globais.

O modo padrão `EffectiveUserName` é a prova preferida quando o engine local aceita os UPNs fictícios. Se o Desktop Windows rejeitar `example.invalid` antes de avaliar RLS, o modo `EphemeralCustomData` cria temporariamente, apenas na memória, uma role de validação cujo filtro é comparado ao filtro de produção e troca somente `USERPRINCIPALNAME()` por `CUSTOMDATA()` para injetar a identidade. O script remove a role no bloco `finally`; depois da execução, confirme que o modelo vivo continua com apenas `SOC_Analyst` e `SOC_Manager`. Essa técnica valida a lógica e as contagens locais, mas não substitui a atribuição de usuários e grupos no Power BI Service.

## 9. Medir desempenho

Ainda com o relatório aberto:

```powershell
powershell -ExecutionPolicy Bypass -File validation/measure_performance.ps1
```

O resultado fica em `validation/results/performance.json`. Compare p50/p95 e status com `docs/PERFORMANCE_BUDGET.md`; não substitua resultados por números manuais. Cache, versão do Desktop e host devem acompanhar a evidência.

## 10. Validar interações e experiência visual

No Desktop, registre versão e execute:

1. Command Center: selecione severidade e confirme cross-filter; limpe e confirme restauração;
2. abra o drillthrough a partir de um `IncidentId` e confirme contexto de uma linha;
3. SOC Operations: altere o estado, acione `Estado padrão` e confirme o bookmark;
4. Command Center: use teclado para navegar até Methodology;
5. percorra as dez páginas em desktop, verificando corte, contraste, ordem, rótulos e tabelas;
6. abra o editor mobile e revise as dez páginas, sem inferir qualidade apenas dos JSONs;
7. teste `Exibir como` conforme `docs/RLS_SECURITY.md`;
8. se alto contraste ou tecnologia assistiva não puder ser testado, marque explicitamente como pendente.

As capturas aprovadas ficam em `screenshots/desktop-final/` e `screenshots/mobile-final-true/`. Uma nova captura só substitui evidência anterior após revisão visual.

A automação de captura pode validar renderização, mas não comprova por si só cliques, drillthrough, bookmark, foco por teclado ou cross-filter. Se o driver de entrada do Windows estiver indisponível, mantenha esses itens explicitamente pendentes e valide apenas o contrato estático de ações, filtros de drillthrough, bookmarks, `altText`, `tabOrder` e layouts mobile.

## 11. Exportar por fluxo suportado

PDF do relatório deve ser criado pelo comando de exportação do Power BI Desktop. PBIX e PBIT só devem ser entregues quando o Desktop oferecer e concluir um fluxo oficial de salvamento/exportação.

Não renomeie PBIP para PBIX/PBIT, não compacte pastas para simular binários e não alegue exportação sem abrir o arquivo produzido. Se o Desktop não oferecer o formato a partir do projeto PBIP, documente a limitação.

## 12. Critérios finais de reprodução

- árvore limpa depois da regeneração determinística;
- suíte portátil aprovada;
- PBIR com zero erros/avisos, quando o validador estiver disponível;
- modelo vivo com todas as asserções aprovadas;
- desempenho dentro do orçamento, sem regressão relevante;
- dez páginas desktop e mobile inspecionadas visualmente;
- RLS descrito conforme seu escopo parcial, sem alegar identidades não testadas;
- nenhum `.env`, banco local, segredo ou dado operacional no inventário;
- nenhuma exportação binária fabricada.

## Limitações de portabilidade

- Power BI Desktop e os scripts de modelo vivo são específicos de Windows;
- `pProjectRoot` precisa apontar para a raiz atual do clone;
- medições variam por host e cache;
- associação de papéis e RLS real no Service dependem de tenant autorizado;
- ações manuais devem ser registradas separadamente de testes automatizados.
