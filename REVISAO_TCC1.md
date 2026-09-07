# Revisão técnica do TCC1 — Análise do Fator Casa na Premier League

Revisão do notebook `tcc1/TCC1_Analise_Fator_Casa_EPL.ipynb` (43 células) cruzada com as
anotações do Prof. Cleber Gimenez Corrêa em `tcc1/TCC1_Sugestoes_Prof_Cleber_Gimenez_Correa.pdf`.

**Diagnóstico geral:** a espinha dorsal está correta e a estrutura CRISP-DM é adequada. O
problema não é falta de trabalho — é que parte das conclusões escritas **não é sustentada
pelos números que o próprio notebook produz**. Há um erro de agregação que inverte um
resultado, testes estatísticos que não testam a hipótese enunciada e uma seção prometida sem
implementação. Nada disso é difícil de corrigir, mas precisa ser corrigido antes de virar
texto, porque são exatamente os pontos que uma banca ataca.

Legenda de prioridade: **P0** = corrigir antes de escrever · **P1** = melhoria metodológica
relevante · **P2** = qualidade de código e reprodutibilidade.

---

## 1. Sumário executivo

| # | Achado | Onde | Prioridade |
|---|--------|------|------------|
| 1 | Agregação Big Six compara mandante × visitante, não casa × fora — conclusão 5.2 é falsa | Célula 39 | **P0** |
| 2 | Teste t trata amostras pareadas como independentes (corr = −0,95) | Célula 8 | **P0** |
| 3 | Qui-quadrado usa H0 uniforme (1/3,1/3,1/3) — hipótese nula errada | Célula 8 | **P0** |
| 4 | Texto diz "média móvel de 3 temporadas", código usa `rolling(window=2)` | Célula 33 | **P0** |
| 5 | Seção "Modernização dos Estádios" prometida, sem nenhuma linha de código | Célula 36 | **P0** |
| 6 | COVID classificado por temporada inteira; a monografia afirma filtro por data | Célula 22 | **P0** |
| 7 | Unidade de análise inflada no teste COVID (partidas em vez de temporadas) | Célula 22 | P1 |
| 8 | Nenhum tamanho de efeito e nenhum intervalo de confiança em todo o trabalho | Global | P1 |
| 9 | Nenhum controle de força do adversário | Células 25/27 | P1 |
| 10 | Efeito teto: diferencial em pontos penaliza mecanicamente times fortes | Células 25/39 | P1 |
| 11 | Ranking por time sem coluna N e sem filtro mínimo de jogos | Célula 25 | P1 |
| 12 | Taxa de conversão: média de razões em vez de razão de somas + viés de seleção | Célula 31 | P1 |
| 13 | Correlação de Pearson sobre variável ordinal e só com dados do mandante | Célula 30 | P1 |
| 14 | Coleta direto da URL sem cache — resultados mudam sozinhos | Célula 4 | P2 |
| 15 | `except Exception` silencioso pode gerar dataset parcial sem erro | Célula 4 | P2 |
| 16 | Sem classificação por temporada — bloqueia o pedido central do professor | — | **P0** |

---

## 2. P0 — Erros que precisam ser corrigidos

### 2.1. Bug crítico: a comparação Big Six × Demais está errada (célula 39)

O código faz:

```python
resumo_bigsix = df_clean.groupby('Home_BigSix').agg(
    Media_Pts_Casa=('PHT', 'mean'),
    Media_Pts_Fora=('PAT', 'mean'),   # <-- aqui
)
```

`PHT` e `PAT` são pontos **da mesma partida**: `PHT` é do mandante, `PAT` é do adversário
visitante. Ao agrupar por `Home_BigSix`, a coluna `Media_Pts_Fora` não mede o desempenho do
Big Six fora de casa — mede o desempenho **dos adversários** que visitaram o Big Six.

A saída do notebook confirma:

```
                Media_Pts_Casa  Media_Pts_Fora     N  Diferencial
Demais Equipes        1.339029        1.408749  2926    -0.069720
Big Six               2.098086        0.700957  1254     1.397129
```

Duas provas de que o número está errado:

1. **O Big Six não faz 0,701 pontos fora de casa.** A tabela da célula 27, no mesmo notebook,
   mostra Man City 2,048 · Liverpool 1,823 · Arsenal 1,612 · Chelsea 1,598 · Man United 1,531
   · Tottenham 1,469 (média 1,68). O valor 0,701 são os pontos dos visitantes de Old Trafford,
   Anfield etc.
2. **A linha "Demais Equipes" diz que times fora do Big Six jogam melhor fora (1,409) do que em
   casa (1,339)**, gerando diferencial negativo. Isso é falso e contradiz frontalmente a tabela
   por time da célula 27, onde praticamente todos os clubes têm diferencial positivo.

**Consequência direta no texto.** A conclusão 5.2 — *"Big Six: maior qualidade, menor
dependência"* — está apoiada nesse número quebrado. E o número correto não sustenta a
afirmação: usando o diferencial casa−fora por time (célula 27, esse sim correto), o Big Six
tem média ≈ **0,418** contra ≈ **0,520** da amostra dos demais times visíveis na tabela. Ou
seja, os valores são próximos e a diferença aponta no sentido oposto ao afirmado.

**Correção.** Calcular o diferencial por *time* e só então agrupar:

```python
dif_por_time = (df_clean.groupby('HomeTeam')['PHT'].mean()
                - df_clean.groupby('AwayTeam')['PAT'].mean()).rename('Dif_Casa_Fora')
dif_por_time = dif_por_time.to_frame()
dif_por_time['Big_Six'] = dif_por_time.index.isin(big_six)
# agora sim: teste entre os dois grupos, n = 6 vs n = k times
```

Note que o teste passa a ter n = número de **times**, não de partidas — o que reduz muito o
poder estatístico e provavelmente tornará a diferença não significativa. Esse é o resultado
honesto.

### 2.2. O teste t compara amostras pareadas como se fossem independentes (célula 8)

`PHT` e `PAT` vêm da mesma linha e são determinísticos entre si: `H → (3,0)`, `D → (1,1)`,
`A → (0,3)`. A soma é sempre 2 ou 3. Reconstruindo a distribuição a partir das contagens
publicadas (H=1853, D=990, A=1337):

```
correlação PHT vs PAT      = -0.948      (independência violada)
ttest_ind (usado no TCC)   : t = 12.878   p = 6.82e-38   <- reproduz exatamente a saída
ttest_rel (pareado)        : t =  9.227   p = 2.15e-20
Cohen d                    = 0.282        (efeito PEQUENO)
```

Duas coisas:

- `equal_var=False` (Welch) resolve variâncias desiguais, **não** resolve dependência entre
  amostras. A anotação do professor na p.13 (*"Usa quando as variâncias dos dois grupos são
  diferentes"*) é justamente um pedido para você explicar a escolha do teste — e a escolha,
  como está, não se justifica.
- A conclusão sobrevive (p continua ínfimo), mas o **tamanho do efeito é pequeno** (d = 0,28).
  A monografia descreve isso como *"assimetria estatística contundente"*. Um p-valor pequeno com
  n = 4.180 não é sinônimo de efeito grande. Reportar d e IC resolve.

### 2.3. O qui-quadrado testa a hipótese errada (célula 8)

O código testa H0: `[1/3, 1/3, 1/3]`. Mas ninguém, nem sob ausência total de fator casa, espera
33% de empates — a taxa histórica de empate no futebol é ~25%. Prova numérica: montei um cenário
contrafactual **sem nenhum fator casa** (mesma taxa real de empates, mas H = A = 1595):

```
chi2 = 175.13   p = 9.35e-39   -> ainda rejeita H0
```

Ou seja, o teste rejeitaria a nula mesmo num mundo onde o fator casa não existe. Ele mede
"a distribuição não é uniforme", não "existe vantagem do mandante".

**Teste correto** (H0: entre jogos decididos, vitórias em casa = vitórias fora):

```
binomial 1853/3190 = 0.5809   p = 3.18e-20   IC95% = [0.5663 ; 1.0]
```

A conclusão do TCC se mantém — mas agora com o teste que de fato corresponde à pergunta.
Alternativa igualmente defensável: qui-quadrado com `f_exp` derivado da taxa de empates
observada e H = A.

### 2.4. Média móvel: texto diz 3, código usa 2 (célula 33)

```python
# Modelando a tendência com uma média móvel de 3 temporadas para suavizar variações
analise_temporal['Home_Adv_Smooth'] = analise_temporal['Home_Advantage_Diff'].rolling(window=2).mean()
```

Comentário e código discordam, e a legenda do gráfico só diz "Média Móvel". Com 11 pontos,
janela 3 é mais defensável; o importante é que o número no texto seja o número no código.

### 2.5. Seção 4.5 prometida e não implementada (célula 36)

*"Estudo de Caso: O Impacto da Modernização dos Estádios"* descreve a análise de West Ham,
Tottenham e Brentford — e **não tem uma única linha de código depois**. Pior: como está proposta,
ela é inviável com esse recorte de dados:

- **Brentford** subiu para a Premier League em 2021/22, já no Gtech. Não existe nenhum jogo dele
  na EPL antes da mudança. Comparação "antes × depois" é impossível.
- **West Ham** mudou em 2016. Com dados a partir de 2015/16, há **uma única temporada** (19 jogos
  em casa) no Upton Park. Base fraca demais para uma afirmação.
- **Tottenham** mudou em abril de 2019, no meio de 2018/19, e ainda jogou 2017/18 e parte de
  2018/19 em Wembley — ou seja, são três sedes, não duas.

Duas saídas: (a) recuar o recorte para ~2010/11 só para esse estudo de caso, o que dá 5–6
temporadas de linha de base para West Ham e Tottenham; ou (b) remover a seção. Manter o texto
sem análise é o pior cenário possível numa defesa.

### 2.6. Classificação COVID por temporada contradiz a monografia (célula 22)

O `covid_map` rotula **temporadas inteiras**. A monografia (p.11, seção 3.3.2) afirma:

> *"As partidas ocorridas entre 17 de junho de 2020 e 23 de maio de 2021 foram catalogadas sob
> uma variável binária indicando a ausência de público"*

Isso não é o que o código faz. E a diferença é material:

- 2019/20 inteira vira "COVID (Parcial)", mas só ~92 dos 380 jogos (de 17/06 a 26/07/2020)
  foram sem público. Os outros ~288 tiveram estádio cheio.
- 2020/21 é rotulada "COVID (Total)", mas houve jogos com público limitado em dezembro/2020 e
  nas rodadas finais de maio/2021.

Você já tem a coluna `Date` convertida. A flag correta é por partida:

```python
df_clean['Sem_Publico'] = df_clean['Date'].between('2020-06-17', '2021-05-18')
```

Isso torna o resultado mais forte, não mais fraco: dentro da mesma temporada 2019/20 você
compara os mesmos times com e sem público — um contrafactual muito melhor do que comparar
temporadas diferentes.

### 2.7. Não existe tabela de classificação — e ela é o pedido central do professor

A anotação da p.12 é o pedido mais substantivo de todo o PDF:

> *"Os times que terminaram a temporada nas primeiras posições possuem o mesmo comportamento
> considerando o Fator Casa dos times que terminaram nas últimas posições."*

Reforçado na p.13: *"Ver o comportamento das equipes em cada temporada"* e *"Ou grupos, os
melhores e os piores times."*

O notebook não calcula classificação em momento nenhum. O `Big Six` é um proxy fixo e
histórico — não é a mesma coisa que **posição final em cada temporada**, e o próprio notebook
reconhece isso nas limitações ("o Big Six não é homogêneo — o Man United declinou"). É preciso
construir a tabela por temporada (pontos, saldo, gols pró) e então segmentar por faixa de
posição (ex.: 1–6, 7–14, 15–20) — dinamicamente, temporada a temporada.

---

## 3. P1 — Melhorias metodológicas

### 3.1. Unidade de análise no teste da COVID

O teste compara 1.520 partidas pré-COVID contra 380 partidas COVID como observações
independentes. Mas o que varia entre os grupos é a **temporada**, não a partida: na prática são
4 temporadas contra 1. Partidas da mesma temporada compartilham calendário, regras (5
substituições), elenco e arbitragem — não são independentes.

O p = 0,0004 reportado é otimista. Caminhos: modelo com efeito aleatório de temporada, bootstrap
por temporada (reamostrando temporadas, não jogos), ou — melhor de todos — a comparação
intratemporada da seção 2.6, que elimina o confundimento de uma vez.

Isso também obriga a suavizar a conclusão *"isola o papel do público como variável causal
central"*. A temporada 2020/21 mudou várias coisas ao mesmo tempo. O que os dados sustentam é
uma associação forte, não um isolamento causal.

### 3.2. Sem tamanho de efeito e sem intervalo de confiança

Em nenhum ponto do trabalho aparece um IC ou um d/OR. Com n grande, p-valor vira ruído
informativo. Passe a reportar, para cada resultado: estimativa pontual, IC 95% e tamanho de
efeito. É uma mudança barata e muda o nível percebido do trabalho.

### 3.3. Nenhum controle de força do adversário

O "fator casa do Newcastle" mistura duas coisas: a vantagem real do St. James' Park e o
calendário que o Newcastle pegou. Sem ajuste, os dois são indistinguíveis.

Essa é a ponte natural para o TCC2: um modelo com efeitos de ataque/defesa por time mais um
termo de mando (Poisson bivariado à la Dixon–Coles, ou logit ordinal) estima o fator casa
*controlando* por quem jogou contra quem. Resolve o problema metodológico e responde a pergunta
do professor "Utilizará Aprendizado de Máquina?" ao mesmo tempo.

### 3.4. Efeito teto na métrica de pontos

Comparar diferenciais brutos favorece mecanicamente times fracos:

```
Man City   casa=2.407  fora=2.048  -> espaço máximo de ganho em casa = 0.952
Hull       casa=1.474  fora=0.316  -> espaço máximo de ganho em casa = 2.684
```

O Man City simplesmente não tem para onde subir. Use métricas sem teto (saldo de gols por jogo,
razão de chances de vitória casa/fora) ou normalize pelo espaço disponível.

### 3.5. Ranking por time sem N e sem filtro mínimo

A tabela da célula 25 é ordenada por `Diferencial_Casa` e o topo é **Hull (1,158)**. Hull
disputou uma única temporada no recorte (2016/17, 19 jogos em casa — confere com a média de gols
28/19). Middlesbrough, idem. Eles aparecem lado a lado com times de 11 temporadas (209 jogos em
casa) como se os números fossem comparáveis.

Adicione uma coluna `N_Jogos`, aplique um mínimo (ex.: 3 temporadas) e considere *shrinkage*
para a média da liga. A conclusão 3.5 sobre o Newcastle (0,568, esse com base sólida) fica mais
forte quando os artefatos de amostra pequena saem da frente. Nota: a conclusão 3.5 cita 0,55 e a
tabela mostra 0,568 — alinhar.

### 3.6. Taxa de conversão: estimador e viés de seleção (célula 31)

Dois problemas:

- **Média de razões ≠ razão de médias.** `mean(FTHG / HST)` dá peso igual a um jogo com 1 chute
  no alvo e a um com 12. A taxa de conversão correta é `sum(FTHG) / sum(HST)`. Reporte a razão de
  somas (com IC por bootstrap).
- **O filtro `HST > 0 & AST > 0` remove 5,3% das partidas** — e não aleatoriamente: remove
  justamente os jogos de pior desempenho ofensivo, que têm conversão 0. Isso infla ambas as
  médias. A razão de somas não precisa desse filtro (o denominador agregado nunca é zero).

O comentário da célula reconhece o problema da divisão mas escolhe a solução errada.

### 3.7. Matriz de correlação (célula 30)

- `PHT` assume só {0, 1, 3} — é ordinal com escala irregular (a distância vitória→empate não é
  o dobro de empate→derrota). Pearson não é o coeficiente adequado; use Spearman, ou modele
  `FTR` diretamente com logit ordinal.
- A matriz só tem variáveis do mandante. O que explica o resultado é o **diferencial**
  (`HST_casa − HST_fora`), não o valor absoluto: 6 chutes no alvo contra um time que fez 2 é
  muito diferente de 6 contra 9.
- Correlação entre variáveis da mesma partida não permite afirmação causal — a interpretação da
  seção 4.2 precisa de linguagem mais cuidadosa.

### 3.8. Ratings ofensivo/defensivo (célula 27)

`(ofensivo_casa + ofensivo_fora) / 2` trata as duas metades como equivalentes, mas elas têm
bases distintas (média de gols em casa 1,55 vs fora 1,26) e não há ajuste por adversário. Se o
modelo Poisson da seção 3.3 entrar no TCC2, ele substitui esses ratings por parâmetros estimados
— com a vantagem de já vir com erro padrão.

---

## 4. P2 — Código e reprodutibilidade

| Item | Problema | Ação |
|------|----------|------|
| Célula 4 | Lê direto das URLs a cada execução. O football-data.co.uk **reescreve** os CSVs (correções, novas colunas de odds). Rodar em duas datas dá resultados diferentes. | Baixar uma vez para `data/raw/`, versionar, registrar data de acesso e hash SHA-256. |
| Célula 4 | `except Exception` só imprime e continua → uma falha de rede gera dataset parcial silenciosamente. | Falhar alto (`raise`) e validar `len(df) == 380 * n_temporadas` no fim. |
| Célula 5 | Checagem de nulos só em 5 colunas. `HS/HST/HC/HF/HY` podem ter nulos e `.mean()` os ignora em silêncio. | Validar todas as colunas usadas e reportar. |
| Global | Sem `requirements.txt`. | Congelar versões (pandas, scipy, matplotlib, seaborn). |
| Células 4/13/20/30 | Imports espalhados por 5 células. | Concentrar num bloco de setup. |
| Células 19 e 20 | Geram o **mesmo gráfico** duas vezes. | Remover a duplicata. |
| Células 8 e 16 | `PHT`/`PAT` criados duas vezes, com `if` de guarda na 8. Ordem de execução importa. | Criar uma vez, na fase de preparação. |
| Célula 13 | `sns.barplot(palette=...)` sem `hue` e `set_xticklabels` sem `set_ticks` → dois warnings; ambos quebram no seaborn 0.14. | Corrigir a API. |
| Global | Só a célula 20 tem `savefig`. As outras figuras teriam que ser recapturadas na mão para o LaTeX. | Exportar **todas** em PDF vetorial, 300 dpi, nomes estáveis, para `figuras/`. |
| Global | Nomes de colunas com acento (`Média_Pts_Casa`) | Usar ASCII internamente e traduzir só na exportação — evita dor de cabeça no LaTeX. |
| Global | Zero funções, zero testes, estado global. | Ver seção 6. |

---

## 5. Checklist das anotações do professor

| p. | Anotação | Situação | Onde resolver |
|----|----------|----------|---------------|
| 3 | "Pode retirar as citações do resumo" | Pendente | Texto |
| 3 | "CRISP-DM" (grafia) | Pendente | Texto |
| 6, 8, 10, 11 | Correções gramaticais e de pontuação | Pendente | Texto |
| 9, 15 | "Colocar uma outra referência: livro ou artigo" / "Buscar outra referência" — trocar Wikipédia e IBM SPSS Guide | Pendente | Referências |
| 10 | **"Utilizará Aprendizado de Máquina?"** | **Não implementado** | TCC2 — seção 6 |
| 12 | **"Os times que terminaram nas primeiras posições possuem o mesmo comportamento... dos times que terminaram nas últimas posições"** | **Não implementado** | Código — seção 2.7 |
| 13 | **"Ver o comportamento das equipes em cada temporada"** | **Não implementado** | Código |
| 13 | **"Ou grupos, os melhores e os piores times"** | **Não implementado** | Código |
| 13 | **"Média de outros dados: chutes, escanteios"** — evolução temporal, não só pontos/gols | **Não implementado** | Código |
| 13 | "Melhorar a figura (colocar cores)" | Parcial | Figuras |
| 13 | "Formatação" (fonte da figura) | Pendente | Texto |
| 13 | "Resultado interessante!" (queda do fator casa na COVID) | Elogio — vale expandir | — |
| 14 | "Usa quando as variâncias dos dois grupos são diferentes" (Welch) | Justificar escolha do teste | Seção 2.2 |

Os cinco itens em negrito são pedidos de **análise nova**, não de redação. São eles que devem
guiar a próxima rodada de código.

---

## 6. Proposta para o TCC2

### 6.1. Estrutura de repositório

```
data/raw/          CSVs baixados uma vez, versionados, com hash
data/processed/    dataset consolidado + tabela de classificação por temporada
src/
  coleta.py        download com cache e validação de integridade
  preparacao.py    limpeza, PHT/PAT, flag Sem_Publico por data, classificação
  features.py      features pré-jogo (rolling form, Elo, descanso) — sem vazamento
  estatistica.py   testes, IC, tamanhos de efeito
  modelos.py       baselines, Poisson/Dixon-Coles, classificadores
  visualizacao.py  tema único de figuras, exportação em PDF vetorial
notebooks/         narrativa CRISP-DM chamando src/ (não reimplementando)
figuras/           saída pronta para \includegraphics
tabelas/           saída pronta para booktabs
tests/
requirements.txt
```

Notebook vira narrativa; a lógica vive em `src/` e é testável. Toda figura e toda tabela do
LaTeX são geradas por script — nada de print copiado à mão. Quando um número mudar, o PDF muda
junto.

### 6.2. O ponto mais perigoso do TCC2: vazamento de dados

Se você usar `HS`, `HST`, `HC`, `HF` como features para prever `FTR`, o modelo terá acurácia
alta e **o trabalho estará errado** — essas estatísticas só existem *depois* da partida. É o erro
mais comum em TCC de previsão esportiva e uma banca com um membro de ML pega na hora.

Features legítimas usam apenas informação disponível **antes do apito**:

- forma recente (pontos, gols, chutes nas últimas k partidas — com `shift(1)`);
- rating Elo ou parâmetros ataque/defesa estimados **só com dados anteriores**;
- dias de descanso, rodada, posição na tabela até ali;
- flag `Sem_Publico`;
- odds de mercado (o dataset já traz `B365H/D/A`) — como *benchmark*, e num modelo separado.

Validação **temporal**, nunca `train_test_split` aleatório: treino 2015/16–2022/23, validação
2023/24, teste 2024/25–2025/26. Ou walk-forward, retreinando a cada temporada.

### 6.3. Baselines obrigatórios

Um modelo só é bom contra uma referência. Reporte sempre:

1. **Sempre prever vitória em casa** — 44,3% de acurácia de graça;
2. **Classe majoritária por par de times** (histórico);
3. **Odds do Bet365**, convertidas em probabilidade com remoção de margem — este é o baseline
   difícil e o mais honesto. Bater as odds seria notável; ficar perto já é um bom resultado, e
   dizer isso explicitamente demonstra maturidade.

Métricas: **log-loss** e **Brier score** como principais (o problema é probabilístico), acurácia
como secundária, mais uma curva de calibração. Acurácia sozinha esconde modelos mal calibrados.

### 6.4. Sequência sugerida

1. Corrigir os P0 e reprocessar tudo — os números da monografia mudam, então isso vem primeiro.
2. Construir a tabela de classificação por temporada e responder ao pedido da p.12
   (primeiros × últimos), com evolução de chutes e escanteios (p.13).
3. Refazer a análise COVID com flag por data e comparação intratemporada.
4. Modelo Poisson/Dixon–Coles com termo de mando — fecha o gap metodológico *e* entrega o ML.
5. Modelo preditivo com validação temporal e os três baselines.
6. Padronizar figuras e tabelas para exportação automática.
7. Só então escrever o LaTeX.

---

## 7. Nota sobre a temporada 2025/26

A monografia lista como limitação que *"a temporada 2025/26 está em andamento, podendo distorcer
ligeiramente as médias"*. O notebook já carrega 380 partidas para `2526` — a temporada está
completa. Essa limitação pode ser removida do texto do TCC2.
