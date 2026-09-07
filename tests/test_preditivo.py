"""Testes da modelagem preditiva.

O teste mais importante deste arquivo é o de vazamento: ele altera o placar de
uma partida e exige que nenhuma feature dessa mesma partida se mova.
"""

import numpy as np
import pandas as pd
import pytest

from tcc import preditivo, preparacao


def _liga_longa(n_temporadas: int = 3, semente: int = 11) -> pd.DataFrame:
    """Gera temporadas sintéticas de 6 times com forças fixas e mando real."""
    gerador = np.random.default_rng(semente)
    times = ["Alfa", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot"]
    forca = dict(zip(times, [0.5, 0.3, 0.0, -0.1, -0.3, -0.5]))

    linhas = []
    dia = pd.Timestamp("2015-08-08")
    for t in range(n_temporadas):
        temporada = f"{15 + t}{16 + t}"
        for casa in times:
            for fora in times:
                if casa == fora:
                    continue
                media_casa = np.exp(0.1 + forca[casa] - forca[fora] + 0.25)
                media_fora = np.exp(0.1 + forca[fora] - forca[casa])
                gols_casa = int(gerador.poisson(media_casa))
                gols_fora = int(gerador.poisson(media_fora))
                resultado = "H" if gols_casa > gols_fora else ("A" if gols_fora > gols_casa else "D")
                linhas.append({
                    "Date": dia, "HomeTeam": casa, "AwayTeam": fora,
                    "FTHG": gols_casa, "FTAG": gols_fora, "FTR": resultado,
                    "HTHG": 0, "HTAG": 0, "HTR": "D",
                    "HS": 12, "AS": 9, "HST": 5, "AST": 3,
                    "HC": 6, "AC": 4, "HF": 11, "AF": 12,
                    "HY": 2, "AY": 2, "HR": 0, "AR": 0,
                    "Season": temporada,
                })
                dia += pd.Timedelta(days=4)
    return pd.DataFrame(linhas)


@pytest.fixture
def features_sinteticas():
    df = preparacao.preparar(_liga_longa())
    longo = preparacao.formato_longo(df)
    return preditivo.construir_features(df, longo)


# ── A trava contra vazamento ─────────────────────────────────────────────────

def test_features_nao_usam_o_resultado_da_propria_partida():
    """Altera o placar de uma partida e exige que suas features não mudem.

    É o teste que separa um modelo preditivo legítimo de um que "adivinha" o
    passado. Se qualquer feature da partida `n` se mover quando só o placar da
    partida `n` muda, existe vazamento.
    """
    bruto = _liga_longa()

    def features_de(quadro):
        df = preparacao.preparar(quadro)
        longo = preparacao.formato_longo(df)
        base = preditivo.construir_features(df, longo)
        return base.sort_values(["Date", "HomeTeam"]).reset_index(drop=True)

    original = features_de(bruto)

    # Escolhe uma partida no meio da base e inverte o placar.
    posicao = len(bruto) // 2
    alterado = bruto.copy()
    alterado.loc[posicao, ["FTHG", "FTAG"]] = [7, 0]
    alterado.loc[posicao, "FTR"] = "H"

    modificado = features_de(alterado)

    chave = ["Date", "HomeTeam", "AwayTeam"]
    alvo_original = original.merge(
        alterado.loc[[posicao], chave], on=chave, how="inner"
    )
    alvo_modificado = modificado.merge(
        alterado.loc[[posicao], chave], on=chave, how="inner"
    )

    assert len(alvo_original) == 1 and len(alvo_modificado) == 1

    for feature in preditivo.FEATURES:
        assert alvo_original.iloc[0][feature] == pytest.approx(
            alvo_modificado.iloc[0][feature], abs=1e-9
        ), f"VAZAMENTO: a feature '{feature}' mudou ao alterar o placar da própria partida"


def test_alterar_uma_partida_muda_as_features_das_seguintes():
    """Contraprova do teste anterior.

    Se nada mudasse em partida nenhuma, o teste acima passaria por acidente — por
    exemplo, se as features fossem todas constantes.
    """
    bruto = _liga_longa()

    def features_de(quadro):
        df = preparacao.preparar(quadro)
        longo = preparacao.formato_longo(df)
        return preditivo.construir_features(df, longo).sort_values(
            ["Date", "HomeTeam"]
        ).reset_index(drop=True)

    original = features_de(bruto)
    posicao = len(bruto) // 2
    alterado = bruto.copy()
    alterado.loc[posicao, ["FTHG", "FTAG"]] = [7, 0]
    alterado.loc[posicao, "FTR"] = "H"
    modificado = features_de(alterado)

    posteriores = original.index > posicao
    assert not np.allclose(
        original.loc[posteriores, "elo_casa"],
        modificado.loc[posteriores, "elo_casa"],
    )


def test_nenhuma_estatistica_pos_jogo_entre_as_features():
    """HS, HST, HC, HF e cartões só existem depois do apito final."""
    proibidas = {"HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF",
                 "HY", "AY", "HR", "AR", "FTHG", "FTAG", "FTR",
                 "HTHG", "HTAG", "HTR", "pts_mandante", "pts_visitante",
                 "saldo_mandante", "gols_totais"}
    assert not (set(preditivo.FEATURES) & proibidas)


# ── Elo ──────────────────────────────────────────────────────────────────────

def test_elo_registra_o_rating_anterior_a_partida(features_sinteticas):
    """Todo time começa em 1500; a primeira partida de cada um usa esse valor."""
    primeira = features_sinteticas.sort_values("Date").iloc[0]
    assert primeira["elo_casa"] == pytest.approx(preditivo.ELO_INICIAL)
    assert primeira["elo_fora"] == pytest.approx(preditivo.ELO_INICIAL)


def test_elo_soma_zero_dentro_de_uma_temporada():
    """O Elo é de soma constante: o que um time ganha, o outro perde."""
    df = preparacao.preparar(_liga_longa(n_temporadas=1))
    com_elo = preditivo.calcular_elo(df)
    # Na primeira partida todos valem 1500; a média não pode ter derivado.
    assert com_elo["elo_casa"].mean() == pytest.approx(
        preditivo.ELO_INICIAL, abs=preditivo.ELO_INICIAL * 0.02
    )


def test_elo_separa_time_forte_de_time_fraco(features_sinteticas):
    ultimo = features_sinteticas.sort_values("Date").tail(80)
    elo_final = {}
    for _, linha in ultimo.iterrows():
        elo_final[linha["HomeTeam"]] = linha["elo_casa"]
    assert elo_final["Alfa"] > elo_final["Foxtrot"]


# ── Métricas ─────────────────────────────────────────────────────────────────

def test_log_loss_premia_a_previsao_correta():
    alvo = np.array(["H", "H", "A"])
    confiante = np.array([[0.9, 0.05, 0.05], [0.9, 0.05, 0.05], [0.05, 0.05, 0.9]])
    incerto = np.tile([1 / 3, 1 / 3, 1 / 3], (3, 1))

    assert preditivo.log_loss(confiante, alvo) < preditivo.log_loss(incerto, alvo)
    assert preditivo.log_loss(incerto, alvo) == pytest.approx(np.log(3), abs=1e-9)


def test_brier_e_zero_na_previsao_perfeita():
    alvo = np.array(["H", "D", "A"])
    perfeito = np.eye(3)[[0, 1, 2]]
    assert preditivo.brier(perfeito, alvo) == pytest.approx(0.0)


def test_acuracia_usa_a_classe_mais_provavel():
    alvo = np.array(["H", "A"])
    probabilidades = np.array([[0.5, 0.3, 0.2], [0.2, 0.3, 0.5]])
    assert preditivo.acuracia(probabilidades, alvo) == pytest.approx(1.0)


# ── Baselines e validação ────────────────────────────────────────────────────

def test_preditor_frequencia_base_reproduz_o_historico(features_sinteticas):
    historico = features_sinteticas[features_sinteticas["Season"] == "1516"]
    bloco = features_sinteticas[features_sinteticas["Season"] == "1617"].head(10)

    probabilidades = preditivo._preditor_frequencia_base(historico, bloco)

    assert probabilidades.shape == (len(bloco), 3)
    assert probabilidades.sum(axis=1) == pytest.approx(np.ones(len(bloco)))
    assert probabilidades[0, 0] == pytest.approx((historico["FTR"] == "H").mean())


def test_todos_os_modelos_veem_o_mesmo_historico(features_sinteticas):
    """Nenhum modelo pode receber mais informação que outro em cada previsão.

    Sem isso, a comparação mediria o protocolo de reajuste em vez da qualidade
    do modelo.
    """
    treino = features_sinteticas[features_sinteticas["Season"] < "1718"]
    teste = features_sinteticas[features_sinteticas["Season"] == "1718"].sort_values(
        preditivo.ORDENACAO
    )

    historicos = []

    def espiao(historico, bloco):
        historicos.append(len(historico))
        return np.tile([1 / 3, 1 / 3, 1 / 3], (len(bloco), 1))

    preditivo._prever_em_blocos(treino, teste, 10, espiao)
    segunda_passada = []

    def espiao2(historico, bloco):
        segunda_passada.append(len(historico))
        return np.tile([1 / 3, 1 / 3, 1 / 3], (len(bloco), 1))

    preditivo._prever_em_blocos(treino, teste, 10, espiao2)

    assert historicos == segunda_passada
    # O histórico só cresce, nunca encolhe nem salta para além do já jogado.
    assert historicos == sorted(historicos)
    assert historicos[0] == len(treino)


def test_baseline_odds_ausente_quando_a_fonte_nao_traz(features_sinteticas):
    """O espelho do GitHub não tem colunas de odds; o código não pode quebrar."""
    assert preditivo.baseline_odds(features_sinteticas) is None


def test_baseline_odds_remove_a_margem_da_casa():
    teste = pd.DataFrame({"B365H": [2.0], "B365D": [4.0], "B365A": [4.0]})
    probabilidades = preditivo.baseline_odds(teste)

    assert probabilidades.sum() == pytest.approx(1.0)
    # 1/2 + 1/4 + 1/4 = 1.0 exatamente: sem margem, as proporções se preservam.
    assert probabilidades[0, 0] == pytest.approx(0.5)


def test_validacao_temporal_nunca_treina_com_o_futuro(features_sinteticas, monkeypatch):
    """Captura as temporadas vistas em cada ajuste e exige que sejam anteriores."""
    vistas = []
    original = preditivo._preditor_sklearn

    def espiao(nome):
        preditor = original(nome)

        def envolver(historico, bloco):
            vistas.append((set(historico["Season"]), set(bloco["Season"])))
            return preditor(historico, bloco)

        return envolver

    monkeypatch.setattr(preditivo, "_preditor_sklearn", espiao)

    preditivo.validacao_temporal(
        features_sinteticas, temporadas_teste=("1617", "1718"), passo_reajuste=60
    )

    assert vistas
    for temporadas_historico, temporadas_bloco in vistas:
        # O histórico pode conter a própria temporada de teste (partidas já
        # jogadas), mas nunca uma temporada posterior à do bloco previsto.
        assert max(temporadas_historico) <= max(temporadas_bloco)


def test_validacao_temporal_produz_metricas_para_todos_os_modelos(features_sinteticas):
    metricas, previsoes = preditivo.validacao_temporal(
        features_sinteticas, temporadas_teste=("1718",), passo_reajuste=60
    )

    modelos_avaliados = set(metricas["modelo"])
    assert {"frequencia_base", "sempre_casa", "dixon_coles",
            "regressao_logistica", "gradient_boosting"} <= modelos_avaliados
    assert (metricas["log_loss"] > 0).all()
    assert previsoes


def test_curva_calibracao_soma_as_partidas(features_sinteticas):
    _, previsoes = preditivo.validacao_temporal(
        features_sinteticas, temporadas_teste=("1718",), passo_reajuste=60
    )
    curva = preditivo.curva_calibracao(previsoes, "dixon_coles", classe="H")

    assert not curva.empty
    assert curva["n"].sum() == 30  # 6 times, turno e returno


def test_previsao_recusa_teste_fora_de_ordem(features_sinteticas):
    """Ordem embaralhada desalinharia probabilidades e alvos em silêncio."""
    teste = features_sinteticas[features_sinteticas["Season"] == "1718"]
    treino = features_sinteticas[features_sinteticas["Season"] < "1718"]
    embaralhado = teste.sample(frac=1.0, random_state=3)

    with pytest.raises(ValueError, match="ordenadas por data"):
        preditivo._prever_em_blocos(
            treino, embaralhado, 30, preditivo._preditor_dixon_coles(0.0)
        )


def test_probabilidades_do_dixon_coles_alinham_com_as_partidas(features_sinteticas):
    """O time mais forte em casa contra o mais fraco tem de liderar a coluna H.

    Se as probabilidades voltassem numa ordem diferente da das partidas, este
    confronto não seria o de maior probabilidade de vitória do mandante.
    """
    teste = features_sinteticas[features_sinteticas["Season"] == "1718"].sort_values(
        preditivo.ORDENACAO
    )
    treino = features_sinteticas[features_sinteticas["Season"] < "1718"]

    probabilidades = preditivo._prever_em_blocos(
        treino, teste, 30, preditivo._preditor_dixon_coles(0.0)
    )

    posicao = int(probabilidades[:, 0].argmax())
    partida = teste.iloc[posicao]
    assert partida["HomeTeam"] == "Alfa"
    assert partida["AwayTeam"] == "Foxtrot"


def test_features_deixam_ausentes_para_imputacao_por_dobra(features_sinteticas):
    """A imputação não pode acontecer na construção das features.

    Preencher ali usaria a mediana de toda a base — temporadas de teste
    incluídas — para montar a estatística de imputação.
    """
    primeiras = features_sinteticas.sort_values(preditivo.ORDENACAO).head(6)
    assert primeiras[["forma_pontos_casa", "descanso_casa"]].isna().any().any()


def test_imputacao_usa_somente_a_mediana_do_treino():
    """Alterar drasticamente o teste não pode mudar os valores imputados."""
    treino = pd.DataFrame({c: [1.0, 2.0, 3.0] for c in preditivo.FEATURES})
    teste = pd.DataFrame({c: [np.nan, 500.0] for c in preditivo.FEATURES})

    _, teste_imputado = preditivo._imputar(treino, teste)

    # Mediana do treino é 2.0; a mediana do teste (500) é irrelevante.
    assert teste_imputado["elo_casa"].iloc[0] == pytest.approx(2.0)


def test_imputacao_preenche_todas_as_features(features_sinteticas):
    treino = features_sinteticas[features_sinteticas["Season"] < "1718"]
    teste = features_sinteticas[features_sinteticas["Season"] == "1718"]

    treino_imputado, teste_imputado = preditivo._imputar(treino, teste)

    assert not treino_imputado[preditivo.FEATURES].isna().any().any()
    assert not teste_imputado[preditivo.FEATURES].isna().any().any()


def test_preditor_dixon_coles_cobre_time_sem_parametro(features_sinteticas):
    """Clube ainda sem parâmetro recebe a frequência base, sem quebrar.

    O array devolvido pelo modelo pode ser uma vista somente leitura do
    DataFrame; o preenchimento precisa funcionar mesmo assim.
    """
    treino = features_sinteticas[features_sinteticas["Season"] == "1516"]
    bloco = features_sinteticas[features_sinteticas["Season"] == "1617"].head(5).copy()
    bloco.loc[bloco.index[0], "HomeTeam"] = "TimePromovido"

    preditor = preditivo._preditor_dixon_coles(0.0)
    saida = preditor(treino, bloco)

    assert saida.shape == (len(bloco), 3)
    assert not np.isnan(saida).any()
    assert saida.sum(axis=1) == pytest.approx(np.ones(len(bloco)), abs=1e-6)
