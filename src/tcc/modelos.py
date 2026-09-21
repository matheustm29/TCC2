"""Modelo de Poisson bivariado (Dixon-Coles) com termo de mando de campo.

Resolve a última lacuna metodológica do TCC1: nenhuma das métricas descritivas
controlava pela força do adversário. O "fator casa do Newcastle" misturava a
vantagem real do St. James' Park com o calendário que o Newcastle enfrentou —
sem ajuste, os dois são indistinguíveis.

Aqui cada clube recebe um parâmetro de ataque e um de defesa, e o mando de campo
entra como um parâmetro `gamma` compartilhado. Como `gamma` é estimado junto com
a força de todos os times, ele mede a vantagem do mandante *já descontada* a
qualidade de quem jogou contra quem.

Especificação
-------------
Para uma partida entre o mandante `i` e o visitante `j`, os gols são modelados
como Poisson com médias::

    lambda_casa = exp(mu + ataque_i - defesa_j + gamma)
    lambda_fora = exp(mu + ataque_j - defesa_i)

`gamma` é o log da razão entre o que um time marca em casa e o que o mesmo time
marcaria fora contra o mesmo adversário. `exp(gamma) - 1` é o acréscimo
percentual de gols atribuível ao mando.

A correção `tau` de Dixon e Coles (1997) ajusta a dependência nos placares
baixos (0-0, 1-0, 0-1, 1-1), onde o Poisson independente subestima empates.

Identificabilidade: ataque e defesa só são determinados a menos de uma constante,
então impõe-se média zero nos parâmetros de ataque.

Referência: DIXON, M. J.; COLES, S. G. Modelling association football scores and
inefficiencies in the football betting market. Journal of the Royal Statistical
Society: Series C, v. 46, n. 2, p. 265-280, 1997.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import optimize, stats

from . import config

MAX_GOLS = 12  # teto da grade de placares usada para derivar probabilidades

# O gradiente é aproximado por diferenças finitas, então cada iteração custa
# (n_parâmetros + 1) avaliações. Com 30 e poucos clubes o modelo passa de 60
# parâmetros e o limite padrão do L-BFGS-B (15.000) é atingido antes da
# convergência — o que fazia o ajuste falhar no meio da validação temporal.
# Tolerância apertada para os ajustes de inferência, onde a curvatura da
# verossimilhança perfilada precisa ser estável até a terceira casa.
OPCOES_OTIMIZADOR = {"maxfun": 300_000, "maxiter": 50_000, "ftol": 1e-10}

# Caminho de previsão: o erro padrão não é usado, então essa precisão toda só
# custa tempo. Com o reajuste a cada bloco de partidas são centenas de ajustes
# por execução, e a tolerância apertada levava a validação temporal de minutos a
# mais de uma hora. As probabilidades previstas não mudam de forma perceptível.
OPCOES_OTIMIZADOR_RAPIDO = {"maxfun": 100_000, "maxiter": 20_000, "ftol": 1e-7}


class ErroDeAjuste(RuntimeError):
    """Levantado quando a otimização não converge."""


@dataclass
class ModeloPoisson:
    """Parâmetros ajustados e as previsões que eles geram."""

    times: list[str]
    ataque: pd.Series
    defesa: pd.Series
    mu: float
    gamma: float
    rho: float
    erro_padrao_gamma: float
    log_verossimilhanca: float
    n_partidas: int
    convergiu: bool

    @property
    def ic_gamma(self) -> tuple[float, float]:
        """IC 95% do parâmetro de mando, na escala logarítmica."""
        critico = stats.norm.ppf(1 - config.ALFA / 2)
        return (
            self.gamma - critico * self.erro_padrao_gamma,
            self.gamma + critico * self.erro_padrao_gamma,
        )

    @property
    def acrescimo_percentual(self) -> float:
        """Acréscimo percentual de gols atribuível ao mando de campo."""
        return float(np.exp(self.gamma) - 1)

    def medias(self, mandante: str, visitante: str) -> tuple[float, float]:
        """Médias esperadas de gols da partida."""
        lambda_casa = np.exp(
            self.mu + self.ataque[mandante] - self.defesa[visitante] + self.gamma
        )
        lambda_fora = np.exp(self.mu + self.ataque[visitante] - self.defesa[mandante])
        return float(lambda_casa), float(lambda_fora)

    def probabilidades(self, mandante: str, visitante: str) -> dict[str, float]:
        """Probabilidades de vitória do mandante, empate e vitória do visitante."""
        lambda_casa, lambda_fora = self.medias(mandante, visitante)
        matriz = _matriz_placares(lambda_casa, lambda_fora, self.rho)
        return {
            "H": float(np.tril(matriz, -1).sum()),
            "D": float(np.trace(matriz)),
            "A": float(np.triu(matriz, 1).sum()),
        }

    def tabela_forcas(self) -> pd.DataFrame:
        """Força de ataque e defesa por clube, ordenada por ataque."""
        tabela = pd.DataFrame({
            "ataque": self.ataque,
            "defesa": self.defesa,
            "forca_liquida": self.ataque + self.defesa,
        })
        return tabela.sort_values("forca_liquida", ascending=False)


def _minimizar(funcao, inicial, limites, tentativas: int = 3, opcoes=None):
    """Minimiza com reinício a partir do último ponto quando o limite é atingido.

    O L-BFGS-B pode parar por esgotar avaliações sem ter convergido. Reiniciar do
    ponto onde parou preserva o progresso e costuma fechar a otimização na
    segunda passada; falhar alto na terceira evita seguir com um ajuste ruim.
    """
    opcoes = opcoes or OPCOES_OTIMIZADOR
    ponto = inicial
    resultado = None
    for _ in range(tentativas):
        resultado = optimize.minimize(
            funcao, ponto, method="L-BFGS-B", bounds=limites, options=opcoes,
        )
        if resultado.success:
            return resultado
        ponto = resultado.x

    raise ErroDeAjuste(
        f"A otimização não convergiu após {tentativas} tentativas: {resultado.message}"
    )


def _tau(gols_casa, gols_fora, lambda_casa, lambda_fora, rho):
    """Correção de Dixon-Coles para a dependência nos placares baixos."""
    tau = np.ones_like(lambda_casa, dtype=float)

    zero_zero = (gols_casa == 0) & (gols_fora == 0)
    zero_um = (gols_casa == 0) & (gols_fora == 1)
    um_zero = (gols_casa == 1) & (gols_fora == 0)
    um_um = (gols_casa == 1) & (gols_fora == 1)

    tau[zero_zero] = 1 - lambda_casa[zero_zero] * lambda_fora[zero_zero] * rho
    tau[zero_um] = 1 + lambda_casa[zero_um] * rho
    tau[um_zero] = 1 + lambda_fora[um_zero] * rho
    tau[um_um] = 1 - rho

    return tau


def _matriz_placares(lambda_casa: float, lambda_fora: float, rho: float) -> np.ndarray:
    """Matriz de probabilidade conjunta dos placares, já com a correção tau."""
    grade = np.arange(MAX_GOLS + 1)
    prob_casa = stats.poisson.pmf(grade, lambda_casa)
    prob_fora = stats.poisson.pmf(grade, lambda_fora)
    matriz = np.outer(prob_casa, prob_fora)

    matriz[0, 0] *= 1 - lambda_casa * lambda_fora * rho
    matriz[0, 1] *= 1 + lambda_casa * rho
    matriz[1, 0] *= 1 + lambda_fora * rho
    matriz[1, 1] *= 1 - rho

    return matriz / matriz.sum()


def _pesos_decaimento(datas: pd.Series, referencia: pd.Timestamp, xi: float) -> np.ndarray:
    """Peso exponencial por idade da partida, como em Dixon-Coles.

    Partidas antigas informam menos sobre a força atual de um clube. `xi = 0`
    desliga o decaimento e trata todas as partidas igualmente.
    """
    if xi <= 0:
        return np.ones(len(datas))
    idade_dias = (referencia - datas).dt.total_seconds().to_numpy() / 86400.0
    return np.exp(-xi * np.maximum(idade_dias, 0.0))


def ajustar_poisson(
    df: pd.DataFrame,
    xi: float = 0.0,
    referencia: pd.Timestamp | None = None,
    usar_correcao_dc: bool = True,
    calcular_erro_padrao: bool = True,
) -> ModeloPoisson:
    """Ajusta o modelo por máxima verossimilhança.

    Args:
        df: partidas preparadas (`preparacao.preparar`).
        xi: taxa de decaimento temporal por dia. 0 desliga o decaimento.
        referencia: data de referência do decaimento. Padrão: última partida.
        usar_correcao_dc: se False, ajusta um Poisson duplo independente (rho = 0),
            útil para mostrar o ganho da correção.
        calcular_erro_padrao: desligue quando só as previsões interessam. O erro
            padrão custa duas reotimizações, o que pesa no laço de validação
            temporal, onde o modelo é reestimado centenas de vezes.

    Raises:
        ErroDeAjuste: se a otimização não convergir.
    """
    times = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))
    indice = {time: i for i, time in enumerate(times)}
    n_times = len(times)

    idx_casa = df["HomeTeam"].map(indice).to_numpy()
    idx_fora = df["AwayTeam"].map(indice).to_numpy()
    gols_casa = df["FTHG"].to_numpy()
    gols_fora = df["FTAG"].to_numpy()

    referencia = referencia or df["Date"].max()
    pesos = _pesos_decaimento(df["Date"], referencia, xi)

    # Vetor: [ataque (n-1 livres), defesa (n), mu, gamma, rho]
    # O último ataque é determinado pela restrição de média zero.
    n_parametros = (n_times - 1) + n_times + 3

    def desempacotar(parametros):
        ataque_livre = parametros[: n_times - 1]
        ataque = np.append(ataque_livre, -ataque_livre.sum())
        defesa = parametros[n_times - 1 : 2 * n_times - 1]
        mu, gamma, rho = parametros[-3:]
        return ataque, defesa, mu, gamma, rho

    def log_verossimilhanca_negativa(parametros):
        ataque, defesa, mu, gamma, rho = desempacotar(parametros)
        if not usar_correcao_dc:
            rho = 0.0

        lambda_casa = np.exp(mu + ataque[idx_casa] - defesa[idx_fora] + gamma)
        lambda_fora = np.exp(mu + ataque[idx_fora] - defesa[idx_casa])

        log_prob = (
            stats.poisson.logpmf(gols_casa, lambda_casa)
            + stats.poisson.logpmf(gols_fora, lambda_fora)
        )

        if usar_correcao_dc:
            tau = _tau(gols_casa, gols_fora, lambda_casa, lambda_fora, rho)
            # tau pode ficar não positivo para rho extremo; penaliza em vez de NaN.
            if np.any(tau <= 0):
                return 1e10
            log_prob = log_prob + np.log(tau)

        return -float(np.sum(pesos * log_prob))

    inicial = np.concatenate([
        np.zeros(n_times - 1),   # ataque
        np.zeros(n_times),       # defesa
        [np.log(df["FTHG"].mean()), 0.2, 0.0],  # mu, gamma, rho
    ])

    limites = (
        [(-3, 3)] * (n_times - 1)
        + [(-3, 3)] * n_times
        + [(-3, 3), (-1, 1), (-0.3, 0.3)]
    )

    resultado = _minimizar(
        log_verossimilhanca_negativa, inicial, limites,
        opcoes=OPCOES_OTIMIZADOR if calcular_erro_padrao else OPCOES_OTIMIZADOR_RAPIDO,
    )
    ataque, defesa, mu, gamma, rho = desempacotar(resultado.x)
    erro_padrao = (
        _erro_padrao_parametro(
            log_verossimilhanca_negativa, resultado.x, len(resultado.x) - 2, limites
        )
        if calcular_erro_padrao
        else float("nan")
    )

    return ModeloPoisson(
        times=times,
        ataque=pd.Series(ataque, index=times, name="ataque"),
        defesa=pd.Series(defesa, index=times, name="defesa"),
        mu=float(mu),
        gamma=float(gamma),
        rho=float(rho) if usar_correcao_dc else 0.0,
        erro_padrao_gamma=erro_padrao,
        log_verossimilhanca=-float(resultado.fun),
        n_partidas=len(df),
        convergiu=bool(resultado.success),
    )


def _erro_padrao_parametro(funcao, parametros, i: int, limites) -> float:
    """Erro padrão de um parâmetro pela curvatura da verossimilhança perfilada.

    A curvatura da log-verossimilhança na direção de um único parâmetro, com
    todos os outros congelados, superestima a precisão sempre que esse parâmetro
    é correlacionado com os demais — e `gamma` é correlacionado com `mu`, já que
    ambos entram na média de gols do mandante. Uma simulação com gamma conhecido
    mostrou cobertura de 83% num intervalo nominal de 95% quando se usava a
    curvatura marginal.

    Perfilar resolve: para cada valor deslocado do parâmetro de interesse, o
    modelo é reotimizado sobre todos os outros. A curvatura da verossimilhança
    perfilada equivale ao elemento correspondente da inversa da matriz hessiana
    completa, a um custo de duas reotimizações em vez de uma hessiana de ordem
    quadrática no número de clubes.
    """
    def reotimizar_com_fixo(valor: float) -> float:
        limites_fixos = list(limites)
        limites_fixos[i] = (valor, valor)
        inicio = parametros.copy()
        inicio[i] = valor
        resultado = optimize.minimize(
            funcao, inicio, method="L-BFGS-B", bounds=limites_fixos,
            options=OPCOES_OTIMIZADOR,
        )
        return float(resultado.fun)

    centro = float(funcao(parametros))

    # Passo na escala do próprio parâmetro: grande o bastante para a diferença
    # não se perder no ruído numérico da otimização, pequeno o bastante para a
    # aproximação quadrática valer.
    passo = 0.05
    acima = reotimizar_com_fixo(parametros[i] + passo)
    abaixo = reotimizar_com_fixo(parametros[i] - passo)

    segunda_derivada = (acima - 2 * centro + abaixo) / passo**2
    if segunda_derivada <= 0:
        return float("nan")
    return float(np.sqrt(1.0 / segunda_derivada))


def mando_por_temporada(df: pd.DataFrame) -> pd.DataFrame:
    """Ajusta o modelo separadamente em cada temporada e devolve gamma.

    Esta é a série temporal do fator casa que a monografia deveria apresentar: ao
    contrário do diferencial bruto de pontos, `gamma` não se confunde com a
    distribuição de força dos elencos daquela temporada nem com o calendário.
    """
    linhas = []
    for temporada, grupo in df.groupby("Season"):
        modelo = ajustar_poisson(grupo)
        inferior, superior = modelo.ic_gamma
        linhas.append({
            "Season": temporada,
            "gamma": modelo.gamma,
            "ic95_inf": inferior,
            "ic95_sup": superior,
            "acrescimo_percentual": modelo.acrescimo_percentual,
            "rho": modelo.rho,
            "n_partidas": modelo.n_partidas,
        })
    return pd.DataFrame(linhas)


def mando_por_regime_de_publico(df: pd.DataFrame) -> pd.DataFrame:
    """Ajusta o modelo separadamente por regime de público.

    Complementa o contraste descritivo de `analise.contraste_publico`: aqui a
    comparação entre regimes já vem ajustada pela força dos times envolvidos em
    cada recorte, o que importa porque os jogos sem público de 2019/20 são as
    rodadas finais, com distribuição de confrontos diferente da temporada toda.
    """
    linhas = []
    for regime, grupo in df.groupby("publico"):
        # Um regime com poucos jogos não sustenta um parâmetro por time.
        if len(grupo) < 100:
            continue
        modelo = ajustar_poisson(grupo)
        inferior, superior = modelo.ic_gamma
        linhas.append({
            "publico": regime,
            "gamma": modelo.gamma,
            "ic95_inf": inferior,
            "ic95_sup": superior,
            "acrescimo_percentual": modelo.acrescimo_percentual,
            "n_partidas": modelo.n_partidas,
        })
    return pd.DataFrame(linhas)


@dataclass
class EfeitoNoMando:
    """Deslocamento do parâmetro de mando associado a uma condição binária."""

    condicao: str
    gamma_base: float
    delta: float
    erro_padrao_delta: float
    n_com_condicao: int
    n_sem_condicao: int

    @property
    def ic_delta(self) -> tuple[float, float]:
        critico = stats.norm.ppf(1 - config.ALFA / 2)
        return (
            self.delta - critico * self.erro_padrao_delta,
            self.delta + critico * self.erro_padrao_delta,
        )

    @property
    def p_valor(self) -> float:
        if not np.isfinite(self.erro_padrao_delta) or self.erro_padrao_delta == 0:
            return float("nan")
        z = self.delta / self.erro_padrao_delta
        return float(2 * stats.norm.sf(abs(z)))

    @property
    def significativo(self) -> bool:
        return self.p_valor < config.ALFA


def ajustar_efeito_no_mando(df: pd.DataFrame, indicadora: str) -> EfeitoNoMando:
    """Estima quanto uma condição binária desloca a vantagem do mandante.

    O mando passa a ser `gamma + delta * indicadora`, com todo o resto do modelo
    inalterado. Como `delta` é um único parâmetro extra, ele é bem identificado
    mesmo em recortes pequenos — ao contrário de ajustar o modelo inteiro
    separadamente em cada subconjunto, que exigiria dois parâmetros por clube em
    cada lado.

    É assim que se testa o efeito da ausência de público **dentro** de uma mesma
    temporada, controlando pela força dos adversários: os 92 jogos sem torcida de
    2019/20 não sustentam um modelo próprio, mas sustentam um `delta`.

    Args:
        df: partidas preparadas.
        indicadora: nome de uma coluna booleana ou 0/1 do DataFrame.
    """
    if indicadora not in df.columns:
        raise ErroDeAjuste(f"Coluna indicadora ausente: {indicadora}")

    times = sorted(set(df["HomeTeam"]) | set(df["AwayTeam"]))
    indice = {time: i for i, time in enumerate(times)}
    n_times = len(times)

    idx_casa = df["HomeTeam"].map(indice).to_numpy()
    idx_fora = df["AwayTeam"].map(indice).to_numpy()
    gols_casa = df["FTHG"].to_numpy()
    gols_fora = df["FTAG"].to_numpy()
    condicao = df[indicadora].to_numpy(dtype=float)

    if condicao.sum() == 0 or condicao.sum() == len(condicao):
        raise ErroDeAjuste(
            f"A coluna '{indicadora}' precisa variar dentro do recorte "
            f"(encontrei {int(condicao.sum())} de {len(condicao)})."
        )

    def desempacotar(parametros):
        ataque_livre = parametros[: n_times - 1]
        ataque = np.append(ataque_livre, -ataque_livre.sum())
        defesa = parametros[n_times - 1 : 2 * n_times - 1]
        mu, gamma, delta, rho = parametros[-4:]
        return ataque, defesa, mu, gamma, delta, rho

    def log_verossimilhanca_negativa(parametros):
        ataque, defesa, mu, gamma, delta, rho = desempacotar(parametros)
        mando = gamma + delta * condicao

        lambda_casa = np.exp(mu + ataque[idx_casa] - defesa[idx_fora] + mando)
        lambda_fora = np.exp(mu + ataque[idx_fora] - defesa[idx_casa])

        tau = _tau(gols_casa, gols_fora, lambda_casa, lambda_fora, rho)
        if np.any(tau <= 0):
            return 1e10

        log_prob = (
            stats.poisson.logpmf(gols_casa, lambda_casa)
            + stats.poisson.logpmf(gols_fora, lambda_fora)
            + np.log(tau)
        )
        return -float(np.sum(log_prob))

    inicial = np.concatenate([
        np.zeros(n_times - 1), np.zeros(n_times),
        [np.log(df["FTHG"].mean()), 0.2, 0.0, 0.0],
    ])
    limites = (
        [(-3, 3)] * (n_times - 1) + [(-3, 3)] * n_times
        + [(-3, 3), (-1, 1), (-1, 1), (-0.3, 0.3)]
    )

    resultado = _minimizar(log_verossimilhanca_negativa, inicial, limites)
    _, _, _, gamma, delta, _ = desempacotar(resultado.x)
    erro_padrao = _erro_padrao_parametro(
        log_verossimilhanca_negativa, resultado.x, len(resultado.x) - 2, limites
    )

    return EfeitoNoMando(
        condicao=indicadora,
        gamma_base=float(gamma),
        delta=float(delta),
        erro_padrao_delta=erro_padrao,
        n_com_condicao=int(condicao.sum()),
        n_sem_condicao=int(len(condicao) - condicao.sum()),
    )


def prever_partidas(modelo: ModeloPoisson, df: pd.DataFrame) -> pd.DataFrame:
    """Probabilidades H/D/A para cada partida, na ordem do DataFrame."""
    linhas = []
    for _, partida in df.iterrows():
        if partida["HomeTeam"] not in modelo.ataque.index:
            linhas.append({"H": np.nan, "D": np.nan, "A": np.nan})
            continue
        if partida["AwayTeam"] not in modelo.ataque.index:
            linhas.append({"H": np.nan, "D": np.nan, "A": np.nan})
            continue
        linhas.append(modelo.probabilidades(partida["HomeTeam"], partida["AwayTeam"]))
    return pd.DataFrame(linhas, index=df.index)
