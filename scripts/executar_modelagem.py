#!/usr/bin/env python3
"""Executa a modelagem: Dixon-Coles e validação temporal dos preditivos.

    python scripts/executar_modelagem.py

Separado de `executar_analise.py` porque é bem mais lento: o Dixon-Coles é
reestimado a cada bloco de partidas dentro de cada temporada de teste.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd

from tcc import coleta, config, modelos, preditivo, preparacao, visualizacao

TEMPORADAS_TESTE = ("1819", "1920", "2021", "2122", "2223", "2324", "2425", "2526")


def _salvar_tabela(df: pd.DataFrame, nome: str, indice: bool = True) -> None:
    config.DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.DIR_TABELAS / f"{nome}.csv", index=indice)
    print(f"  tabelas/{nome}.csv")


def main() -> int:
    inicio = time.time()

    print("1. Dados")
    df = preparacao.preparar(coleta.obter_bruto(config.TEMPORADAS))
    longo = preparacao.formato_longo(df)
    print(f"   {len(df)} partidas")

    print("2. Dixon-Coles sobre o recorte completo")
    modelo = modelos.ajustar_poisson(df)
    inferior, superior = modelo.ic_gamma
    print(f"   gamma = {modelo.gamma:.4f}  IC95% [{inferior:.4f}; {superior:.4f}]")
    print(f"   acréscimo de gols pelo mando: {modelo.acrescimo_percentual * 100:.1f}%")
    print(f"   rho = {modelo.rho:.4f}   log-verossimilhança = {modelo.log_verossimilhanca:.1f}")

    forcas = modelo.tabela_forcas()
    resumo_global = pd.DataFrame([{
        "gamma": modelo.gamma,
        "ic95_inf": inferior,
        "ic95_sup": superior,
        "acrescimo_percentual": modelo.acrescimo_percentual,
        "rho": modelo.rho,
        "log_verossimilhanca": modelo.log_verossimilhanca,
        "n_partidas": modelo.n_partidas,
    }])

    print("3. Mando de campo ajustado, por temporada")
    por_temporada = modelos.mando_por_temporada(df)
    print(por_temporada[["Season", "gamma", "ic95_inf", "ic95_sup"]].round(4).to_string(index=False))

    print("4. Mando de campo ajustado, por regime de público")
    por_publico = modelos.mando_por_regime_de_publico(df)
    print(por_publico.round(4).to_string(index=False))

    print("4b. Efeito do público sobre o mando, com o modelo ajustado")
    df = df.copy()
    df["sem_publico"] = (df["publico"] == "sem").astype(int)
    efeitos = []
    recortes = {
        "2019/20 (intratemporada)": df[df["Season"] == "1920"],
        "recorte completo (19/20 + 20/21)": df[df["publico"] != "limitado"],
    }
    for rotulo, recorte in recortes.items():
        efeito = modelos.ajustar_efeito_no_mando(recorte, "sem_publico")
        inferior, superior = efeito.ic_delta
        efeitos.append({
            "recorte": rotulo,
            "gamma_com_publico": efeito.gamma_base,
            "delta_sem_publico": efeito.delta,
            "ic95_inf": inferior,
            "ic95_sup": superior,
            "p_valor": efeito.p_valor,
            "n_sem_publico": efeito.n_com_condicao,
            "n_com_publico": efeito.n_sem_condicao,
        })
        print(f"   {rotulo}: delta = {efeito.delta:+.4f} "
              f"[{inferior:+.4f}; {superior:+.4f}]  p = {efeito.p_valor:.4f}")
    efeito_publico = pd.DataFrame(efeitos)

    print("5. Validação temporal (isso demora)")
    features = preditivo.construir_features(df, longo)
    metricas, previsoes = preditivo.validacao_temporal(features, TEMPORADAS_TESTE)
    resumo = preditivo.resumo_por_modelo(metricas)
    print(resumo.round(4).to_string())

    print("6. Calibração")
    calibracoes = []
    for nome in resumo.index:
        curva = preditivo.curva_calibracao(previsoes, nome, classe="H")
        if not curva.empty:
            curva.insert(0, "modelo", nome)
            calibracoes.append(curva)
    calibracao = pd.concat(calibracoes, ignore_index=True) if calibracoes else pd.DataFrame()

    print("7. Tabelas")
    _salvar_tabela(resumo_global, "dixon_coles_global", indice=False)
    _salvar_tabela(forcas, "dixon_coles_forcas")
    _salvar_tabela(por_temporada, "mando_ajustado_por_temporada", indice=False)
    _salvar_tabela(por_publico, "mando_ajustado_por_publico", indice=False)
    _salvar_tabela(efeito_publico, "efeito_publico_ajustado", indice=False)
    _salvar_tabela(metricas, "preditivo_metricas_por_temporada", indice=False)
    _salvar_tabela(resumo, "preditivo_resumo")
    if not calibracao.empty:
        _salvar_tabela(calibracao, "preditivo_calibracao", indice=False)

    print("8. Figuras")
    visualizacao.aplicar_tema()
    figuras = [
        ("mando_ajustado_por_temporada",
         visualizacao.mando_ajustado_por_temporada(por_temporada)),
        ("preditivo_desempenho", visualizacao.desempenho_preditivo(resumo)),
    ]
    if not calibracao.empty:
        figuras.append(("preditivo_calibracao",
                        visualizacao.calibracao(calibracao)))
    for nome, figura in figuras:
        visualizacao.salvar(figura, nome)
        print(f"  figuras/{nome}.pdf")

    print(f"\nConcluído em {time.time() - inicio:.0f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
