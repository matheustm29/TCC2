"""Tema único de figuras e exportação para o LaTeX.

O TCC1 exportava apenas uma figura (`plt.savefig` na célula 20); as demais teriam
que ser recapturadas à mão. Aqui toda figura sai em PDF vetorial e PNG 300 dpi
com nome estável, de modo que `\\includegraphics` no LaTeX sempre aponte para a
versão atual dos dados.

Decisões de codificação visual:

* Identidade nunca depende só de cor: cada série carrega marcador e traço
  próprios, porque a monografia será impressa e pode sair em tons de cinza.
* Paleta categórica em ordem fixa (mandante = azul, visitante = laranja), nunca
  ciclada. Validada para daltonismo (ΔE mínimo 24,7 em protanopia).
* Nada de eixo duplo. Métricas de escalas diferentes viram figuras separadas.
* Grade e eixos recessivos; rótulos diretos onde substituem a leitura no eixo.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

from . import config

# Paleta categórica em ordem fixa.
AZUL = "#2a78d6"      # slot 1 — mandante
LARANJA = "#eb6834"   # slot 2 — visitante
AQUA = "#1baf7a"      # slot 3 — terceira categoria
VERMELHO = "#e34948"  # polo negativo do par divergente

TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_SUAVE = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
SUPERFICIE = "#fcfcfb"

CORES_MANDO = {"casa": AZUL, "fora": LARANJA}
MARCADORES_MANDO = {"casa": "o", "fora": "s"}
TRACOS_MANDO = {"casa": "-", "fora": "--"}

CORES_FAIXA = {
    "G6 (1-6)": AZUL,
    "Meio (7-14)": LARANJA,
    "Z6 (15-20)": AQUA,
}


def aplicar_tema() -> None:
    """Aplica o tema a todas as figuras seguintes."""
    mpl.rcParams.update({
        "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE,
        "savefig.facecolor": SUPERFICIE,
        "axes.edgecolor": EIXO,
        "axes.linewidth": 0.8,
        "axes.labelcolor": TINTA_SECUNDARIA,
        "axes.titlecolor": TINTA_PRIMARIA,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRADE,
        "grid.linewidth": 0.7,
        "grid.alpha": 1.0,
        "xtick.color": TINTA_SUAVE,
        "ytick.color": TINTA_SUAVE,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "lines.linewidth": 2.0,
        "lines.markersize": 8,
        "font.size": 10,
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,  # fontes embutidas, não convertidas em curvas
    })


def salvar(fig: plt.Figure, nome: str, dir_figuras: Path | None = None) -> list[Path]:
    """Salva a figura em PDF vetorial e PNG 300 dpi.

    Args:
        nome: nome do arquivo sem extensão. Use nomes estáveis — o LaTeX
            referencia esses caminhos.
    """
    dir_figuras = dir_figuras or config.DIR_FIGURAS
    dir_figuras.mkdir(parents=True, exist_ok=True)
    caminhos = []
    for extensao in ("pdf", "png"):
        caminho = dir_figuras / f"{nome}.{extensao}"
        fig.savefig(caminho)
        caminhos.append(caminho)
    plt.close(fig)
    return caminhos


def _rotular_temporada(codigo: str) -> str:
    """'1516' -> '15/16'."""
    return f"{codigo[:2]}/{codigo[2:]}"


def evolucao_pontos(evolucao, janela: int = 3) -> plt.Figure:
    """Pontos por jogo de mandantes e visitantes ao longo das temporadas."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    rotulos = [_rotular_temporada(s) for s in evolucao["Season"]]

    for mando in ("casa", "fora"):
        ax.plot(
            rotulos, evolucao[f"pontos_{mando}"],
            color=CORES_MANDO[mando], marker=MARCADORES_MANDO[mando],
            linestyle=TRACOS_MANDO[mando],
            label="Mandante" if mando == "casa" else "Visitante",
            markeredgecolor=SUPERFICIE, markeredgewidth=1.5,
        )

    ax.set_title("Média de pontos por jogo: mandantes e visitantes")
    ax.set_xlabel("Temporada")
    ax.set_ylabel("Pontos por jogo")
    ax.legend(loc="lower left")
    ax.grid(axis="x", visible=False)
    return fig


def diferencial_por_temporada(evolucao) -> plt.Figure:
    """Diferencial de pontos casa menos fora, por temporada.

    Codificação divergente: o sinal é a informação, então azul e vermelho marcam
    os polos e o zero é a referência neutra.
    """
    fig, ax = plt.subplots(figsize=(9, 4.5))
    rotulos = [_rotular_temporada(s) for s in evolucao["Season"]]
    valores = evolucao["dif_pontos"]
    cores = [AZUL if v >= 0 else VERMELHO for v in valores]

    ax.bar(rotulos, valores, color=cores, width=0.68)
    ax.axhline(0, color=EIXO, linewidth=1.0)

    for x, valor in zip(rotulos, valores):
        deslocamento = 0.012 if valor >= 0 else -0.012
        ax.text(
            x, valor + deslocamento, f"{valor:+.2f}",
            ha="center", va="bottom" if valor >= 0 else "top",
            fontsize=8.5, color=TINTA_SECUNDARIA,
        )

    ax.set_title("Diferencial de pontos por jogo (mandante − visitante)")
    ax.set_xlabel("Temporada")
    ax.set_ylabel("Diferença de pontos")
    ax.grid(axis="x", visible=False)
    ax.margins(y=0.18)
    return fig


def fator_casa_por_faixa(por_faixa) -> plt.Figure:
    """Diferencial casa-fora por faixa de posição final.

    Responde visualmente à pergunta da banca sobre primeiros e últimos colocados.
    """
    fig, ax = plt.subplots(figsize=(7, 4.2))
    faixas = list(por_faixa.index)
    valores = por_faixa["dif_pontos"]

    barras = ax.barh(faixas, valores, color=[CORES_FAIXA[f] for f in faixas], height=0.6)
    for barra, valor in zip(barras, valores):
        ax.text(
            valor + 0.008, barra.get_y() + barra.get_height() / 2,
            f"{valor:.3f}", va="center", fontsize=9.5, color=TINTA_SECUNDARIA,
        )

    ax.set_title("Vantagem do mandante por faixa de posição final")
    ax.set_xlabel("Diferencial de pontos por jogo (casa − fora)")
    ax.grid(axis="y", visible=False)
    ax.invert_yaxis()
    ax.margins(x=0.16)
    return fig


def volume_ofensivo_por_temporada(evolucao) -> plt.Figure:
    """Evolução de chutes no alvo e escanteios, por mando.

    Duas métricas de escalas diferentes ficam em painéis separados, nunca em eixo
    duplo. Atende ao pedido da banca por "média de outros dados: chutes,
    escanteios", que o TCC1 só mostrava agregada no período inteiro.
    """
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    rotulos = [_rotular_temporada(s) for s in evolucao["Season"]]

    painels = (
        (axes[0], "chutes_alvo", "Chutes no alvo por jogo"),
        (axes[1], "escanteios", "Escanteios por jogo"),
    )
    for ax, metrica, titulo in painels:
        for mando in ("casa", "fora"):
            ax.plot(
                rotulos, evolucao[f"{metrica}_{mando}"],
                color=CORES_MANDO[mando], marker=MARCADORES_MANDO[mando],
                linestyle=TRACOS_MANDO[mando],
                label="Mandante" if mando == "casa" else "Visitante",
                markeredgecolor=SUPERFICIE, markeredgewidth=1.5,
            )
        ax.set_title(titulo)
        ax.set_xlabel("Temporada")
        ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", rotation=45)

    axes[0].set_ylabel("Média por jogo")
    axes[0].legend(loc="upper left")
    fig.tight_layout()
    return fig


def dispersao_casa_fora(por_time) -> plt.Figure:
    """Pontos em casa contra pontos fora, um ponto por clube.

    A linha de identidade separa quem depende do mando. Só clubes com amostra
    suficiente recebem rótulo, para não dar destaque a quem tem uma temporada.
    """
    fig, ax = plt.subplots(figsize=(7.5, 6.5))

    grupos = (
        (~por_time["big_six"], "Demais clubes", LARANJA, "o", 55),
        (por_time["big_six"], "Big Six", AZUL, "D", 90),
    )
    for mascara, rotulo, cor, marcador, tamanho in grupos:
        recorte = por_time[mascara]
        ax.scatter(
            recorte["pontos_fora"], recorte["pontos_casa"],
            color=cor, marker=marcador, s=tamanho, label=rotulo,
            edgecolor=SUPERFICIE, linewidth=1.2, zorder=3,
        )

    limite = max(por_time["pontos_casa"].max(), por_time["pontos_fora"].max()) + 0.2
    ax.plot([0, limite], [0, limite], linestyle=":", color=TINTA_SUAVE,
            linewidth=1.5, label="Casa = fora", zorder=1)

    destaques = por_time[por_time["amostra_suficiente"] & (
        por_time["big_six"] | (por_time["dif_pontos"] > por_time["dif_pontos"].quantile(0.85))
    )]
    # Clubes de desempenho parecido ficam colados; alternar o lado do rótulo
    # evita que um texto cubra o marcador do vizinho.
    ordenados = destaques.sort_values("pontos_casa", ascending=False)
    for posicao, (nome, linha) in enumerate(ordenados.iterrows()):
        acima = posicao % 2 == 0
        ax.annotate(
            nome, (linha["pontos_fora"], linha["pontos_casa"]),
            xytext=(8, 4) if acima else (-8, -12),
            textcoords="offset points",
            ha="left" if acima else "right",
            fontsize=8.5, color=TINTA_SECUNDARIA,
        )

    ax.set_title("Desempenho em casa e fora, por clube")
    ax.set_xlabel("Pontos por jogo como visitante")
    ax.set_ylabel("Pontos por jogo como mandante")
    ax.legend(loc="upper left")
    return fig


def contraste_publico(contraste) -> plt.Figure:
    """Vantagem do mandante por regime de público."""
    fig, ax = plt.subplots(figsize=(9, 4.4))
    cenarios = list(contraste.index)
    valores = contraste["dif_pontos"]
    cores = [AZUL if v >= 0 else VERMELHO for v in valores]

    barras = ax.barh(cenarios, valores, color=cores, height=0.6)
    ax.axvline(0, color=EIXO, linewidth=1.0)

    for barra, valor in zip(barras, valores):
        deslocamento = 0.01 if valor >= 0 else -0.01
        ax.text(
            valor + deslocamento, barra.get_y() + barra.get_height() / 2,
            f"{valor:+.3f}", va="center",
            ha="left" if valor >= 0 else "right",
            fontsize=9.5, color=TINTA_SECUNDARIA,
        )

    ax.set_title("Vantagem do mandante por regime de público")
    ax.set_xlabel("Diferencial de pontos por jogo (casa − fora)")
    ax.grid(axis="y", visible=False)
    ax.invert_yaxis()
    ax.margins(x=0.22)
    return fig


def mando_ajustado_por_temporada(por_temporada) -> plt.Figure:
    """Parâmetro de mando do Dixon-Coles por temporada, com IC 95%.

    Diferente do diferencial bruto de pontos, `gamma` já está ajustado pela força
    dos times e pelo calendário, e vem com incerteza — o que deixa claro quando
    uma oscilação entre temporadas é ruído.
    """
    fig, ax = plt.subplots(figsize=(9, 4.6))
    rotulos = [_rotular_temporada(s) for s in por_temporada["Season"]]

    ax.errorbar(
        rotulos, por_temporada["gamma"],
        yerr=[
            por_temporada["gamma"] - por_temporada["ic95_inf"],
            por_temporada["ic95_sup"] - por_temporada["gamma"],
        ],
        fmt="o-", color=AZUL, ecolor=EIXO, elinewidth=1.5, capsize=4,
        markeredgecolor=SUPERFICIE, markeredgewidth=1.5,
    )
    ax.axhline(0, color=VERMELHO, linewidth=1.2, linestyle="--",
               label="Ausência de vantagem")

    ax.set_title("Vantagem do mandante ajustada por força do adversário (γ)")
    ax.set_xlabel("Temporada")
    ax.set_ylabel("γ — log da razão de gols")
    ax.legend(loc="lower left")
    ax.grid(axis="x", visible=False)
    return fig


def desempenho_preditivo(resumo) -> plt.Figure:
    """Log-loss dos modelos, do melhor para o pior.

    Log-loss é a métrica principal porque o problema é probabilístico: acurácia
    sozinha não distingue um modelo bem calibrado de um confiante e errado.
    """
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ordenado = resumo.sort_values("log_loss", ascending=False)

    cores = [AQUA if nome in ("frequencia_base", "sempre_casa", "odds_mercado")
             else AZUL for nome in ordenado.index]
    barras = ax.barh(list(ordenado.index), ordenado["log_loss"], color=cores, height=0.6)

    for barra, (valor, acuracia) in zip(
        barras, zip(ordenado["log_loss"], ordenado["acuracia"])
    ):
        ax.text(
            valor + 0.004, barra.get_y() + barra.get_height() / 2,
            f"{valor:.4f}  (acurácia {acuracia:.1%})",
            va="center", fontsize=9, color=TINTA_SECUNDARIA,
        )

    ax.set_title("Desempenho preditivo — validação temporal")
    ax.set_xlabel("Log-loss (menor é melhor)")
    ax.grid(axis="y", visible=False)
    ax.margins(x=0.30)
    return fig


def calibracao(curvas) -> plt.Figure:
    """Frequência observada contra probabilidade prevista, por modelo."""
    fig, ax = plt.subplots(figsize=(6.5, 6))

    ax.plot([0, 1], [0, 1], linestyle=":", color=TINTA_SUAVE, linewidth=1.5,
            label="Calibração perfeita", zorder=1)

    interessantes = [m for m in curvas["modelo"].unique()
                     if m not in ("frequencia_base", "sempre_casa")]
    cores = [AZUL, LARANJA, AQUA]
    marcadores = ["o", "s", "^"]

    for i, nome in enumerate(interessantes[:3]):
        recorte = curvas[curvas["modelo"] == nome]
        ax.plot(
            recorte["prob_prevista"], recorte["freq_observada"],
            marker=marcadores[i], color=cores[i], label=nome.replace("_", " "),
            markeredgecolor=SUPERFICIE, markeredgewidth=1.2, zorder=3,
        )

    ax.set_title("Calibração — vitória do mandante")
    ax.set_xlabel("Probabilidade prevista")
    ax.set_ylabel("Frequência observada")
    ax.legend(loc="upper left")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return fig
