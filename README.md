# HospIntel SP — Enterprise Challenge

Pipeline reprodutível para análise das internações hospitalares do SUS nos
municípios do estado de São Paulo em 2025.

## Arquitetura

```text
DATASUS/SIH-SUS
    → limpeza e validação em Python
    → CSV longo em UTF-8
    → Oracle Autonomous Database
    → views analíticas
    → Power BI (visualização)
    → Streamlit + Oracle Select AI (consultas em linguagem natural)
```

## Estrutura

```text
data/raw/          exportação original do DATASUS
data/processed/    CSV utilizado no Oracle
src/               transformação e validação em Python
sql/               tabela, views, validações e função de colaboração
docs/              documentação do pipeline e guia do Power BI
powerbi/            espaço reservado para o arquivo PBIX mestre
ai_mvp/             conexão, Select AI, demonstração e proteção de SQL
tests/              testes automatizados do MVP
legacy/             protótipo original com cinco municípios
```

## Como reproduzir

Requisito do pipeline: Python 3.11 ou superior. A transformação dos dados não
possui dependências externas.

```bash
python src/transformar_datasus.py \
  data/raw/sih_cnv_qisp153716177_181_5_154.csv \
  data/processed/internacoes_sp_2025_long_reproduzido.csv

python src/validar_dataset.py \
  data/processed/internacoes_sp_2025_long_reproduzido.csv
```

Resultados esperados:

| Indicador | Valor |
|---|---:|
| Municípios | 327 |
| Meses | 12 |
| Linhas | 3.924 |
| Internações | 2.896.345 |

## Escopo analítico dos dados

O dataset atual contém município, código do município, mês, ano e quantidade de
internações. Ele permite analisar totais, evolução mensal, rankings e variações
absolutas ou percentuais entre períodos.

Perguntas sobre hospitais ou unidades, leitos disponíveis, permanência média,
tipos de atendimento, regiões de saúde ou Grande São Paulo exigem uma futura
ampliação do dataset. Essas limitações estão documentadas em
`docs/mvp_linguagem_natural.md`.

## Carregamento no Oracle

1. Execute `sql/01_criar_tabela.sql`.
2. Importe `data/processed/internacoes_sp_2025_long.csv` para
   `ADMIN.INTERNACOES_SP`.
3. Execute `sql/02_criar_views_powerbi.sql`.
4. Execute `sql/03_validar_dados.sql`.

## MVP de linguagem natural

O aplicativo funciona separadamente do Power BI. Para testar imediatamente:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Escolha **Demonstração local**. Esse modo usa o CSV já validado e não solicita
credenciais. Para ativar perguntas livres com Oracle Select AI, consulte
`docs/mvp_linguagem_natural.md` e prepare o perfil a partir de
`sql/05_preparar_select_ai.sql`.

## Segurança

Este repositório não deve conter senhas, wallets do Oracle, chaves de API ou
credenciais pessoais. Cada colaborador deve utilizar uma conta individual.

## Origem dos dados

Ministério da Saúde — DATASUS, Sistema de Informações Hospitalares do SUS
(SIH/SUS), internações por local de internação, São Paulo, 2025. Os dados do
TabNet podem sofrer atualizações posteriores; a exportação original utilizada
no projeto foi preservada em `data/raw/`.
