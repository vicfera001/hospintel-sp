"""HospIntel SP - MVP Streamlit independente do Power BI."""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from ai_mvp.database import oracle_connection
from ai_mvp.demo import answer_demo, load_demo_data
from ai_mvp.select_ai import ask_select_ai


load_dotenv()
st.set_page_config(page_title="HospIntel SP", page_icon="🏥", layout="wide")

st.title("HospIntel SP")
st.caption(
    "Perguntas em linguagem natural sobre internações, capacidade hospitalar SUS "
    "e população dos municípios paulistas"
)

with st.sidebar:
    st.header("Configuração")
    mode = st.radio("Fonte da resposta", ["Demonstração local", "Oracle Select AI"])
    st.info("Este aplicativo é independente do Power BI. Ambos consultam a mesma base Oracle.")
    st.markdown(
        "**Views autorizadas**\n"
        "- VW_INTERNACOES_DASHBOARD\n"
        "- VW_INTERNACOES_MENSAIS\n"
        "- VW_RANKING_MUNICIPIOS\n"
        "- VW_PRESSAO_ASSISTENCIAL_POPULACAO"
    )
    st.caption(
        "Internações por leito SUS é um indicador relativo de pressão de demanda; "
        "não representa taxa de ocupação."
    )

examples = [
    "Qual foi o total de internações em 2025?",
    "Mostre a evolução mensal das internações.",
    "Quais são os 10 municípios com mais internações?",
    "Em janeiro de 2025, qual município teve mais internações por leito SUS?",
    "Compare as internações por 100 mil habitantes em janeiro de 2025.",
]
question = st.text_input("Faça uma pergunta em português", placeholder=examples[0])
selected = st.selectbox("Ou escolha um exemplo", ["Selecione..."] + examples)
if selected != "Selecione...":
    question = selected

if st.button("Analisar", type="primary", use_container_width=True):
    try:
        with st.spinner("Consultando os dados..."):
            if mode == "Demonstração local":
                answer, result, sql, chart = answer_demo(question, load_demo_data())
            else:
                with oracle_connection() as connection:
                    sql, result = ask_select_ai(
                        connection,
                        question,
                        os.getenv("SELECT_AI_PROFILE", ""),
                    )
                answer = f"A consulta retornou {len(result)} linha(s)."
                if {"municipio", "internacoes_por_leito_sus_mes"} <= set(result.columns):
                    chart = "pressure_beds"
                elif {"municipio", "internacoes_por_100_mil_hab"} <= set(result.columns):
                    chart = "pressure_population"
                else:
                    chart = "table"

        st.success(answer)
        if chart == "line" and {"mes_referencia", "internacoes"} <= set(result.columns):
            st.line_chart(result.set_index("mes_referencia")["internacoes"])
        elif chart == "bar" and {"municipio", "internacoes"} <= set(result.columns):
            st.bar_chart(result.set_index("municipio")["internacoes"])
        elif chart == "pressure_beds":
            st.bar_chart(result.set_index("municipio")["internacoes_por_leito_sus_mes"])
        elif chart == "pressure_population":
            st.bar_chart(result.set_index("municipio")["internacoes_por_100_mil_hab"])
        elif chart == "metric":
            st.metric("Total de internações", f"{int(result.iloc[0, 0]):,}".replace(",", "."))
        st.dataframe(result, use_container_width=True, hide_index=True)
        with st.expander("SQL utilizado"):
            st.code(sql, language="sql")
    except Exception as exc:
        st.error(str(exc))

st.divider()
st.caption(
    "MVP educacional. Apenas consultas de leitura às views autorizadas são permitidas. "
    "Fontes: SIH/SUS, CNES e IBGE."
)
