SELECT
    COUNT(*) AS total_linhas,
    COUNT(DISTINCT codigo_municipio) AS municipios,
    COUNT(DISTINCT mes_referencia) AS meses,
    MIN(mes_referencia) AS primeiro_mes,
    MAX(mes_referencia) AS ultimo_mes,
    SUM(internacoes) AS total_internacoes
FROM internacoes_sp;

SELECT
    'VW_INTERNACOES_MENSAIS' AS fonte,
    COUNT(*) AS linhas
FROM vw_internacoes_mensais
UNION ALL
SELECT 'VW_RANKING_MUNICIPIOS', COUNT(*)
FROM vw_ranking_municipios
UNION ALL
SELECT 'VW_INTERNACOES_DASHBOARD', COUNT(*)
FROM vw_internacoes_dashboard;

SELECT
    TRUNC(mes_referencia, 'MM') AS mes_referencia,
    SUM(internacoes) AS total_internacoes
FROM internacoes_sp
GROUP BY TRUNC(mes_referencia, 'MM')
ORDER BY mes_referencia;
