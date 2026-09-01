# Data Quality CLI

Projeto de portfólio/estudo em Python para validar arquivos CSV antes de uma carga ou análise de dados.

## O que demonstra

- Validação de colunas obrigatórias e campos não vazios.
- Detecção de chaves duplicadas.
- Validação de datas no padrão ISO 8601 (`YYYY-MM-DD`).
- Relatório legível ou JSON para integração com pipelines.
- Código sem dependências de runtime e testes automatizados com `pytest`.

## Uso rápido

```powershell
python -m pip install -e ".[dev]"
python data_quality_cli.py sample_orders.csv `
  --required id,customer_email,created_at `
  --unique-key id `
  --non-empty customer_email `
  --date-column created_at
```

Para JSON, adicione `--json`. O comando retorna `0` quando não encontra problemas, `1` quando encontra problemas de qualidade e `2` para erro de configuração ou leitura.

## Desenvolvimento

```powershell
python -m pytest
```

O workflow do GitHub Actions executa os testes em cada push e pull request.

Este repositório é um projeto independente de portfólio/estudo; não representa um sistema de produção.

