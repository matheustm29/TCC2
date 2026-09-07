"""Análises do fator casa.

Concentra as correções de conteúdo do TCC1:

* `fator_casa_por_time` substitui a célula 39, que agregava `PHT` e `PAT` da mesma
  partida e por isso media o desempenho dos adversários, não o do grupo estudado.
* `taxa_conversao` usa razão de somas em vez de média de razões e dispensa o
  filtro `HST > 0`, que removia justamente as partidas de conversão zero.
* `contraste_publico` compara jogos com e sem torcida dentro da mesma temporada.
* `fator_casa_por_faixa` responde à pergunta da banca sobre primeiros e últimos
  colocados.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config, estatistica, preparacao


def fator_casa_por_time(
    longo: pd.DataFrame, min_temporadas: int = config.MIN_TEMPORADAS_RANKING
) -> pd.DataFrame:
    """Calcula o diferencial casa-fora de cada clube, na perspectiva do clube.

    Diferente da célula 39 do TCC1, aqui `pontos_fora` é o desempenho do próprio
    clube atuando como visitante. O formato longo torna o erro impossível: cada
    linha já é uma observação de um time, com o mando explícito.

    A coluna `n_temporadas` e o parâmetro `min_temporadas` existem porque o
    ranking do TCC1 era liderado pelo Hull, que disputou uma única temporada do
    recorte (19 jogos em casa), à frente de clubes com 11 temporadas.

    Args:
        longo: saída de `preparacao.formato_longo`.
        min_temporadas: clubes abaixo do mínimo recebem `amostra_suficiente=False`
            em vez de serem removidos, para que a limitação fique visível.
    """
    por_time_mando = longo.groupby(["time", "mando"]).agg(
        jogos=("pontos", "size"),
        pontos=("pontos", "mean"),
        gols_pro=("gols_pro", "mean"),
        gols_contra=("gols_contra", "mean"),
        saldo=("saldo", "mean"),
        chutes=("chutes", "mean"),
        chutes_alvo=("chutes_alvo", "mean"),
        escanteios=("escanteios", "mean"),
    )

    casa = por_time_mando.xs("casa", level="mando")
    fora = por_time_mando.xs("fora", level="mando")

    tabela = pd.DataFrame({
        "jogos_casa": casa["jogos"],
        "jogos_fora": fora["jogos"],
        "pontos_casa": casa["pontos"],
        "pontos_fora": fora["pontos"],
        "saldo_casa": casa["saldo"],
        "saldo_fora": fora["saldo"],
        "chutes_alvo_casa": casa["chutes_alvo"],
        "chutes_alvo_fora": fora["chutes_alvo"],
        "escanteios_casa": casa["escanteios"],
        "escanteios_fora": fora["escanteios"],
    })

    tabela["dif_pontos"] = tabela["pontos_casa"] - tabela["pontos_fora"]
    tabela["dif_saldo"] = tabela["saldo_casa"] - tabela["saldo_fora"]

    # Métrica sem efeito teto: quanto do espaço ainda disponível para melhorar o
    # clube converte em casa. Com pontos brutos, o Man City (2,05 fora) só pode
    # ganhar 0,95 e o Hull (0,32 fora) pode ganhar 2,68 — comparar diferenciais
    # crus penaliza mecanicamente os times fortes.
    espaco = 3 - tabela["pontos_fora"]
    tabela["ganho_relativo"] = np.where(espaco > 0, tabela["dif_pontos"] / espaco, np.nan)

    tabela["n_temporadas"] = longo.groupby("time")["Season"].nunique()
    tabela["amostra_suficiente"] = tabela["n_temporadas"] >= min_temporadas
    tabela["big_six"] = tabela.index.isin(config.BIG_SIX)

    return tabela.sort_values("dif_pontos", ascending=False)


def comparar_big_six(por_time: pd.DataFrame) -> estatistica.Resultado:
    """Compara o diferencial casa-fora do Big Six com o dos demais clubes.

    A unidade de análise é o clube, não a partida. É a correção da célula 39: lá,
    o `n` de 1.254 partidas dava a impressão de um teste poderoso, mas a
    comparação não era entre times — era entre mandantes e visitantes.
    """
    elegiveis = por_time[por_time["amostra_suficiente"]]
    grupo_big = elegiveis.loc[elegiveis["big_six"], "dif_pontos"]
    grupo_demais = elegiveis.loc[~elegiveis["big_six"], "dif_pontos"]

    return estatistica.comparar_grupos(
        grupo_big, grupo_demais,
        nome="Diferencial casa-fora: Big Six vs demais clubes",
        rotulo_a="big_six", rotulo_b="demais",
    )


def fator_casa_por_faixa(longo_com_posicao: pd.DataFrame) -> pd.DataFrame:
    """Fator casa por faixa de posição final, temporada a temporada.

    Responde à pergunta da banca: os times que terminam nas primeiras posições se
    comportam como os que terminam nas últimas, em relação ao mando de campo?

    A faixa é recalculada a cada temporada, ao contrário do `Big Six`, que é um
    rótulo fixo — o próprio TCC1 reconhece nas limitações que o grupo não é
    homogêneo ao longo do período.
    """
    agregado = longo_com_posicao.groupby(["faixa", "mando"]).agg(
        jogos=("pontos", "size"),
        pontos=("pontos", "mean"),
        gols_pro=("gols_pro", "mean"),
        gols_contra=("gols_contra", "mean"),
        chutes=("chutes", "mean"),
        chutes_alvo=("chutes_alvo", "mean"),
        escanteios=("escanteios", "mean"),
    )

    casa = agregado.xs("casa", level="mando")
    fora = agregado.xs("fora", level="mando")

    tabela = pd.DataFrame({
        "jogos_casa": casa["jogos"],
        "pontos_casa": casa["pontos"],
        "pontos_fora": fora["pontos"],
        "dif_pontos": casa["pontos"] - fora["pontos"],
        "gols_pro_casa": casa["gols_pro"],
        "gols_pro_fora": fora["gols_pro"],
        "dif_gols_pro": casa["gols_pro"] - fora["gols_pro"],
        "chutes_alvo_casa": casa["chutes_alvo"],
        "chutes_alvo_fora": fora["chutes_alvo"],
        "dif_chutes_alvo": casa["chutes_alvo"] - fora["chutes_alvo"],
        "escanteios_casa": casa["escanteios"],
        "escanteios_fora": fora["escanteios"],
        "dif_escanteios": casa["escanteios"] - fora["escanteios"],
    })

    return tabela.reindex([f for f in config.FAIXAS_POSICAO if f in tabela.index])


def dif_por_time_temporada(longo_com_posicao: pd.DataFrame) -> pd.DataFrame:
    """Diferencial casa-fora de cada time em cada temporada.

    Atende ao pedido de "ver o comportamento das equipes em cada temporada". É
    também a base para testes que usam o clube-temporada como unidade de análise.
    """
    agregado = longo_com_posicao.groupby(["Season", "time", "mando"]).agg(
        pontos=("pontos", "mean"),
        gols_pro=("gols_pro", "mean"),
        chutes_alvo=("chutes_alvo", "mean"),
        escanteios=("escanteios", "mean"),
    )

    casa = agregado.xs("casa", level="mando")
    fora = agregado.xs("fora", level="mando")

    tabela = pd.DataFrame({
        "pontos_casa": casa["pontos"],
        "pontos_fora": fora["pontos"],
        "dif_pontos": casa["pontos"] - fora["pontos"],
        "dif_chutes_alvo": casa["chutes_alvo"] - fora["chutes_alvo"],
        "dif_escanteios": casa["escanteios"] - fora["escanteios"],
    }).reset_index()

    chaves = longo_com_posicao[["Season", "time", "posicao", "faixa"]].drop_duplicates()
    return tabela.merge(chaves, on=["Season", "time"], validate="one_to_one")


def evolucao_temporal(longo: pd.DataFrame, janela: int = 3) -> pd.DataFrame:
    """Evolução por temporada de pontos, gols, chutes e escanteios.

    O TCC1 só acompanhava pontos e gols ao longo do tempo. A banca pediu
    explicitamente "média de outros dados: chutes, escanteios".

    Args:
        janela: janela da média móvel. O TCC1 documentava 3 no comentário e usava
            2 no código (`rolling(window=2)`); aqui o valor é explícito e único.
    """
    agregado = longo.groupby(["Season", "mando"]).agg(
        pontos=("pontos", "mean"),
        gols_pro=("gols_pro", "mean"),
        chutes=("chutes", "mean"),
        chutes_alvo=("chutes_alvo", "mean"),
        escanteios=("escanteios", "mean"),
        faltas=("faltas", "mean"),
        amarelos=("amarelos", "mean"),
    )

    casa = agregado.xs("casa", level="mando")
    fora = agregado.xs("fora", level="mando")

    tabela = pd.DataFrame(index=casa.index)
    for metrica in ("pontos", "gols_pro", "chutes", "chutes_alvo", "escanteios",
                    "faltas", "amarelos"):
        tabela[f"{metrica}_casa"] = casa[metrica]
        tabela[f"{metrica}_fora"] = fora[metrica]
        tabela[f"dif_{metrica}"] = casa[metrica] - fora[metrica]

    tabela = tabela.sort_index()
    tabela[f"dif_pontos_mm{janela}"] = (
        tabela["dif_pontos"].rolling(window=janela, min_periods=janela).mean()
    )
    return tabela.reset_index()


def taxa_conversao(df: pd.DataFrame) -> pd.DataFrame:
    """Taxa de conversão de chutes no alvo em gols, por mando.

    Duas correções sobre a célula 31 do TCC1:

    * A taxa é `soma(gols) / soma(chutes no alvo)`, não a média das razões por
      partida. A média de razões dá o mesmo peso a um jogo com 1 chute no alvo e a
      um com 12, e não é a taxa de conversão do período.
    * Sem o filtro `HST > 0 & AST > 0`. O filtro descartava 5,3% das partidas —
      não aleatoriamente, mas justamente aquelas de pior desempenho ofensivo, onde
      a conversão é zero por construção. Isso inflava as duas médias. Com razão de
      somas o denominador agregado nunca é zero e o filtro é desnecessário.
    """
    linhas = []
    for mando, gols, alvo in (
        ("casa", "FTHG", "HST"),
        ("fora", "FTAG", "AST"),
    ):
        total_gols = int(df[gols].sum())
        total_alvo = int(df[alvo].sum())
        # Bernoulli implícita: cada chute no alvo converte ou não.
        conversoes = np.concatenate([
            np.ones(total_gols), np.zeros(max(total_alvo - total_gols, 0))
        ])
        inferior, superior = estatistica.ic_bootstrap(conversoes)
        linhas.append({
            "mando": mando,
            "gols": total_gols,
            "chutes_alvo": total_alvo,
            "taxa_conversao": total_gols / total_alvo,
            "ic95_inf": inferior,
            "ic95_sup": superior,
        })
    return pd.DataFrame(linhas).set_index("mando")


def contraste_publico(longo: pd.DataFrame) -> pd.DataFrame:
    """Fator casa por regime de público, com recorte por data da partida.

    O TCC1 rotulava temporadas inteiras. A linha `2019/20 (sem publico)` desta
    tabela é o contraste mais valioso do estudo: mesma temporada, mesmos elencos,
    mesmo calendário, com e sem torcida.

    Partidas de público limitado aparecem em separado e não devem ser somadas a
    nenhum dos dois regimes — não sabemos quais receberam torcida.
    """
    recorte = longo.copy()
    rotulos_1920 = {"total": "(com público)", "sem": "(sem público)"}
    recorte["cenario"] = np.where(
        recorte["Season"] == "1920",
        "2019/20 " + recorte["publico"].map(rotulos_1920).fillna("(público limitado)"),
        np.where(recorte["publico"] == "total", "demais temporadas (com público)",
                 np.where(recorte["publico"] == "sem", "2020/21 (sem público)",
                          "2020/21 (público limitado)")),
    )

    agregado = recorte.groupby(["cenario", "mando"]).agg(
        jogos=("pontos", "size"),
        pontos=("pontos", "mean"),
        gols_pro=("gols_pro", "mean"),
        amarelos=("amarelos", "mean"),
        faltas=("faltas", "mean"),
    )

    casa = agregado.xs("casa", level="mando")
    fora = agregado.xs("fora", level="mando")

    return pd.DataFrame({
        "jogos": casa["jogos"],
        "pontos_casa": casa["pontos"],
        "pontos_fora": fora["pontos"],
        "dif_pontos": casa["pontos"] - fora["pontos"],
        "dif_gols": casa["gols_pro"] - fora["gols_pro"],
        "dif_amarelos": casa["amarelos"] - fora["amarelos"],
    }).sort_values("dif_pontos", ascending=False)


def teste_publico_intratemporada(
    df: pd.DataFrame, temporada: str = "1920"
) -> estatistica.Resultado:
    """Testa o efeito da ausência de público dentro de uma única temporada.

    Este é o contraste mais limpo disponível no estudo, e só se torna possível com
    a classificação de público por data. Dentro de 2019/20, os mesmos elencos, o
    mesmo calendário e as mesmas regras jogaram com e sem torcida — a única coisa
    que muda entre os dois grupos é o público.

    A comparação entre temporadas que o TCC1 fazia (pré-COVID contra 2020/21)
    confunde a ausência de torcida com tudo o mais que mudou em 2020/21:
    pré-temporada encurtada, calendário congestionado e cinco substituições.
    """
    recorte = df[df["Season"] == temporada]
    diferenca = recorte["pts_mandante"] - recorte["pts_visitante"]

    com_publico = diferenca[recorte["publico"] == "total"]
    sem_publico = diferenca[recorte["publico"] == "sem"]

    return estatistica.comparar_grupos(
        com_publico, sem_publico,
        nome=f"Vantagem do mandante em {temporada[:2]}/{temporada[2:]}: com público vs sem público",
        rotulo_a="com_publico", rotulo_b="sem_publico",
    )


def estudo_mudanca_estadio(
    longo_estendido: pd.DataFrame, min_jogos: int = 30
) -> pd.DataFrame:
    """Compara o fator casa de um clube antes e depois de mudar de estádio.

    A seção 4.5 do TCC1 descrevia este estudo sem nenhuma linha de código, e era
    inviável no recorte de 2015/16 em diante: o West Ham tinha uma única temporada
    no Upton Park e o Brentford sequer disputou a Premier League antes da mudança.
    Com o recorte estendido (2009/10 em diante) West Ham e Tottenham ganham linha
    de base; o Brentford segue impossível e por isso não entra na tabela.

    As métricas de finalização só são reportadas quando os dois períodos ficam do
    mesmo lado da quebra de série de 2013/14 (ver `config`). Sem esse cuidado, o
    West Ham "perderia" dois chutes no alvo por jogo ao mudar de estádio — efeito
    que é só a troca de critério do provedor dos dados.

    Args:
        longo_estendido: formato longo do recorte estendido.
        min_jogos: mínimo de jogos em casa de cada lado da mudança.
    """
    linhas = []
    for time, info in config.MUDANCAS_ESTADIO.items():
        jogos = longo_estendido[longo_estendido["time"] == time]
        if jogos.empty:
            continue
        corte = pd.Timestamp(info["data"])

        for rotulo, recorte in (
            ("antes", jogos[jogos["Date"] < corte]),
            ("depois", jogos[jogos["Date"] >= corte]),
        ):
            casa = recorte[recorte["mando"] == "casa"]
            fora = recorte[recorte["mando"] == "fora"]
            if len(casa) < min_jogos:
                continue
            comparavel = bool(
                (casa["Season"] >= config.PRIMEIRA_TEMPORADA_HST_COMPARAVEL).all()
            )
            linhas.append({
                "time": time,
                "periodo": rotulo,
                "estadio": info["de"] if rotulo == "antes" else info["para"],
                "jogos_casa": len(casa),
                "pontos_casa": casa["pontos"].mean(),
                "pontos_fora": fora["pontos"].mean(),
                "dif_pontos": casa["pontos"].mean() - fora["pontos"].mean(),
                "gols_casa": casa["gols_pro"].mean(),
                "chutes_alvo_casa": casa["chutes_alvo"].mean() if comparavel else np.nan,
                "hst_comparavel": comparavel,
            })

    if not linhas:
        return pd.DataFrame()

    tabela = pd.DataFrame(linhas).set_index(["time", "periodo"])

    # Se qualquer lado da comparação for incomparável, a métrica não deve ser
    # confrontada nem no lado "bom": a coluna inteira do clube é anulada.
    for time in tabela.index.get_level_values("time").unique():
        if not tabela.loc[time, "hst_comparavel"].all():
            tabela.loc[time, "chutes_alvo_casa"] = np.nan

    return tabela


def verificar_quebras_de_serie(longo: pd.DataFrame, tolerancia: float = 0.30) -> pd.DataFrame:
    """Sinaliza métricas com salto abrupto entre temporadas consecutivas.

    Uma variação grande de uma temporada para a outra numa métrica de volume é
    quase sempre mudança de critério do provedor, não mudança do jogo. Rodar esta
    checagem antes de qualquer comparação histórica evita atribuir a um clube um
    efeito que é da planilha.

    Args:
        tolerancia: variação relativa a partir da qual a temporada é sinalizada.
    """
    metricas = ["chutes", "chutes_alvo", "escanteios", "gols_pro", "faltas", "amarelos"]
    medias = longo.groupby("Season")[metricas].mean().sort_index()

    variacao = medias.pct_change().abs()
    suspeitas = []
    for metrica in metricas:
        for temporada, valor in variacao[metrica].items():
            if pd.notna(valor) and valor >= tolerancia:
                suspeitas.append({
                    "metrica": metrica,
                    "temporada": temporada,
                    "media_anterior": medias[metrica].shift(1)[temporada],
                    "media": medias[metrica][temporada],
                    "variacao_relativa": valor,
                })
    return pd.DataFrame(suspeitas)
