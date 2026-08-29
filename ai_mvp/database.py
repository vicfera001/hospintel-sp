"""Conexão Oracle e execução de consultas somente leitura."""

from __future__ import annotations

import base64
import io
import os
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from .sql_guard import validate_read_only_sql


_wallet_temp_dir: tempfile.TemporaryDirectory | None = None


def _resolve_oracle_config_dir() -> str | None:
    """Usa a wallet local ou reconstrói uma wallet fornecida como segredo Base64."""
    global _wallet_temp_dir

    configured = os.getenv("ORACLE_CONFIG_DIR")
    if configured and Path(configured).is_dir():
        return configured

    encoded_wallet = os.getenv("ORACLE_WALLET_ZIP_B64")
    if not encoded_wallet:
        return configured or None

    if _wallet_temp_dir is None:
        wallet_bytes = base64.b64decode(encoded_wallet)
        _wallet_temp_dir = tempfile.TemporaryDirectory(prefix="hospintel_wallet_")
        destination = Path(_wallet_temp_dir.name).resolve()

        with zipfile.ZipFile(io.BytesIO(wallet_bytes)) as archive:
            for member in archive.infolist():
                target = (destination / member.filename).resolve()
                if target != destination and destination not in target.parents:
                    raise RuntimeError("A wallet contém um caminho de arquivo inválido.")
            archive.extractall(destination)

        for path in destination.rglob("*"):
            if path.is_file():
                path.chmod(0o600)

    return _wallet_temp_dir.name


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

    config_dir = _resolve_oracle_config_dir()
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


def query_dataframe(
    connection,
    sql: str,
    params: dict | None = None,
) -> pd.DataFrame:
    safe_sql = validate_read_only_sql(sql)
    with connection.cursor() as cursor:
        cursor.execute(safe_sql, params or {})
        columns = [item[0].lower() for item in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)
