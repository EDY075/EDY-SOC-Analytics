# Como contribuir

1. Preserve a natureza totalmente sintética do dataset.
2. Não inclua credenciais, PII, IPs públicos, hostnames reais ou logs operacionais.
3. Execute `python generator/generate_dataset.py` e `python -m unittest discover -s tests -v`.
4. Atualize o dicionário, o contrato e os valores esperados quando alterar o modelo.
5. Diferencie implementação de validação nos checkpoints.

