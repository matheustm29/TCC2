"""Testes de hipótese, intervalos de confiança e tamanhos de efeito.

Corrige os dois testes da célula 8 do TCC1:

* O qui-quadrado testava H0 uniforme (1/3, 1/3, 1/3). Essa nula é rejeitada mesmo
  num mundo sem fator casa, porque a taxa de empates no futebol nunca chega a
  33%. Ele mede "a distribuição não é uniforme", não "o mandante leva vantagem".
* O teste t aplicava `ttest_ind` a duas colunas da mesma partida. `pts_mandante` e
  `pts_visitante` são determinísticos entre si (H→3/0, D→1/1, A→0/3) e têm
  correlação de -0,95: a hipótese de independência não se sustenta.

Todas as funções devolvem, além do p-valor, o tamanho de efeito e o intervalo de
confiança — ausentes no TCC1. Com n = 4.180, p-valores minúsculos são baratos; o
que informa a magnitude do fenômeno é o tamanho de efeito.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

from . import config


@dataclass
class Resultado:
    """Resultado de um teste, no formato que vai para tabela e texto."""

    nome: str
    estatistica: float
    p_valor: float
    estimativa: float
    ic_inferior: float
    ic_superior: float
    tamanho_efeito: float | None = None
    nome_efeito: str = ""
    n: int = 0
    detalhes: dict = field(default_factory=dict)

    @property
    def significativo(self) -> bool:
        return self.p_valor < config.ALFA

    def linha(self) -> dict:
        return {
            "teste": self.nome,
            "n": self.n,
            "estimativa": self.estimativa,
            "ic95_inf": self.ic_inferior,
            "ic95_sup": self.ic_superior,
            "estatistica": self.estatistica,
            "p_valor": self.p_valor,
            "tamanho_efeito": self.tamanho_efeito,
            "medida_efeito": self.nome_efeito,
            "significativo": self.significativo,
        }


def vantagem_mandante_binomial(ftr: pd.Series) -> Resultado:
    """Testa se o mandante vence mais que o visitante entre os jogos decididos.

    H0: entre partidas que não terminam em empate, vitórias do mandante e do
    visitante são igualmente prováveis (p = 0,5).

    Condicionar nos jogos decididos remove os empates da conta, e com isso a
    hipótese nula passa a corresponder exatamente à pergunta de pesquisa — o que
    o qui-quadrado contra a distribuição uniforme não fazia.
    """
    vitorias_casa = int((ftr == "H").sum())
    vitorias_fora = int((ftr == "A").sum())
    decididos = vitorias_casa + vitorias_fora

    teste = stats.binomtest(vitorias_casa, decididos, 0.5, alternative="greater")
    ic = stats.binomtest(vitorias_casa, decididos, 0.5).proportion_ci(
        confidence_level=1 - config.ALFA
    )
    proporcao = vitorias_casa / decididos

    return Resultado(
        nome="Binomial — vitórias do mandante entre jogos decididos",
        estatistica=float(vitorias_casa),
        p_valor=float(teste.pvalue),
        estimativa=proporcao,
        ic_inferior=float(ic.low),
        ic_superior=float(ic.high),
        tamanho_efeito=proporcao / (1 - proporcao),
        nome_efeito="razão de chances casa/fora",
        n=decididos,
        detalhes={
            "vitorias_casa": vitorias_casa,
            "vitorias_fora": vitorias_fora,
            "empates": int((ftr == "D").sum()),
        },
    )


def distribuicao_resultados_qui2(ftr: pd.Series) -> Resultado:
    """Qui-quadrado com hipótese nula correta: H = A, empates na taxa observada.

    A nula do TCC1 (1/3 para cada resultado) embute a afirmação de que 33% dos
    jogos terminariam empatados, o que nenhuma teoria do fator casa prevê. Aqui a
    taxa de empates observada é tomada como dada e só se testa a simetria entre
    vitórias do mandante e do visitante.
    """
    contagem = ftr.value_counts()
    casa = int(contagem.get("H", 0))
    empate = int(contagem.get("D", 0))
    fora = int(contagem.get("A", 0))
    total = casa + empate + fora

    decididos_esperados = (casa + fora) / 2
    esperado = [decididos_esperados, empate, decididos_esperados]

    # Um parâmetro (a taxa de empates) foi estimado dos dados: 1 grau de
    # liberdade a menos do que o padrão do scipy.
    qui2, _ = stats.chisquare([casa, empate, fora], esperado)
    p_valor = float(stats.chi2.sf(qui2, df=1))

    return Resultado(
        nome="Qui-quadrado — simetria casa/fora dada a taxa de empates",
        estatistica=float(qui2),
        p_valor=p_valor,
        estimativa=(casa - fora) / total,
        ic_inferior=float("nan"),
        ic_superior=float("nan"),
        n=total,
        detalhes={"observado": [casa, empate, fora], "esperado": esperado},
    )


def diferenca_pontos_pareada(
    pts_mandante: pd.Series, pts_visitante: pd.Series
) -> Resultado:
    """Compara pontos de mandante e visitante respeitando o pareamento.

    As duas séries vêm da mesma partida, então o teste é sobre a diferença
    intrapartida (`pts_mandante - pts_visitante`), que assume apenas os valores
    -3, 0 e +3. Reporta-se o d de Cohen para amostras pareadas.
    """
    diferenca = (pts_mandante - pts_visitante).to_numpy(dtype=float)
    n = diferenca.size

    teste = stats.ttest_rel(pts_mandante, pts_visitante, alternative="greater")
    media = float(diferenca.mean())
    desvio = float(diferenca.std(ddof=1))
    erro_padrao = desvio / np.sqrt(n)
    critico = stats.t.ppf(1 - config.ALFA / 2, df=n - 1)

    return Resultado(
        nome="Teste t pareado — pontos do mandante menos pontos do visitante",
        estatistica=float(teste.statistic),
        p_valor=float(teste.pvalue),
        estimativa=media,
        ic_inferior=media - critico * erro_padrao,
        ic_superior=media + critico * erro_padrao,
        tamanho_efeito=media / desvio,
        nome_efeito="d de Cohen (pareado)",
        n=n,
    )


def comparar_grupos(
    amostra_a: np.ndarray | pd.Series,
    amostra_b: np.ndarray | pd.Series,
    nome: str,
    rotulo_a: str = "A",
    rotulo_b: str = "B",
) -> Resultado:
    """Compara dois grupos independentes com Welch, d de Cohen e IC da diferença.

    Use apenas quando as observações forem de fato independentes entre os grupos —
    a comparação entre times, por exemplo, e não entre partidas de temporadas
    diferentes, onde a dependência dentro da temporada é forte.
    """
    a = np.asarray(amostra_a, dtype=float)
    b = np.asarray(amostra_b, dtype=float)

    teste = stats.ttest_ind(a, b, equal_var=False)
    diferenca = float(a.mean() - b.mean())

    erro_padrao = np.sqrt(a.var(ddof=1) / a.size + b.var(ddof=1) / b.size)
    graus = (a.var(ddof=1) / a.size + b.var(ddof=1) / b.size) ** 2 / (
        (a.var(ddof=1) / a.size) ** 2 / (a.size - 1)
        + (b.var(ddof=1) / b.size) ** 2 / (b.size - 1)
    )
    critico = stats.t.ppf(1 - config.ALFA / 2, df=graus)

    desvio_agrupado = np.sqrt(
        ((a.size - 1) * a.var(ddof=1) + (b.size - 1) * b.var(ddof=1))
        / (a.size + b.size - 2)
    )

    return Resultado(
        nome=nome,
        estatistica=float(teste.statistic),
        p_valor=float(teste.pvalue),
        estimativa=diferenca,
        ic_inferior=diferenca - critico * erro_padrao,
        ic_superior=diferenca + critico * erro_padrao,
        tamanho_efeito=diferenca / desvio_agrupado if desvio_agrupado else float("nan"),
        nome_efeito="d de Cohen",
        n=a.size + b.size,
        detalhes={
            f"media_{rotulo_a}": float(a.mean()), f"n_{rotulo_a}": int(a.size),
            f"media_{rotulo_b}": float(b.mean()), f"n_{rotulo_b}": int(b.size),
        },
    )


def ic_bootstrap(
    valores: np.ndarray | pd.Series,
    estatistica=np.mean,
    n_reamostras: int = config.N_BOOTSTRAP,
    semente: int = config.SEMENTE,
) -> tuple[float, float]:
    """Intervalo de confiança por bootstrap percentílico."""
    dados = np.asarray(valores, dtype=float)
    gerador = np.random.default_rng(semente)
    reamostras = gerador.choice(dados, size=(n_reamostras, dados.size), replace=True)
    distribuicao = estatistica(reamostras, axis=1)
    inferior, superior = np.percentile(
        distribuicao, [100 * config.ALFA / 2, 100 * (1 - config.ALFA / 2)]
    )
    return float(inferior), float(superior)


def ic_bootstrap_agrupado(
    df: pd.DataFrame,
    coluna_valor: str,
    coluna_grupo: str,
    n_reamostras: int = config.N_BOOTSTRAP,
    semente: int = config.SEMENTE,
) -> tuple[float, float]:
    """IC por bootstrap que reamostra grupos inteiros, não observações.

    Necessário quando as observações são dependentes dentro do grupo. No teste da
    COVID, por exemplo, o TCC1 tratou 1.520 partidas pré-pandemia como
    independentes, quando o que de fato varia entre os cenários é a temporada
    (4 contra 1). Reamostrar temporadas em vez de partidas produz um intervalo
    honesto, tipicamente bem mais largo.
    """
    grupos = [g[coluna_valor].to_numpy(dtype=float) for _, g in df.groupby(coluna_grupo)]
    gerador = np.random.default_rng(semente)
    n_grupos = len(grupos)

    medias = np.empty(n_reamostras)
    for i in range(n_reamostras):
        indices = gerador.integers(0, n_grupos, size=n_grupos)
        medias[i] = np.concatenate([grupos[j] for j in indices]).mean()

    inferior, superior = np.percentile(
        medias, [100 * config.ALFA / 2, 100 * (1 - config.ALFA / 2)]
    )
    return float(inferior), float(superior)


def tabela_resultados(resultados: list[Resultado]) -> pd.DataFrame:
    """Consolida vários resultados numa tabela pronta para exportação."""
    return pd.DataFrame([r.linha() for r in resultados])
