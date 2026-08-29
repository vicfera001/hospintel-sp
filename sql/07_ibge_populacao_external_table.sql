-- HospIntel SP - fonte auxiliar CSV por Oracle External Table
-- Antes de executar, envie ibge_populacao_5_municipios_2022.csv ao OCI Object Storage
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
            'rejectlimit' VALUE '0'
        ),
        column_list     => '
            MUNICIPIO_CODIGO       VARCHAR2(6),
            IBGE_CODIGO_7          VARCHAR2(7),
            MUNICIPIO              VARCHAR2(100),
            POPULACAO_CENSO_2022   NUMBER,
            UF                     CHAR(2),
            ANO_REFERENCIA         NUMBER(4),
            FONTE                  VARCHAR2(50)'
    );
END;
/

CREATE OR REPLACE VIEW VW_PRESSAO_ASSISTENCIAL_POPULACAO AS
SELECT
    p.municipio_codigo,
    p.municipio,
    p.mes_referencia,
    p.internacoes,
    p.leitos_sus,
    p.internacoes_por_leito_sus_mes,
    e.populacao_censo_2022,
    ROUND(p.internacoes / NULLIF(e.populacao_censo_2022, 0) * 100000, 2)
        AS internacoes_por_100_mil_hab
FROM vw_pressao_assistencial p
JOIN ext_ibge_populacao e
  ON e.municipio_codigo = p.municipio_codigo;

-- Validações esperadas: 5 municípios na tabela externa e 60 linhas integradas.
SELECT COUNT(*) AS MUNICIPIOS_EXTERNOS FROM EXT_IBGE_POPULACAO;
SELECT COUNT(*) AS LINHAS_INTEGRADAS FROM VW_PRESSAO_ASSISTENCIAL_POPULACAO;
