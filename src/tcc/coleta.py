"""Coleta dos dados com cache local e validação de integridade.

O TCC1 lia os CSVs direto da URL a cada execução e engolia falhas com um
`except Exception` que apenas imprimia a mensagem. Dois problemas:

1. O football-data.co.uk reescreve os arquivos (correções de placar, novas
   colunas de odds). Duas execuções em datas diferentes podiam produzir números
   diferentes, sem que nada no notebook indicasse isso.
2. Uma falha de rede gerava um dataset parcial e a análise seguia normalmente,
   com resultados silenciosamente errados.

Aqui o download acontece uma vez, o arquivo fica em `data/raw/`, cada arquivo tem
o SHA-256 registrado num manifesto, e qualquer inconsistência interrompe a
execução.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd

from . import config

URL_PRIMARIA = "https://www.football-data.co.uk/mmz4281/{temporada}/E0.csv"
URL_ESPELHO = (
    "https://raw.githubusercontent.com/datasets/football-datasets/master/"
    "datasets/premier-league/season-{temporada}.csv"
)

NOME_MANIFESTO = "manifesto.json"

COLUNAS_OBRIGATORIAS = (
    "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR",
    "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF", "HY", "AY", "HR", "AR",
)


class ErroDeColeta(RuntimeError):
    """Levantado quando os dados coletados não passam na validação."""


def _sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _baixar(temporada: str, destino: Path) -> str:
    """Baixa uma temporada, tentando a fonte primária e depois o espelho.

    Retorna a URL efetivamente usada. Falha alto se nenhuma fonte responder — o
    silêncio do TCC1 aqui era o que permitia um dataset parcial passar batido.
    """
    erros = []
    for url in (URL_PRIMARIA, URL_ESPELHO):
        endereco = url.format(temporada=temporada)
        try:
            with urlopen(endereco, timeout=60) as resposta:
                conteudo = resposta.read()
        except (URLError, OSError, TimeoutError) as erro:
            erros.append(f"{endereco}: {type(erro).__name__}: {erro}")
            continue
        if not conteudo.strip():
            erros.append(f"{endereco}: resposta vazia")
            continue
        destino.write_bytes(conteudo)
        return endereco

    detalhe = "\n  ".join(erros)
    raise ErroDeColeta(
        f"Não foi possível baixar a temporada {temporada}. Tentativas:\n  {detalhe}"
    )


def baixar_temporadas(
    temporadas: tuple[str, ...] = config.TEMPORADAS,
    dir_raw: Path | None = None,
    forcar: bool = False,
) -> dict:
    """Garante que os CSVs brutos existam localmente e atualiza o manifesto.

    Args:
        temporadas: códigos no formato do football-data ('1516', '1617', ...).
        dir_raw: diretório de destino. Padrão: `data/raw/`.
        forcar: rebaixa os arquivos mesmo que já existam em disco.

    Returns:
        O manifesto, com URL de origem, data de acesso e SHA-256 por temporada.
    """
    dir_raw = dir_raw or config.DIR_RAW
    dir_raw.mkdir(parents=True, exist_ok=True)
    caminho_manifesto = dir_raw / NOME_MANIFESTO

    manifesto = {}
    if caminho_manifesto.exists():
        manifesto = json.loads(caminho_manifesto.read_text(encoding="utf-8"))

    for temporada in temporadas:
        destino = dir_raw / f"E0_{temporada}.csv"
        if destino.exists() and not forcar:
            continue
        url = _baixar(temporada, destino)
        manifesto[temporada] = {
            "url": url,
            "acessado_em": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "sha256": _sha256(destino),
            "bytes": destino.stat().st_size,
        }

    caminho_manifesto.write_text(
        json.dumps(manifesto, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifesto


def _verificar_integridade(dir_raw: Path, temporadas: tuple[str, ...]) -> None:
    """Compara os arquivos em disco com os hashes do manifesto."""
    caminho_manifesto = dir_raw / NOME_MANIFESTO
    if not caminho_manifesto.exists():
        return
    manifesto = json.loads(caminho_manifesto.read_text(encoding="utf-8"))
    for temporada in temporadas:
        registro = manifesto.get(temporada)
        caminho = dir_raw / f"E0_{temporada}.csv"
        if registro is None or not caminho.exists():
            continue
        if _sha256(caminho) != registro["sha256"]:
            raise ErroDeColeta(
                f"O arquivo da temporada {temporada} mudou desde a coleta "
                f"(SHA-256 não confere com o manifesto). Rode com forcar=True e "
                f"reprocesse a análise, ciente de que os números vão mudar."
            )


def carregar_bruto(
    temporadas: tuple[str, ...] = config.TEMPORADAS,
    dir_raw: Path | None = None,
) -> pd.DataFrame:
    """Carrega e consolida os CSVs brutos, validando o resultado.

    Raises:
        ErroDeColeta: se faltar arquivo, faltar coluna obrigatória ou o número de
            partidas divergir do esperado.
    """
    dir_raw = dir_raw or config.DIR_RAW
    _verificar_integridade(dir_raw, temporadas)

    quadros = []
    for temporada in temporadas:
        caminho = dir_raw / f"E0_{temporada}.csv"
        if not caminho.exists():
            raise ErroDeColeta(
                f"Arquivo ausente: {caminho}. Rode `baixar_temporadas()` antes."
            )
        quadro = pd.read_csv(caminho)
        faltantes = [c for c in COLUNAS_OBRIGATORIAS if c not in quadro.columns]
        if faltantes:
            raise ErroDeColeta(
                f"Temporada {temporada} sem as colunas obrigatórias: {faltantes}"
            )
        quadro["Season"] = temporada
        quadros.append(quadro)

    bruto = pd.concat(quadros, ignore_index=True)

    esperado = config.JOGOS_POR_TEMPORADA * len(temporadas)
    if len(bruto) != esperado:
        contagem = bruto.groupby("Season").size().to_dict()
        raise ErroDeColeta(
            f"Esperava {esperado} partidas ({len(temporadas)} temporadas x "
            f"{config.JOGOS_POR_TEMPORADA}), encontrei {len(bruto)}. "
            f"Partidas por temporada: {contagem}"
        )

    return bruto


def obter_bruto(
    temporadas: tuple[str, ...] = config.TEMPORADAS,
    dir_raw: Path | None = None,
) -> pd.DataFrame:
    """Baixa (se preciso) e carrega os dados brutos. Ponto de entrada usual."""
    baixar_temporadas(temporadas, dir_raw)
    return carregar_bruto(temporadas, dir_raw)
