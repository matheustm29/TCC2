"""Testes do modelo de Poisson bivariado com termo de mando."""

import numpy as np
import pandas as pd
import pytest

from tcc import modelos, preparacao


def _liga_poisson(gamma_real=0.25, n_temporadas=4, semente=5, delta_publico=0.0):
    """Gera partidas a partir do próprio modelo, com gamma conhecido.

    Se o ajuste recupera o gamma usado na simulação, a implementação está certa.
    """
    gerador = np.random.default_rng(semente)
    times = [f"T{i:02d}" for i in range(12)]
    ataque = dict(zip(times, np.linspace(0.45, -0.45, len(times))))
    defesa = dict(zip(times, np.linspace(0.35, -0.35, len(times))))

    linhas = []
    dia = pd.Timestamp("2015-08-08")
    for t in range(n_temporadas):
        temporada = f"{15 + t}{16 + t}"
        for casa in times:
            for fora in times:
                if casa == fora:
                    continue
                sem_publico = 1 if (t == n_temporadas - 1) else 0
                mando = gamma_real + delta_publico * sem_publico
                media_casa = np.exp(0.1 + ataque[casa] - defesa[fora] + mando)
                media_fora = np.exp(0.1 + ataque[fora] - defesa[casa])
                gc = int(gerador.poisson(media_casa))
                gf = int(gerador.poisson(media_fora))
                ftr = "H" if gc > gf else ("A" if gf > gc else "D")
                linhas.append({
                    "Date": dia.strftime("%Y-%m-%d"), "HomeTeam": casa, "AwayTeam": fora,
                    "FTHG": gc, "FTAG": gf, "FTR": ftr,
                    "HTHG": 0, "HTAG": 0, "HTR": "D",
                    "HS": 12, "AS": 9, "HST": 5, "AST": 3,
                    "HC": 6, "AC": 4, "HF": 11, "AF": 12,
                    "HY": 2, "AY": 2, "HR": 0, "AR": 0,
                    "Season": temporada, "_sem_publico": sem_publico,
                })
                dia += pd.Timedelta(days=1)
    return pd.DataFrame(linhas)


def test_ajuste_recupera_o_gamma_usado_na_simulacao():
    """Teste de recuperação de parâmetro: a prova de que o modelo está correto.

    Usa várias sementes e avalia a média, porque um IC de 95% erra o alvo em uma
    em cada vinte amostras por construção — checar uma única simulação
    transformaria o teste numa loteria.
    """
    estimativas = []
    for semente in range(6):
        bruto = _liga_poisson(gamma_real=0.25, semente=semente)
        df = preparacao.preparar(bruto.drop(columns="_sem_publico"))
        modelo = modelos.ajustar_poisson(df)
        assert modelo.convergiu
        estimativas.append(modelo.gamma)

    media = float(np.mean(estimativas))
    erro_padrao_da_media = float(np.std(estimativas, ddof=1) / np.sqrt(len(estimativas)))

    assert media == pytest.approx(0.25, abs=max(3 * erro_padrao_da_media, 0.05))


def test_erro_padrao_acompanha_a_variabilidade_real():
    """O erro padrão perfilado tem de refletir a dispersão entre simulações.

    A versão anterior usava a curvatura marginal e subestimava a incerteza em
    cerca de 25%, produzindo cobertura de 83% num intervalo nominal de 95%.
    """
    estimativas, erros = [], []
    for semente in range(8):
        bruto = _liga_poisson(gamma_real=0.25, semente=semente)
        df = preparacao.preparar(bruto.drop(columns="_sem_publico"))
        modelo = modelos.ajustar_poisson(df)
        estimativas.append(modelo.gamma)
        erros.append(modelo.erro_padrao_gamma)

    dispersao_real = float(np.std(estimativas, ddof=1))
    erro_reportado = float(np.mean(erros))

    # Com 8 amostras a dispersão empírica é ela mesma ruidosa; a faixa é larga
    # de propósito. O que o teste barra é a subestimação sistemática.
    assert 0.5 * dispersao_real < erro_reportado < 2.0 * dispersao_real


def test_forcas_recuperam_a_ordem_dos_times():
    bruto = _liga_poisson()
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))
    forcas = modelos.ajustar_poisson(df).tabela_forcas()

    # T00 é o mais forte por construção, T11 o mais fraco.
    assert forcas.index[0] == "T00"
    assert forcas.index[-1] == "T11"


def test_probabilidades_somam_um_e_favorecem_o_mandante():
    bruto = _liga_poisson()
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))
    modelo = modelos.ajustar_poisson(df)

    entre_iguais = modelo.probabilidades("T05", "T06")
    assert sum(entre_iguais.values()) == pytest.approx(1.0)
    assert entre_iguais["H"] > entre_iguais["A"]

    # O mesmo confronto invertido tem de espelhar a vantagem.
    invertido = modelo.probabilidades("T06", "T05")
    assert invertido["H"] > invertido["A"]


def test_acrescimo_percentual_corresponde_a_gamma():
    bruto = _liga_poisson()
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))
    modelo = modelos.ajustar_poisson(df)

    assert modelo.acrescimo_percentual == pytest.approx(np.exp(modelo.gamma) - 1)


def test_efeito_no_mando_recupera_o_delta_simulado():
    """Trava do teste de público: delta conhecido tem de ser recuperado."""
    bruto = _liga_poisson(gamma_real=0.25, delta_publico=-0.30)
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))
    df["sem_publico"] = bruto["_sem_publico"].to_numpy()

    efeito = modelos.ajustar_efeito_no_mando(df, "sem_publico")

    inferior, superior = efeito.ic_delta
    assert inferior < -0.30 < superior, f"delta real fora do IC: [{inferior}; {superior}]"
    assert efeito.significativo


def test_efeito_no_mando_nao_acusa_efeito_inexistente():
    """Contraprova: sem efeito simulado, delta não pode ser significativo."""
    bruto = _liga_poisson(gamma_real=0.25, delta_publico=0.0)
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))
    df["sem_publico"] = bruto["_sem_publico"].to_numpy()

    efeito = modelos.ajustar_efeito_no_mando(df, "sem_publico")

    assert not efeito.significativo
    assert efeito.ic_delta[0] < 0 < efeito.ic_delta[1]


def test_efeito_exige_variacao_na_indicadora():
    bruto = _liga_poisson()
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))
    df["constante"] = 0

    with pytest.raises(modelos.ErroDeAjuste, match="precisa variar"):
        modelos.ajustar_efeito_no_mando(df, "constante")


def test_mando_por_temporada_devolve_uma_linha_por_temporada():
    bruto = _liga_poisson(n_temporadas=3)
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))

    tabela = modelos.mando_por_temporada(df)

    assert len(tabela) == 3
    assert (tabela["ic95_inf"] < tabela["gamma"]).all()
    assert (tabela["gamma"] < tabela["ic95_sup"]).all()


def test_correcao_dixon_coles_melhora_a_verossimilhanca():
    """A correção tau existe para os placares baixos; deve pagar seu parâmetro."""
    bruto = _liga_poisson()
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))

    com = modelos.ajustar_poisson(df, usar_correcao_dc=True)
    sem = modelos.ajustar_poisson(df, usar_correcao_dc=False)

    assert com.log_verossimilhanca >= sem.log_verossimilhanca
    assert sem.rho == 0.0


def test_caminho_rapido_nao_muda_as_probabilidades():
    """O ajuste rápido do laço de previsão precisa ser equivalente ao apertado.

    A tolerância apertada existe para estabilizar a curvatura da verossimilhança
    perfilada, usada só na inferência. No laço de previsão o erro padrão não é
    calculado, e a precisão extra levava a validação temporal de minutos a mais de
    uma hora. Este teste garante que a troca não altera o que o modelo prevê.
    """
    bruto = _liga_poisson(n_temporadas=3)
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))

    apertado = modelos.ajustar_poisson(df, calcular_erro_padrao=True)
    rapido = modelos.ajustar_poisson(df, calcular_erro_padrao=False)

    assert rapido.gamma == pytest.approx(apertado.gamma, abs=5e-3)

    previsto_apertado = modelos.prever_partidas(apertado, df)
    previsto_rapido = modelos.prever_partidas(rapido, df)
    diferenca = (previsto_apertado - previsto_rapido).abs().to_numpy().max()

    assert diferenca < 5e-3, f"probabilidades divergiram em {diferenca:.2e}"


def test_caminho_rapido_dispensa_o_erro_padrao():
    bruto = _liga_poisson(n_temporadas=2)
    df = preparacao.preparar(bruto.drop(columns="_sem_publico"))

    rapido = modelos.ajustar_poisson(df, calcular_erro_padrao=False)

    assert np.isnan(rapido.erro_padrao_gamma)
