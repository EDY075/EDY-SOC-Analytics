# Integração conceitual com o ecossistema EDY

## Escopo desta sprint

O EDY SOC Analytics é um consumidor analítico autônomo. Não acessa bancos de outros produtos, não modifica o EDY SIEM e não importa logs reais. A integração futura ocorre por exportação versionada CSV/JSON, validada por adapter local.

```text
EDY Shield ─┐
EDY Sentinel├─> EDY SIEM ─> contrato v1 ─> adapter ─> staging ─> modelo analítico
EDY RECON ──┘
```

## Auditoria segura realizada

Foram localizados, em modo somente leitura, EDY SIEM v0.3.0 e EDY Shield v2.3.0. EDY Sentinel e EDY RECON não estavam presentes na pasta solicitada. Nenhum `.env`, banco, log, backup, credencial ou dado pessoal foi acessado.

Padrões preservados conceitualmente:

- Pipeline `RawEvent → ParsedEvent → CanonicalEvent → EnrichedEvent → Correlation → Detection → Alert → Incident → Case`.
- `trace_id` e `correlation_id` para rastreabilidade futura.
- Adapter de entrada, outbox/inbox e idempotência.
- Separação entre `event_timestamp` e `received_at`.
- Vocabulário de alertas, incidentes, SLA, risco, regra, MITRE e ativo.

## Contrato analítico v1

Arquivo normativo: `contracts/edy-siem-export.schema.json`.

O envelope contém versão, identificador de exportação, geração, produto-fonte, classificação e registros. Cada registro contém apenas atributos necessários à análise. `safeSummary` é texto sintético e não operacional; payloads, evidências, comandos, hashes reais e credenciais não fazem parte do contrato.

O contrato é deliberadamente menor que os modelos internos do EDY SIEM. O objetivo é reduzir acoplamento e risco de drift. Campos de máquina usam inglês; rótulos do relatório usam português.

## Idempotência e tempo

- Chave de negócio do export: `exportId`.
- Chave de registro: prefixo tipado + oito dígitos no demonstrador.
- Em integração real, a deduplicação deve considerar produto/instância + ID do evento e hash canônico, não apenas o ID.
- Timestamps são ISO 8601 com offset/UTC.
- Atraso de ingestão é calculado entre ocorrência e recebimento.
- Eventos fora de ordem devem ser aceitos dentro de watermark documentado.

## Adapter local

`validation/contract_validator.py` valida amostras sem dependências externas. A amostra válida deve produzir lista vazia; a inválida deve produzir múltiplos erros. O adapter nunca executa conteúdo recebido.

## Contrato CSV futuro

O CSV deverá possuir um arquivo por entidade, cabeçalho UTF-8, timestamps ISO 8601, delimitador vírgula e manifesto com SHA-256. A versão 1 usará as mesmas restrições semânticas do JSON. Mudanças incompatíveis exigem nova major version.

## Riscos e controles

| Risco | Controle |
|---|---|
| Drift frontend/backend | JSON Schema como fonte normativa e testes de contrato |
| Reprocessamento | Dedupe idempotente e hash canônico |
| PII em evidência | Allowlist de campos; dados sintéticos; scanner automatizado |
| Severidade da origem ≠ risco analítico | Preservar severidade de origem e versionar regra de risco |
| Linha de atualização ≠ incidente único | Estado atual e lifecycle separados |
| Métricas legadas ambíguas | Recalcular do evento-base com relógios documentados |

