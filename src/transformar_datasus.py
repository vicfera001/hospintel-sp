#!/usr/bin/env python3
"""Transforma a exportação larga do DATASUS SIH/SUS em CSV longo para Oracle.

Uso:
    python src/transformar_datasus.py \
        data/raw/sih_cnv_qisp153716177_181_5_154.csv \
        data/processed/internacoes_sp_2025_long.csv

O script utiliza apenas a biblioteca padrão do Python.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from pathlib import Path


MESES = {
    "Jan": 1,
    "Fev": 2,
    "Mar": 3,
    "Abr": 4,
    "Mai": 5,
    "Jun": 6,
    "Jul": 7,
    "Ago": 8,
    "Set": 9,
    "Out": 10,
    "Nov": 11,
    "Dez": 12,
}


def normalizar_nome(texto: str) -> str:
    """Remove acentos, preserva espaços e devolve o nome em maiúsculas."""
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return " ".join(sem_acentos.upper().split())


def ler_tabela_datasus(caminho: Path) -> tuple[list[str], list[list[str]], list[str]]:
    """Localiza o cabeçalho do TabNet e devolve cabeçalho, municípios e total."""
    with caminho.open("r", encoding="latin-1", newline="") as arquivo:
        linhas = list(csv.reader(arquivo, delimiter=";", quotechar='"'))

    indice_cabecalho = next(
        (i for i, linha in enumerate(linhas) if linha and linha[0] == "Município"),
        None,
    )
    if indice_cabecalho is None:
        raise ValueError("Cabeçalho 'Município' não encontrado no arquivo DATASUS.")

    cabecalho = linhas[indice_cabecalho]
    registros: list[list[str]] = []
    total_publicado: list[str] | None = None

    for linha in linhas[indice_cabecalho + 1 :]:
        if not linha:
            continue
        if linha[0] == "Total":
            total_publicado = linha
            break
        if len(linha) == len(cabecalho) and re.match(r"^\d{6}\s+", linha[0]):
            registros.append(linha)

    if total_publicado is None:
        raise ValueError("Linha de total geral não encontrada.")
    return cabecalho, registros, total_publicado


def transformar(entrada: Path, saida: Path) -> dict[str, int]:
    cabecalho, registros, total_publicado = ler_tabela_datasus(entrada)

    colunas_mensais: list[tuple[int, int]] = []
    for indice, titulo in enumerate(cabecalho[1:13], start=1):
        try:
            ano_texto, mes_abreviado = titulo.split("/", maxsplit=1)
            ano = int(ano_texto)
            mes = MESES[mes_abreviado]
        except (ValueError, KeyError) as erro:
            raise ValueError(f"Coluna mensal inválida: {titulo!r}") from erro
        colunas_mensais.append((ano, mes))

    saida.parent.mkdir(parents=True, exist_ok=True)
    totais_calculados = [0] * 12
    linhas_geradas = 0

    with saida.open("w", encoding="utf-8", newline="") as arquivo_saida:
        escritor = csv.writer(arquivo_saida, lineterminator="\n")
        escritor.writerow(["codigo_municipio", "municipio", "mes_referencia", "internacoes"])

        # Ordem mês -> município, igual ao arquivo que foi importado no Oracle.
        for indice_mes, (ano, mes) in enumerate(colunas_mensais, start=1):
            for linha in registros:
                correspondencia = re.match(r"^(\d{6})\s+(.+)$", linha[0])
                if correspondencia is None:
                    raise ValueError(f"Município inválido: {linha[0]!r}")

                codigo, nome = correspondencia.groups()
                valor_texto = linha[indice_mes].strip()
                internacoes = 0 if valor_texto in {"", "-"} else int(valor_texto)
                if internacoes < 0:
                    raise ValueError(f"Valor negativo para o município {codigo}.")

                escritor.writerow(
                    [codigo, normalizar_nome(nome), f"{ano:04d}-{mes:02d}-01", internacoes]
                )
                totais_calculados[indice_mes - 1] += internacoes
                linhas_geradas += 1

    totais_origem = [int(valor) for valor in total_publicado[1:13]]
    if totais_calculados != totais_origem:
        raise ValueError(
            f"Totais mensais divergentes. Calculados={totais_calculados}; origem={totais_origem}"
        )

    total_geral = sum(totais_calculados)
    if total_geral != int(total_publicado[13]):
        raise ValueError("Total geral divergente da linha publicada pelo DATASUS.")

    return {
        "municipios": len(registros),
        "meses": len(colunas_mensais),
        "linhas": linhas_geradas,
        "total_internacoes": total_geral,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="CSV bruto exportado pelo DATASUS")
    parser.add_argument("saida", type=Path, help="CSV longo em UTF-8")
    argumentos = parser.parse_args()
    resultado = transformar(argumentos.entrada, argumentos.saida)
    print("Transformação concluída:")
    for chave, valor in resultado.items():
        print(f"  {chave}: {valor}")


if __name__ == "__main__":
    main()
