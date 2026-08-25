# EDY SOC Analytics

![Signal Grid - EDY SOC Analytics](screenshots/desktop-final/1.%20Command%20Center.png)

Camada analítica profissional de SOC construída em Power BI para o ecossistema conceitual **EDY Shield → EDY Sentinel → EDY SIEM → EDY SOC Analytics**, com contribuição do **EDY RECON**. O projeto combina engenharia de dados, modelagem dimensional, DAX, visualização, segurança e documentação para demonstrar competências de Power BI/PL-300 e Blue Team.

Todos os registros são **sintéticos, determinísticos e seguros**. Nenhum banco, log, segredo ou evidência operacional dos projetos EDY existentes foi utilizado.

## O problema

Operações de SOC precisam transformar grande volume de telemetria em decisões: o que exige atenção agora, onde o backlog cresce, quais ativos concentram risco, quais detecções geram ruído e quanto tempo cada etapa de resposta consome. O EDY SOC Analytics organiza essas perguntas em uma narrativa de dez páginas, do resumo executivo ao detalhe do incidente e à metodologia.

## Demonstração

| Desktop | Mobile |
|---|---|
| [Visão das 10 páginas](screenshots/desktop-contact-sheet-final.png) | [Layouts mobile reais](screenshots/mobile-contact-sheet-final.png) |

Interações verificadas no Power BI Desktop:

- seleção cruzada: a seleção de incidentes críticos alterou `Incidentes ativos` de 253 para 7 e a limpeza restaurou 253;
- drillthrough: uma linha do Command Center abriu o detalhe filtrado de um único incidente, com timeline e MITRE;
- bookmark/reset: uma seleção reduziu alertas de 18 mil para 2 mil e `Estado padrão` restaurou 18 mil;
- navegação por ação e teclado: Command Center → Methodology;
- RLS: `SOC_Manager` visualizou as 3.200 linhas; `SOC_Analyst` sem identidade correspondente recebeu zero linhas (deny-by-default).

## Arquitetura

```text
Gerador Python (seed fixa)
  ├─ data/raw          CSVs com inconsistências controladas
  ├─ data/reference    dimensões de referência
  └─ data/expected     oracle para testes
          ↓
Power Query M parametrizado
          ↓
Modelo estrela TMDL (21 tabelas, 41 medidas, 2 papéis RLS)
          ↓
PBIR Signal Grid (10 páginas, 101 visuais nativos, layout mobile)
```

O modelo usa fatos de eventos, alertas, incidentes, lifecycle e SLA, dimensões conformadas e ponte controlada incidente-técnica MITRE. A direção de filtro é unidirecional por padrão; a ponte MITRE é a exceção documentada.

## Dataset sintético

- 120.000 eventos;
- 18.000 alertas;
- 3.200 incidentes;
- 18.034 transições de ciclo de vida;
- 4.000 vínculos incidente-técnica MITRE;
- 18 meses de histórico;
- seed fixa e manifesto com hashes;
- sazonalidade, picos, backlog, violações de SLA, regras ruidosas, nulls e duplicidades controladas.

## Páginas

1. **Command Center** — prioridades, backlog, SLA, MTTD, MTTR e tendência.
2. **SOC Operations** — volume, conversão, fontes e regras ruidosas.
3. **Incident Lifecycle** — relógios separados, aging e SLA.
4. **Threat & MITRE** — táticas, técnicas e cobertura observada.
5. **Assets & Exposure** — criticidade, risco acumulado e concentração.
6. **Detection Engineering** — sinal, ruído, fidelidade e ajuste de regras.
7. **Analyst & SLA** — carga contextualizada, sem ranking simplista.
8. **Data Quality** — completude, validade, rejeições e linhagem.
9. **Incident Drillthrough** — contexto, timeline, ativo, regra e MITRE.
10. **Methodology** — definições, ética, segurança, limites e fontes.

## Power Query e DAX

O ETL em M executa tipagem, limpeza, padronização, tratamento de null, deduplicação, normalização de severidades/status, geração de chaves e validação de qualidade. O caminho é parametrizado por `pProjectRoot`; staging e funções ficam separados das tabelas carregadas.

As 41 medidas cobrem volume, conversão, backlog, SLA, falsos positivos, reaberturas, escalonamentos, MTTD, MTTA, triagem, contenção, resolução, recuperação, tendência, período anterior, MITRE, risco de ativos e qualidade. Consulte [DAX_MEASURES.md](docs/DAX_MEASURES.md).

## Identidade Signal Grid

Interface original em dark graphite, superfícies discretas, ciano técnico, âmbar para atenção e vermelho apenas para crítico. Foram usados somente visuais nativos, com tema JSON registrado, grid consistente, alt text, títulos descritivos, ordem de tabulação e tabelas equivalentes aos gráficos.

## Mobile, acessibilidade e segurança

- 10 layouts mobile configurados e revisados no editor móvel real;
- 91 estados mobile; navegadores horizontais são omitidos para legibilidade;
- contraste, rótulos, alt text, foco, ordem de tabulação e alternativas tabulares;
- papéis `SOC_Analyst` e `SOC_Manager` no TMDL;
- dados marcados `SYNTHETIC_DEMO_DATA`;
- nenhum segredo, `.env`, log privado ou caminho pessoal no inventário público.

## Desempenho medido

Cinco consultas DAX representativas foram executadas no modelo local com cinco repetições aquecidas. O maior p95 da execução final foi **8,16 ms**, abaixo do orçamento interno de 2.000 ms. A captura/navegação das dez páginas pelo Desktop Bridge levou 17,40 s no total, média de **1.740,07 ms por página**. Esses números são medições locais, não SLAs da Microsoft.

Resultados: `validation/results/performance.json` e `validation/results/render-performance.json`.

## Como executar

Pré-requisitos: Python 3.12+ para geração/testes e Power BI Desktop com suporte a PBIP/PBIR/TMDL para abrir o relatório.

```powershell
cd D:\EDY-Projects\EDY-SOC-Analytics
python generator\generate_dataset.py
python generator\generate_pbip.py
python -m unittest discover -s tests -v
```

Abra [EDY SOC Analytics.pbip](powerbi/EDY%20SOC%20Analytics.pbip) no Power BI Desktop. O parâmetro `pProjectRoot` pode ser ajustado sem editar as demais queries.

Validações com o relatório aberto:

```powershell
validation\validate_live_model.ps1
validation\measure_performance.ps1
powerbi-report-author validate "powerbi\EDY SOC Analytics.Report" --pretty
```

## Estrutura

```text
contracts/     contrato EDY SIEM e amostras
data/          raw, reference, expected e manifesto
docs/          pesquisa, modelo, DAX, segurança e relatório acadêmico
generator/     dataset, PBIP/PBIR e PDF
powerbi/       PBIP, PBIR, TMDL e Power Query
screenshots/   evidências desktop/mobile
tests/         suíte segura e determinística
validation/    validadores e medições locais
theme/         design system Signal Grid
```

## Testes e CI

```powershell
python -m unittest discover -s tests -v
```

A suíte cobre determinismo, schemas, tipos, chaves, integridade referencial, lifecycle, SLA, MITRE, PII/segredos, KPIs esperados, contrato EDY SIEM e links. O GitHub Actions regenera o dataset e exige árvore limpa; não depende do Power BI Desktop nem de credenciais.

## Limitações

- o dataset demonstra comportamento plausível, não representa risco real;
- Power BI Service não foi usado e nenhuma credencial foi configurada;
- o teste `Outro usuário` para uma identidade fictícia específica não foi concluído; acesso integral de gerente e deny-by-default do analista foram validados;
- tempos variam por host, versão do Desktop e cache;
- PBIX/PBIT/PDF do relatório visual são listados somente quando exportados de modo real.

## Documentação

- [Relatório acadêmico](docs/RELATORIO_ACADEMICO.md)
- [Relatório acadêmico em PDF](output/pdf/RELATORIO_ACADEMICO.pdf)
- [Exportação real do relatório Power BI em PDF](output/pdf/EDY_SOC_ANALYTICS_REPORT.pdf)
- [Pesquisa e benchmark](docs/RESEARCH_BENCHMARK.md)
- [Modelo dimensional](docs/DIMENSIONAL_MODEL.md)
- [Integração EDY](docs/EDY_ECOSYSTEM_INTEGRATION.md)
- [Segurança e RLS](docs/RLS_SECURITY.md)
- [Acessibilidade](docs/ACCESSIBILITY_CHECKLIST.md)
- [Performance](docs/PERFORMANCE_BUDGET.md)

## Roadmap

- conectar export real do EDY SIEM após contrato e autorização;
- publicar em workspace controlado e atribuir papéis RLS no serviço;
- incorporar atualização incremental e monitoramento de qualidade;
- validar com tecnologia assistiva e usuários finais.

Autor: **Edmilson Gomes** · GitHub: **EDY075**
