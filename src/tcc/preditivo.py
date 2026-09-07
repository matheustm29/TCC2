"""Modelagem preditiva com validação temporal.

O risco central desta etapa é **vazamento de dados**. As colunas `HS`, `HST`,
`HC`, `HF` do dataset só existem depois do apito final: usá-las para prever `FTR`
produz acurácia alta e um trabalho errado. É o erro mais comum em TCC de previsão
esportiva.

Aqui todas as features são construídas com informação estritamente anterior ao
apito inicial da partida — forma recente, rating Elo, dias de descanso, rodada e
regime de público. O módulo `tests/test_preditivo.py` contém uma trava
experimental para isso: alterar o placar de uma partida não pode mudar nenhuma
feature dessa mesma partida.

A validação é temporal (`walk-forward`): para prever uma temporada, o modelo só vê
temporadas anteriores. `train_test_split` aleatório embaralharia futuro com
passado e inflaria todas as métricas.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import config, modelos

CLASSES = ("H", "D", "A")

# Ordem total e única das partidas: nenhum clube joga duas vezes no mesmo dia,
# então esta chave não depende da estabilidade do algoritmo de ordenação.
ORDENACAO = ["Date", "HomeTeam"]

# Features disponíveis antes do apito inicial. Qualquer coluna de estatística de
# jogo (HS, HST, HC, HF, HY...) está deliberadamente fora desta lista.
FEATURES = [
    "elo_casa", "elo_fora", "elo_diferenca",
    "forma_pontos_casa", "forma_pontos_fora",
    "forma_gols_pro_casa", "forma_gols_pro_fora",
    "forma_gols_contra_casa", "forma_gols_contra_fora",
    "forma_casa_mandante", "forma_fora_visitante",
    "descanso_casa", "descanso_fora",
    "rodada", "sem_publico",
]

ELO_INICIAL = 1500.0
ELO_K = 20.0
ELO_VANTAGEM_CASA = 60.0
ELO_REGRESSAO_ENTRE_TEMPORADAS = 0.25  # puxa 25% em direção à média a cada ano


def _resultado_para_placar(ftr: str) -> float:
    return {"H": 1.0, "D": 0.5, "A": 0.0}[ftr]


def calcular_elo(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula o rating Elo de cada time imediatamente ANTES de cada partida.

    O rating é atualizado depois de registrar o valor usado na previsão, então a
    linha da partida nunca contém informação do seu próprio resultado.

    Entre temporadas os ratings regridem parcialmente à média, para refletir a
    troca de elencos e a entrada de times promovidos.
    """
    df = df.sort_values(ORDENACAO).reset_index(drop=True)
    ratings: dict[str, float] = {}
    temporada_anterior = None

    elo_casa = np.empty(len(df))
    elo_fora = np.empty(len(df))

    for posicao, partida in enumerate(df.itertuples(index=False)):
        if temporada_anterior is not None and partida.Season != temporada_anterior:
            for time in ratings:
                ratings[time] += ELO_REGRESSAO_ENTRE_TEMPORADAS * (
                    ELO_INICIAL - ratings[time]
                )
        temporada_anterior = partida.Season

        casa = ratings.setdefault(partida.HomeTeam, ELO_INICIAL)
        fora = ratings.setdefault(partida.AwayTeam, ELO_INICIAL)

        elo_casa[posicao] = casa
        elo_fora[posicao] = fora

        esperado_casa = 1 / (1 + 10 ** ((fora - casa - ELO_VANTAGEM_CASA) / 400))
        obtido_casa = _resultado_para_placar(partida.FTR)
        ajuste = ELO_K * (obtido_casa - esperado_casa)

        ratings[partida.HomeTeam] = casa + ajuste
        ratings[partida.AwayTeam] = fora - ajuste

    df["elo_casa"] = elo_casa
    df["elo_fora"] = elo_fora
    df["elo_diferenca"] = elo_casa - elo_fora
    return df


def _forma_por_time(longo: pd.DataFrame, janela: int) -> pd.DataFrame:
    """Média móvel das últimas `janela` partidas de cada time, sem a partida atual.

    O `shift(1)` é o que impede o vazamento: a média da partida `n` usa apenas as
    partidas `n-janela` até `n-1`.
    """
    longo = longo.sort_values(["time", "Date"]).copy()
    agrupado = longo.groupby("time", sort=False)

    for metrica in ("pontos", "gols_pro", "gols_contra"):
        longo[f"forma_{metrica}"] = (
            agrupado[metrica]
            .transform(lambda s: s.shift(1).rolling(janela, min_periods=1).mean())
        )

    longo["descanso"] = (
        agrupado["Date"].transform(lambda s: s.diff().dt.days)
    )

    # Forma específica de mando: como o time vem se saindo em casa (ou fora).
    por_time_mando = longo.groupby(["time", "mando"], sort=False)
    longo["forma_pontos_mando"] = por_time_mando["pontos"].transform(
        lambda s: s.shift(1).rolling(janela, min_periods=1).mean()
    )

    return longo


def construir_features(
    df: pd.DataFrame, longo: pd.DataFrame, janela: int = 5
) -> pd.DataFrame:
    """Monta a matriz de features pré-jogo.

    Args:
        df: partidas preparadas.
        longo: formato longo correspondente (`preparacao.formato_longo`).
        janela: número de partidas anteriores na média móvel de forma.

    Returns:
        O DataFrame de partidas acrescido das colunas de `FEATURES`, mais `alvo`.
    """
    base = calcular_elo(df.copy())
    forma = _forma_por_time(longo, janela)

    colunas_forma = [
        "Date", "time", "mando", "forma_pontos", "forma_gols_pro",
        "forma_gols_contra", "forma_pontos_mando", "descanso",
    ]

    do_mandante = forma[forma["mando"] == "casa"][colunas_forma].rename(columns={
        "time": "HomeTeam",
        "forma_pontos": "forma_pontos_casa",
        "forma_gols_pro": "forma_gols_pro_casa",
        "forma_gols_contra": "forma_gols_contra_casa",
        "forma_pontos_mando": "forma_casa_mandante",
        "descanso": "descanso_casa",
    }).drop(columns="mando")

    do_visitante = forma[forma["mando"] == "fora"][colunas_forma].rename(columns={
        "time": "AwayTeam",
        "forma_pontos": "forma_pontos_fora",
        "forma_gols_pro": "forma_gols_pro_fora",
        "forma_gols_contra": "forma_gols_contra_fora",
        "forma_pontos_mando": "forma_fora_visitante",
        "descanso": "descanso_fora",
    }).drop(columns="mando")

    base = base.merge(do_mandante, on=["Date", "HomeTeam"], how="left", validate="one_to_one")
    base = base.merge(do_visitante, on=["Date", "AwayTeam"], how="left", validate="one_to_one")

    base["rodada"] = base.groupby("Season").cumcount() // 10 + 1
    base["sem_publico"] = (base["publico"] == "sem").astype(int)
    base["alvo"] = base["FTR"]

    # Os ausentes (primeira partida de cada clube, sem histórico) ficam como NaN
    # de propósito. Preencher aqui com a mediana da base inteira usaria as
    # temporadas de teste para construir a estatística de imputação — uma forma
    # discreta de vazamento. A imputação acontece dentro de cada dobra da
    # validação temporal, a partir do treino apenas (ver `_imputar`).
    return base


def _imputar(treino: pd.DataFrame, teste: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Preenche ausentes com a mediana calculada SOMENTE no treino.

    A mediana é um parâmetro aprendido como qualquer outro: calculá-la sobre o
    conjunto completo deixaria a distribuição do teste influenciar o treino.
    """
    medianas = treino[FEATURES].median()
    return (
        treino.assign(**{c: treino[c].fillna(medianas[c]) for c in FEATURES}),
        teste.assign(**{c: teste[c].fillna(medianas[c]) for c in FEATURES}),
    )


# ── Métricas ──────────────────────────────────────────────────────────────────

def log_loss(probabilidades: np.ndarray, alvo: np.ndarray) -> float:
    """Log-loss multiclasse. Métrica principal: o problema é probabilístico."""
    indices = np.array([CLASSES.index(c) for c in alvo])
    prob_verdadeira = probabilidades[np.arange(len(alvo)), indices]
    return float(-np.mean(np.log(np.clip(prob_verdadeira, 1e-15, 1.0))))


def brier(probabilidades: np.ndarray, alvo: np.ndarray) -> float:
    """Brier score multiclasse (soma dos quadrados sobre as três classes)."""
    real = np.zeros_like(probabilidades)
    for i, classe in enumerate(alvo):
        real[i, CLASSES.index(classe)] = 1.0
    return float(np.mean(np.sum((probabilidades - real) ** 2, axis=1)))


def acuracia(probabilidades: np.ndarray, alvo: np.ndarray) -> float:
    previsto = np.array(CLASSES)[probabilidades.argmax(axis=1)]
    return float(np.mean(previsto == alvo))


def avaliar(probabilidades: np.ndarray, alvo: np.ndarray) -> dict:
    return {
        "log_loss": log_loss(probabilidades, alvo),
        "brier": brier(probabilidades, alvo),
        "acuracia": acuracia(probabilidades, alvo),
        "n": len(alvo),
    }


# ── Modelos ───────────────────────────────────────────────────────────────────

@dataclass
class Previsao:
    """Probabilidades de um modelo sobre um conjunto de teste."""

    modelo: str
    temporada: str
    probabilidades: np.ndarray
    alvo: np.ndarray
    detalhes: dict = field(default_factory=dict)


def baseline_odds(teste: pd.DataFrame, colunas=("B365H", "B365D", "B365A")) -> np.ndarray | None:
    """Converte odds de mercado em probabilidades, removendo a margem da casa.

    Este é o baseline difícil e o mais honesto do trabalho: as odds embutem
    informação que nenhuma feature deste módulo tem (escalações, lesões, mercado).
    Chegar perto delas já é um bom resultado, e dizer isso explicitamente vale
    mais do que uma comparação escolhida para favorecer o modelo.

    Returns:
        None quando a fonte de dados não traz as colunas de odds — é o caso do
        espelho do GitHub usado quando o portal está inacessível.
    """
    if not all(coluna in teste.columns for coluna in colunas):
        return None
    odds = teste[list(colunas)].to_numpy(dtype=float)
    if np.isnan(odds).any():
        return None
    implicitas = 1.0 / odds
    return implicitas / implicitas.sum(axis=1, keepdims=True)


def _prever_em_blocos(
    treino: pd.DataFrame,
    teste: pd.DataFrame,
    passo: int,
    ajustar_e_prever,
) -> np.ndarray:
    """Percorre a temporada de teste em blocos, reajustando a cada bloco.

    Todos os modelos passam por aqui, de modo que todos enxergam exatamente o
    mesmo conjunto de informação em cada previsão: o treino mais as partidas da
    temporada de teste que já aconteceram. Sem isso, um modelo que reestima
    parâmetros ao longo da temporada levaria vantagem sobre outro que não
    reestima, e a comparação mediria o protocolo em vez do modelo.

    Args:
        ajustar_e_prever: função `(historico, bloco) -> array (len(bloco), 3)`.
    """
    if not teste["Date"].is_monotonic_increasing:
        raise ValueError(
            "As partidas de teste precisam estar ordenadas por data. "
            "Use ORDENACAO como chave."
        )

    probabilidades = np.full((len(teste), 3), np.nan)

    for inicio in range(0, len(teste), passo):
        bloco = teste.iloc[inicio : inicio + passo]
        historico = pd.concat([treino, teste.iloc[:inicio]], ignore_index=True)
        probabilidades[inicio : inicio + len(bloco)] = ajustar_e_prever(historico, bloco)

    return probabilidades


def _preditor_dixon_coles(xi: float):
    """Devolve um preditor que reestima o Dixon-Coles a cada bloco."""
    def ajustar_e_prever(historico, bloco):
        modelo = modelos.ajustar_poisson(
            historico, xi=xi, referencia=bloco["Date"].min(),
            calcular_erro_padrao=False,
        )
        previsto = modelos.prever_partidas(modelo, bloco)
        # `to_numpy` pode devolver uma vista somente leitura do bloco de memória
        # do DataFrame; a cópia garante que o preenchimento abaixo funcione.
        saida = np.array(previsto[["H", "D", "A"]], dtype=float, copy=True)

        # Clubes recém-promovidos ainda não têm parâmetro no primeiro ajuste em
        # que aparecem; recorre-se à frequência base do histórico.
        faltantes = np.isnan(saida).any(axis=1)
        if faltantes.any():
            frequencias = np.array([(historico["FTR"] == c).mean() for c in CLASSES])
            saida[faltantes] = frequencias
        return saida

    return ajustar_e_prever


def _modelo_sklearn(nome: str):
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    if nome == "regressao_logistica":
        return make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, C=1.0, random_state=config.SEMENTE),
        )
    if nome == "gradient_boosting":
        return HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.05, max_depth=4,
            l2_regularization=1.0, random_state=config.SEMENTE,
        )
    raise ValueError(f"Modelo desconhecido: {nome}")


def _preditor_sklearn(nome: str):
    """Devolve um preditor que retreina o estimador a cada bloco."""
    def ajustar_e_prever(historico, bloco):
        estimador = _modelo_sklearn(nome)
        estimador.fit(historico[FEATURES], historico["alvo"])
        previsto = estimador.predict_proba(bloco[FEATURES])
        # sklearn ordena as classes alfabeticamente (A, D, H); reordena p/ H, D, A.
        ordem = [list(estimador.classes_).index(c) for c in CLASSES]
        return previsto[:, ordem]

    return ajustar_e_prever


def _preditor_frequencia_base(historico, bloco):
    """Frequências H/D/A do histórico, repetidas para todo o bloco."""
    frequencias = np.array([(historico["FTR"] == c).mean() for c in CLASSES])
    return np.tile(frequencias, (len(bloco), 1))


def _preditor_sempre_casa(historico, bloco):
    """Vitória do mandante com a confiança que o histórico justifica."""
    taxa_casa = float((historico["FTR"] == "H").mean())
    resto = (1 - taxa_casa) / 2
    return np.tile(np.array([taxa_casa, resto, resto]), (len(bloco), 1))


def validacao_temporal(
    features: pd.DataFrame,
    temporadas_teste: tuple[str, ...],
    xi: float = 0.0035,
    passo_reajuste: int = 10,
) -> tuple[pd.DataFrame, list[Previsao]]:
    """Executa a validação walk-forward sobre as temporadas indicadas.

    Para prever a temporada `t`, o conjunto de treino é tudo o que aconteceu
    antes dela; dentro da temporada, o histórico cresce a cada bloco de partidas
    e todos os modelos são reajustados sobre ele. Nenhum modelo enxerga o futuro
    em momento algum, e todos enxergam exatamente a mesma informação.

    Args:
        features: saída de `construir_features`.
        temporadas_teste: temporadas avaliadas, em ordem cronológica.
        xi: decaimento temporal do Dixon-Coles, por dia. 0,0035 corresponde a uma
            meia-vida de cerca de 200 dias.
        passo_reajuste: de quantas em quantas partidas todos os modelos são
            reajustados dentro da temporada de teste.

    Returns:
        Uma tabela de métricas por modelo e temporada, e a lista de previsões
        brutas (para curvas de calibração).
    """
    linhas = []
    previsoes = []

    for temporada in temporadas_teste:
        treino = features[features["Season"] < temporada]
        teste = features[features["Season"] == temporada].sort_values(ORDENACAO)

        if treino.empty or teste.empty:
            continue

        treino, teste = _imputar(treino, teste)
        alvo = teste["alvo"].to_numpy()

        preditores = {
            "frequencia_base": _preditor_frequencia_base,
            "sempre_casa": _preditor_sempre_casa,
            "dixon_coles": _preditor_dixon_coles(xi),
            "regressao_logistica": _preditor_sklearn("regressao_logistica"),
            "gradient_boosting": _preditor_sklearn("gradient_boosting"),
        }
        candidatos = {
            nome: _prever_em_blocos(treino, teste, passo_reajuste, preditor)
            for nome, preditor in preditores.items()
        }

        odds = baseline_odds(teste)
        if odds is not None:
            candidatos["odds_mercado"] = odds

        for nome, probabilidades in candidatos.items():
            metricas = avaliar(probabilidades, alvo)
            linhas.append({"modelo": nome, "Season": temporada, **metricas})
            previsoes.append(Previsao(nome, temporada, probabilidades, alvo))

    return pd.DataFrame(linhas), previsoes


def resumo_por_modelo(metricas: pd.DataFrame) -> pd.DataFrame:
    """Agrega as métricas de todas as temporadas de teste, ponderando por partidas."""
    def media_ponderada(grupo, coluna):
        return np.average(grupo[coluna], weights=grupo["n"])

    resumo = metricas.groupby("modelo").apply(
        lambda g: pd.Series({
            "log_loss": media_ponderada(g, "log_loss"),
            "brier": media_ponderada(g, "brier"),
            "acuracia": media_ponderada(g, "acuracia"),
            "n": g["n"].sum(),
            "temporadas": g["Season"].nunique(),
        }),
        include_groups=False,
    )
    return resumo.sort_values("log_loss")


def curva_calibracao(
    previsoes: list[Previsao], modelo: str, classe: str = "H", n_faixas: int = 10
) -> pd.DataFrame:
    """Frequência observada contra probabilidade prevista, em faixas.

    Um modelo bem calibrado põe os pontos sobre a diagonal: entre as partidas em
    que ele diz "70% de chance de vitória do mandante", o mandante deve vencer
    cerca de 70% das vezes. Acurácia sozinha não revela isso.
    """
    indice_classe = CLASSES.index(classe)
    previstas, observadas = [], []

    for previsao in previsoes:
        if previsao.modelo != modelo:
            continue
        previstas.append(previsao.probabilidades[:, indice_classe])
        observadas.append((previsao.alvo == classe).astype(float))

    if not previstas:
        return pd.DataFrame()

    previstas = np.concatenate(previstas)
    observadas = np.concatenate(observadas)

    faixas = np.linspace(0, 1, n_faixas + 1)
    indices = np.clip(np.digitize(previstas, faixas) - 1, 0, n_faixas - 1)

    linhas = []
    for faixa in range(n_faixas):
        mascara = indices == faixa
        if not mascara.any():
            continue
        linhas.append({
            "faixa_inferior": faixas[faixa],
            "faixa_superior": faixas[faixa + 1],
            "prob_prevista": float(previstas[mascara].mean()),
            "freq_observada": float(observadas[mascara].mean()),
            "n": int(mascara.sum()),
        })
    return pd.DataFrame(linhas)
