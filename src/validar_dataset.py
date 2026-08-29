#!/usr/bin/env python3
"""Valida estrutura, chaves, datas e totais do CSV longo de internações."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date
from pathlib import Path


COLUNAS = ["codigo_municipio", "municipio", "mes_referencia", "internacoes"]


def validar(caminho: Path) -> dict[str, int | str]:
    chaves: set[tuple[str, str]] = set()
    codigos: set[str] = set()
    meses: set[str] = set()
    nomes_por_codigo: dict[str, str] = {}
    totais_mensais: Counter[str] = Counter()
    total = 0
    linhas = 0

    with caminho.open("r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != COLUNAS:
            raise ValueError(f"Colunas inválidas: {leitor.fieldnames}; esperado: {COLUNAS}")

        for numero_linha, registro in enumerate(leitor, start=2):
            codigo = registro["codigo_municipio"]
            nome = registro["municipio"]
            mes = registro["mes_referencia"]
            internacoes = int(registro["internacoes"])

            if len(codigo) != 6 or not codigo.isdigit():
                raise ValueError(f"Código inválido na linha {numero_linha}: {codigo!r}")
            data_mes = date.fromisoformat(mes)
            if data_mes.day != 1 or data_mes.year != 2025:
                raise ValueError(f"Data inválida na linha {numero_linha}: {mes}")
            if internacoes < 0:
                raise ValueError(f"Internações negativas na linha {numero_linha}")

            chave = (codigo, mes)
            if chave in chaves:
                raise ValueError(f"Chave duplicada na linha {numero_linha}: {chave}")
            chaves.add(chave)

            nome_anterior = nomes_por_codigo.setdefault(codigo, nome)
            if nome_anterior != nome:
                raise ValueError(f"Nomes divergentes para o código {codigo}")

            codigos.add(codigo)
            meses.add(mes)
            totais_mensais[mes] += internacoes
            total += internacoes
            linhas += 1

    esperado = {
        "linhas": 3924,
        "municipios": 327,
        "meses": 12,
        "total_internacoes": 2896345,
    }
    observado = {
        "linhas": linhas,
        "municipios": len(codigos),
        "meses": len(meses),
        "total_internacoes": total,
    }
    if observado != esperado:
        raise ValueError(f"Validação divergente: observado={observado}; esperado={esperado}")

    return {
        **observado,
        "primeiro_mes": min(meses),
        "ultimo_mes": max(meses),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", type=Path)
    argumentos = parser.parse_args()
    resultado = validar(argumentos.arquivo)
    print("Dataset validado com sucesso:")
    for chave, valor in resultado.items():
        print(f"  {chave}: {valor}")


if __name__ == "__main__":
    main()
