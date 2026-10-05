# Data Quality CLI

Projeto de estudo em Python para validar um arquivo CSV antes de uma carga ou análise de dados.

> **English summary.** Study project: a single-file Python CLI (standard library only) that checks a CSV file before it is loaded or analyzed. It validates required columns, duplicate keys, empty fields and ISO 8601 dates, prints a text or JSON report, and returns exit codes 0/1/2 so it can gate a script or CI step. Tested with pytest on GitHub Actions (Python 3.11 and 3.12).

## Problema

Antes de carregar uma planilha exportada em um banco ou relatório, vale conferir o básico: as colunas esperadas existem, a chave não se repete, campos obrigatórios estão preenchidos e as datas estão em um formato único. Esta CLI faz essas conferências com regras explícitas na linha de comando e devolve um código de saída, para que um script ou pipeline de CI possa parar a carga quando o arquivo não passa.

## O que valida

- Colunas obrigatórias (`--required`).
- Valores duplicados em uma coluna-chave (`--unique-key`).
- Campos que não podem ficar vazios (`--non-empty`).
- Datas ISO 8601, conferidas com `date.fromisoformat`; o formato esperado é `YYYY-MM-DD` (`--date-column`).

## Arquitetura

Um único módulo, `data_quality_cli.py`, sem dependências de runtime:

- `validate_csv()` lê o arquivo com `csv.DictReader` e aplica as regras, acumulando objetos `Issue` (linha, coluna, código e mensagem).
- `QualityReport` reúne o resultado e o serializa para texto ou JSON (`to_dict()`).
- `main()` faz o parsing dos argumentos (`argparse`) e define o código de saída.

| Código | Significado |
| --- | --- |
| `0` | Nenhum problema encontrado. |
| `1` | Problemas de qualidade encontrados. |
| `2` | Argumentos inválidos ou erro de leitura do arquivo (ex.: `ERROR: [Errno 2] No such file or directory`). |

## Instalação

Requer Python 3.11 ou posterior.

```sh
python -m venv .venv
# PowerShell: .\.venv\Scripts\Activate.ps1    macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Uso

```sh
python data_quality_cli.py sample_orders.csv \
  --required id,customer_email,created_at \
  --unique-key id \
  --non-empty customer_email \
  --date-column created_at
```

No PowerShell, troque `\` por `` ` `` no fim das linhas. Adicione `--json` para um relatório legível por máquina.

### Saída de exemplo

Arquivo válido (`sample_orders.csv`, incluído no repositório):

```text
PASS: 2 row(s) checked in sample_orders.csv
```

Arquivo com problemas (mesmas regras, CSV com chave repetida, e-mail vazio e data inválida na linha 3):

```text
FAIL: 3 issue(s) in bad_orders.csv
  row 3, id: duplicate_key - Value already appears on row 2
  row 3, customer_email: empty_value - Value must not be empty
  row 3, created_at: invalid_date - Use the YYYY-MM-DD format
```

O mesmo resultado com `--json` (código de saída `1`):

```json
{
  "file": "bad_orders.csv",
  "columns": ["id", "customer_email", "created_at", "total"],
  "total_rows": 2,
  "passed": false,
  "issues": [
    { "row": 3, "column": "id", "code": "duplicate_key", "message": "Value already appears on row 2" },
    { "row": 3, "column": "customer_email", "code": "empty_value", "message": "Value must not be empty" },
    { "row": 3, "column": "created_at", "code": "invalid_date", "message": "Use the YYYY-MM-DD format" }
  ]
}
```

## Testes

```sh
python -m pytest
```

Os testes cobrem arquivo válido, duplicidade/campo vazio/data inválida e colunas ausentes. O [workflow do GitHub Actions](.github/workflows/ci.yml) roda a suíte em cada push e pull request, com Python 3.11 e 3.12.

## Limites

Projeto independente de estudo, não um sistema de produção. As linhas são lidas em streaming, mas os valores da coluna-chave ficam em memória para detectar duplicidade. Não há inferência de tipos além das datas.

## Licença

[MIT](LICENSE).
