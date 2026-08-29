-- HospIntel SP - CNES/Leitos 2025 em JSON
-- Execute antes de src/carregar_cnes_json_oracle.py.

CREATE TABLE cnes_hospitais_json (
    codigo_cnes  VARCHAR2(7) NOT NULL,
    documento    CLOB NOT NULL,
    carregado_em TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT pk_cnes_hospitais_json PRIMARY KEY (codigo_cnes),
    CONSTRAINT ck_cnes_hospitais_documento_json CHECK (documento IS JSON)
);

CREATE OR REPLACE VIEW vw_cnes_leitos_hospital_mes AS
SELECT
    h.codigo_cnes,
    jt.codigo_municipio,
    jt.municipio,
    jt.nome_estabelecimento,
    TO_DATE(jt.competencia || '-01', 'YYYY-MM-DD') AS mes_referencia,
    jt.leitos_existentes,
    jt.leitos_sus,
    jt.uti_total_existente,
    jt.uti_total_sus
FROM cnes_hospitais_json h,
     JSON_TABLE(
         h.documento,
         '$'
         COLUMNS (
             codigo_municipio      VARCHAR2(6)   PATH '$.codigo_municipio',
             municipio             VARCHAR2(100) PATH '$.municipio',
             nome_estabelecimento  VARCHAR2(200) PATH '$.nome_estabelecimento_2025',
             NESTED PATH '$.leitos_por_mes[*]'
             COLUMNS (
                 competencia         VARCHAR2(7) PATH '$.competencia',
                 leitos_existentes   NUMBER      PATH '$.leitos_existentes',
                 leitos_sus          NUMBER      PATH '$.leitos_sus',
                 uti_total_existente NUMBER      PATH '$.uti_total_existente',
                 uti_total_sus       NUMBER      PATH '$.uti_total_sus'
             )
         )
     ) jt;

CREATE OR REPLACE VIEW vw_cnes_capacidade_municipal AS
SELECT
    codigo_municipio,
    municipio,
    mes_referencia,
    SUM(leitos_existentes) AS leitos_existentes,
    SUM(leitos_sus) AS leitos_sus,
    SUM(uti_total_existente) AS uti_total_existente,
    SUM(uti_total_sus) AS uti_total_sus
FROM vw_cnes_leitos_hospital_mes
GROUP BY codigo_municipio, municipio, mes_referencia;

CREATE OR REPLACE VIEW vw_pressao_assistencial AS
SELECT
    i.codigo_municipio,
    i.municipio,
    i.mes_referencia,
    i.internacoes,
    c.leitos_existentes,
    c.leitos_sus,
    c.uti_total_existente,
    c.uti_total_sus,
    ROUND(i.internacoes / NULLIF(c.leitos_sus, 0), 4)
        AS internacoes_por_leito_sus_mes
FROM internacoes_sp i
JOIN vw_cnes_capacidade_municipal c
  ON c.codigo_municipio = i.codigo_municipio
 AND c.mes_referencia = i.mes_referencia;

-- Validações esperadas para o recorte inicial:
SELECT COUNT(*) AS documentos_json FROM cnes_hospitais_json; -- 298
SELECT COUNT(*) AS hospital_mes FROM vw_cnes_leitos_hospital_mes; -- 3475
SELECT COUNT(*) AS municipio_mes FROM vw_cnes_capacidade_municipal; -- 60
SELECT COUNT(*) AS linhas_integradas FROM vw_pressao_assistencial; -- 60
