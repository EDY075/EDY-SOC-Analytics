# Segurança e RLS demonstrativa

## Papéis

- `SOC_Analyst`: acesso dinâmico à equipe/região mapeada na tabela fictícia `SecurityAccess`.
- `SOC_Manager`: acesso a todas as equipes demonstrativas.

Exemplo de filtro dinâmico na tabela de autorização:

```DAX
LOWER ( SecurityAccess[UPN] ) = LOWER ( USERPRINCIPALNAME () )
```

No dataset público, os UPNs são rótulos fictícios do domínio reservado `example.invalid`; não correspondem a pessoas reais.

## Propagação

`SecurityAccess` filtra `DimAnalyst`/equipe por relação ativa e daí alcança `FactIncidents`. O filtro não é aplicado diretamente ao fato. Para o gerente demonstrativo, a role não restringe linhas.

## Limitação do serviço

RLS restringe consumidores Viewer. Usuários Admin, Member ou Contributor do workspace não são limitados por RLS. Membership de papéis precisa ser configurada e testada após deploy; o projeto local demonstra a definição, não a associação operacional do serviço.

## Testes reais no Desktop

| Cenário | Resultado | Estado |
|---|---|---|
| `Exibir como: SOC_Manager` | total = 3.200 incidentes | VALIDADO |
| `Exibir como: SOC_Analyst` sem identidade correspondente | nenhum dado | VALIDADO |
| identidade fictícia específica em `Outro usuário` | campo não aceitou valor de modo confiável | BLOQUEADO |

O relatório foi retirado do modo `Exibir como` após o teste. O comportamento sem correspondência demonstra deny-by-default; a simulação de equipe específica não é alegada como validada.
