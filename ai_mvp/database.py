"""Conexão Oracle e execução de consultas somente leitura."""

from __future__ import annotations

import os
from contextlib import contextmanager

import pandas as pd

from .sql_guard import validate_read_only_sql


@contextmanager
def oracle_connection():
    try:
        import oracledb
    except ImportError as exc:
        raise RuntimeError("Instale a dependência 'oracledb'.") from exc

    required = ["ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Variáveis ausentes: " + ", ".join(missing))

    config_dir = os.getenv("ORACLE_CONFIG_DIR") or None
    wallet_password = os.getenv("ORACLE_WALLET_PASSWORD") or None
    options = dict(
        user=os.environ["ORACLE_USER"],
        password=os.environ["ORACLE_PASSWORD"],
        dsn=os.environ["ORACLE_DSN"],
    )
    if config_dir:
        options.update(config_dir=config_dir, wallet_location=config_dir)
    if wallet_password:
        options["wallet_password"] = wallet_password
    connection = oracledb.connect(**options)
    try:
        yield connection
    finally:
        connection.close()


def query_dataframe(connection, sql: str, params: dict | None = None) -> pd.DataFrame:
    safe_sql = validate_read_only_sql(sql)
    with connection.cursor() as cursor:
        cursor.execute(safe_sql, params or {})
        columns = [item[0].lower() for item in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)
