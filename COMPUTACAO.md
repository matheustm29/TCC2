# A dimensão computacional do trabalho

Material de apoio para a reunião de orientação. Responde às perguntas do
orientador sobre os procedimentos técnicos e aponta o que falta levar para o
texto da monografia.

Todos os números abaixo foram conferidos no repositório na data desta revisão.

---

## Resumo em uma frase

O trabalho tem um pipeline de dados implementado em Python, com 2.733 linhas em
sete módulos, 515 linhas de scripts de execução e 1.329 linhas de teste cobrindo
81 casos. Nada disso aparece na monografia, que hoje cita apenas "Python" e uma
lista de bibliotecas. A lacuna é de redação, não de trabalho.

---

## 1. Como eram os arquivos de dados originais?

**Formato.** CSV, um arquivo por temporada, servidos pelo portal
Football-Data.co.uk no padrão `mmz4281/<temporada>/E0.csv`.

**Volume.** 17 arquivos baixados (2009/10 a 2025/26), dos quais 11 compõem o
recorte do estudo (2015/16 a 2025/26). Cerca de 495 KB no total, ~30 KB por
arquivo. As quatro temporadas anteriores a 2013/14 entram apenas no teste de
quebra de série descrito adiante.

**Estrutura.** Uma linha por partida, 380 linhas por temporada, 22 colunas:

| Grupo | Colunas |
|---|---|
| Identificação | `Date`, `HomeTeam`, `AwayTeam`, `Referee` |
| Placar | `FTHG`, `FTAG`, `FTR`, `HTHG`, `HTAG`, `HTR` |
| Finalizações | `HS`, `AS`, `HST`, `AST` |
| Outras estatísticas | `HC`, `AC`, `HF`, `AF`, `HY`, `AY`, `HR`, `AR` |

O portal primário serve ainda dezenas de colunas de cotações de casas de
apostas, não usadas no recorte atual.

**Ponto a destacar na reunião:** o dado bruto é pequeno em bytes e grande em
armadilhas. O trabalho computacional não está no volume; está no tratamento.

---

## 2. Quais procedimentos de limpeza e preparação foram realizados?

Esta é a pergunta com a melhor resposta, porque cada procedimento nasceu de um
defeito real encontrado nos dados, não de uma lista genérica de boas práticas.

### 2.1 Três formatos de data no mesmo acervo

Os arquivos misturam `YYYY-MM-DD`, `DD/MM/YYYY` e `DD/MM/YY`. O pandas infere um
único formato e converte o resto para `NaT`: 380 partidas perdiam a data em
silêncio. Pior, `dayfirst=True` corrompe datas ISO sem erro algum — `2019-08-10`
vira 8 de outubro.

A solução detecta o formato por expressão regular, normaliza cada subconjunto
para ISO separadamente e só então faz uma conversão final, o que mantém o tipo
da coluna consistente:

```python
FORMATOS_DE_DATA = (
    (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
    (r"\d{2}/\d{2}/\d{4}", "%d/%m/%Y"),
    (r"\d{2}/\d{2}/\d{2}", "%d/%m/%y"),
)
```

### 2.2 Linha de preenchimento no arquivo de 2014/15

O arquivo tem 381 linhas: a última é uma vírgula solta, lida como registro
totalmente nulo. O descarte exige que **todas** as colunas de identidade estejam
nulas; uma linha parcialmente preenchida levanta exceção em vez de ser
descartada, porque aí o problema é outro e precisa de inspeção.

### 2.3 Reescrita silenciosa da fonte

O portal corrige placares e acrescenta colunas ao longo do tempo. Duas execuções
em datas diferentes produziam números diferentes sem aviso. O download passou a
ocorrer uma vez, com cache em `data/raw/`, e cada arquivo tem procedência e
SHA-256 registrados em `data/manifesto_referencia.json`:

```json
"1516": {
  "acessado_em": "2026-09-07",
  "bytes": 29349,
  "sha256": "5389973e…",
  "url": "https://…/season-1516.csv"
}
```

Qualquer divergência interrompe a execução.

### 2.4 Quebra de série detectada automaticamente

A média de finalizações no alvo cai 37% entre 2012/13 e 2013/14, enquanto gols e
finalizações totais seguem estáveis. Não é mudança no jogo: é mudança de critério
do provedor. A rotina `verificar_quebras_de_serie` detecta o salto, e a constante
`PRIMEIRA_TEMPORADA_HST_COMPARAVEL` impede comparações que atravessem essa
fronteira. O estudo de mudança de estádio anula as métricas de finalização
justamente por isso.

### 2.5 Validações estruturais

Contagem de partidas por temporada, `2 × (n_times − 1)` jogos por clube na tabela
de classificação, e checagem de que nenhum clube joga duas vezes no mesmo dia —
o que garante que `(Date, HomeTeam)` é chave de ordenação total.

---

## 3. Como os dados ficaram depois do processamento?

| Artefato | Dimensões | Conteúdo |
|---|---|---|
| `data/processed/partidas.csv` | 4.180 × 29 | 22 colunas originais + 7 derivadas |
| `data/processed/classificacao.csv` | 220 × 12 | 11 temporadas × 20 clubes |
| formato longo (em memória) | 8.360 × … | uma linha por clube por partida |
| `tabelas/` | 18 arquivos CSV | tudo que vira tabela no LaTeX |
| `figuras/` | 9 figuras (PDF + PNG) | tudo que vira figura no LaTeX |

**Variáveis derivadas:** `pts_mandante`, `pts_visitante`, `saldo_mandante`,
`gols_totais`, `publico`, `mandante_big_six`, `visitante_big_six`.

**Cobertura:** 11 temporadas, 34 clubes distintos, 4.180 partidas, distribuídas
em 3.708 jogos com público pleno, 419 sem público e 53 com público limitado.

### A transformação que mais importa

O `formato_longo` converte a tabela de partidas (uma linha, dois times) em uma
tabela por clube (duas linhas, uma por time). Parece cosmético, mas é a correção
estrutural do erro central do TCC 1: agregar `pts_mandante` e `pts_visitante` da
mesma partida por um rótulo do mandante misturava o desempenho do Big Six em casa
com o desempenho dos **adversários** do Big Six fora. Com uma linha por clube, o
erro deixa de ser possível de cometer.

---

## 4. Quais algoritmos, bibliotecas e técnicas foram usados?

**Ambiente:** Python 3, com versões fixadas em `requirements.txt` — pandas 3.0.5,
NumPy 2.3.4, SciPy 1.17.1, scikit-learn 1.9.0, Matplotlib 3.10.7, pytest 8.4.2.

### Implementado do zero (não é biblioteca pronta)

**Modelo de Poisson bivariado de Dixon-Coles.** Estimação por máxima
verossimilhança de 70 parâmetros livres (34 clubes: ataque com `n−1` graus de
liberdade, defesa com `n`, mais `μ`, `γ` e `ρ`):

- otimizador L-BFGS-B via `scipy.optimize.minimize`, com reinício a partir do
  último ponto quando o limite de avaliações é atingido sem convergência;
- restrição de identificabilidade: ataque de média zero, imposta
  estruturalmente no desempacotamento do vetor, não por penalização;
- correção `ρ` para placares baixos, que o Poisson duplo independente modela mal;
- decaimento temporal exponencial opcional, por data de referência;
- **erro padrão por verossimilhança perfilada**, não pela curvatura marginal.

**Rating Elo.** `K = 20`, vantagem de mando de 60 pontos, regressão de 25% à
média da liga entre temporadas. Calculado **antes** de cada partida, de modo que
a linha nunca contém informação do próprio resultado.

### Biblioteca

- `LogisticRegression` dentro de um `Pipeline` com `StandardScaler`;
- `HistGradientBoostingClassifier`;
- testes de hipótese e otimização do SciPy.

### Técnicas de avaliação

Log-loss e escore de Brier como regras de pontuação estritamente próprias,
acurácia como métrica secundária, curvas de calibração, bootstrap agrupado por
clube, teste binomial condicionado às partidas decididas, teste *t* pareado,
Welch com *d* de Cohen e intervalos de confiança em todos os contrastes.

---

## 5. Como o pipeline foi organizado?

Pacote `src/tcc/`, em camadas, sem dependência circular:

```
config.py        constantes do estudo (recorte, janelas, limiares, semente)
    ↓
coleta.py        download, cache, manifesto SHA-256, validação estrutural
    ↓
preparacao.py    datas, variáveis derivadas, formato longo, classificação
    ↓
    ├── estatistica.py   testes de hipótese, efeito, IC, bootstrap
    ├── analise.py       recortes do estudo (faixa, Big Six, público)
    ├── modelos.py       Dixon-Coles e variantes do parâmetro de mando
    └── preditivo.py     features pré-jogo, walk-forward, métricas
    ↓
visualizacao.py  tema, paleta validada, as 9 figuras
```

Dois pontos de entrada, separados por custo:

| Script | O que faz |
|---|---|
| `scripts/executar_analise.py` | coleta → preparação → testes → figuras. Rápido. |
| `scripts/executar_modelagem.py` | Dixon-Coles e validação temporal. Lento. |
| `scripts/gerar_tabelas_latex.py` | converte `tabelas/*.csv` em tabelas `booktabs` |

**Regra que organiza tudo:** nenhum número é copiado à mão para o LaTeX. Toda
tabela e toda figura da monografia saem de `tabelas/` e `figuras/`, gerados por
script. Mudou o dado, reexecuta, recompila.

---

## 6. Houve modelagem ou definição de arquitetura?

Sim, e vale apresentar como decisões com justificativa, não como organização de
pastas.

**Separação entre lógica e narrativa.** O TCC 1 era um notebook único. O erro do
Big Six passou despercebido porque não havia teste possível em uma célula. Hoje o
notebook consome funções testadas em vez de reimplementá-las.

**Trava experimental contra vazamento de dados.** As colunas `HS`, `HST`, `HC`,
`HF` só existem depois do apito final; usá-las para prever o resultado produz
acurácia alta e trabalho errado. O conjunto de 15 variáveis preditoras contém
apenas informação anterior ao apito inicial, e há um teste automatizado que
**altera o placar de uma partida e exige que nenhuma variável daquela mesma
partida mude**. É a forma executável de afirmar ausência de vazamento.

**Protocolo único de previsão.** Todos os modelos passam pela mesma função
`_prever_em_blocos`, que caminha pela temporada de teste reajustando a cada 10
partidas. Sem isso, um modelo que reestima ao longo da temporada levaria vantagem
sobre outro que não reestima, e a comparação mediria o protocolo em vez do
modelo. São 8 temporadas de teste, 3.040 partidas avaliadas e 304 reajustes por
modelo.

**Imputação ajustada apenas no treino de cada janela**, nunca na série completa.

**Dois perfis de otimizador.** O cálculo do erro padrão custa duas
reotimizações, o que é proibitivo dentro do laço de validação. Existe um perfil
rápido para o laço e um preciso para as estimativas publicadas; a diferença
máxima nas probabilidades previstas entre os dois é de 1,2 × 10⁻³, verificada
antes de adotar o perfil rápido.

**Validação por recuperação de parâmetro.** Simulando partidas com `γ` conhecido,
o intervalo construído pela curvatura marginal cobria o valor verdadeiro em 83%
das réplicas, não em 95%. Foi o que motivou a troca pela verossimilhança
perfilada, que elevou a cobertura a 97,5%. É um resultado de engenharia: o
primeiro método estava subestimando a incerteza em cerca de um quarto.

---

## 7. Como as etapas foram integradas?

Pela fronteira de arquivos, não por chamadas diretas entre notebooks:

1. `data/raw/` — CSVs originais, imutáveis, com manifesto;
2. `data/processed/` — dataset tratado, regenerável;
3. `tabelas/` e `figuras/` — artefatos de saída, consumidos pelo LaTeX;
4. `tests/` — 81 casos que fixam o comportamento de cada etapa.

Cada camada consome a anterior e falha alto: um erro de coleta interrompe a
execução em vez de deixar passar um conjunto parcial. A reexecução é
determinística, com semente fixa em `config.SEMENTE = 42`.

---

## O que levar para a monografia

### A mudança principal

Transformar a Seção 3.1, que hoje é uma lista de bibliotecas, num bloco de
implementação. Proposta de estrutura:

| Seção | Conteúdo | Figura ou tabela |
|---|---|---|
| Arquitetura do pipeline | camadas, fronteiras, pontos de entrada | **diagrama novo** |
| Caracterização dos dados brutos | formato, volume, colunas, procedência | tabela nova |
| Problemas encontrados e tratamento | os cinco da Seção 2 acima | tabela nova |
| Conjunto resultante | antes/depois e dicionário das derivadas | tabela nova |
| Implementação do Dixon-Coles | parametrização, otimizador, identificabilidade | pseudocódigo |
| Protocolo de validação temporal | janelas, blocos, trava anti-vazamento | **diagrama novo** |
| Verificação e reprodutibilidade | testes, manifesto, semente, custo | tabela nova |

### O mapeamento do CRISP-DM

Hoje o CRISP-DM é descrito na fundamentação e nunca mais aparece. O orientador
diz exatamente isso. Uma tabela ligando cada fase ao que a implementa resolve:

| Fase CRISP-DM | Onde está | O que foi feito |
|---|---|---|
| Entendimento do negócio | Cap. 1 | pergunta de pesquisa e objetivos |
| Entendimento dos dados | `coleta.py`, `verificar_quebras_de_serie` | procedência, integridade, quebra de série |
| Preparação dos dados | `preparacao.py` | datas, derivadas, formato longo, classificação |
| Modelagem | `modelos.py`, `preditivo.py` | Dixon-Coles, Elo, regressão, boosting |
| Avaliação | `estatistica.py`, métricas e calibração | log-loss, Brier, IC, recuperação de parâmetro |
| Implantação | `scripts/`, `tabelas/`, `figuras/` | pipeline reexecutável e código publicado |

### Sobre a densidade do texto

O orientador disse ter tido dificuldade com os resultados. Vale abrir o Capítulo
4 com um quadro de duas colunas — pergunta e achado em uma linha cada — antes de
entrar nos números, e fechar cada seção com uma frase de leitura em linguagem
comum. O conteúdo não muda; muda o caminho de entrada.
