# TCC2 — Análise do Fator Casa na Premier League

Continuação do TCC1 (*Análise do Fator Casa na Premier League*, metodologia CRISP-DM),
de Matheus Ferreira Alphonse dos Anjos.

Recorte: 11 temporadas da Premier League (2015/16 a 2025/26), 4.180 partidas,
a partir do portal `football-data.co.uk`.

## Como rodar

```bash
pip install -r requirements.txt
python scripts/executar_analise.py     # análise descritiva e inferencial
python scripts/executar_modelagem.py   # Dixon-Coles e modelos preditivos (lento)
pytest tests/ -q
```

O script baixa os dados uma vez para `data/raw/`, registra o SHA-256 de cada arquivo
em `data/raw/manifesto.json` e interrompe a execução se algum arquivo mudar depois
disso. Tudo que vai para o LaTeX sai daqui: nenhum número deve ser copiado à mão de
uma saída de célula.

## Fontes de dados

`coleta.py` tenta o portal `football-data.co.uk` primeiro e cai para um espelho no
GitHub (`datasets/football-datasets`) quando o portal está inacessível. A URL
efetivamente usada em cada temporada fica registrada em `data/raw/manifesto.json`.

**Atenção para o TCC2:** o espelho traz apenas as colunas de jogo (placar,
finalizações, escanteios, faltas, cartões). As **odds das casas de apostas**
(`B365H`, `B365D`, `B365A` e demais) existem só na fonte primária. Como as odds são
o baseline mais honesto para o modelo preditivo, a etapa de aprendizado de máquina
precisa ser rodada num ambiente com acesso ao `football-data.co.uk` — o Colab
resolve. O manifesto versionado neste repositório foi gerado a partir do espelho,
porque o portal está bloqueado pela política de rede do ambiente onde a análise foi
executada; ao rodar de um ambiente com acesso, o manifesto é reescrito apontando
para a fonte primária.

## Documentos

| Caminho | Descrição |
|---------|-----------|
| `REVISAO_TCC1.md` | Revisão técnica do TCC1: bugs, problemas metodológicos e proposta para o TCC2 |
| `RESULTADOS.md` | O que mudou nos números depois das correções |
| `MODELAGEM.md` | Dixon-Coles com termo de mando e modelagem preditiva |
| `tcc1/` | Material original do TCC1 (notebook e correções da banca), preservado como baseline |

## Estrutura

```
src/tcc/
  config.py        Constantes do estudo — temporadas, janelas de público, faixas
  coleta.py        Download com cache, manifesto e validação de integridade
  preparacao.py    Limpeza, variáveis derivadas e tabela de classificação
  estatistica.py   Testes de hipótese, intervalos de confiança e tamanhos de efeito
  analise.py       Fator casa por time, faixa, temporada e regime de público
  modelos.py       Poisson bivariado (Dixon-Coles) com termo de mando de campo
  preditivo.py     Features pré-jogo, baselines e validação temporal
  visualizacao.py  Tema único de figuras e exportação em PDF vetorial
scripts/           Execução da análise ponta a ponta
tests/             Travas para cada bug corrigido do TCC1 e para vazamento de dados
tabelas/           Saída em CSV, pronta para booktabs
figuras/           Saída em PDF vetorial e PNG 300 dpi, pronta para \includegraphics
```

## Estado

Correções do `REVISAO_TCC1.md` aplicadas e verificadas com os dados reais, e a
modelagem do TCC2 implementada: Dixon-Coles com termo de mando e modelos
preditivos com validação temporal.

Pendente: o baseline com odds de mercado, que exige acesso ao portal
`football-data.co.uk` (ver a seção *Fontes de dados* acima), e as correções de
redação e referências apontadas pela banca.
