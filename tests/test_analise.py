"""Testes das análises, com foco em travar os erros encontrados no TCC1."""

import numpy as np
import pandas as pd
import pytest

from tcc import analise, preparacao


def test_pontos_fora_sao_do_proprio_time_nao_dos_adversarios(liga_sintetica):
    """Trava o bug da célula 39 do TCC1.

    Lá, `groupby('Home_BigSix')` agregava PHT e PAT da mesma partida, de modo que
    a coluna "pontos fora" media o desempenho dos adversários visitantes. Na liga
    sintética todo mandante vence (exceto um empate), então nenhum time pode ter
    média fora maior que a média em casa.
    """
    df = preparacao.preparar(liga_sintetica)
    longo = preparacao.formato_longo(df)
    por_time = analise.fator_casa_por_time(longo, min_temporadas=1)

    assert (por_time["pontos_casa"] >= por_time["pontos_fora"]).all()
    assert (por_time["dif_pontos"] >= 0).all()

    # Alfa vence os 3 jogos em casa (3,0 pts/jogo) e perde os 3 fora (0,0).
    assert por_time.loc["Alfa", "pontos_casa"] == pytest.approx(3.0)
    assert por_time.loc["Alfa", "pontos_fora"] == pytest.approx(0.0)
    assert por_time.loc["Alfa", "dif_pontos"] == pytest.approx(3.0)


def test_jogos_casa_e_fora_sao_iguais_para_cada_time(liga_sintetica):
    df = preparacao.preparar(liga_sintetica)
    longo = preparacao.formato_longo(df)
    por_time = analise.fator_casa_por_time(longo, min_temporadas=1)

    assert (por_time["jogos_casa"] == por_time["jogos_fora"]).all()


def test_amostra_insuficiente_e_sinalizada(liga_sintetica):
    """O ranking do TCC1 era liderado por um time de uma única temporada."""
    df = preparacao.preparar(liga_sintetica)
    longo = preparacao.formato_longo(df)
    por_time = analise.fator_casa_por_time(longo, min_temporadas=3)

    assert (por_time["n_temporadas"] == 1).all()
    assert not por_time["amostra_suficiente"].any()


def test_taxa_conversao_usa_razao_de_somas():
    """Trava a correção da célula 31 do TCC1.

    Com duas partidas — uma de 1 gol em 1 chute no alvo, outra de 1 gol em 9 — a
    taxa de conversão é 2/10 = 0,20. A média das razões usada pelo TCC1 daria
    (1,00 + 0,111)/2 = 0,556, quase três vezes maior.
    """
    df = pd.DataFrame({
        "FTHG": [1, 1], "HST": [1, 9],
        "FTAG": [0, 0], "AST": [4, 4],
    })
    conversao = analise.taxa_conversao(df)

    assert conversao.loc["casa", "taxa_conversao"] == pytest.approx(0.2)

    media_de_razoes = np.mean([1 / 1, 1 / 9])
    assert conversao.loc["casa", "taxa_conversao"] != pytest.approx(media_de_razoes)


def test_taxa_conversao_nao_descarta_partidas_sem_chute_no_alvo():
    """O filtro `HST > 0` do TCC1 removia justamente a conversão zero.

    Aqui a segunda partida tem 0 gols em 5 chutes no alvo. Descartá-la elevaria a
    taxa de 1/10 para 1/5.
    """
    df = pd.DataFrame({
        "FTHG": [1, 0], "HST": [5, 5],
        "FTAG": [0, 0], "AST": [3, 3],
    })
    conversao = analise.taxa_conversao(df)

    assert conversao.loc["casa", "taxa_conversao"] == pytest.approx(0.1)


def test_evolucao_temporal_usa_a_janela_declarada():
    """O TCC1 documentava média móvel de 3 temporadas e usava `rolling(window=2)`."""
    linhas = []
    for i, temporada in enumerate(["1516", "1617", "1718", "1819"]):
        for _ in range(2):
            linhas.append({
                "Season": temporada, "mando": "casa", "pontos": float(i),
                "gols_pro": 1.0, "chutes": 10.0, "chutes_alvo": 4.0,
                "escanteios": 5.0, "faltas": 10.0, "amarelos": 2.0,
            })
            linhas.append({
                "Season": temporada, "mando": "fora", "pontos": 0.0,
                "gols_pro": 1.0, "chutes": 10.0, "chutes_alvo": 4.0,
                "escanteios": 5.0, "faltas": 10.0, "amarelos": 2.0,
            })
    longo = pd.DataFrame(linhas)

    evolucao = analise.evolucao_temporal(longo, janela=3)

    # dif_pontos por temporada: 0, 1, 2, 3. Média móvel de 3: NaN, NaN, 1, 2.
    esperado = [np.nan, np.nan, 1.0, 2.0]
    assert evolucao["dif_pontos_mm3"].round(6).tolist()[2:] == esperado[2:]
    assert evolucao["dif_pontos_mm3"].isna().sum() == 2
    assert "dif_pontos_mm3" in evolucao.columns


def test_fator_casa_por_faixa_separa_primeiros_e_ultimos(liga_sintetica):
    df = preparacao.preparar(liga_sintetica)
    longo = preparacao.formato_longo(df)
    tabela = preparacao.tabela_classificacao(df)
    longo_pos = preparacao.anexar_posicao(longo, tabela)
    por_faixa = analise.fator_casa_por_faixa(longo_pos)

    assert "dif_pontos" in por_faixa.columns
    assert "dif_chutes_alvo" in por_faixa.columns
    assert "dif_escanteios" in por_faixa.columns
    assert len(por_faixa) >= 1


def test_contraste_publico_separa_a_mesma_temporada(liga_com_covid):
    """A comparação mais valiosa: 2019/20 com e sem público, mesmos elencos."""
    df = preparacao.preparar(liga_com_covid)
    longo = preparacao.formato_longo(df)
    contraste = analise.contraste_publico(longo)

    cenarios = set(contraste.index)
    assert "2019/20 (com público)" in cenarios
    assert "2019/20 (sem público)" in cenarios
    # Jogos de público limitado não são somados a nenhum dos dois regimes.
    assert not any("limitado" in c and "sem" in c for c in cenarios)


def test_quebra_de_serie_e_detectada():
    """A fonte mudou o critério de chutes no alvo em 2013/14.

    A média da liga cai de ~7,1 para ~4,3 sem que gols ou chutes totais se movam.
    Comparar essa métrica através da fronteira produziria um efeito inexistente.
    """
    linhas = []
    for temporada, alvo in [("1213", 7.1), ("1314", 4.4), ("1415", 4.3)]:
        for _ in range(50):
            linhas.append({
                "Season": temporada, "chutes": 12.5, "chutes_alvo": alvo,
                "escanteios": 5.5, "gols_pro": 1.4, "faltas": 11.0, "amarelos": 2.0,
            })
    quebras = analise.verificar_quebras_de_serie(pd.DataFrame(linhas))

    assert not quebras.empty
    assert set(quebras["metrica"]) == {"chutes_alvo"}
    assert quebras.iloc[0]["temporada"] == "1314"


def test_serie_estavel_nao_gera_alarme_falso():
    linhas = []
    for temporada, alvo in [("2223", 4.40), ("2324", 4.93), ("2425", 4.55)]:
        for _ in range(50):
            linhas.append({
                "Season": temporada, "chutes": 12.5, "chutes_alvo": alvo,
                "escanteios": 5.5, "gols_pro": 1.4, "faltas": 11.0, "amarelos": 2.0,
            })
    assert analise.verificar_quebras_de_serie(pd.DataFrame(linhas)).empty


def test_estudo_de_estadio_anula_metrica_que_cruza_a_quebra():
    """O West Ham 'perderia' 2 chutes no alvo por jogo só por causa da fonte."""
    from tcc import config

    linhas = []
    for temporada, data, alvo in [
        ("1213", "2013-01-15", 7.0),   # antes da quebra e antes da mudança
        ("1415", "2015-01-15", 4.3),   # depois da quebra, antes da mudança
        ("1617", "2017-01-15", 4.3),   # depois da mudança
    ]:
        for dia in range(40):
            linhas.append({
                "Season": temporada,
                "Date": pd.Timestamp(data) + pd.Timedelta(days=dia),
                "time": "West Ham", "adversario": "Outro",
                "mando": "casa" if dia % 2 == 0 else "fora",
                "pontos": 1.5, "gols_pro": 1.4, "gols_contra": 1.2,
                "chutes": 12.0, "chutes_alvo": alvo, "escanteios": 5.0,
                "faltas": 11.0, "amarelos": 2.0, "vermelhos": 0.0,
                "publico": "total", "saldo": 0.2,
            })
    longo = pd.DataFrame(linhas)

    resultado = analise.estudo_mudanca_estadio(longo, min_jogos=10)

    assert not resultado.empty
    # O período "antes" cruza a quebra de 2013/14, então a métrica de finalização
    # é anulada nos dois períodos — não faz sentido comparar só um lado.
    assert resultado.loc[("West Ham", "antes"), "chutes_alvo_casa"] != resultado.loc[
        ("West Ham", "antes"), "chutes_alvo_casa"
    ]  # NaN != NaN
    assert pd.isna(resultado.loc[("West Ham", "depois"), "chutes_alvo_casa"])
    # Pontos e gols seguem comparáveis.
    assert pd.notna(resultado.loc[("West Ham", "antes"), "dif_pontos"])
