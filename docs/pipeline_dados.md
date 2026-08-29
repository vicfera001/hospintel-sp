# Pipeline de dados do HospIntel SP

## 1. Fonte

- Sistema: DATASUS TabNet.
- Base: Sistema de Informações Hospitalares do SUS (SIH/SUS).
- Medida: internações por local de internação.
- Abrangência: municípios do estado de São Paulo.
- Período: janeiro a dezembro de 2025.
- Arquivo exportado: `sih_cnv_qisp153716177_181_5_154.csv`.

O arquivo original foi preservado sem alterações em `data/raw/`. Ele utiliza
codificação ISO-8859-1, delimitador `;` e uma linha por município, com os doze
meses distribuídos em colunas.

## 2. Transformação

### 2.1 Protótipo inicial

O primeiro script, preservado em
`legacy/transform_sih_sus_5_municipios.mjs`, transformava somente cinco
municípios e gerava 60 linhas. Essa etapa serviu para validar a leitura do
formato TabNet e a conversão largo → longo.

### 2.2 Pipeline completo

O script `src/transformar_datasus.py`:

1. localiza o cabeçalho real dentro do relatório do TabNet;
2. interpreta o arquivo em ISO-8859-1;
3. separa o código municipal de seis dígitos e o nome;
4. converte `-` e campos vazios para zero;
5. remove acentos dos nomes para reproduzir o arquivo utilizado no Oracle;
6. transforma as doze colunas mensais em 12 registros por município;
7. cria datas no primeiro dia de cada mês (`YYYY-MM-01`);
8. grava CSV UTF-8 separado por vírgulas;
9. confere os totais mensais e o total geral publicados pelo DATASUS.

## 3. Resultado

O arquivo `data/processed/internacoes_sp_2025_long.csv` contém:

- 3.924 linhas;
- 327 municípios;
- 12 meses;
- 2.896.345 internações;
- chave lógica: `codigo_municipio + mes_referencia`.

## 4. Oracle

O CSV processado foi importado para `ADMIN.INTERNACOES_SP`. A tabela utiliza
restrição de chave primária por município e mês e impede valores negativos.
Três views foram criadas para o Power BI:

- `VW_INTERNACOES_MENSAIS`;
- `VW_RANKING_MUNICIPIOS`;
- `VW_INTERNACOES_DASHBOARD`.

## 5. Power BI e IA

O Power BI consome as views do Oracle por meio de contas individuais. A camada
de IA planejada utiliza linguagem natural para gerar consultas SQL controladas
sobre essas mesmas views, preservando a rastreabilidade dos resultados.

## 6. Reprodutibilidade

Na raiz do projeto, execute:

```bash
python src/transformar_datasus.py \
  data/raw/sih_cnv_qisp153716177_181_5_154.csv \
  data/processed/internacoes_sp_2025_long_reproduzido.csv

python src/validar_dataset.py \
  data/processed/internacoes_sp_2025_long_reproduzido.csv
```

Compare o arquivo reproduzido com o arquivo utilizado no Oracle:

```bash
cmp \
  data/processed/internacoes_sp_2025_long.csv \
  data/processed/internacoes_sp_2025_long_reproduzido.csv
```

Ausência de saída do `cmp` significa igualdade byte a byte.
