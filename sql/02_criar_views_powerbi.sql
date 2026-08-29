CREATE OR REPLACE VIEW vw_internacoes_mensais AS
SELECT
    TRUNC(mes_referencia, 'MM') AS mes_referencia,
    SUM(internacoes) AS total_internacoes
FROM internacoes_sp
GROUP BY TRUNC(mes_referencia, 'MM');

CREATE OR REPLACE VIEW vw_ranking_municipios AS
SELECT
    codigo_municipio,
    municipio,
    'SP' AS uf,
    'Brasil' AS pais,
    SUM(internacoes) AS total_internacoes,
    ROUND(AVG(internacoes), 2) AS media_mensal
FROM internacoes_sp
GROUP BY codigo_municipio, municipio;

CREATE OR REPLACE VIEW vw_internacoes_dashboard AS
SELECT
    codigo_municipio,
    municipio,
    'SP' AS uf,
    'Brasil' AS pais,
    mes_referencia,
    EXTRACT(YEAR FROM mes_referencia) AS ano,
    EXTRACT(MONTH FROM mes_referencia) AS numero_mes,
    internacoes
FROM internacoes_sp;
