#!/usr/bin/env python3
"""Carrega os documentos CNES/Leitos na tabela JSON do Oracle."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import oracledb


def obrigatoria(nome: str) -> str:
    valor = os.getenv(nome)
    if not valor:
        raise RuntimeError(f"Variável de ambiente obrigatória ausente: {nome}")
    return valor


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_processado", type=Path)
    args = parser.parse_args()

    documentos = json.loads(args.json_processado.read_text(encoding="utf-8"))
    linhas = [
        (
            str(documento["codigo_cnes"]).zfill(7),
            json.dumps(documento, ensure_ascii=False, separators=(",", ":")),
        )
        for documento in documentos
    ]

    opcoes_conexao = {
        "user": obrigatoria("ORACLE_USER"),
        "password": obrigatoria("ORACLE_PASSWORD"),
        "dsn": obrigatoria("ORACLE_DSN"),
    }
    config_dir = os.getenv("ORACLE_CONFIG_DIR")
    wallet_password = os.getenv("ORACLE_WALLET_PASSWORD")
    if config_dir:
        opcoes_conexao.update(
            config_dir=config_dir,
            wallet_location=config_dir,
        )
    if wallet_password:
        opcoes_conexao["wallet_password"] = wallet_password

    conexao = oracledb.connect(**opcoes_conexao)
    try:
        with conexao.cursor() as cursor:
            cursor.executemany(
                """
                MERGE INTO cnes_hospitais_json destino
                USING (
                    SELECT :1 AS codigo_cnes, :2 AS documento FROM dual
                ) origem
                ON (destino.codigo_cnes = origem.codigo_cnes)
                WHEN MATCHED THEN UPDATE SET
                    destino.documento = origem.documento,
                    destino.carregado_em = SYSTIMESTAMP
                WHEN NOT MATCHED THEN INSERT (
                    codigo_cnes, documento
                ) VALUES (
                    origem.codigo_cnes, origem.documento
                )
                """,
                linhas,
            )
        conexao.commit()
        print(f"Documentos CNES carregados/atualizados: {len(linhas)}")
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
