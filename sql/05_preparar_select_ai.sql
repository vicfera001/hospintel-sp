-- Execute como ADMIN.
-- Pré-requisito: credencial COHERE_CRED criada no esquema ADMIN.
-- O perfil envia ao provedor somente metadados das três views autorizadas.
-- O bloco CREATE_PROFILE deve ser executado apenas se HOSPINTEL_AI ainda não existir.

BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'HOSPINTEL_AI',
        attributes   => '{
            "provider": "cohere",
            "credential_name": "COHERE_CRED",
            "object_list": [
                {"owner": "ADMIN", "name": "VW_INTERNACOES_DASHBOARD"},
                {"owner": "ADMIN", "name": "VW_INTERNACOES_MENSAIS"},
                {"owner": "ADMIN", "name": "VW_RANKING_MUNICIPIOS"}
            ],
            "comments": true,
            "conversation": false
        }',
        description  => 'NL2SQL do MVP HospIntel SP'
    );
END;
/

-- Orientações adicionais para geração consistente de SQL.
BEGIN
    DBMS_CLOUD_AI.SET_ATTRIBUTE(
        profile_name    => 'HOSPINTEL_AI',
        attribute_name  => 'additional_instructions',
        attribute_value => 'Os valores da coluna MUNICIPIO estão armazenados em letras maiúsculas e sem acentos. Ao filtrar por município, transforme o nome informado em maiúsculas e remova os acentos do literal. Exemplos: Santo André deve ser SANTO ANDRE; São Paulo deve ser SAO PAULO. Para totais com SUM, use NVL(SUM(...), 0). Quando a pergunta solicitar a categoria, município ou mês associado ao maior ou menor valor, nunca calcule MAX ou MIN separadamente sobre a dimensão e a medida. Ordene pela medida e use FETCH FIRST 1 ROW ONLY para retornar ambos da mesma linha. Para comparar internações de dois meses por município, use VW_INTERNACOES_DASHBOARD, agrupe por CODIGO_MUNICIPIO e MUNICIPIO e calcule cada mês com SUM(CASE WHEN NUMERO_MES = numero_do_mes THEN INTERNACOES ELSE 0 END). O crescimento absoluto é o total do mês final menos o total do mês inicial. A redução deve ser apresentada como valor positivo, calculando o total do mês inicial menos o total do mês final. Para variação percentual, exclua denominadores iguais a zero. Não use LAG sobre VW_RANKING_MUNICIPIOS.'
    );
END;
/

-- Ponte controlada para o usuário restrito do aplicativo.
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

-- Teste de geração sem executar o SQL produzido.
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt       => 'Quais são os dez municípios com mais internações?',
    profile_name => 'HOSPINTEL_AI',
    action       => 'showsql'
) AS sql_gerado
FROM dual;
