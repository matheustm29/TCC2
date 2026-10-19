#!/usr/bin/env python3
"""Converte as tabelas de resultados em tabelas LaTeX prontas para a monografia.

Cada tabela de `tabelas/*.csv` vira um `tcc2/tabelas/*.tex` com `booktabs`, já
com cabeçalhos em português e vírgula como separador decimal. O texto da
monografia apenas inclui esses arquivos, de modo que reexecutar a análise
atualiza o PDF sem nenhuma edição manual — e sem o risco de um número no texto
divergir do número que o código produziu.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd

from tcc import config

DIR_SAIDA = RAIZ / "tcc2" / "tabelas"


def _num(valor, casas=3, sinal=False):
    """Formata um número no padrão brasileiro, com vírgula decimal.

    O hífen do Python não é o sinal de menos tipográfico: em modo texto o LaTeX
    o compõe como traço curto, visivelmente diferente do menos das fórmulas. Os
    negativos saem, por isso, com o menos em modo matemático.
    """
    if pd.isna(valor):
        return "---"
    formato = f"{{:+.{casas}f}}" if sinal else f"{{:.{casas}f}}"
    texto = formato.format(valor).replace(".", ",")
    return texto.replace("-", "$-$", 1) if texto.startswith("-") else texto


def _p(valor):
    """p-valores muito pequenos viram notação científica legível."""
    if pd.isna(valor):
        return "---"
    if valor < 0.001:
        expoente = f"{valor:.0e}".split("e")[1]
        return f"$<10^{{{int(expoente) + 1}}}$"
    return _num(valor, 3)


def _temporada(codigo) -> str:
    """'1516' -> '15/16'.

    O código da temporada é texto, mas o CSV o devolve como inteiro quando todos
    os valores são numéricos — e aí '1516'[:2] falha. A normalização aqui evita
    depender de cada chamada lembrar de passar o dtype na leitura.
    """
    texto = codigo if isinstance(codigo, str) else f"{int(codigo):04d}"
    return f"{texto[:2]}/{texto[2:]}"


def _escrever(nome: str, linhas: list[str], colunas: str, cabecalho: list[str]) -> None:
    DIR_SAIDA.mkdir(parents=True, exist_ok=True)
    corpo = "\n".join(f"  {linha} \\\\" for linha in linhas)
    conteudo = (
        f"% Gerado por scripts/gerar_tabelas_latex.py --- não editar à mão.\n"
        f"\\begin{{tabular}}{{{colunas}}}\n"
        f"  \\toprule\n"
        f"  {' & '.join(cabecalho)} \\\\\n"
        f"  \\midrule\n"
        f"{corpo}\n"
        f"  \\bottomrule\n"
        f"\\end{{tabular}}\n"
    )
    (DIR_SAIDA / f"{nome}.tex").write_text(conteudo, encoding="utf-8")
    print(f"  tcc2/tabelas/{nome}.tex")


def testes_estatisticos(tabelas: Path) -> None:
    df = pd.read_csv(tabelas / "testes_estatisticos.csv")
    rotulos = {
        "Binomial — vitórias do mandante entre jogos decididos":
            "Binomial (vitórias do mandante entre jogos decididos)",
        "Qui-quadrado — simetria casa/fora dada a taxa de empates":
            "Qui-quadrado (simetria casa/fora)",
        "Teste t pareado — pontos do mandante menos pontos do visitante":
            "Teste $t$ pareado (diferença de pontos)",
        "Diferencial casa-fora: Big Six vs demais clubes":
            "Diferencial casa--fora: \\textit{Big Six} vs.\\ demais",
        "Vantagem do mandante em 19/20: com público vs sem público":
            "Vantagem do mandante em 2019/20: com vs.\\ sem público",
    }
    linhas = []
    for _, r in df.iterrows():
        efeito = "---" if pd.isna(r["tamanho_efeito"]) else _num(r["tamanho_efeito"])
        linhas.append(" & ".join([
            rotulos.get(r["teste"], r["teste"]),
            f"{int(r['n'])}",
            _num(r["estimativa"], 4),
            f"[{_num(r['ic95_inf'], 3)}; {_num(r['ic95_sup'], 3)}]"
            if not pd.isna(r["ic95_inf"]) else "---",
            _p(r["p_valor"]),
            efeito,
        ]))
    _escrever("testes_estatisticos", linhas, "lrrccr",
              ["Teste", "$n$", "Estimativa", "IC 95\\%", "$p$", "Efeito"])


def fator_casa_por_faixa(tabelas: Path) -> None:
    df = pd.read_csv(tabelas / "fator_casa_por_faixa.csv", index_col=0)
    linhas = [" & ".join([
        faixa, f"{int(r['jogos_casa'])}",
        _num(r["pontos_casa"]), _num(r["pontos_fora"]), _num(r["dif_pontos"], sinal=True),
        _num(r["dif_gols_pro"], sinal=True), _num(r["dif_chutes_alvo"], sinal=True),
        _num(r["dif_escanteios"], sinal=True),
    ]) for faixa, r in df.iterrows()]
    _escrever("fator_casa_por_faixa", linhas, "lrrrrrrr",
              ["Faixa", "Jogos", "Pts casa", "Pts fora", "$\\Delta$ pts",
               "$\\Delta$ gols", "$\\Delta$ chutes alvo", "$\\Delta$ escant."])


def contraste_publico(tabelas: Path) -> None:
    df = pd.read_csv(tabelas / "contraste_publico.csv", index_col=0)
    linhas = [" & ".join([
        cenario, f"{int(r['jogos'])}",
        _num(r["pontos_casa"]), _num(r["pontos_fora"]),
        _num(r["dif_pontos"], sinal=True), _num(r["dif_gols"], sinal=True),
        _num(r["dif_amarelos"], sinal=True),
    ]) for cenario, r in df.iterrows()]
    _escrever("contraste_publico", linhas, "lrrrrrr",
              ["Cenário", "Jogos", "Pts casa", "Pts fora",
               "$\\Delta$ pts", "$\\Delta$ gols", "$\\Delta$ amarelos"])


def taxa_conversao(tabelas: Path) -> None:
    df = pd.read_csv(tabelas / "taxa_conversao.csv", index_col=0)
    rotulo = {"casa": "Mandante", "fora": "Visitante"}
    linhas = [" & ".join([
        rotulo[mando], f"{int(r['gols'])}", f"{int(r['chutes_alvo'])}",
        _num(r["taxa_conversao"], 4),
        f"[{_num(r['ic95_inf'], 4)}; {_num(r['ic95_sup'], 4)}]",
    ]) for mando, r in df.iterrows()]
    _escrever("taxa_conversao", linhas, "lrrrc",
              ["Mando", "Gols", "Chutes no alvo", "Taxa", "IC 95\\%"])


def evolucao_temporal(tabelas: Path) -> None:
    df = pd.read_csv(tabelas / "evolucao_temporal.csv")
    linhas = [" & ".join([
        _temporada(r["Season"]),
        _num(r["dif_pontos"], sinal=True),
        _num(r["dif_pontos_mm3"], sinal=True),
        _num(r["dif_chutes_alvo"], sinal=True),
        _num(r["dif_escanteios"], sinal=True),
        _num(r["dif_amarelos"], sinal=True),
    ]) for _, r in df.iterrows()]
    _escrever("evolucao_temporal", linhas, "lrrrrr",
              ["Temporada", "$\\Delta$ pts", "Média móvel (3)",
               "$\\Delta$ chutes alvo", "$\\Delta$ escant.", "$\\Delta$ amarelos"])


def mando_ajustado(tabelas: Path) -> None:
    df = pd.read_csv(tabelas / "mando_ajustado_por_temporada.csv")
    linhas = [" & ".join([
        _temporada(r["Season"]), _num(r["gamma"], 4),
        f"[{_num(r['ic95_inf'], 3)}; {_num(r['ic95_sup'], 3)}]",
        _num(r["acrescimo_percentual"] * 100, 1) + "\\%",
    ]) for _, r in df.iterrows()]
    _escrever("mando_ajustado_por_temporada", linhas, "lrcr",
              ["Temporada", "$\\gamma$", "IC 95\\%", "Acréscimo de gols"])


def efeito_publico(tabelas: Path) -> None:
    df = pd.read_csv(tabelas / "efeito_publico_ajustado.csv")
    linhas = [" & ".join([
        r["recorte"], _num(r["gamma_com_publico"], 4),
        _num(r["delta_sem_publico"], 4, sinal=True),
        f"[{_num(r['ic95_inf'], 3)}; {_num(r['ic95_sup'], 3)}]",
        _p(r["p_valor"]),
        f"{int(r['n_sem_publico'])} / {int(r['n_com_publico'])}",
    ]) for _, r in df.iterrows()]
    _escrever("efeito_publico_ajustado", linhas, "lrrccr",
              ["Recorte", "$\\gamma$", "$\\delta$", "IC 95\\%", "$p$",
               "$n$ sem / com"])


def desempenho_preditivo(tabelas: Path) -> None:
    df = pd.read_csv(tabelas / "preditivo_resumo.csv", index_col=0)
    rotulos = {
        "dixon_coles": "Dixon-Coles",
        "regressao_logistica": "Regressão logística",
        "gradient_boosting": "\\textit{Gradient boosting}",
        "frequencia_base": "Frequência base",
        "sempre_casa": "Sempre o mandante",
        "odds_mercado": "Odds de mercado",
    }
    linhas = [" & ".join([
        rotulos.get(modelo, modelo), _num(r["log_loss"], 4), _num(r["brier"], 4),
        _num(r["acuracia"] * 100, 1) + "\\%", f"{int(r['n'])}",
    ]) for modelo, r in df.sort_values("log_loss").iterrows()]
    _escrever("preditivo_resumo", linhas, "lrrrr",
              ["Modelo", "\\textit{Log-loss}", "Brier", "Acurácia", "$n$"])


def fator_casa_por_time(tabelas: Path, n: int = 10) -> None:
    df = pd.read_csv(tabelas / "fator_casa_por_time.csv", index_col=0)
    df = df[df["amostra_suficiente"]].sort_values("dif_pontos", ascending=False)
    linhas = [" & ".join([
        time, f"{int(r['jogos_casa'])}", f"{int(r['n_temporadas'])}",
        "Sim" if r["big_six"] else "Não",
        _num(r["pontos_casa"]), _num(r["pontos_fora"]),
        _num(r["dif_pontos"], sinal=True), _num(r["ganho_relativo"]),
    ]) for time, r in df.head(n).iterrows()]
    _escrever("fator_casa_por_time", linhas, "lrrcrrrr",
              ["Clube", "Jogos casa", "Temp.", "\\textit{Big Six}",
               "Pts casa", "Pts fora", "$\\Delta$ pts", "Ganho rel."])


def mudanca_estadio(tabelas: Path) -> None:
    caminho = tabelas / "mudanca_estadio.csv"
    if not caminho.exists():
        return
    df = pd.read_csv(caminho)
    linhas = [" & ".join([
        r["time"], r["periodo"].capitalize(), r["estadio"],
        f"{int(r['jogos_casa'])}", _num(r["pontos_casa"]), _num(r["pontos_fora"]),
        _num(r["dif_pontos"], sinal=True),
    ]) for _, r in df.iterrows()]
    _escrever("mudanca_estadio", linhas, "lllrrrr",
              ["Clube", "Período", "Estádio", "Jogos casa",
               "Pts casa", "Pts fora", "$\\Delta$ pts"])


def main() -> int:
    tabelas = config.DIR_TABELAS
    if not tabelas.exists():
        print("Rode scripts/executar_analise.py e scripts/executar_modelagem.py antes.")
        return 1

    print("Gerando tabelas LaTeX:")
    testes_estatisticos(tabelas)
    fator_casa_por_faixa(tabelas)
    contraste_publico(tabelas)
    taxa_conversao(tabelas)
    evolucao_temporal(tabelas)
    mando_ajustado(tabelas)
    efeito_publico(tabelas)
    desempenho_preditivo(tabelas)
    fator_casa_por_time(tabelas)
    mudanca_estadio(tabelas)

    # As figuras vão em PDF vetorial, com o mesmo nome usado no texto.
    destino = RAIZ / "tcc2" / "figuras"
    destino.mkdir(parents=True, exist_ok=True)
    copiadas = 0
    for figura in sorted(config.DIR_FIGURAS.glob("*.pdf")):
        (destino / figura.name).write_bytes(figura.read_bytes())
        copiadas += 1
    print(f"Figuras copiadas para tcc2/figuras/: {copiadas}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
