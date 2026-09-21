# Modelagem — Dixon-Coles e previsão de resultados

Fecha as duas lacunas que restavam do TCC1: a ausência de controle por força do
adversário e a pergunta da banca *"Utilizará Aprendizado de Máquina?"* (p.10).

Gerado por `scripts/executar_modelagem.py`. Tabelas em `tabelas/`, figuras em
`figuras/`.

---

## 1. Por que um modelo, e não mais uma média

Todas as métricas do TCC1 são médias condicionais: pontos em casa, pontos fora, a
diferença entre as duas. Nenhuma controla **contra quem** cada clube jogou.

O "fator casa do Newcastle" (+0,568) mistura duas coisas indistinguíveis sem
modelo: a vantagem real do St. James' Park e o calendário que o Newcastle pegou.
Se por acaso ele recebeu adversários mais fracos do que visitou, parte do
diferencial é sorteio de tabela, não mando de campo.

O modelo de Poisson bivariado resolve isso dando a cada clube um parâmetro de
ataque e um de defesa, e ao mando um parâmetro **compartilhado**:

```
λ_casa = exp(μ + ataque_i − defesa_j + γ)
λ_fora = exp(μ + ataque_j − defesa_i)
```

Como γ é estimado junto com a força de todos os clubes, ele mede a vantagem do
mandante **já descontada** a qualidade de quem jogou contra quem. `exp(γ) − 1` é o
acréscimo percentual de gols atribuível ao mando.

A correção τ de Dixon e Coles ajusta a dependência nos placares baixos (0-0, 1-0,
0-1, 1-1), onde o Poisson independente subestima empates.

---

## 2. Resultado principal

Ajustado sobre as 4.180 partidas do recorte:

| Parâmetro | Estimativa | IC 95% |
|---|---|---|
| **γ (mando)** | **0,1967** | [0,1605; 0,2329] |
| Acréscimo de gols pelo mando | **+21,7%** | — |
| ρ (correção Dixon-Coles) | −0,0388 | — |

Jogar em casa vale cerca de **22% a mais de gols**, controlando por adversário. O
ρ negativo confirma o que a literatura descreve: o Poisson independente
subestima empates de placar baixo.

As forças estimadas ordenam os clubes de forma reconhecível — Man City no topo
(ataque +0,64, defesa +0,55), Huddersfield na lanterna —, o que é uma checagem de
sanidade do ajuste. Tabela completa em `tabelas/dixon_coles_forcas.csv`.

### Validação do estimador

O modelo foi testado contra dados simulados a partir dele mesmo, com γ conhecido.
Em 40 simulações independentes, a média das estimativas foi **0,2362** para um γ
real de **0,25**, e a cobertura do IC 95% foi de **97,5%**. Isso está em
`tests/test_modelos.py` e é o que sustenta a confiança nos números acima.

Durante essa validação apareceu um problema no cálculo original do erro padrão: a
curvatura da verossimilhança na direção de γ, com os demais parâmetros congelados,
subestimava a incerteza em cerca de 25%, produzindo cobertura de 83% num intervalo
nominal de 95%. A causa é a correlação entre γ e μ, que entram os dois na média de
gols do mandante. A versão atual usa **verossimilhança perfilada** — reotimizando
todos os outros parâmetros a cada deslocamento de γ —, o que corrige a cobertura.
É por isso que os intervalos aqui são mais largos que os de uma implementação
ingênua.

---

## 3. O fator casa ao longo do tempo, ajustado

| Temporada | γ | IC 95% |
|---|---|---|
| 15/16 | 0,211 | [0,088; 0,333] |
| 16/17 | 0,286 | [0,165; 0,407] |
| 17/18 | 0,294 | [0,171; 0,418] |
| 18/19 | 0,225 | [0,104; 0,345] |
| 19/20 | 0,231 | [0,109; 0,354] |
| **20/21** | **0,007** | **[−0,115; 0,129]** |
| 21/22 | 0,148 | [0,028; 0,268] |
| 22/23 | 0,291 | [0,171; 0,412] |
| 23/24 | 0,197 | [0,085; 0,308] |
| **24/25** | **0,063** | **[−0,055; 0,180]** |
| 25/26 | 0,215 | [0,093; 0,336] |

Duas temporadas têm intervalo contendo zero: **2020/21**, já conhecida, e
**2024/25** — que não teve nada de pandemia. Esse segundo caso é novo e não
aparecia no diferencial bruto de pontos com a mesma clareza.

A leitura honesta é que γ **oscila bastante entre temporadas** e os intervalos se
sobrepõem quase todos. Falar em "tendência de queda" exige cautela: 22/23 (0,291)
está no mesmo patamar de 16/17 e 17/18. O que os dados mostram é variabilidade
alta em torno de um patamar estável, com dois vales.

---

## 4. Público: o modelo separa o que a média não separava

Agrupando as partidas por regime de público e ajustando o modelo em cada grupo:

| Regime | γ | IC 95% | Acréscimo | Partidas |
|---|---|---|---|---|
| Com público | 0,2137 | [0,1753; 0,2521] | +23,8% | 3.708 |
| Sem público | 0,0511 | [−0,0658; 0,1679] | +5,2% | 419 |

Mas essa comparação tem um problema: **78% das partidas sem público vêm de
2020/21**, temporada que mudou muito além do público. Para separar as duas coisas,
o mando foi modelado como `γ + δ·(sem público)`, com δ estimado **dentro** de um
mesmo recorte:

| Recorte | δ (sem público) | IC 95% | p |
|---|---|---|---|
| **2019/20, intratemporada** | **+0,040** | [−0,151; +0,231] | **0,68** |
| Recorte completo (19/20 + 20/21) | −0,123 | [−0,210; −0,036] | 0,006 |

Dentro de 2019/20 — mesmos elencos, mesmo calendário, mesmas regras — a ausência
de torcida **não desloca o mando de campo**. O efeito agregado, significativo,
vem inteiramente de 2020/21.

Note que o intervalo de 2019/20 ainda contém −0,123. Ou seja: os dados **não
excluem** um efeito do tamanho do agregado; eles mostram que a evidência do efeito
repousa quase toda sobre uma única temporada atípica. Não é possível construir o
contraste dentro de 2020/21, porque nenhuma partida daquela temporada teve público
pleno na classificação adotada.

**Conclusão para a monografia:** a afirmação do TCC1 de que o experimento natural
*"isola o papel do público como variável causal central"* não se sustenta. O que
se pode afirmar é que a vantagem do mandante caiu a zero em 2020/21, e que atribuir
essa queda especificamente à ausência de torcida é uma inferência que os dados de
2019/20 não corroboram.

---

## 5. Modelo preditivo

### 5.1. O erro que o desenho evita

As colunas `HS`, `HST`, `HC`, `HF` e cartões só existem **depois** do apito final.
Usá-las para prever `FTR` produziria acurácia alta e um trabalho errado. Nenhuma
delas entra nas features.

As features usam apenas informação disponível antes do apito inicial: rating Elo,
forma recente (pontos, gols pró e contra nas últimas 5 partidas), forma específica
de mando, dias de descanso, rodada e regime de público.

Isso não é apenas uma declaração de intenção. `tests/test_preditivo.py` contém uma
trava experimental: o teste altera o placar de uma partida no meio da base,
reconstrói todas as features e **exige que nenhuma feature daquela mesma partida se
mova**. Um teste-contraprova verifica que as partidas *seguintes* mudam — senão a
primeira asserção passaria trivialmente com features constantes.

### 5.2. Protocolo

Validação **walk-forward**: para prever a temporada `t`, o treino é tudo o que
aconteceu antes dela; dentro da temporada o histórico cresce a cada 10 partidas e
todos os modelos são reajustados sobre ele.

Todos passam pelo mesmo laço de propósito: se o Dixon-Coles reestimasse parâmetros
ao longo da temporada e os classificadores não, a comparação mediria o protocolo em
vez do modelo.

Temporadas de teste: 2018/19 a 2025/26 (as três primeiras servem de treino inicial).

### 5.3. Métricas

**Log-loss** e **Brier** são as métricas principais, porque o problema é
probabilístico. Acurácia entra como secundária: ela não distingue um modelo bem
calibrado de um confiante e errado, e num problema com 44% de vitórias do mandante
ela é enganosamente fácil de parecer boa.

### 5.4. Resultados

Agregado das 8 temporadas de teste (3.040 partidas), ponderado por partidas:

| Modelo | Log-loss | Brier | Acurácia |
|---|---|---|---|
| **dixon_coles** | **0,9762** | **0,5785** | 0,5359 |
| regressao_logistica | 0,9880 | 0,5834 | **0,5362** |
| frequencia_base | 1,0669 | 0,6457 | 0,4395 |
| sempre_casa | 1,0747 | 0,6500 | 0,4395 |
| gradient_boosting | 1,0807 | 0,6257 | 0,5066 |

Três leituras.

**O modelo estatístico venceu os de aprendizado de máquina.** O Dixon-Coles tem o
melhor log-loss e o melhor Brier, com a regressão logística logo atrás — a
diferença entre os dois é pequena e elas se alternam entre temporadas (o
Dixon-Coles lidera em 6 das 8). Isso não é um acidente: o Dixon-Coles incorpora a
estrutura do problema (gols são contagens, cada clube tem ataque e defesa, o mando
desloca a média) em vez de tentar aprendê-la de 15 features.

**O gradient boosting perdeu para a frequência base.** Log-loss de 1,0807 contra
1,0669 do modelo que apenas repete as frequências históricas. Ao mesmo tempo, sua
acurácia (0,5066) é bem melhor que a do baseline (0,4395). Essa combinação —
acurácia boa, log-loss ruim — é a assinatura de um modelo **mal calibrado**, e é
exatamente o motivo de a acurácia não servir como métrica principal.

**Todos os modelos batem o "sempre o mandante".** A heurística do senso comum
entrega 43,95% de acerto; o Dixon-Coles chega a 53,59%. O ganho é real, mas
modesto: o futebol tem um teto de previsibilidade baixo, e nenhum modelo se
aproxima de "resolver" o problema.

#### Desempenho por temporada (log-loss, menor é melhor)

| Temporada | dixon_coles | reg. logística | grad. boosting | freq. base | sempre casa |
|---|---|---|---|---|---|
| 18/19 | **0,8993** | 0,9056 | 1,0656 | 1,0444 | 1,0562 |
| 19/20 | **0,9763** | 1,0514 | 1,1321 | 1,0650 | 1,0684 |
| 20/21 | **1,0207** | 1,0428 | 1,1718 | 1,0856 | 1,1048 |
| 21/22 | 0,9615 | **0,9603** | 1,0322 | 1,0698 | 1,0795 |
| 22/23 | 1,0042 | **0,9763** | 1,0940 | 1,0509 | 1,0534 |
| 23/24 | **0,9293** | 0,9374 | 1,0052 | 1,0543 | 1,0644 |
| 24/25 | **0,9792** | 0,9971 | 1,0564 | 1,0811 | 1,0898 |
| 25/26 | 1,0391 | **1,0333** | 1,0883 | 1,0836 | 1,0807 |

Note 2020/21: **todos** os modelos pioram naquela temporada. É a mesma anomalia
que aparece no γ — sem a vantagem do mandante, o sinal mais forte do problema
desaparece e a previsão fica mais difícil para todo mundo.

#### Calibração

A tabela abaixo responde à pergunta que a acurácia não alcança: entre as partidas
em que o modelo diz "70% de chance de vitória do mandante", o mandante vence de
fato cerca de 70% das vezes?

| Prob. prevista | Dixon-Coles observado | Grad. boosting observado |
|---|---|---|
| 0,06 | 0,076 | **0,160** |
| 0,15 | 0,185 | **0,228** |
| 0,25 | 0,268 | 0,295 |
| 0,35 | 0,393 | 0,402 |
| 0,45 | 0,429 | 0,431 |
| 0,55 | 0,550 | 0,480 |
| 0,65 | 0,641 | **0,523** |
| 0,75 | 0,711 | **0,581** |
| 0,85 | 0,873 | **0,682** |
| 0,93 | 0,926 | **0,806** |

O Dixon-Coles fica praticamente sobre a diagonal. O gradient boosting é
**sistematicamente exagerado nos dois extremos**: quando diz 94%, acerta 81%;
quando diz 6%, o evento ocorre 16% das vezes. Ele empurra as probabilidades para
as pontas, o que melhora a acurácia (a classe mais provável costuma estar certa)
e destrói o log-loss (as previsões confiantes e erradas custam caro).

**Para a monografia**, este é provavelmente o resultado mais didático do trabalho:
um modelo mais complexo, com mais capacidade, perdendo para um modelo estatístico
simples — e a razão sendo visível na curva de calibração, não na acurácia.

---

## 6. Limitações

- **Sem as odds de mercado.** O baseline mais honesto seria a probabilidade
  implícita nas odds do Bet365, que embutem escalações, lesões e o agregado do
  mercado. O espelho de dados usado neste ambiente não traz essas colunas; o
  código já as consome quando existem (`preditivo.baseline_odds`). Rodar num
  ambiente com acesso ao `football-data.co.uk` completa essa comparação, e ela
  deve entrar na monografia.
- **γ é um só para toda a liga.** O modelo não estima uma vantagem de mando por
  clube. Estimá-la exigiria um parâmetro por clube, com amostra pequena por clube
  e forte encolhimento — extensão natural, mas fora do escopo atual.
- **Sem variáveis de contexto** que a literatura aponta: distância de viagem,
  horário da partida, árbitro designado, ocupação do estádio.
- **A classificação de público é por janela de datas.** As liberações parciais de
  dezembro/2020 e maio/2021 variavam por clube e por semana; essas partidas ficam
  num rótulo próprio e fora dos contrastes, em vez de serem atribuídas a um regime
  por suposição.
