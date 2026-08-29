-- Execute como ADMIN depois dos scripts 01 a 07.
-- Pre-requisito: credencial COHERE_CRED criada no esquema ADMIN.
-- O bloco CREATE_PROFILE deve ser executado apenas se HOSPINTEL_AI ainda nao existir.
-- Nenhuma senha, wallet ou URL PAR deve ser gravada neste arquivo.

BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'HOSPINTEL_AI',
        attributes   => '{
            "provider": "cohere",
            "credential_name": "COHERE_CRED",
            "object_list": [
                {"owner": "ADMIN", "name": "VW_INTERNACOES_DASHBOARD"},
                {"owner": "ADMIN", "name": "VW_INTERNACOES_MENSAIS"},
                {"owner": "ADMIN", "name": "VW_RANKING_MUNICIPIOS"},
                {"owner": "ADMIN", "name": "VW_PRESSAO_ASSISTENCIAL_POPULACAO"}
            ],
            "comments": true,
            "conversation": false
        }',
        description  => 'NL2SQL municipal do HospIntel SP: SIH/SUS, CNES e IBGE 2025'
    );
END;
/

BEGIN
    DBMS_CLOUD_AI.SET_ATTRIBUTE(
        profile_name    => 'HOSPINTEL_AI',
        attribute_name  => 'additional_instructions',
        attribute_value => 'Os valores de MUNICIPIO estao em letras maiusculas e sem acentos. Ao filtrar, converta o nome informado para esse padrao. Use NVL(SUM(...), 0) para totais. Para retornar a dimensao associada ao maior ou menor valor, ordene pela medida e use FETCH FIRST 1 ROW ONLY; nao calcule MAX ou MIN separadamente sobre dimensao e medida. Para comparar meses, use NUMERO_MES nas views de internacoes ou MES_REFERENCIA na view integrada. Para crescimento percentual, calcule (valor_final - valor_inicial) / NULLIF(valor_inicial, 0) * 100. VW_PRESSAO_ASSISTENCIAL_POPULACAO contem somente cinco municipios e integra internacoes do SIH/SUS, leitos SUS do CNES e populacao estimada pelo IBGE para 2025. INTERNACOES_POR_LEITO_SUS_MES e um indicador relativo de pressao de demanda e nao representa taxa de ocupacao. INTERNACOES_POR_100_MIL_HAB permite comparacao relativa por populacao. Nao responda perguntas sobre permanencia media, tipos de atendimento, regiao de saude, taxa de ocupacao ou internacoes por hospital, pois esses dados nao estao disponiveis.'
    );
END;
/

CREATE OR REPLACE FUNCTION HOSPINTEL_GENERATE_SQL (
    p_prompt IN VARCHAR2
) RETURN CLOB
AUTHID DEFINER
AS
BEGIN
    RETURN DBMS_CLOUD_AI.GENERATE(
        prompt       => p_prompt,
        profile_name => 'HOSPINTEL_AI',
        action       => 'showsql'
    );
END;
/

GRANT EXECUTE ON HOSPINTEL_GENERATE_SQL TO HOSPINTELAPP;
GRANT SELECT ON VW_INTERNACOES_DASHBOARD TO HOSPINTELAPP;
GRANT SELECT ON VW_INTERNACOES_MENSAIS TO HOSPINTELAPP;
GRANT SELECT ON VW_RANKING_MUNICIPIOS TO HOSPINTELAPP;
GRANT SELECT ON VW_PRESSAO_ASSISTENCIAL_POPULACAO TO HOSPINTELAPP;
GRANT READ ON DIRECTORY DATA_PUMP_DIR TO HOSPINTELAPP;

-- Testes de geracao: mostram o SQL sem executa-lo.
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt       => 'Em janeiro de 2025, qual municipio teve mais internacoes por leito SUS?',
    profile_name => 'HOSPINTEL_AI',
    action       => 'showsql'
) AS sql_gerado
FROM dual;

SELECT DBMS_CLOUD_AI.GENERATE(
    prompt       => 'Compare as internacoes por 100 mil habitantes em janeiro de 2025.',
    profile_name => 'HOSPINTEL_AI',
    action       => 'showsql'
) AS sql_gerado
FROM dual;
