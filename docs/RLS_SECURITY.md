# Segurança e RLS demonstrativa

## Escopo efetivamente implementado

O modelo possui dois papéis TMDL:

- `SOC_Analyst`: filtra `DimAnalyst` pelas equipes associadas ao UPN fictício em `SecurityAccess`;
- `SOC_Manager`: papel estático de leitura sem filtro de linha e, portanto, com visão integral.

O filtro dinâmico de `SOC_Analyst` é:

```DAX
VAR CurrentUPN = LOWER ( USERPRINCIPALNAME () )
RETURN
    DimAnalyst[Team]
        IN CALCULATETABLE (
            VALUES ( SecurityAccess[Team] ),
            FILTER ( SecurityAccess, LOWER ( SecurityAccess[UPN] ) = CurrentUPN )
        )
```

Os UPNs publicados pertencem ao domínio reservado `example.invalid`, são sintéticos e não identificam pessoas reais.

## Fronteira de segurança

O RLS de analista protege o **domínio centrado em incidentes**. O filtro aplicado a `DimAnalyst` alcança `FactIncidents` pela relação ativa em `AnalystKey` e, a partir do incidente, alcança `FactIncidentLifecycle`, `FactSLA` e `BridgeIncidentTechnique`.

`SecurityAccess` não possui relacionamento físico com `DimAnalyst`; ela é consultada pela expressão DAX da role. `FactSecurityEvents` e `FactAlerts` não possuem `AnalystKey` nem outra rota de propagação da equipe. Consequentemente, no estado atual:

- incidentes, lifecycle, SLA e vínculos MITRE são restritos por equipe;
- eventos e alertas continuam globais sob `SOC_Analyst`;
- medidas baseadas em alertas, como MTTD e falso positivo, continuam globais;
- medidas baseadas em incidentes, como MTTA, MTTR e SLA, respeitam a equipe;
- `SecurityAccess` não recebe filtro próprio e não deve ser apresentada em visuais.

Portanto, “deny-by-default” significa **zero linhas no domínio de incidentes para um UPN sem correspondência**, e não ausência de dados em todo o modelo. Ocultar páginas ou visuais não seria um controle de segurança.

## Matriz de resultado esperado

As contagens abaixo são o oracle estático derivado dos CSVs versionados. Elas devem ser confirmadas no modelo vivo por conexão com `Roles` e `EffectiveUserName`, ou pelo fluxo `Exibir como` do Power BI Desktop.

O script `validation/validate_live_rls.ps1` automatiza os cinco cenários e compara incidentes, lifecycle, ponte MITRE, SLA, eventos, alertas e medidas de volume. Ele só produz aprovação depois de consultar o modelo vivo; indisponibilidade de autenticação local mantém o gate pendente.

| Papel e identidade fictícia | Equipe | Analistas | Incidentes | Lifecycle | Ponte MITRE | SLA | Eventos | Alertas |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `SOC_Analyst` + `analyst.blue-a@example.invalid` | Blue-A | 6 | 1.060 | 6.006 | 1.371 | 1.060 | 120.000 | 18.000 |
| `SOC_Analyst` + `analyst.blue-b@example.invalid` | Blue-B | 6 | 1.037 | 5.817 | 1.281 | 1.037 | 120.000 | 18.000 |
| `SOC_Analyst` + `analyst.blue-c@example.invalid` | Blue-C | 6 | 1.087 | 6.124 | 1.328 | 1.087 | 120.000 | 18.000 |
| `SOC_Analyst` + UPN sem correspondência | nenhuma | 0 | 0 | 0 | 0 | 0 | 120.000 | 18.000 |
| `SOC_Manager` + qualquer membro atribuído à role | todas | 19 | 3.200 | 18.034 | 4.000 | 3.200 | 120.000 | 18.000 |

Os 16 incidentes associados ao membro `Unassigned` não pertencem às equipes Blue-A, Blue-B ou Blue-C e não aparecem nas visões dos três analistas.

## Procedimento reproduzível

1. Abra o PBIP e atualize o modelo.
2. Em **Modelagem → Exibir como**, selecione uma única role.
3. Para `SOC_Analyst`, informe uma identidade fictícia em **Outro usuário** quando o Desktop/tenant aceitar a simulação.
4. Confira `COUNTROWS` de `DimAnalyst`, `FactIncidents`, `FactIncidentLifecycle`, `BridgeIncidentTechnique` e `FactSLA` contra a matriz.
5. Confira separadamente `FactSecurityEvents` e `FactAlerts`; no desenho atual elas devem permanecer globais.
6. Para uma identidade Blue-A, filtre explicitamente `DimAnalyst[Team] = "Blue-B"`; o resultado de incidentes deve ser zero.
7. Execute `CALCULATE ( COUNTROWS ( FactIncidents ), REMOVEFILTERS ( DimAnalyst ) )`; RLS não deve ser removido e o total deve continuar limitado à equipe.
8. Teste um UPN sem correspondência; o domínio de incidentes deve retornar zero.
9. Teste `SOC_Manager`; os totais devem corresponder à linha gerencial.
10. Saia de **Exibir como** e registre versão do Desktop, identidade fictícia, role, data e resultados, sem capturar contas reais.

## Evidência obtida até a versão 1.0.0

| Cenário | Resultado obtido | Estado |
|---|---|---|
| `Exibir como: SOC_Manager` | 3.200 incidentes | validado no Desktop |
| `Exibir como: SOC_Analyst` sem identidade correspondente | zero incidentes | validado no Desktop |
| identidade fictícia específica em `Outro usuário` | o campo não aceitou o valor de modo confiável | pendente; não alegado como validado |

Os totais específicos Blue-A, Blue-B e Blue-C são resultados esperados, ainda não evidência de execução viva. O relatório foi retirado do modo `Exibir como` após o teste registrado.

## Power BI Service e governança

- RLS restringe consumidores com função Viewer; Admin, Member e Contributor do workspace não são limitados por RLS.
- A coluna `RoleName` de `SecurityAccess` é metadado demonstrativo; a autorização de `SOC_Manager` depende da associação operacional da role no Service.
- Papéis são cumulativos. Um usuário associado simultaneamente a `SOC_Manager` e `SOC_Analyst` recebe a união permissiva e, neste modelo, visão integral.
- Conceder Build, Analyze in Excel ou exportação amplia a superfície de consulta. `SecurityAccess` deve ser ocultada/filtrada antes de uso operacional.
- Atribuição de role, grupos Entra ID, princípio do menor privilégio e testes pós-publicação são responsabilidades de implantação.

## Decisão necessária antes de dados reais

Há duas opções válidas, mas elas não são equivalentes:

1. manter RLS apenas no domínio de incidentes e declarar eventos/alertas como telemetria global; ou
2. criar uma chave de escopo/equipe também para eventos e alertas, com relações sem caminhos ambíguos, para obter isolamento integral.

A segunda opção altera dados, modelo, medidas e resultados de páginas mistas; exige decisão arquitetural, regressão DAX, novo teste de desempenho e validação visual. Nenhum dado operacional deve ser conectado antes dessa decisão e da validação no Power BI Service.
