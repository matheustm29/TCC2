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


# ─────────────────── diagramas estruturais ───────────────────
# Não dependem dos dados: descrevem a organização do processamento. Ficam aqui,
# e não num editor de diagramas, pela mesma razão das demais figuras — o que vai
# para a monografia é gerado por código.

def _caixa(ax, x, y, w, h, texto, *, cor=None, tinta=None, negrito=False,
           tamanho=9, mono=False, raio=0.02):
    """Retângulo arredondado com rótulo centralizado."""
    from matplotlib.patches import FancyBboxPatch
    cor = cor or SUPERFICIE
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={raio}",
        facecolor=cor, edgecolor=EIXO, linewidth=0.9, zorder=2,
    ))
    ax.text(
        x + w / 2, y + h / 2, texto,
        ha="center", va="center", zorder=3,
        fontsize=tamanho, color=tinta or TINTA_PRIMARIA,
        fontweight="bold" if negrito else "normal",
        family="monospace" if mono else None,
        linespacing=1.45,
    )


def _seta(ax, x1, y1, x2, y2, texto=None):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=TINTA_SECUNDARIA,
                        linewidth=1.1, shrinkA=0, shrinkB=0),
        zorder=4,
    )
    if texto:
        ax.text((x1 + x2) / 2 + 0.012, (y1 + y2) / 2, texto,
                ha="left", va="center", fontsize=7.5, color=TINTA_SUAVE)


def arquitetura_pipeline() -> plt.Figure:
    """Camadas do processamento, da fonte externa ao texto da monografia."""
    fig, ax = plt.subplots(figsize=(7.0, 6.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.grid(False)

    xe, we = 0.075, 0.40          # coluna dos módulos
    xd, wd = 0.555, 0.37          # coluna dos artefatos
    h = 0.082
    cx_e, cx_d = xe + we / 2, xd + wd / 2

    niveis = [0.885, 0.715, 0.545, 0.300, 0.130]

    # fonte externa, atravessando as duas colunas
    _caixa(ax, xe, niveis[0], wd + xd - xe, h,
           "Football-Data.co.uk\nCSV por temporada",
           cor="#eef1f6", negrito=True)

    etapas = [
        (1, "coleta.py", "data/raw/\nmanifesto SHA-256", "download único"),
        (2, "preparacao.py", "data/processed/\n4.180 × 29", "tratamento"),
    ]
    for idx, modulo, artefato, rotulo in etapas:
        y = niveis[idx]
        _caixa(ax, xe, y, we, h, modulo, negrito=True, mono=True)
        _caixa(ax, xd, y, wd, h, artefato, cor="#f6f5f1",
               tinta=TINTA_SECUNDARIA, tamanho=8.2, mono=True)
        _seta(ax, xe + we, y + h / 2, xd, y + h / 2)
        _seta(ax, cx_e, niveis[idx - 1], cx_e, y + h, rotulo)

    # camada de análise: quatro módulos lado a lado
    y = niveis[3]
    analise_h = 0.135
    larg = (wd + xd - xe)
    _caixa(ax, xe, y, larg, analise_h, "", cor="#f6f5f1")
    nomes = ["estatistica", "analise", "modelos", "preditivo"]
    passo = larg / len(nomes)
    for i, nome in enumerate(nomes):
        _caixa(ax, xe + 0.012 + i * passo, y + 0.016, passo - 0.024,
               analise_h - 0.032, nome, mono=True, tamanho=8.2, negrito=True)
    _seta(ax, cx_e, niveis[2], cx_e, y + analise_h, "análise e modelagem")

    # saída
    y = niveis[4]
    _caixa(ax, xe, y, we, h, "visualizacao.py", negrito=True, mono=True)
    _caixa(ax, xd, y, wd, h, "tabelas/  ·  figuras/\n→ LaTeX", cor="#eef1f6",
           tinta=TINTA_SECUNDARIA, tamanho=8.2, mono=True)
    _seta(ax, xe + we, y + h / 2, xd, y + h / 2)
    _seta(ax, cx_e, niveis[3], cx_e, y + h)

    # bandas laterais: o que atravessa todas as camadas
    for x, rotulo in ((0.028, "config.py"), (0.962, "tests/  81 casos")):
        ax.text(x, 0.505, rotulo, rotation=90, ha="center", va="center",
                fontsize=8, color=TINTA_SUAVE, family="monospace")
    for x in (0.047, 0.945):
        ax.plot([x, x], [0.13, 0.885 + h], color=EIXO, linewidth=0.8,
                linestyle=(0, (3, 3)), zorder=1)

    ax.set_title("Organização do processamento", pad=14)
    return fig


def validacao_temporal(temporadas_teste=None, por_temporada: int = 380,
                       passo: int = 10) -> plt.Figure:
    """Janelas expansivas e o reajuste em blocos dentro da temporada de teste."""
    temporadas_teste = list(temporadas_teste or
                            ("1819", "1920", "2021", "2122",
                             "2223", "2324", "2425", "2526"))
    todas = list(config.TEMPORADAS)
    fig, (ax, az) = plt.subplots(
        2, 1, figsize=(7.0, 5.4), gridspec_kw={"height_ratios": [3, 1],
                                               "hspace": 0.45})

    for eixo in (ax, az):
        eixo.grid(False)
        eixo.set_facecolor(SUPERFICIE)
        for lado in ("top", "right", "left", "bottom"):
            eixo.spines[lado].set_visible(False)

    for linha, temporada in enumerate(temporadas_teste):
        y = len(temporadas_teste) - linha - 1
        corte = todas.index(temporada)
        ax.barh(y, corte, left=0, height=0.62, color=AZUL, alpha=0.85,
                edgecolor=SUPERFICIE, linewidth=1.2)
        ax.barh(y, 1, left=corte, height=0.62, color=LARANJA,
                edgecolor=SUPERFICIE, linewidth=1.2)
        ax.text(corte + 1.18, y, _rotular_temporada(temporada),
                va="center", fontsize=8.5, color=TINTA_SECUNDARIA)

    ax.set_xlim(0, len(todas) + 1.6)
    ax.set_ylim(-0.7, len(temporadas_teste) - 0.3)
    ax.set_yticks([])
    ax.set_xticks(range(len(todas)))
    ax.set_xticklabels([_rotular_temporada(t) for t in todas],
                       fontsize=7.5, rotation=45, ha="right")
    ax.tick_params(length=0)
    ax.set_title("Validação temporal: a janela de treino só olha para trás",
                 pad=10)

    from matplotlib.patches import Patch
    # canto superior direito: as barras crescem para baixo, então sobra espaço lá
    ax.legend(handles=[Patch(facecolor=AZUL, label="treino"),
                       Patch(facecolor=LARANJA, label="teste")],
              loc="upper right", bbox_to_anchor=(1.0, 1.02), ncol=1)

    # painel inferior: o reajuste em blocos
    blocos = por_temporada // passo
    for i in range(blocos):
        az.barh(0, 0.84, left=i, height=0.5, color=LARANJA,
                alpha=0.35 + 0.65 * (i == 12), edgecolor="none")
    az.annotate(
        f"a cada {passo} partidas o histórico cresce\ne todos os modelos reajustam",
        xy=(12.4, 0.26), xytext=(16.5, 0.95), fontsize=8,
        color=TINTA_SECUNDARIA,
        arrowprops=dict(arrowstyle="-|>", color=TINTA_SECUNDARIA, linewidth=1.0),
    )
    az.set_xlim(-0.6, blocos + 0.6)
    az.set_ylim(-0.45, 1.5)
    az.set_yticks([])
    az.set_xticks([0, blocos // 2, blocos])
    az.set_xticklabels(["1", f"{por_temporada // 2}", f"{por_temporada}"],
                       fontsize=8)
    az.tick_params(length=0)
    az.set_xlabel("partida dentro da temporada de teste", fontsize=9)
    az.set_title(f"{blocos} blocos por temporada", fontsize=10, pad=6)
    return fig


def crisp_dm() -> plt.Figure:
    """As seis fases do CRISP-DM, o núcleo de dados e o ciclo externo.

    Desenhada a partir da descrição em Chapman et al. (2000). O anel externo
    envolve todas as fases, e não apenas o retorno ao entendimento do negócio:
    é o processo inteiro que se repete a cada iteração.
    """
    import numpy as np
    from matplotlib.patches import Circle, FancyArrowPatch

    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    ax.axis("off"); ax.grid(False)

    fases = {
        "negocio":     (0.335, 0.820, "Entendimento\ndo negócio"),
        "dados":       (0.665, 0.820, "Entendimento\ndos dados"),
        "preparacao":  (0.825, 0.500, "Preparação\ndos dados"),
        "modelagem":   (0.665, 0.180, "Modelagem"),
        "avaliacao":   (0.335, 0.180, "Avaliação"),
        "implantacao": (0.175, 0.500, "Implantação"),
    }
    w, h = 0.190, 0.120
    for x, y, rotulo in fases.values():
        _caixa(ax, x - w / 2, y - h / 2, w, h, rotulo,
               cor="#eef1f6", negrito=True, tamanho=8.5, raio=0.03)

    # núcleo: os dados, que todas as fases consultam
    ax.add_patch(Circle((0.5, 0.5), 0.098, facecolor=SUPERFICIE,
                        edgecolor=EIXO, linewidth=1.0, zorder=2))
    ax.text(0.5, 0.5, "Dados", ha="center", va="center", zorder=3,
            fontsize=10, fontweight="bold", color=TINTA_SECUNDARIA)

    def liga(a, b, duplo=False):
        (x1, y1, _), (x2, y2, _) = fases[a], fases[b]
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle="<|-|>" if duplo else "-|>",
            mutation_scale=10, color=TINTA_SECUNDARIA, linewidth=1.1,
            zorder=1, shrinkA=40, shrinkB=40,
        ))

    # os retornos entre fases vizinhas são o que caracteriza o modelo
    liga("negocio", "dados", duplo=True)
    liga("dados", "preparacao")
    liga("preparacao", "modelagem", duplo=True)
    liga("modelagem", "avaliacao")
    liga("avaliacao", "implantacao")
    liga("avaliacao", "negocio")

    # anel externo: o processo inteiro se repete, no sentido das fases
    raio = 0.470
    for inicio in (100, 10, -80, -170):
        angulos = np.radians(np.linspace(inicio, inicio - 70, 90))
        ax.plot(0.5 + raio * np.cos(angulos), 0.5 + raio * np.sin(angulos),
                color=AZUL, linewidth=1.6, solid_capstyle="round", zorder=1)
        a1, a2 = np.radians(inicio - 69), np.radians(inicio - 70)
        ax.annotate(
            "", xytext=(0.5 + raio * np.cos(a1), 0.5 + raio * np.sin(a1)),
            xy=(0.5 + raio * np.cos(a2), 0.5 + raio * np.sin(a2)),
            arrowprops=dict(arrowstyle="-|>", color=AZUL, linewidth=1.6,
                            shrinkA=0, shrinkB=0),
            zorder=1,
        )

    ax.set_title("As seis fases do CRISP-DM", pad=12)
    return fig
