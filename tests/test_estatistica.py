"""Testes dos testes estatísticos, com foco nos erros da célula 8 do TCC1."""

import numpy as np
import pandas as pd
import pytest

from tcc import estatistica


def _serie_ftr(casa: int, empate: int, fora: int) -> pd.Series:
    return pd.Series(["H"] * casa + ["D"] * empate + ["A"] * fora)


def test_qui2_nao_acusa_fator_casa_quando_nao_existe():
    """Trava a correção da hipótese nula.

    Cenário sem nenhum fator casa: mesmas vitórias para mandante e visitante, com
    a taxa de empates real do futebol (~24%). A nula uniforme do TCC1 rejeitaria
    aqui; a nula correta não pode.
    """
    ftr = _serie_ftr(casa=1595, empate=990, fora=1595)

    resultado = estatistica.distribuicao_resultados_qui2(ftr)
    assert not resultado.significativo

    # O teste do TCC1, para comparação: rejeita mesmo sem fator casa.
    from scipy import stats
    total = len(ftr)
    qui2_uniforme, p_uniforme = stats.chisquare([1595, 990, 1595], [total / 3] * 3)
    assert p_uniforme < 0.05


def test_qui2_detecta_fator_casa_quando_existe():
    ftr = _serie_ftr(casa=1853, empate=990, fora=1337)
    assert estatistica.distribuicao_resultados_qui2(ftr).significativo


def test_binomial_ignora_empates_e_estima_a_proporcao():
    ftr = _serie_ftr(casa=1853, empate=990, fora=1337)
    resultado = estatistica.vantagem_mandante_binomial(ftr)

    assert resultado.n == 1853 + 1337
    assert resultado.estimativa == pytest.approx(1853 / 3190)
    assert resultado.significativo
    assert resultado.ic_inferior < resultado.estimativa < 1.0


def test_binomial_nao_rejeita_sob_simetria():
    ftr = _serie_ftr(casa=1500, empate=900, fora=1500)
    assert not estatistica.vantagem_mandante_binomial(ftr).significativo


def test_teste_pareado_difere_do_independente():
    """Trava a correção do teste t.

    `pts_mandante` e `pts_visitante` vêm da mesma partida e têm correlação de
    -0,95. Tratá-las como independentes, como fazia o TCC1, superestima a
    estatística do teste.
    """
    from scipy import stats

    ftr = _serie_ftr(casa=1853, empate=990, fora=1337)
    mandante = ftr.map({"H": 3, "D": 1, "A": 0})
    visitante = ftr.map({"A": 3, "D": 1, "H": 0})

    assert np.corrcoef(mandante, visitante)[0, 1] < -0.9

    resultado = estatistica.diferenca_pontos_pareada(mandante, visitante)
    t_independente, _ = stats.ttest_ind(
        mandante, visitante, equal_var=False, alternative="greater"
    )

    assert resultado.estatistica < t_independente
    assert resultado.tamanho_efeito is not None
    assert resultado.nome_efeito.startswith("d de Cohen")


def test_resultado_sempre_traz_efeito_e_intervalo():
    """O TCC1 não reportava nem tamanho de efeito nem IC em nenhum teste."""
    ftr = _serie_ftr(casa=1853, empate=990, fora=1337)
    resultado = estatistica.vantagem_mandante_binomial(ftr)
    linha = resultado.linha()

    for campo in ("estimativa", "ic95_inf", "ic95_sup", "tamanho_efeito", "p_valor"):
        assert campo in linha


def test_comparar_grupos_devolve_ic_da_diferenca():
    gerador = np.random.default_rng(7)
    a = gerador.normal(0.5, 0.1, 30)
    b = gerador.normal(0.4, 0.1, 30)

    resultado = estatistica.comparar_grupos(a, b, nome="teste", rotulo_a="a", rotulo_b="b")

    assert resultado.ic_inferior < resultado.estimativa < resultado.ic_superior
    assert resultado.detalhes["n_a"] == 30


def test_bootstrap_agrupado_e_mais_largo_que_o_ingenuo():
    """Trava a correção da unidade de análise.

    Quatro temporadas com médias bem distintas: reamostrar partidas ignora essa
    variação entre temporadas e produz um intervalo artificialmente estreito, que
    foi o que sustentou o p = 0,0004 do teste da COVID no TCC1.
    """
    linhas = []
    for temporada, media in zip(["1516", "1617", "1718", "1819"], [0.1, 0.4, 0.7, 1.0]):
        linhas.extend({"Season": temporada, "dif": media} for _ in range(380))
    df = pd.DataFrame(linhas)

    inferior_ing, superior_ing = estatistica.ic_bootstrap(df["dif"], n_reamostras=2000)
    inferior_agr, superior_agr = estatistica.ic_bootstrap_agrupado(
        df, "dif", "Season", n_reamostras=2000
    )

    assert (superior_agr - inferior_agr) > (superior_ing - inferior_ing)
