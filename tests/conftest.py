"""Fixtures compartilhadas: uma mini-liga sintética com fator casa conhecido."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))


def _partida(data, casa, fora, gols_casa, gols_fora, **extras):
    resultado = "H" if gols_casa > gols_fora else ("A" if gols_fora > gols_casa else "D")
    linha = {
        "Date": data, "HomeTeam": casa, "AwayTeam": fora,
        "FTHG": gols_casa, "FTAG": gols_fora, "FTR": resultado,
        "HTHG": 0, "HTAG": 0, "HTR": "D",
        "HS": 12, "AS": 9, "HST": 5, "AST": 3,
        "HC": 6, "AC": 4, "HF": 11, "AF": 12,
        "HY": 2, "AY": 2, "HR": 0, "AR": 0,
        "Season": "2324",
    }
    linha.update(extras)
    return linha


@pytest.fixture
def liga_sintetica():
    """Liga de 4 times, turno e returno (12 partidas), com fator casa embutido.

    Construída para que o resultado correto seja verificável na mão: todo
    mandante vence, exceto um empate. Assim o diferencial casa-fora de cada time
    é conhecido antes de rodar qualquer código.
    """
    times = ["Alfa", "Bravo", "Charlie", "Delta"]
    linhas = []
    dia = pd.Timestamp("2023-08-12")
    for casa in times:
        for fora in times:
            if casa == fora:
                continue
            # Charlie x Delta em casa termina empatado; o resto o mandante vence.
            if casa == "Charlie" and fora == "Delta":
                linhas.append(_partida(dia, casa, fora, 1, 1))
            else:
                linhas.append(_partida(dia, casa, fora, 2, 0))
            dia += pd.Timedelta(days=3)
    return pd.DataFrame(linhas)


@pytest.fixture
def liga_com_covid():
    """Partidas de 2019/20 em três regimes de público, para testar o recorte."""
    linhas = [
        _partida("2019-08-10", "Alfa", "Bravo", 2, 0, Season="1920"),      # com público
        _partida("2020-02-01", "Bravo", "Alfa", 1, 0, Season="1920"),      # com público
        _partida("2020-06-20", "Alfa", "Charlie", 0, 2, Season="1920"),    # sem público
        _partida("2020-07-10", "Charlie", "Alfa", 0, 1, Season="1920"),    # sem público
        _partida("2020-12-10", "Alfa", "Delta", 1, 1, Season="2021"),      # limitado
        _partida("2021-02-15", "Delta", "Alfa", 0, 3, Season="2021"),      # sem público
    ]
    return pd.DataFrame(linhas)
