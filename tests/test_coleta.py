"""Testes da coleta: integridade dos arquivos e validação de contagem."""

import pandas as pd
import pytest

from tcc import coleta, config


def _csv_de_temporada(caminho, n_partidas=380, linha_extra=None):
    """Escreve um CSV no formato do football-data.co.uk."""
    colunas = list(coleta.COLUNAS_OBRIGATORIAS)
    linhas = []
    for i in range(n_partidas):
        linha = {c: 0 for c in colunas}
        linha.update({
            "Date": f"{(i % 28) + 1:02d}/08/2014",
            "HomeTeam": f"Time{i % 20:02d}",
            "AwayTeam": f"Time{(i + 1) % 20:02d}",
            "FTHG": 1, "FTAG": 0, "FTR": "H",
        })
        linhas.append(linha)

    quadro = pd.DataFrame(linhas, columns=colunas)
    quadro.to_csv(caminho, index=False)

    if linha_extra is not None:
        with open(caminho, "a") as arquivo:
            arquivo.write(linha_extra + "\n")


def test_linha_de_preenchimento_no_fim_do_arquivo_e_descartada(tmp_path):
    """O arquivo de 2014/15 do portal chega com 381 linhas para 380 partidas.

    A causa são vírgulas sobrando no fim do CSV, que o pandas lê como uma linha
    inteira de NaN.
    """
    vazia = "," * (len(coleta.COLUNAS_OBRIGATORIAS) - 1)
    _csv_de_temporada(tmp_path / "E0_1415.csv", linha_extra=vazia)

    assert len(pd.read_csv(tmp_path / "E0_1415.csv")) == 381

    bruto = coleta.carregar_bruto(("1415",), dir_raw=tmp_path)

    assert len(bruto) == config.JOGOS_POR_TEMPORADA


def test_linha_incompleta_nao_e_varrida_para_debaixo_do_tapete(tmp_path):
    """Lixo de fim de arquivo é uma coisa; dado corrompido é outra."""
    colunas = list(coleta.COLUNAS_OBRIGATORIAS)
    parcial = dict.fromkeys(colunas, "")
    parcial["Date"] = "10/05/2015"          # tem data
    parcial["HomeTeam"] = "TimeFantasma"    # tem mandante
    # ...mas não tem visitante nem placar.
    linha = ",".join(str(parcial[c]) for c in colunas)
    _csv_de_temporada(tmp_path / "E0_1415.csv", linha_extra=linha)

    with pytest.raises(coleta.ErroDeColeta, match="identidade incompletos"):
        coleta.carregar_bruto(("1415",), dir_raw=tmp_path)


def test_temporada_incompleta_e_denunciada_pelo_nome(tmp_path):
    """A mensagem precisa dizer qual temporada está fora do padrão."""
    _csv_de_temporada(tmp_path / "E0_1415.csv", n_partidas=379)

    with pytest.raises(coleta.ErroDeColeta) as erro:
        coleta.carregar_bruto(("1415",), dir_raw=tmp_path)

    mensagem = str(erro.value)
    assert "1415" in mensagem
    assert "379" in mensagem


def test_arquivo_ausente_falha_alto(tmp_path):
    """O TCC1 engolia a falha e seguia com um dataset parcial."""
    with pytest.raises(coleta.ErroDeColeta, match="Arquivo ausente"):
        coleta.carregar_bruto(("1516",), dir_raw=tmp_path)


def test_coluna_obrigatoria_ausente_falha_alto(tmp_path):
    _csv_de_temporada(tmp_path / "E0_1415.csv")
    quadro = pd.read_csv(tmp_path / "E0_1415.csv").drop(columns=["HST"])
    quadro.to_csv(tmp_path / "E0_1415.csv", index=False)

    with pytest.raises(coleta.ErroDeColeta, match="colunas obrigatórias"):
        coleta.carregar_bruto(("1415",), dir_raw=tmp_path)


def test_arquivo_sem_registro_no_manifesto_e_registrado(tmp_path):
    """O manifesto pode se perder sem que os CSVs se percam junto.

    Acontece quando o ambiente restaura o repositório por cima da área de
    trabalho: os dados baixados são ignorados pelo Git e sobrevivem, o manifesto
    não. Rebaixar descartaria arquivos válidos; seguir sem registro desligaria a
    verificação de integridade em silêncio.
    """
    _csv_de_temporada(tmp_path / "E0_1415.csv")
    assert not (tmp_path / coleta.NOME_MANIFESTO).exists()

    manifesto = coleta.baixar_temporadas(("1415",), dir_raw=tmp_path)

    assert "1415" in manifesto
    assert manifesto["1415"]["url"] == coleta.ORIGEM_DESCONHECIDA
    assert manifesto["1415"]["sha256"]


def test_integridade_volta_a_proteger_apos_reconstruir_o_manifesto(tmp_path):
    """Depois de reconstruído, o manifesto precisa denunciar uma alteração."""
    _csv_de_temporada(tmp_path / "E0_1415.csv")
    coleta.baixar_temporadas(("1415",), dir_raw=tmp_path)

    alvo = tmp_path / "E0_1415.csv"
    alvo.write_text(alvo.read_text() + "\n")

    with pytest.raises(coleta.ErroDeColeta, match="não confere com o manifesto"):
        coleta.carregar_bruto(("1415",), dir_raw=tmp_path)


def test_erro_de_integridade_diz_a_procedencia_registrada(tmp_path):
    """A mensagem precisa permitir distinguir fonte trocada de arquivo alterado."""
    _csv_de_temporada(tmp_path / "E0_1415.csv")
    coleta.baixar_temporadas(("1415",), dir_raw=tmp_path)

    alvo = tmp_path / "E0_1415.csv"
    alvo.write_text(alvo.read_text() + "\n")

    with pytest.raises(coleta.ErroDeColeta) as erro:
        coleta.carregar_bruto(("1415",), dir_raw=tmp_path)

    mensagem = str(erro.value)
    assert "Manifesto registra" in mensagem
    assert "Acessado em" in mensagem


def test_manifesto_existente_nao_e_sobrescrito(tmp_path):
    """Um registro legítimo de procedência não pode virar 'desconhecida'."""
    _csv_de_temporada(tmp_path / "E0_1415.csv")
    coleta.baixar_temporadas(("1415",), dir_raw=tmp_path)

    manifesto = coleta.baixar_temporadas(("1415",), dir_raw=tmp_path)

    assert manifesto["1415"]["url"] == coleta.ORIGEM_DESCONHECIDA
    primeiro_hash = manifesto["1415"]["sha256"]
    assert coleta.baixar_temporadas(("1415",), dir_raw=tmp_path)["1415"]["sha256"] == primeiro_hash
