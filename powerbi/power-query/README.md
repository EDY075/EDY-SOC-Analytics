# Power Query

As expressões M desta pasta são a fonte auditável das transformações. No PBIP, as mesmas expressões são armazenadas no modelo semântico TMDL.

## Ordem

1. `Parameters.m`
2. `Functions.m`
3. `Dimensions.m`
4. `FactSecurityEvents.m`
5. `FactAlerts.m`
6. `FactIncidents.m`
7. `Quality.m`

As queries `Stg_*` e funções auxiliares ficam sem carga. CSV não fornece query folding; as otimizações aplicadas são redução precoce de colunas, tipagem explícita e merges apenas após deduplicação.

