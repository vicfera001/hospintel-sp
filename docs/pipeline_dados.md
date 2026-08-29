# Pipeline de dados do HospIntel SP

## 1. Fontes e formatos

A solução utiliza três formatos, cada um com uma finalidade distinta:

| Fonte | Formato | Finalidade |
|---|---|---|
| SIH/SUS — DATASUS | CSV relacional | Internações por município e mês em 2025 |
| CNES — Ministério da Saúde | JSON | Hospitais e capacidade de leitos SUS |
| IBGE | CSV em OCI Object Storage | População estimada em 1º de julho de 2025 |

## 2. SIH/SUS — internações

A exportação original `sih_cnv_qisp153716177_181_5_154.csv` foi preservada em `data/raw/`. Ela utiliza ISO-8859-1, delimitador `;` e uma linha por município, com os meses em colunas.

O script `src/transformar_datasus.py`:

1. localiza o cabeçalho real;
2. interpreta ISO-8859-1;
3. separa código e nome municipal;
4. converte campos vazios ou `-` para zero;
5. transforma o formato largo em longo;
6. cria datas mensais `YYYY-MM-01`;
7. grava CSV UTF-8;
8. confere totais mensais e total geral.

Resultado: 3.924 linhas, 327 municípios, 12 meses e 2.896.345 internações. A chave lógica é `codigo_municipio + mes_referencia`.

## 3. CNES — hospitais e leitos

O processamento gera `data/processed/cnes_hospitais_leitos_5_municipios_2025.json`. O arquivo contém 298 documentos de hospitais nos municípios de São Paulo, Guarulhos, Osasco, Santo André e São Bernardo do Campo.

A carga é realizada por:

```bash
python -m dotenv run -- \
python src/carregar_cnes_json_oracle.py \
data/processed/cnes_hospitais_leitos_5_municipios_2025.json
```

O script aceita conexão Oracle com wallet e realiza inserção ou atualização dos documentos. O script `sql/06_cnes_json_capacidade.sql` cria as projeções analíticas:

- 3.475 registros hospital-mês;
- 60 registros município-mês;
- `VW_PRESSAO_ASSISTENCIAL`, integrando internações e leitos.

## 4. IBGE — população estimada em 2025

O arquivo `data/processed/ibge_populacao_5_municipios_2025.csv` contém cinco municípios e as estimativas de população residente para 1º de julho de 2025.

O CSV é armazenado no OCI Object Storage e acessado pelo Oracle por meio de uma External Table. O procedimento é:

1. enviar o CSV ao bucket;
2. criar uma solicitação pré-autenticada somente leitura para esse objeto;
3. substituir localmente `<URL_PAR_DO_CSV>` em `sql/07_ibge_populacao_external_table.sql`;
4. executar o script no Oracle;
5. manter a URL real fora do GitHub.

O script cria `EXT_IBGE_POPULACAO` e `VW_PRESSAO_ASSISTENCIAL_POPULACAO`. A view final possui 60 linhas e calcula:

```text
internacoes_por_leito_sus_mes = internacoes / leitos_sus
internacoes_por_100_mil_hab   = internacoes / populacao_estimada_2025 × 100.000
```

O primeiro indicador é uma aproximação de pressão relativa e **não** uma taxa de ocupação.

## 5. Oracle e views

A tabela relacional principal é `ADMIN.INTERNACOES_SP`. As views autorizadas são:

- `VW_INTERNACOES_MENSAIS`;
- `VW_RANKING_MUNICIPIOS`;
- `VW_INTERNACOES_DASHBOARD`;
- `VW_PRESSAO_ASSISTENCIAL_POPULACAO`.

O Power BI consome as views para análise estruturada. O Streamlit solicita ao Oracle Select AI a geração de SQL, aplica um validador local de somente leitura e executa apenas objetos autorizados.

## 6. Ordem de reprodução no Oracle

1. `sql/01_criar_tabela.sql`;
2. carga do CSV SIH/SUS processado;
3. `sql/02_criar_views_powerbi.sql`;
4. `sql/03_validar_dados.sql`;
5. `sql/04_configurar_colaboradores.sql`;\n6. carga do JSON CNES;\n7. `sql/06_cnes_json_capacidade.sql`;\n8. preparação do objeto e da URL PAR do CSV IBGE;\n9. `sql/07_ibge_populacao_external_table.sql`;\n10. para uma instalação nova, `sql/05_preparar_select_ai.sql`;\n11. para atualizar um perfil já existente, `sql/08_atualizar_select_ai_integracao.sql`.

## 7. Validações esperadas

| Verificação | Valor |
|---|---:|
| SIH/SUS — linhas | 3.924 |
| SIH/SUS — municípios | 327 |
| SIH/SUS — meses | 12 |
| SIH/SUS — internações | 2.896.345 |
| CNES — documentos | 298 |
| CNES — hospital-mês | 3.475 |
| CNES — município-mês | 60 |
| IBGE — municípios | 5 |
| View integrada | 60 |

## 8. Limites

A integração final tem granularidade município-mês. Ela não contém internações por hospital, permanência média, tipo de atendimento, região de saúde, pacientes-dia ou leitos-dia. Portanto, esses conceitos não devem ser inferidos a partir dos indicadores disponíveis.
