"""Análises locais determinísticas para demonstrar o MVP sem credenciais Oracle."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data" / "processed" / "internacoes_sp_2025_long.csv"


def load_demo_data(path: Path = DEFAULT_DATA) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"codigo_municipio": "string"}, parse_dates=["mes_referencia"])
    return df


def _normalize(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", plain.lower()).strip()


def answer_demo(question: str, df: pd.DataFrame) -> tuple[str, pd.DataFrame, str, str]:
    q = _normalize(question)
    if any(term in q for term in ["mes", "mensal", "evolucao", "evoluir", "tendencia"]):
        result = (df.groupby("mes_referencia", as_index=False)["internacoes"].sum()
                    .sort_values("mes_referencia"))
        peak = result.loc[result["internacoes"].idxmax()]
        answer = f"O maior total mensal ocorreu em {peak['mes_referencia']:%m/%Y}, com {int(peak['internacoes']):,} internações.".replace(",", ".")
        sql = "SELECT mes_referencia, total_internacoes FROM ADMIN.VW_INTERNACOES_MENSAIS ORDER BY mes_referencia"
        return answer, result, sql, "line"

    if any(term in q for term in ["ranking", "maiores", "mais internacoes", "top"]):
        match = re.search(r"\b(\d{1,2})\b", q)
        limit = min(int(match.group(1)), 50) if match else 10
        result = (df.groupby(["codigo_municipio", "municipio"], as_index=False)["internacoes"].sum()
                    .sort_values("internacoes", ascending=False).head(limit))
        answer = f"{result.iloc[0]['municipio']} lidera o ranking, com {int(result.iloc[0]['internacoes']):,} internações em 2025.".replace(",", ".")
        sql = f"SELECT * FROM ADMIN.VW_RANKING_MUNICIPIOS ORDER BY total_internacoes DESC FETCH FIRST {limit} ROWS ONLY"
        return answer, result, sql, "bar"

    if any(term in q for term in ["total", "quantas", "quantidade"]):
        total = int(df["internacoes"].sum())
        result = pd.DataFrame({"total_internacoes": [total]})
        answer = f"O conjunto contém {total:,} internações registradas em 2025.".replace(",", ".")
        sql = "SELECT SUM(internacoes) AS total_internacoes FROM ADMIN.VW_INTERNACOES_DASHBOARD"
        return answer, result, sql, "metric"

    raise ValueError("No modo demonstração, tente perguntar sobre total, evolução mensal ou ranking de municípios.")

