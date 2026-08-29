"""Validação defensiva de SQL gerado pelo Oracle Select AI."""

from __future__ import annotations

import re


ALLOWED_OBJECTS = {
    "ADMIN.VW_INTERNACOES_DASHBOARD",
    "ADMIN.VW_INTERNACOES_MENSAIS",
    "ADMIN.VW_RANKING_MUNICIPIOS",
    "VW_INTERNACOES_DASHBOARD",
    "VW_INTERNACOES_MENSAIS",
    "VW_RANKING_MUNICIPIOS",
}

FORBIDDEN = {
    "ALTER", "BEGIN", "CALL", "COMMIT", "CREATE", "DECLARE", "DELETE",
    "DROP", "EXEC", "EXECUTE", "GRANT", "INSERT", "LOCK", "MERGE",
    "REVOKE", "ROLLBACK", "TRUNCATE", "UPDATE",
}


class UnsafeQueryError(ValueError):
    """A consulta não atende às regras de somente leitura do MVP."""


def validate_read_only_sql(sql: str) -> str:
    """Retorna SQL normalizado quando ele é um SELECT restrito às views permitidas."""
    if not sql or not sql.strip():
        raise UnsafeQueryError("A consulta SQL está vazia.")

    cleaned = sql.strip().rstrip(";").strip()
    upper = re.sub(r"\s+", " ", cleaned.upper()).replace('"', "")

    if "--" in cleaned or "/*" in cleaned or "*/" in cleaned:
        raise UnsafeQueryError("Comentários SQL não são aceitos.")
    if ";" in cleaned:
        raise UnsafeQueryError("Somente uma instrução SQL é permitida.")
    if not re.match(r"^(SELECT|WITH)\b", upper):
        raise UnsafeQueryError("Somente consultas SELECT são permitidas.")

    tokens = set(re.findall(r"\b[A-Z_]+\b", upper))
    blocked = sorted(tokens & FORBIDDEN)
    if blocked:
        raise UnsafeQueryError(f"Comando não permitido: {blocked[0]}.")

    object_scan = re.sub(r"\bEXTRACT\s*\([^)]*\)", " ", upper)
    object_refs = re.findall(r"\b(?:FROM|JOIN)\s+([A-Z][A-Z0-9_$#.]*)", object_scan)
    if not object_refs:
        raise UnsafeQueryError("A consulta precisa acessar uma view autorizada.")
    invalid = sorted({ref for ref in object_refs if ref not in ALLOWED_OBJECTS})
    if invalid:
        raise UnsafeQueryError(f"Objeto não autorizado: {invalid[0]}.")

    return cleaned
