# MVP de linguagem natural — HospIntel SP

O `app.py` é independente do Power BI. Ambos consultam a mesma base Oracle, mas atendem a formas complementares de análise.

## Concentração analítica do modelo

O Select AI foi modelado para perguntas municipais sobre:

- internações mensais do SIH/SUS em 2025;
- rankings, totais e variações entre períodos;
- leitos SUS do CNES nos cinco municípios integrados;
- população estimada pelo IBGE em 2025;
- internações por leito SUS no mês;
- internações por 100 mil habitantes.

**Internações por leito SUS no mês é um indicador relativo de pressão de demanda. Não representa taxa de ocupação**, pois o modelo não contém pacientes-dia, leitos-dia disponíveis nem tempo de permanência.

## Modos disponíveis

1. **Demonstração local:** utiliza o CSV processado e exemplos previamente definidos; não exige wallet.
2. **Oracle Select AI:** transforma perguntas livres em SQL, valida o SQL localmente e somente depois executa a consulta no Oracle.

## Views autorizadas

- `VW_INTERNACOES_DASHBOARD`;
- `VW_INTERNACOES_MENSAIS`;
- `VW_RANKING_MUNICIPIOS`;
- `VW_PRESSAO_ASSISTENCIAL_POPULACAO`.

A última view integra SIH/SUS, CNES e IBGE para cinco municípios e doze meses de 2025.

## Perguntas recomendadas

### Visão estadual do SIH/SUS

- Qual foi o total de internações nos municípios paulistas em 2025?
- Quais foram os dez municípios com mais internações em 2025?
- Quais dos cinco municípios analisados apresentaram maior crescimento percentual de internações entre novembro e dezembro de 2025?

### Visão municipal integrada

- Em janeiro de 2025, qual município teve mais internações por leito SUS?
- Compare as internações por 100 mil habitantes dos cinco municípios em janeiro de 2025.
- Considerando janeiro de 2025, quais municípios apresentaram maior pressão assistencial relativa, medida por internações por leito SUS e internações por 100 mil habitantes?
- Compare internações e leitos SUS disponíveis por município em janeiro de 2025.

## Perguntas fora do escopo

O modelo não deve ser usado para responder:

- quais hospitais têm maior permanência média;
- quais hospitais têm maior razão entre internações e leitos;
- quais tipos de atendimento cresceram mais;
- comparações por região de saúde;
- qual é a taxa de ocupação;
- quais regiões devem receber expansão da rede.

Essas perguntas dependem de granularidades ou medidas ausentes. A última pergunta também exige critérios de política pública que não podem ser inferidos automaticamente a partir dos dois indicadores descritivos.

## Evidências de funcionamento

No aplicativo publicado, foram validadas duas consultas integradas:

| Pergunta | Resultado |
|---|---|
| Em janeiro de 2025, qual município teve mais internações por leito SUS? | Santo André — 5,3836 |
| Compare as internações por 100 mil habitantes em janeiro de 2025. | 5 municípios; Santo André 511,48; São Paulo 509,01; São Bernardo do Campo 392,44; Guarulhos 333,63; Osasco 306,11 |

Nos dois casos, o SQL exibido utilizou `ADMIN.VW_PRESSAO_ASSISTENCIAL_POPULACAO`, aplicou o filtro de janeiro de 2025 e retornou somente colunas autorizadas.

## Arquitetura do Select AI

O perfil `HOSPINTEL_AI` pertence ao esquema `ADMIN` e utiliza o provedor Cohere. O usuário restrito `HOSPINTELAPP` não acessa diretamente a credencial de IA.

```text
Pergunta no Streamlit
    → HOSPINTELAPP
    → ADMIN.HOSPINTEL_GENERATE_SQL
    → perfil HOSPINTEL_AI
    → geração de SQL pelo Select AI
    → validação local de somente leitura
    → execução nas views autorizadas
    → resultado, gráfico, tabela e SQL utilizado
```

## Publicação no Streamlit Community Cloud

A wallet Oracle não deve ser adicionada ao repositório. O ZIP da wallet é convertido para Base64 e armazenado exclusivamente nos Secrets do Streamlit.

```text
APP_MODE=oracle
ORACLE_USER=HOSPINTELAPP
ORACLE_PASSWORD=<SENHA_DO_USUARIO_DO_BANCO>
ORACLE_DSN=fiap_low
ORACLE_WALLET_PASSWORD=<SENHA_DA_WALLET>
SELECT_AI_PROFILE=HOSPINTEL_AI
ORACLE_WALLET_ZIP_B64=<CONTEUDO_BASE64_DO_ZIP_DA_WALLET>
```

No ambiente hospedado, `ORACLE_CONFIG_DIR` deve permanecer ausente. O aplicativo decodifica a wallet em um diretório temporário protegido.

A External Table do IBGE utiliza uma URL PAR somente leitura para um único objeto. A URL real permanece fora do GitHub; o script versionado contém apenas `<URL_PAR_DO_CSV>`.
