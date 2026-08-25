# Linhagem do dataset

```mermaid
flowchart LR
  G[Gerador Python\nseed 75075] --> R[data/raw\ninconsistências controladas]
  G --> Ref[data/reference\ndimensões seguras]
  G --> E[data/expected\noracle de testes]
  R --> S[Power Query staging\nsem carga]
  Ref --> S
  S --> Q[Limpeza e conformação]
  Q --> M[Modelo estrela\nTMDL]
  M --> D[DAX]
  D --> P[Relatório Signal Grid]
  E --> V[Validação automatizada]
  V --> M
```

## Rastreabilidade

- Configuração: `generator/config.json`.
- Código: `generator/generate_dataset.py`.
- Manifesto, contagens e SHA-256: `data/dataset_manifest.json`.
- Contrato de exportação: `contracts/edy-siem-export.schema.json`.
- Power Query: `powerbi/power-query/*.m` e expressões no modelo semântico.
- Modelo: `powerbi/EDY SOC Analytics.SemanticModel/definition/`.
- Medidas: catálogo em `docs/DAX_MEASURES.md` e TMDL.

