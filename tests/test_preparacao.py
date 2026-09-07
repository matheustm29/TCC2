"""Testes da preparação: variáveis derivadas, público por data e classificação."""

import pandas as pd
import pytest

from tcc import preparacao


def test_pontos_seguem_a_regra_oficial(liga_sintetica):
    df = preparacao.preparar(liga_sintetica)
    vitorias_casa = df[df["FTR"] == "H"]
    empates = df[df["FTR"] == "D"]

    assert (vitorias_casa["pts_mandante"] == 3).all()
    assert (vitorias_casa["pts_visitante"] == 0).all()
    assert (empates["pts_mandante"] == 1).all()
    assert (empates["pts_visitante"] == 1).all()


def test_soma_de_pontos_da_partida_e_sempre_2_ou_3(liga_sintetica):
    df = preparacao.preparar(liga_sintetica)
    soma = df["pts_mandante"] + df["pts_visitante"]
    assert set(soma.unique()) <= {2, 3}


def test_publico_e_classificado_por_data_nao_por_temporada(liga_com_covid):
    df = preparacao.preparar(liga_com_covid)
    por_data = dict(zip(df["Date"].dt.strftime("%Y-%m-%d"), df["publico"]))

    # A mesma temporada 2019/20 tem jogos com e sem público. O TCC1 rotulava a
    # temporada inteira como "COVID (Parcial)".
    assert por_data["2019-08-10"] == "total"
    assert por_data["2020-02-01"] == "total"
    assert por_data["2020-06-20"] == "sem"
    assert por_data["2020-07-10"] == "sem"

    # A janela de liberação parcial não é tratada como ausência de público.
    assert por_data["2020-12-10"] == "limitado"
    assert por_data["2021-02-15"] == "sem"


def test_formato_longo_dobra_as_linhas_e_preserva_a_perspectiva(liga_sintetica):
    df = preparacao.preparar(liga_sintetica)
    longo = preparacao.formato_longo(df)

    assert len(longo) == 2 * len(df)
    assert set(longo["mando"].unique()) == {"casa", "fora"}

    # Os gols pró do visitante são os gols do visitante da partida, não do mandante.
    partida = df.iloc[0]
    linha_fora = longo[
        (longo["time"] == partida["AwayTeam"])
        & (longo["adversario"] == partida["HomeTeam"])
        & (longo["mando"] == "fora")
    ].iloc[0]
    assert linha_fora["gols_pro"] == partida["FTAG"]
    assert linha_fora["gols_contra"] == partida["FTHG"]
    assert linha_fora["pontos"] == partida["pts_visitante"]


def test_classificacao_soma_os_pontos_corretamente(liga_sintetica):
    df = preparacao.preparar(liga_sintetica)
    tabela = preparacao.tabela_classificacao(df)

    # 4 times, 6 jogos cada (3 em casa, 3 fora).
    assert len(tabela) == 4
    assert (tabela["jogos"] == 6).all()

    pontos = dict(zip(tabela["time"], tabela["pontos"]))
    # Todo mandante vence, exceto Charlie 1x1 Delta. Cada time joga 3 em casa.
    # Alfa e Bravo: 3 vitórias em casa = 9. Charlie: 2 vitórias + 1 empate = 7.
    # Delta: 3 vitórias em casa = 9, mais 1 empate fora = 10.
    assert pontos["Alfa"] == 9
    assert pontos["Bravo"] == 9
    assert pontos["Charlie"] == 7
    assert pontos["Delta"] == 10


def test_classificacao_ordena_por_pontos_saldo_e_gols(liga_sintetica):
    df = preparacao.preparar(liga_sintetica)
    tabela = preparacao.tabela_classificacao(df)

    assert tabela.iloc[0]["time"] == "Delta"
    assert list(tabela["posicao"]) == [1, 2, 3, 4]
    assert tabela["pontos"].is_monotonic_decreasing


def test_preparacao_rejeita_nulos_em_coluna_numerica(liga_sintetica):
    corrompido = liga_sintetica.copy()
    corrompido.loc[0, "HST"] = None
    with pytest.raises(preparacao.ErroDePreparacao, match="nulos"):
        preparacao.preparar(corrompido)


def test_preparacao_rejeita_resultado_invalido(liga_sintetica):
    corrompido = liga_sintetica.copy()
    corrompido.loc[0, "FTR"] = "X"
    with pytest.raises(preparacao.ErroDePreparacao, match="FTR"):
        preparacao.preparar(corrompido)


def test_colunas_extras_sao_preservadas_quando_existem(liga_sintetica):
    """As odds só existem na fonte primária e precisam sobreviver à preparação."""
    com_odds = liga_sintetica.copy()
    com_odds["B365H"] = 2.0
    com_odds["B365D"] = 3.4
    com_odds["B365A"] = 3.8

    df = preparacao.preparar(com_odds, colunas_extras=("B365H", "B365D", "B365A"))

    assert {"B365H", "B365D", "B365A"} <= set(df.columns)
    assert (df["B365H"] == 2.0).all()


def test_colunas_extras_ausentes_nao_quebram(liga_sintetica):
    """O espelho do GitHub não traz odds; o pipeline roda com as duas fontes."""
    df = preparacao.preparar(liga_sintetica, colunas_extras=("B365H", "B365D"))

    assert "B365H" not in df.columns
    assert len(df) == len(liga_sintetica)
