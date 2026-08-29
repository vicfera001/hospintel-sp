-- Atualizacao idempotente do perfil existente apos a integracao SIH/SUS + CNES + IBGE.
-- Execute como ADMIN depois dos scripts 06 e 07.
-- Nao inclua neste arquivo a URL PAR real, senhas ou dados da wallet.

GRANT SELECT ON VW_PRESSAO_ASSISTENCIAL_POPULACAO TO HOSPINTELAPP;
GRANT READ ON DIRECTORY DATA_PUMP_DIR TO HOSPINTELAPP;

BEGIN
    DBMS_CLOUD_AI.SET_ATTRIBUTE(
        profile_name    => 'HOSPINTEL_AI',
        attribute_name  => 'object_list',
        attribute_value => '[
            {"owner": "ADMIN", "name": "VW_INTERNACOES_DASHBOARD"},
            {"owner": "ADMIN", "name": "VW_INTERNACOES_MENSAIS"},
            {"owner": "ADMIN", "name": "VW_RANKING_MUNICIPIOS"},
            {"owner": "ADMIN", "name": "VW_PRESSAO_ASSISTENCIAL_POPULACAO"}
        ]'
    );
END;
/

BEGIN
    DBMS_CLOUD_AI.SET_ATTRIBUTE(
        profile_name    => 'HOSPINTEL_AI',
        attribute_name  => 'additional_instructions',
        attribute_value => 'Os valores de MUNICIPIO estao em letras maiusculas e sem acentos. Ao filtrar, converta o nome informado para esse padrao. Use NVL(SUM(...), 0) para totais. Para retornar a dimensao associada ao maior ou menor valor, ordene pela medida e use FETCH FIRST 1 ROW ONLY. Para comparar meses, use NUMERO_MES nas views de internacoes ou MES_REFERENCIA na view integrada. Para crescimento percentual, calcule (valor_final - valor_inicial) / NULLIF(valor_inicial, 0) * 100. VW_PRESSAO_ASSISTENCIAL_POPULACAO contem cinco municipios e integra internacoes do SIH/SUS, leitos SUS do CNES e populacao estimada pelo IBGE para 2025. INTERNACOES_POR_LEITO_SUS_MES e pressao relativa de demanda, nao taxa de ocupacao. Nao responda perguntas sobre permanencia media, tipos de atendimento, regiao de saude, taxa de ocupacao ou internacoes por hospital.'
    );
END;
/

-- Verificacoes de acesso pelo usuario da aplicacao:
-- SELECT COUNT(*) FROM ADMIN.VW_PRESSAO_ASSISTENCIAL_POPULACAO;
-- Resultado esperado: 60.

-- Evidencias Select AI validadas no aplicativo:
-- 1) Em janeiro de 2025, qual municipio teve mais internacoes por leito SUS?
-- 2) Compare as internacoes por 100 mil habitantes em janeiro de 2025.
