-- HospIntel SP - fonte auxiliar CSV por Oracle External Table
-- Populacoes estimadas pelo IBGE para 1 de julho de 2025.
-- Antes de executar, envie ibge_populacao_5_municipios_2025.csv ao OCI Object Storage
-- e substitua <URL_PAR_DO_CSV> pela URL pre-autenticada (PAR) do objeto.

BEGIN
    DBMS_CLOUD.CREATE_EXTERNAL_TABLE(
        table_name      => 'EXT_IBGE_POPULACAO',
        credential_name => NULL,
        file_uri_list   => '<URL_PAR_DO_CSV>',
        format          => JSON_OBJECT(
            'type' VALUE 'csv',
            'skipheaders' VALUE '1',
            'delimiter' VALUE ',',
            'dateformat' VALUE 'yyyy-mm-dd',
            'rejectlimit' VALUE '0'
        ),
        column_list     => '
            MUNICIPIO_CODIGO          VARCHAR2(6),
            IBGE_CODIGO_7             VARCHAR2(7),
            MUNICIPIO                 VARCHAR2(100),
            POPULACAO_ESTIMADA_2025   NUMBER,
            UF                        CHAR(2),
            DATA_REFERENCIA           DATE,
            FONTE                     VARCHAR2(60)'
    );
END;
/

CREATE OR REPLACE VIEW VW_PRESSAO_ASSISTENCIAL_POPULACAO AS
SELECT
    p.codigo_municipio,
    p.municipio,
    p.mes_referencia,
    p.internacoes,
    p.leitos_sus,
    p.internacoes_por_leito_sus_mes,
    e.populacao_estimada_2025,
    ROUND(p.internacoes / NULLIF(e.populacao_estimada_2025, 0) * 100000, 2)
        AS internacoes_por_100_mil_hab
FROM vw_pressao_assistencial p
JOIN ext_ibge_populacao e
  ON e.municipio_codigo = p.codigo_municipio;

-- Validacoes esperadas: 5 municipios na tabela externa e 60 linhas integradas.
SELECT COUNT(*) AS MUNICIPIOS_EXTERNOS FROM EXT_IBGE_POPULACAO;
SELECT COUNT(*) AS LINHAS_INTEGRADAS FROM VW_PRESSAO_ASSISTENCIAL_POPULACAO;
