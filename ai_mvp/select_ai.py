"""Integração segura com Oracle Select AI: gerar SQL, validar e somente então executar."""

from __future__ import annotations

from .database import query_dataframe
from .sql_guard import validate_read_only_sql


def generate_sql(connection, prompt: str, profile_name: str) -> str:
    if not prompt.strip():
        raise ValueError("Escreva uma pergunta.")
    if not profile_name.strip():
        raise ValueError("Defina SELECT_AI_PROFILE no arquivo .env.")

    statement = """
        SELECT ADMIN.HOSPINTEL_GENERATE_SQL(:prompt) AS generated_sql
        FROM dual
    """
    with connection.cursor() as cursor:
        cursor.execute(statement, {"prompt": prompt})
        value = cursor.fetchone()[0]
    if hasattr(value, "read"):
        value = value.read()
    return validate_read_only_sql(str(value))


def ask_select_ai(connection, prompt: str, profile_name: str):
    sql = generate_sql(connection, prompt, profile_name)
    return sql, query_dataframe(connection, sql)

