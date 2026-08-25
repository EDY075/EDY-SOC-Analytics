# EDY SOC Analytics — Registro de Decisões

Atualizado em: 2026-08-24

## ADR-001 — Isolamento total do projeto

- Estado: aceito.
- Decisão: todos os artefatos do produto ficam em `D:\EDY-Projects\EDY-SOC-Analytics`.
- Razão: impedir impacto nos projetos EDY existentes.
- Consequência: integrações desta sprint serão contratuais e demonstrativas; nenhum projeto-fonte será modificado.

## ADR-002 — Dados inteiramente sintéticos

- Estado: aceito.
- Decisão: usar gerador determinístico com seed fixa e endereços reservados/documentais quando algum identificador de rede for necessário.
- Razão: privacidade, segurança, reprodutibilidade e CI.
- Consequência: nenhum banco ou log real do ecossistema EDY será lido ou copiado.

## ADR-003 — Modelo estrela e filtros unidirecionais por padrão

- Estado: aceito.
- Decisão: fatos de granularidade explícita, dimensões conformadas e pontes somente para many-to-many justificado.
- Razão: clareza semântica, desempenho e alinhamento com a orientação oficial do Power BI.

## ADR-004 — Checkpoints no disco são a fonte oficial

- Estado: aceito.
- Decisão: os quatro arquivos de checkpoint são atualizados em marcos, pré/pós etapas longas e antes de Git/Power BI.
- Razão: continuidade independente do histórico da conversa.

## ADR-005 — Veracidade de validação

- Estado: aceito.
- Decisão: usar `VALIDADO` somente após execução e aprovação do teste correspondente.
- Razão: preservar rastreabilidade acadêmica e profissional.

## ADRs pendentes

- Formato exato PBIP/PBIR/TMDL suportado pela versão local do Power BI Desktop.
- Volume final do dataset após orçamento de desempenho.
- Estratégia de materialização dos dados esperados e de execução dos testes DAX.

## ADR-006 — Instalação oficial do Power BI Desktop

- Estado: aceito.
- Decisão: instalar a versão Microsoft 64-bit 2.157.879.0, publicada em 19/08/2026 e verificada via winget com SHA-256 divulgado pelo catálogo.
- Razão: o usuário exigiu artefatos reais, round-trip e validação visual; o aplicativo estava ausente.
- Consequência: criar checkpoint pré/pós instalação e não declarar PBIP/PBIR/TMDL validado antes de abrir e salvar no Desktop.

Resultado: instalado e confirmado em 24/08/2026. O aplicativo ainda não foi aberto neste checkpoint.

## ADR-007 — PBIP como fonte auditável e round-trip obrigatório

- Estado: aceito.
- Decisão: manter PBIR/TMDL gerados em texto como fonte auditável, validar contra schemas oficiais e exigir abertura, refresh e salvamento reais no Desktop antes de qualquer marcação `VALIDADO`.
- Razão: arquivos sintaticamente válidos não comprovam compatibilidade semântica nem funcionamento.
- Evidência atual: três aberturas reais identificaram e permitiram corrigir erros de sintaxe M, chave primária e caminho de filtro ambíguo.

## ADR-008 — Caminhos Windows em Power Query

- Estado: aceito.
- Decisão: o parâmetro `pProjectRoot` mantém barras simples e `fxCsv` usa `Character.FromNumber(92)` para normalizar separadores.
- Razão: Power Query M não usa a barra invertida como caractere de escape; duplicá-la cria um caminho inválido.

## ADR-009 — Asset ausente usa membro desconhecido

- Estado: aceito.
- Decisão: eventos com `asset_id` ausente permanecem no fato com `AssetKey = 0`, ligado ao membro `Ativo não informado`; somente chave de evento, timestamp ou severidade irrecuperáveis entram em `DQ_RejectedRows`.
- Razão: preservar a contagem de eventos e demonstrar tratamento dimensional explícito, sem inventar a identidade do ativo.
- Consequência: alertas e incidentes sintéticos são gerados somente a partir de eventos com ativo conhecido, mantendo KPIs e integridade referencial coerentes entre raw, Power Query e oracle.

## ADR-010 — Chaves substitutas reprodutíveis no ETL

- Estado: aceito.
- Decisão: `EventKey`, `AlertKey` e `IncidentKey` são derivados do sufixo numérico dos IDs sintéticos, nunca da ordem física do CSV.
- Razão: os arquivos raw são deliberadamente embaralhados; índices posicionais corromperiam silenciosamente relações com lifecycle, SLA e MITRE.
- Consequência: o Power Query reproduz as chaves do oracle independentemente da ordem de entrada.

## ADR-011 — Analista ausente e filtro MITRE

- Estado: aceito.
- Decisão: analista ausente usa `DimAnalyst[AnalystKey] = 0` (`Não atribuído`) no raw, oracle, lifecycle e Power Query. A relação Incident–Technique é bidirecional somente na ponte controlada.
- Razão: preservar totais gerenciais/RLS e permitir que tática/técnica filtre as medidas de incidente sem criar uma segunda rota no modelo.
- Consequência: usuários analistas não recebem incidentes não atribuídos; o gerente recebe todos. Medidas de incidente por técnica passam a respeitar o contexto MITRE.

## ADR-012 — Privacy firewall limitado ao arquivo sintético

- Estado: aceito com restrição.
- Decisão: manter a origem `d:\` classificada como `Privado`; para este PBIP, permitir `Ignorar os Níveis de Privacidade` somente no escopo do arquivo atual.
- Razão: todas as fontes são CSVs sintéticos do mesmo projeto local e o firewall do Power Query bloqueou combinações internas entre staging/dimensões, apesar de existir uma única origem física privada.
- Controles: nenhuma fonte externa, banco real, rede ou dado privado é combinado; a configuração não é global e deve ser removida antes de conectar qualquer origem real.
- Evidência: após a configuração file-scoped, 21 tabelas foram carregadas sem erro e as contagens foram validadas no modelo em memória.

## ADR-013 — Round-trip como gate do modelo semântico

- Estado: aceito e validado.
- Decisão: considerar modelo, Power Query e DAX validados somente após salvar, fechar, reabrir e repetir as consultas automatizadas no modelo em memória.
- Razão: a primeira carga não comprova persistência nem compatibilidade serializada do PBIP/TMDL.
- Evidência: o projeto reabriu sem erro e `validation/validate_live_model.ps1` aprovou novamente os 13 asserts, incluindo rejeitados igual a zero e filtro MITRE.

## ADR-014 — Visuais nativos e geração PBIR auditável

- Estado: aceito para execução.
- Decisão: priorizar visuais nativos do Power BI e gerar as definições PBIR em texto pelo gerador do projeto, preservando versões de schema compatíveis com o Desktop instalado.
- Razão: auditabilidade, portabilidade, segurança e ausência de dependências externas desnecessárias.
- Gate: nenhum visual ou interação será marcado como validado antes de renderização e teste real no Desktop.

## ADR-015 — Composição visual e layout mobile

- Estado: aceito e validado.
- Decisão: usar somente visuais nativos, cartões com no máximo três KPIs por contêiner e layout mobile explícito sem navegador horizontal de páginas.
- Razão: legibilidade, acessibilidade, desempenho e auditabilidade no PBIR.
- Evidência: 94 visuais renderizados em desktop, 84 estados mobile e validação oficial com zero erros/avisos.

## ADR-016 — RLS demonstrativa verificável

- Estado: aceito parcialmente.
- Decisão: validar `SOC_Manager` com visão integral e `SOC_Analyst` sem identidade correspondente como deny-by-default; não alegar simulação de equipe específica enquanto o campo `Outro usuário` não aceitar a identidade fictícia de forma confiável.
- Evidência: `SOC_Manager` exibiu 3.200 incidentes; `SOC_Analyst` sem correspondência não exibiu linhas.
- Limitação: teste de um analista fictício específico permanece pendente.

## ADR-017 — Restauração de filtros com ações nativas

- Estado: aceito e validado.
- Decisão: usar um bookmark real para restaurar o estado padrão da página SOC Operations e ações `ClearAllSlicers` nas demais páginas aplicáveis.
- Razão: combinar uma demonstração verificável de bookmark com uma ação nativa simples e resistente a mudanças dos filtros.
- Evidência: a seleção testada reduziu alertas de 18 mil para 2 mil; `Ctrl+Enter` no botão restaurou 18 mil. O PBIR final possui 101 visuais e 91 estados mobile.

## ADR-018 — Orçamento de desempenho baseado em medição

- Estado: aceito e validado.
- Decisão: registrar tempos obtidos por scripts reproduzíveis, sem estimativas substituindo medições.
- Evidência final: maior p95 de consulta de 8,16 ms; renderização integral de 17.400,69 ms e média de 1.740,07 ms por página.
- Artefatos: `validation/results/performance.json` e `validation/results/render-performance.json`.

## ADR-019 — Não fabricar PBIX/PBIT

- Estado: aceito.
- Decisão: manter o PBIP auditável como fonte oficial e declarar PBIX/PBIT indisponíveis quando o fluxo real de `Salvar como` não os produzir.
- Razão: o Desktop criou um segundo projeto `.pbip` e suas pastas, não um arquivo binário PBIX/PBIT. Renomear ou simular esse resultado violaria o gate de veracidade.
- Controle: a tentativa foi movida para `archive/failed-pbix-export`, excluída do inventário público.

## ADR-020 — Dois PDFs com finalidades distintas

- Estado: aceito e validado.
- Decisão: entregar o PDF visual exportado pelo Power BI e um relatório acadêmico A4 gerado a partir da documentação.
- Razão: preservar tanto a evidência fiel das dez páginas do dashboard quanto a narrativa técnica adequada para avaliação acadêmica e recrutamento.
- Evidência: ambos foram renderizados página a página e revisados visualmente; o PDF do Power BI tem dez páginas e o acadêmico seis.

## ADR-021 — Publicação segura e reprodutível

- Estado: aceito e validado.
- Decisão: publicar somente após testes locais, inventário de segredos/PII, revisão do stage e CI Linux com regeneração do dataset seguida de `git diff --exit-code`.
- Razão: impedir vazamento de artefatos locais e provar que o dataset determinístico é idêntico entre Windows e Linux.
- Evidência: o primeiro CI detectou diferenças de newline/ordenação; a geração foi corrigida com bytes LF explícitos para JSON, CRLF explícito para CSV e ordenação `casefold`. O workflow subsequente passou integralmente.
- Repositório: `https://github.com/EDY075/EDY-SOC-Analytics`, público, sem licença e sem force push.

## ADR-022 — Release imutável sobre snapshot validado

- Estado: aceito e validado.
- Decisão: criar `v1.0.0` somente após o CI verde do checkpoint técnico/documental e anexar os dois PDFs revisados.
- Razão: a tag identifica exatamente o snapshot reproduzível aprovado, enquanto registros pós-release podem evoluir na branch `main` sem reescrever a tag.
- Evidência: `v1.0.0` aponta para `53386f3285a8b328b03f803b784e15b4c3adc531` e está publicada com os dois artefatos PDF.
