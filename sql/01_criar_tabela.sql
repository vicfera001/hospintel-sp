CREATE TABLE internacoes_sp (
    codigo_municipio VARCHAR2(6) NOT NULL,
    municipio        VARCHAR2(100) NOT NULL,
    mes_referencia   DATE NOT NULL,
    internacoes      NUMBER(10, 0) NOT NULL,
    CONSTRAINT pk_internacoes_sp
        PRIMARY KEY (codigo_municipio, mes_referencia),
    CONSTRAINT ck_internacoes_sp_nao_negativas
        CHECK (internacoes >= 0)
);
