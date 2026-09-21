"""Limpeza, variáveis derivadas e tabela de classificação por temporada.

Corrige dois pontos do TCC1:

* A classificação de público era feita por temporada inteira (`covid_map`), o que
  contradiz a seção 3.3.2 da monografia — que afirma filtro por data — e é
  factualmente errado: apenas 92 dos 380 jogos de 2019/20 foram sem público.
* Não existia tabela de classificação. Sem ela é impossível responder à pergunta
  da banca sobre o comportamento dos primeiros frente aos últimos colocados.
"""

from __future__ import annotations

import pandas as pd

from . import config

COLUNAS_INTERESSE = [
    "Season", "Date", "HomeTeam", "AwayTeam",
    "FTHG", "FTAG", "FTR",
    "HTHG", "HTAG", "HTR",
    "HS", "AS", "HST", "AST",
    "HC", "AC", "HF", "AF",
    "HY", "AY", "HR", "AR",
]

COLUNAS_NUMERICAS = [
    "FTHG", "FTAG", "HTHG", "HTAG", "HS", "AS", "HST", "AST",
    "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR",
]

# Aplicados na ordem, cada um às linhas que casam com o padrão.
FORMATOS_DE_DATA = (
    (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
    (r"\d{2}/\d{2}/\d{4}", "%d/%m/%Y"),
    (r"\d{2}/\d{2}/\d{2}", "%d/%m/%y"),
)

PONTOS_MANDANTE = {"H": 3, "D": 1, "A": 0}
PONTOS_VISITANTE = {"A": 3, "D": 1, "H": 0}


class ErroDePreparacao(RuntimeError):
    """Levantado quando os dados não passam nas validações de preparação."""


def converter_datas(datas: pd.Series) -> pd.Series:
    """Converte a coluna de data lidando com os formatos das fontes.

    Três formatos aparecem na prática:

    * `YYYY-MM-DD` — espelho no GitHub;
    * `DD/MM/YYYY` — arquivos recentes do football-data.co.uk;
    * `DD/MM/YY` — arquivos antigos do football-data.co.uk.

    Como as temporadas são concatenadas antes da conversão, a coluna pode conter
    mais de um formato ao mesmo tempo. Deixar o pandas inferir sozinho não
    resolve: ele deduz um único formato a partir dos primeiros valores e converte
    todo o resto em `NaT`. Também não serve passar `dayfirst=True` para tudo,
    porque isso corrompe o formato ISO em silêncio — `2019-08-10` viraria 8 de
    outubro, deslocando as janelas de público sem gerar erro algum.

    Por isso cada formato é aplicado explicitamente às linhas que casam com ele.
    """
    if datas.dtype.kind == "M":
        return datas

    texto = datas.astype(str).str.strip()

    # Cada formato é normalizado para ISO e só no fim há uma única conversão.
    # Montar o resultado peça por peça faria o dtype depender de qual formato
    # apareceu primeiro, e duas fontes equivalentes devolveriam séries com dtypes
    # diferentes.
    iso = pd.Series(pd.NA, index=datas.index, dtype="object")
    pendentes = pd.Series(True, index=datas.index)

    for padrao, formato in FORMATOS_DE_DATA:
        alvo = pendentes & texto.str.fullmatch(padrao)
        if alvo.any():
            iso[alvo] = (
                pd.to_datetime(texto[alvo], format=formato, errors="coerce")
                .dt.strftime("%Y-%m-%d")
            )
            pendentes &= ~alvo

    return pd.to_datetime(iso, format="%Y-%m-%d", errors="coerce")


def _classificar_publico(datas: pd.Series) -> pd.Series:
    """Rotula cada partida como 'total', 'limitado' ou 'sem'.

    A granularidade é a partida, não a temporada. As janelas de público limitado
    ficam com rótulo próprio porque o público por partida não está disponível: as
    liberações de dez/2020 e maio/2021 variavam por clube e por semana. Supor
    presença ou ausência de torcida nesses jogos seria inventar dado.
    """
    rotulo = pd.Series("total", index=datas.index, dtype="object")
    for inicio, fim in config.JANELAS_SEM_PUBLICO:
        rotulo[datas.between(inicio, fim)] = "sem"
    for inicio, fim in config.JANELAS_PUBLICO_LIMITADO:
        rotulo[datas.between(inicio, fim)] = "limitado"
    return rotulo


def preparar(
    bruto: pd.DataFrame, colunas_extras: tuple[str, ...] = ()
) -> pd.DataFrame:
    """Devolve o dataset limpo com as variáveis derivadas do estudo.

    Args:
        bruto: consolidado de `coleta.carregar_bruto`.
        colunas_extras: colunas adicionais a preservar quando existirem no bruto,
            como as odds de mercado (`config.COLUNAS_ODDS`). Colunas pedidas mas
            ausentes na fonte são ignoradas em silêncio, porque a disponibilidade
            depende da fonte usada e o pipeline precisa rodar com as duas.

    Colunas acrescentadas:
        pts_mandante, pts_visitante  Pontos pela regra oficial (3/1/0).
        saldo_mandante               FTHG - FTAG.
        gols_totais                  FTHG + FTAG.
        publico                      'total' | 'limitado' | 'sem'.
        mandante_big_six             Booleano.
        visitante_big_six            Booleano.
    """
    faltantes = [c for c in COLUNAS_INTERESSE if c not in bruto.columns]
    if faltantes:
        raise ErroDePreparacao(f"Colunas ausentes no dataset bruto: {faltantes}")

    disponiveis = [c for c in colunas_extras if c in bruto.columns]
    df = bruto[COLUNAS_INTERESSE + disponiveis].copy()
    df["Date"] = converter_datas(df["Date"])

    if df["Date"].isna().any():
        invalidas = bruto.loc[df["Date"].isna(), "Date"]
        exemplos = invalidas.astype(str).str.strip().unique()[:5]
        temporadas = sorted(bruto.loc[df["Date"].isna(), "Season"].unique())
        raise ErroDePreparacao(
            f"{len(invalidas)} partidas com data inválida após a conversão.\n"
            f"  Temporadas afetadas: {temporadas}\n"
            f"  Exemplos de valor: {list(exemplos)}\n"
            f"  Formatos reconhecidos: {[f for _, f in FORMATOS_DE_DATA]}"
        )

    # O TCC1 checava nulos em apenas 5 colunas. Médias sobre colunas com NaN são
    # calculadas em silêncio sobre um denominador menor.
    nulos = df[COLUNAS_NUMERICAS].isna().sum()
    if nulos.any():
        raise ErroDePreparacao(
            f"Valores nulos nas colunas numéricas:\n{nulos[nulos > 0].to_string()}"
        )

    resultados_validos = set(PONTOS_MANDANTE)
    invalidos = set(df["FTR"].unique()) - resultados_validos
    if invalidos:
        raise ErroDePreparacao(f"Valores inesperados em FTR: {sorted(invalidos)}")

    df["pts_mandante"] = df["FTR"].map(PONTOS_MANDANTE)
    df["pts_visitante"] = df["FTR"].map(PONTOS_VISITANTE)
    df["saldo_mandante"] = df["FTHG"] - df["FTAG"]
    df["gols_totais"] = df["FTHG"] + df["FTAG"]
    df["publico"] = _classificar_publico(df["Date"])
    df["mandante_big_six"] = df["HomeTeam"].isin(config.BIG_SIX)
    df["visitante_big_six"] = df["AwayTeam"].isin(config.BIG_SIX)

    return df.sort_values(["Season", "Date"]).reset_index(drop=True)


def formato_longo(df: pd.DataFrame) -> pd.DataFrame:
    """Converte de uma linha por partida para duas linhas por partida.

    Cada partida vira duas observações — a do mandante e a do visitante — com as
    métricas sempre na perspectiva do time (`gols_pro`, `gols_contra`, ...).

    Este é o formato que evita o erro da célula 39 do TCC1: com uma linha por
    time por jogo, agrupar por time e por mando é direto, e não há como confundir
    o desempenho de um clube fora de casa com o dos adversários que o visitaram.
    """
    mandante = pd.DataFrame({
        "Season": df["Season"],
        "Date": df["Date"],
        "time": df["HomeTeam"],
        "adversario": df["AwayTeam"],
        "mando": "casa",
        "pontos": df["pts_mandante"],
        "gols_pro": df["FTHG"],
        "gols_contra": df["FTAG"],
        "chutes": df["HS"],
        "chutes_alvo": df["HST"],
        "escanteios": df["HC"],
        "faltas": df["HF"],
        "amarelos": df["HY"],
        "vermelhos": df["HR"],
        "publico": df["publico"],
    })
    visitante = pd.DataFrame({
        "Season": df["Season"],
        "Date": df["Date"],
        "time": df["AwayTeam"],
        "adversario": df["HomeTeam"],
        "mando": "fora",
        "pontos": df["pts_visitante"],
        "gols_pro": df["FTAG"],
        "gols_contra": df["FTHG"],
        "chutes": df["AS"],
        "chutes_alvo": df["AST"],
        "escanteios": df["AC"],
        "faltas": df["AF"],
        "amarelos": df["AY"],
        "vermelhos": df["AR"],
        "publico": df["publico"],
    })
    longo = pd.concat([mandante, visitante], ignore_index=True)
    longo["saldo"] = longo["gols_pro"] - longo["gols_contra"]
    return longo.sort_values(["Season", "Date", "time"]).reset_index(drop=True)


def tabela_classificacao(df: pd.DataFrame) -> pd.DataFrame:
    """Monta a classificação final de cada temporada.

    Ordena pelo critério oficial da Premier League: pontos, saldo de gols e gols
    marcados. Desempates seguintes (confronto direto, play-off) não são aplicados
    — na prática eles quase nunca alteram a faixa de posição, mas a limitação fica
    registrada aqui.

    Returns:
        DataFrame com uma linha por time por temporada, contendo `posicao`,
        `pontos`, `saldo_gols`, `gols_pro`, `gols_contra`, `vitorias`, `empates`,
        `derrotas` e `faixa` (G6 / Meio / Z6).
    """
    longo = formato_longo(df)

    tabela = longo.groupby(["Season", "time"]).agg(
        jogos=("pontos", "size"),
        pontos=("pontos", "sum"),
        gols_pro=("gols_pro", "sum"),
        gols_contra=("gols_contra", "sum"),
        vitorias=("pontos", lambda s: int((s == 3).sum())),
        empates=("pontos", lambda s: int((s == 1).sum())),
    ).reset_index()

    tabela["derrotas"] = tabela["jogos"] - tabela["vitorias"] - tabela["empates"]
    tabela["saldo_gols"] = tabela["gols_pro"] - tabela["gols_contra"]

    tabela = tabela.sort_values(
        ["Season", "pontos", "saldo_gols", "gols_pro"],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)

    tabela["posicao"] = tabela.groupby("Season").cumcount() + 1
    tabela["faixa"] = tabela["posicao"].map(_faixa_de_posicao)

    # Validação estrutural em vez de números fixos: numa liga de pontos corridos
    # em turno e returno, todo time joga 2 x (n_times - 1) partidas. Isso detecta
    # temporada incompleta ou partida duplicada sem depender do tamanho da liga.
    for temporada, grupo in tabela.groupby("Season"):
        n_times = len(grupo)
        jogos_esperados = 2 * (n_times - 1)
        if not (grupo["jogos"] == jogos_esperados).all():
            observado = grupo.loc[grupo["jogos"] != jogos_esperados, ["time", "jogos"]]
            raise ErroDePreparacao(
                f"Temporada {temporada}: com {n_times} times, cada um deveria ter "
                f"{jogos_esperados} jogos. Fora do padrão:\n{observado.to_string(index=False)}"
            )

    colunas = [
        "Season", "posicao", "time", "faixa", "jogos", "vitorias", "empates",
        "derrotas", "gols_pro", "gols_contra", "saldo_gols", "pontos",
    ]
    return tabela[colunas]


def _faixa_de_posicao(posicao: int) -> str:
    for nome, faixa in config.FAIXAS_POSICAO.items():
        if posicao in faixa:
            return nome
    raise ErroDePreparacao(f"Posição fora das faixas configuradas: {posicao}")


def anexar_posicao(longo: pd.DataFrame, tabela: pd.DataFrame) -> pd.DataFrame:
    """Anexa a posição final e a faixa do time e do adversário em cada partida."""
    chaves = tabela[["Season", "time", "posicao", "faixa"]]

    resultado = longo.merge(chaves, on=["Season", "time"], how="left", validate="many_to_one")
    resultado = resultado.merge(
        chaves.rename(columns={
            "time": "adversario",
            "posicao": "posicao_adversario",
            "faixa": "faixa_adversario",
        }),
        on=["Season", "adversario"],
        how="left",
        validate="many_to_one",
    )

    if resultado[["posicao", "posicao_adversario"]].isna().any().any():
        raise ErroDePreparacao("Falha ao cruzar partidas com a classificação.")

    return resultado
