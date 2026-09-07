"""Constantes do estudo.

Centraliza tudo que o TCC1 tinha espalhado em células soltas, para que texto e
código não possam divergir.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DIR_RAW = RAIZ / "data" / "raw"
DIR_PROCESSED = RAIZ / "data" / "processed"
DIR_FIGURAS = RAIZ / "figuras"
DIR_TABELAS = RAIZ / "tabelas"

# ── Recorte temporal ──────────────────────────────────────────────────────────
# Recorte principal do estudo, idêntico ao do TCC1.
TEMPORADAS = (
    "1516", "1617", "1718", "1819", "1920", "2021",
    "2122", "2223", "2324", "2425", "2526",
)

# Recorte estendido, usado somente no estudo de caso de mudança de estádio
# (seção 4.5 do TCC1), que precisa de linha de base anterior a 2015/16.
TEMPORADAS_ESTENDIDAS = (
    "0910", "1011", "1112", "1213", "1314", "1415",
) + TEMPORADAS

JOGOS_POR_TEMPORADA = 380  # 20 equipes, turno e returno

# ── Janelas de público ────────────────────────────────────────────────────────
# O TCC1 classificava temporadas inteiras como "COVID", o que é impreciso: apenas
# 92 dos 380 jogos de 2019/20 foram sem público, e 2020/21 teve rodadas com
# público parcial. Aqui a classificação é por data da partida.
#
# ATENÇÃO: as janelas de público limitado (dez/2020 e maio/2021) dependiam do
# sistema de "tiers" e variavam por clube e por semana. Como não temos o público
# por partida, essas janelas recebem o rótulo 'limitado' e as análises que exigem
# um contraste limpo devem excluí-las (ver `analise.contraste_publico`), em vez de
# supor presença ou ausência de torcida.
JANELAS_SEM_PUBLICO = (
    ("2020-06-17", "2020-07-26"),  # retomada da 2019/20 após a paralisação
    ("2020-09-12", "2020-12-01"),  # início da 2020/21
    ("2020-12-20", "2021-05-16"),  # 2020/21 após o recuo das liberações
)

JANELAS_PUBLICO_LIMITADO = (
    ("2020-12-02", "2020-12-19"),  # liberação parcial por tiers
    ("2021-05-17", "2021-05-23"),  # rodadas finais da 2020/21
)

# ── Quebra de série nas estatísticas de finalização ───────────────────────────
# A média de chutes no alvo da liga cai de ~7,1 (2009/10 a 2012/13) para ~4,3
# (2013/14 em diante), enquanto gols e chutes totais seguem estáveis. Não é queda
# de desempenho: é mudança de critério do provedor, que antes contabilizava
# finalizações bloqueadas como chutes no alvo. Comparar HST/AST através dessa
# fronteira produz um efeito puramente artificial.
#
# O recorte principal (2015/16 em diante) está inteiramente depois da quebra e
# portanto não é afetado. Só o recorte estendido precisa do cuidado.
PRIMEIRA_TEMPORADA_HST_COMPARAVEL = "1314"

METRICAS_AFETADAS_PELA_QUEBRA = ("chutes_alvo",)

# ── Segmentações ──────────────────────────────────────────────────────────────
BIG_SIX = (
    "Arsenal", "Chelsea", "Liverpool",
    "Man City", "Man United", "Tottenham",
)

# Faixas de posição final, para responder à pergunta da banca sobre o
# comportamento dos primeiros colocados frente aos últimos.
FAIXAS_POSICAO = {
    "G6 (1-6)": range(1, 7),
    "Meio (7-14)": range(7, 15),
    "Z6 (15-20)": range(15, 21),
}

# Mínimo de temporadas para um clube entrar em rankings por time. O TCC1 colocava
# Hull (1 temporada, 19 jogos em casa) no topo do ranking, lado a lado com clubes
# de 11 temporadas.
MIN_TEMPORADAS_RANKING = 3

# ── Estatística ───────────────────────────────────────────────────────────────
ALFA = 0.05
N_BOOTSTRAP = 10_000
SEMENTE = 42

# ── Mudanças de sede no período estendido (seção 4.5) ─────────────────────────
# Data do primeiro jogo oficial em casa no novo estádio.
MUDANCAS_ESTADIO = {
    "West Ham": {
        "de": "Boleyn Ground (Upton Park)",
        "para": "London Stadium",
        "data": "2016-08-21",
    },
    "Tottenham": {
        "de": "White Hart Lane / Wembley",
        "para": "Tottenham Hotspur Stadium",
        "data": "2019-04-03",
    },
}
