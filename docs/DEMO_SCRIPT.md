# Roteiro de demonstração — 75 segundos

Objetivo: apresentar valor, profundidade técnica e limites do EDY SOC Analytics sem acelerar a leitura nem exibir dados pessoais.

## 0–10 s — proposta

**Tela:** capa do README e Command Center.

> “Este é o EDY SOC Analytics: um produto Power BI de Blue Team que transforma eventos, alertas e incidentes sintéticos em decisões operacionais auditáveis.”

## 10–25 s — prioridade

**Tela:** Command Center. Selecionar uma severidade e limpar o filtro.

> “O Command Center prioriza incidentes ativos e críticos, backlog, SLA, MTTD e MTTR. A seleção cruzada permite partir do resumo para a fila de investigação.”

## 25–38 s — operação e detecção

**Tela:** SOC Operations e Detection Engineering.

> “A operação conecta volume, conversão e fidelidade. Em Detection Engineering, regras com alto volume e falso positivo viram candidatas a tuning, sem confundir ruído com cobertura.”

## 38–52 s — investigação

**Tela:** Threat & MITRE e drillthrough filtrado por um `IncidentId`.

> “O contexto ATT&CK mostra táticas e técnicas observadas. Pelo drillthrough, um incidente reúne ativo, regra, risco, timeline e MITRE em uma única trilha investigativa.”

## 52–65 s — engenharia e confiança

**Tela:** diagrama de arquitetura e Data Quality.

> “A solução é versionada em PBIP, PBIR e TMDL, usa 21 tabelas, 41 medidas e dados determinísticos. Testes validam dataset, contrato, segurança, inventário, alt text e links.”

## 65–75 s — segurança e fechamento

**Tela:** documentação RLS/Methodology.

> “O projeto é honesto sobre limites: o RLS atual restringe incidentes por equipe, enquanto eventos e alertas permanecem globais. Essa transparência faz parte da qualidade técnica, não de uma nota de rodapé.”

## Checklist de gravação

- usar 1920×1080, zoom legível e cursor lento;
- ocultar painel de filtros e qualquer caminho local antes de gravar;
- não mostrar e-mails, perfis, notificações ou outras janelas;
- usar apenas capturas com dados classificados `SYNTHETIC_DEMO_DATA`;
- abrir o drillthrough a partir de uma linha para que o detalhe mostre um único incidente;
- não afirmar publicação, alto contraste, leitor de tela ou RLS integral sem evidência.
