#!/usr/bin/env python3
"""Executa a análise completa e escreve tabelas e figuras.

    python scripts/executar_analise.py

Tudo que vai para o LaTeX sai daqui: `tabelas/*.csv` e `figuras/*.pdf`. Nenhum
número deve ser copiado à mão de uma saída de célula.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd

from tcc import analise, coleta, config, estatistica, preparacao, visualizacao


def _salvar_tabela(df: pd.DataFrame, nome: str, indice: bool = True) -> None:
    config.DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.DIR_TABELAS / f"{nome}.csv", index=indice)
    print(f"  tabelas/{nome}.csv")


def main() -> int:
    print("1. Coleta")
    bruto = coleta.obter_bruto(config.TEMPORADAS)
    print(f"   {len(bruto)} partidas, {len(config.TEMPORADAS)} temporadas")

    print("2. Preparação")
    df = preparacao.preparar(bruto)
    longo = preparacao.formato_longo(df)
    tabela = preparacao.tabela_classificacao(df)
    longo_pos = preparacao.anexar_posicao(longo, tabela)
    config.DIR_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(config.DIR_PROCESSED / "partidas.csv", index=False)
    tabela.to_csv(config.DIR_PROCESSED / "classificacao.csv", index=False)
    print(f"   {df['publico'].value_counts().to_dict()}")

    print("3. Testes estatísticos")
    resultados = [
        estatistica.vantagem_mandante_binomial(df["FTR"]),
        estatistica.distribuicao_resultados_qui2(df["FTR"]),
        estatistica.diferenca_pontos_pareada(df["pts_mandante"], df["pts_visitante"]),
    ]

    por_time = analise.fator_casa_por_time(longo)
    resultados.append(analise.comparar_big_six(por_time))
    resultados.append(analise.teste_publico_intratemporada(df, "1920"))

    for resultado in resultados:
        efeito = (
            f" | {resultado.nome_efeito} = {resultado.tamanho_efeito:.3f}"
            if resultado.tamanho_efeito is not None else ""
        )
        print(f"   {resultado.nome}")
        print(
            f"     estimativa = {resultado.estimativa:.4f} "
            f"[{resultado.ic_inferior:.4f}; {resultado.ic_superior:.4f}] "
            f"p = {resultado.p_valor:.3e}{efeito}"
        )

    print("4. Análises")
    por_faixa = analise.fator_casa_por_faixa(longo_pos)
    por_time_temporada = analise.dif_por_time_temporada(longo_pos)
    evolucao = analise.evolucao_temporal(longo, janela=3)
    conversao = analise.taxa_conversao(df)
    publico = analise.contraste_publico(longo)

    print("5. Estudo de caso: mudança de estádio (recorte estendido)")
    bruto_ext = coleta.obter_bruto(config.TEMPORADAS_ESTENDIDAS)
    longo_ext = preparacao.formato_longo(preparacao.preparar(bruto_ext))
    quebras = analise.verificar_quebras_de_serie(longo_ext)
    if not quebras.empty:
        print("   quebras de série detectadas na fonte:")
        print(quebras.to_string(index=False))
    estadios = analise.estudo_mudanca_estadio(longo_ext)

    print("6. Tabelas")
    _salvar_tabela(estatistica.tabela_resultados(resultados), "testes_estatisticos", indice=False)
    _salvar_tabela(tabela, "classificacao_por_temporada", indice=False)
    _salvar_tabela(por_faixa, "fator_casa_por_faixa")
    _salvar_tabela(por_time, "fator_casa_por_time")
    _salvar_tabela(por_time_temporada, "fator_casa_por_time_temporada", indice=False)
    _salvar_tabela(evolucao, "evolucao_temporal", indice=False)
    _salvar_tabela(conversao, "taxa_conversao")
    _salvar_tabela(publico, "contraste_publico")
    if not estadios.empty:
        _salvar_tabela(estadios, "mudanca_estadio")
    if not quebras.empty:
        _salvar_tabela(quebras, "quebras_de_serie", indice=False)

    print("7. Figuras")
    visualizacao.aplicar_tema()
    figuras = (
        ("evolucao_pontos", visualizacao.evolucao_pontos(evolucao)),
        ("diferencial_por_temporada", visualizacao.diferencial_por_temporada(evolucao)),
        ("fator_casa_por_faixa", visualizacao.fator_casa_por_faixa(por_faixa)),
        ("volume_ofensivo", visualizacao.volume_ofensivo_por_temporada(evolucao)),
        ("dispersao_casa_fora", visualizacao.dispersao_casa_fora(por_time)),
        ("contraste_publico", visualizacao.contraste_publico(publico)),
    )
    for nome, figura in figuras:
        visualizacao.salvar(figura, nome)
        print(f"  figuras/{nome}.pdf")

    print("\nConcluído.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
