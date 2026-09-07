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

<!-- RESULTADOS_PREDITIVOS -->

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
