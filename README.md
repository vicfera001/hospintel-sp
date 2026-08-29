# HospIntel SP — Enterprise Challenge

MVP de apoio à análise municipal da pressão assistencial em São Paulo, com integração de três fontes públicas no Oracle Autonomous Database e consultas em linguagem natural pelo Oracle Select AI.

**Aplicação:** https://hospintel-sp-ai.streamlit.app

## Objetivo e escopo atual

O HospIntel SP combina:

- internações hospitalares mensais do **SIH/SUS**;
- hospitais e leitos SUS do **CNES**;
- estimativas populacionais municipais do **IBGE para 1º de julho de 2025**.

A visão estadual do SIH/SUS contém 327 municípios. A integração entre internações, leitos e população concentra-se em cinco municípios: São Paulo, Guarulhos, Osasco, Santo André e São Bernardo do Campo.

O modelo responde a perguntas sobre totais, evolução mensal, rankings, variações entre períodos e dois indicadores relativos:

- **internações por leito SUS no mês** — aproximação de pressão de demanda, não taxa de ocupação;
- **internações por 100 mil habitantes**.

## Arquitetura

```text
SIH/SUS 2025 (CSV relacional)
CNES 2025 (JSON)
IBGE 2025 (CSV no OCI Object Storage / Oracle External Table)
        ↓
Python: transformação, integração e validação
        ↓
Oracle Autonomous Database
        ↓
views analíticas + VW_PRESSAO_ASSISTENCIAL_POPULACAO
        ↓
Power BI                         Streamlit
análise estruturada              Oracle Select AI / Cohere
```

O Power BI e o aplicativo Streamlit são independentes, mas consultam a mesma base Oracle.

## Evidências validadas

| Camada | Resultado |
|---|---:|
| SIH/SUS — linhas | 3.924 |
| SIH/SUS — municípios | 327 |
| SIH/SUS — meses | 12 |
| SIH/SUS — internações | 2.896.345 |
| CNES — documentos JSON | 298 |
| CNES — registros hospital-mês | 3.475 |
| CNES — registros município-mês | 60 |
| IBGE — municípios na External Table | 5 |
| View final integrada | 60 linhas |
| Testes automatizados | 9 aprovados |

Consultas Select AI validadas no ambiente publicado:

1. **“Em janeiro de 2025, qual município teve mais internações por leito SUS?”**  
   Resultado: Santo André, 5,3836.
2. **“Compare as internações por 100 mil habitantes em janeiro de 2025.”**  
   Resultado: cinco municípios; Santo André (511,48), São Paulo (509,01), São Bernardo do Campo (392,44), Guarulhos (333,63) e Osasco (306,11).

## Perguntas alinhadas ao modelo

- Qual foi o total de internações nos municípios paulistas em 2025?
- Quais foram os dez municípios com mais internações em 2025?
- Quais dos cinco municípios apresentaram maior crescimento percentual de internações entre novembro e dezembro de 2025?
- Em janeiro de 2025, qual município teve mais internações por leito SUS?
- Compare as internações por 100 mil habitantes dos cinco municípios em janeiro de 2025.
- Considerando janeiro de 2025, quais municípios apresentaram maior pressão assistencial relativa pelos dois indicadores?
- Compare internações e leitos SUS disponíveis por município em janeiro de 2025.

## Limites interpretativos

A versão atual **não** contém internações individualizadas por hospital, permanência média, tipos de atendimento ou agregação por região de saúde. Portanto, não sustenta:

- rankings hospitalares de internações ou permanência;
- cálculo de taxa de ocupação;
- razão entre internações e leitos por hospital;
- comparação por região de saúde;
- recomendações automáticas sobre onde expandir a rede.

Essas perguntas exigem outras fontes, granularidades e regras de negócio. Os indicadores atuais oferecem evidências descritivas para apoiar análise, não decisões prescritivas.

## Estrutura do repositório

```text
data/raw/          exportação original do SIH/SUS
data/processed/    CSV relacional, JSON CNES e CSV IBGE processados
src/               transformação, validação e carga JSON no Oracle
sql/               tabelas, views, integração, validações e Select AI
docs/              relatório técnico, pipeline e guia do Power BI
powerbi/           espaço do arquivo PBIX mestre
ai_mvp/            conexão, Select AI e proteção de SQL
tests/             testes automatizados
legacy/            protótipo inicial
```

## Reprodução resumida

Requisito: Python 3.11 ou superior.

```bash
python src/transformar_datasus.py \
  data/raw/sih_cnv_qisp153716177_181_5_154.csv \
  data/processed/internacoes_sp_2025_long_reproduzido.csv

python src/validar_dataset.py \
  data/processed/internacoes_sp_2025_long_reproduzido.csv
```

No Oracle, execute os scripts na ordem:

1. `01_criar_tabela.sql`;
2. carga de `internacoes_sp_2025_long.csv`;
3. `02_criar_views_powerbi.sql`;
4. `03_validar_dados.sql`;
5. `04_configurar_colaboradores.sql`;\n6. carga do JSON CNES com `src/carregar_cnes_json_oracle.py`;\n7. `06_cnes_json_capacidade.sql`;\n8. envio do CSV IBGE ao OCI Object Storage e substituição local de `<URL_PAR_DO_CSV>`;\n9. `07_ibge_populacao_external_table.sql`;\n10. para uma instalação nova, `05_preparar_select_ai.sql`;\n11. para atualizar um perfil já existente, `08_atualizar_select_ai_integracao.sql`.

A URL PAR é um segredo operacional e nunca deve ser gravada no GitHub.

## Execução do aplicativo

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O modo **Demonstração local** usa exemplos predefinidos. O modo **Oracle Select AI** aceita perguntas livres, mostra o SQL gerado, valida-o como somente leitura e executa apenas nas views autorizadas.

## Segurança

- senhas, wallets, credenciais e URLs PAR permanecem fora do repositório;
- o usuário `HOSPINTELAPP` tem permissões restritas;
- o validador aceita somente consultas de leitura e objetos autorizados;
- o SQL executado é exibido para auditoria;
- a wallet hospedada fica nos Secrets do Streamlit e é reconstruída em diretório temporário protegido.

## Fontes

- Ministério da Saúde — DATASUS, SIH/SUS, internações por local de internação, São Paulo, 2025;
- Ministério da Saúde — CNES, estabelecimentos e leitos SUS, 2025;
- IBGE — estimativas da população residente para 1º de julho de 2025.
