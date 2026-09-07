# Resultados após as correções

Este documento registra o que mudou nos números do TCC1 depois das correções, para
que a escrita da monografia parta dos valores corretos. Todos os números saem de
`scripts/executar_analise.py` e estão em `tabelas/`.

Recorte: 11 temporadas da Premier League (2015/16 a 2025/26), 4.180 partidas —
idêntico ao do TCC1, o que torna a comparação direta.

---

## 1. O que se manteve

**O fator casa existe e é robusto.** A conclusão central do TCC1 sobrevive a todos
os testes corrigidos:

| Teste | Estimativa | IC 95% | p | Tamanho de efeito |
|---|---|---|---|---|
| Binomial (vitórias do mandante entre jogos decididos) | 0,5809 | [0,5635; 0,5981] | 3,2 × 10⁻²⁰ | razão de chances 1,386 |
| Qui-quadrado (simetria casa/fora dada a taxa de empates) | — | — | 6,5 × 10⁻²⁰ | — |
| Teste t pareado (pontos mandante − visitante) | 0,3703 | [0,2917; 0,4490] | 2,1 × 10⁻²⁰ | **d = 0,143** |

O ponto novo é o **tamanho de efeito**: d = 0,143 é um efeito **pequeno**. A
monografia descrevia o fenômeno como "assimetria estatística contundente". O que os
dados sustentam é um efeito consistente, altamente significativo e de magnitude
modesta — 0,37 ponto por jogo. Com n = 4.180, significância estatística é barata;
o que informa é a magnitude.

---

## 2. O que mudou

### 2.1. A conclusão sobre o Big Six caiu

| | TCC1 (célula 39, com bug) | Corrigido |
|---|---|---|
| Diferencial Big Six | +1,397 | **+0,418** |
| Diferencial demais clubes | −0,070 | **+0,366** |
| Diferença entre grupos | — | **+0,051** |
| IC 95% da diferença | — | **[−0,069; +0,172]** |
| p | 0,0000 | **0,351** |
| n | 1.254 partidas | 28 clubes (6 vs 22) |

Seis clubes ficaram fora do teste por terem menos de 3 temporadas no recorte
(Hull, Middlesbrough, Luton, Cardiff, Huddersfield e Ipswich) — são justamente os
que lideravam o ranking do TCC1 por artefato de amostra pequena.

Duas mudanças de fundo:

1. **A diferença não é significativa** (p = 0,35). O Big Six não depende menos do
   mando de campo que os demais clubes.
2. **O sinal é o oposto** do que a monografia afirma: o Big Six tem diferencial
   ligeiramente *maior* (+0,05), não menor.

A conclusão 5.2 — *"Big Six: maior qualidade, menor dependência"* — precisa ser
reescrita. O achado correto é que **não há evidência de diferença** entre os grupos.

### 2.2. Times de cima têm MAIS fator casa, não menos

Segmentando por posição final em cada temporada (o que a banca pediu, p.12):

| Faixa | Jogos | Pts casa | Pts fora | **Dif. pontos** | Dif. gols | Dif. chutes no alvo | Dif. escanteios |
|---|---|---|---|---|---|---|---|
| **G6 (1–6)** | 1.254 | 2,180 | 1,730 | **0,450** | 0,430 | 1,096 | 1,190 |
| **Meio (7–14)** | 1.672 | 1,504 | 1,154 | **0,349** | 0,221 | 0,624 | 0,881 |
| **Z6 (15–20)** | 1.254 | 1,037 | 0,719 | **0,319** | 0,197 | 0,555 | 0,917 |

O gradiente é monotônico e aparece em todas as métricas: pontos, gols, chutes no
alvo e escanteios. Times que terminam no G6 ganham mais com o mando do que times
que terminam no Z6.

E o achado é **mais forte do que parece**, por causa do efeito teto: o G6 já faz
1,73 ponto por jogo fora, então só lhe restam 1,27 ponto de margem até o máximo; o
Z6 faz 0,72 fora e tem 2,28 de margem. Mesmo com muito menos espaço para crescer, o
G6 cresce mais. Usando `ganho_relativo` (fração do espaço disponível convertida em
casa), a vantagem do G6 fica ainda mais nítida.

Isso substitui com folga a segmentação por "Big Six", que era um rótulo fixo — e o
próprio TCC1 reconhecia nas limitações que o grupo não é homogêneo ao longo do
período.

### 2.3. O público não explica a queda de 2020/21

Esta é a mudança mais importante, e só apareceu com a classificação de público **por
data da partida**:

| Cenário | Jogos | Dif. pontos | Dif. gols | Dif. amarelos |
|---|---|---|---|---|
| **2019/20 sem público** | 92 | **+0,457** | +0,370 | +0,033 |
| **2019/20 com público** | 288 | **+0,438** | +0,292 | −0,247 |
| Demais temporadas (com público) | 3.420 | +0,411 | +0,302 | −0,215 |
| 2020/21 público limitado | 53 | +0,226 | +0,132 | −0,377 |
| **2020/21 sem público** | 327 | **−0,119** | −0,009 | +0,034 |

Dentro da **mesma temporada 2019/20** — mesmos elencos, mesmo calendário, mesmas
regras —, tirar a torcida não reduziu a vantagem do mandante: 0,457 sem público
contra 0,438 com público.

Teste formal desse contraste: diferença = −0,019, IC 95% [−0,637; +0,599], p = 0,95.

**Leitura honesta:** com 92 jogos o intervalo é largo demais para descartar efeitos
grandes — o resultado é *inconclusivo*, não é prova de que a torcida não importa. Mas
ele é incompatível com a afirmação da monografia de que o experimento natural
*"isola o papel do público como variável causal central"*. O colapso aconteceu em
2020/21, temporada que mudou várias coisas ao mesmo tempo além do público:
pré-temporada encurtada, calendário congestionado e cinco substituições.

**Achado secundário, e talvez o mais interessante do trabalho:** a coluna de cartões
amarelos separa os dois mecanismos. Com público, o mandante recebe *menos* amarelos
que o visitante (−0,25 em 2019/20; −0,22 nas demais temporadas). Sem público, essa
vantagem desaparece (+0,03 nos dois recortes sem torcida) — e ela desaparece já em
2019/20, quando a vantagem em pontos **não** caiu. Ou seja: a torcida parece influenciar
a arbitragem, mas o viés de arbitragem não é o que sustenta a vantagem em pontos.
Isso é material para uma seção inteira da monografia.

### 2.4. Taxa de conversão: valores menores

| | TCC1 | Corrigido | IC 95% |
|---|---|---|---|
| Mandante | 0,3327 | **0,3258** | [0,3193; 0,3323] |
| Visitante | 0,3212 | **0,3175** | [0,3104; 0,3244] |

Os valores do TCC1 estavam inflados pelo filtro `HST > 0`, que removia justamente as
partidas de conversão zero. A conclusão qualitativa se mantém e agora tem IC: as
faixas quase se tocam, o que reforça a tese de que **o fator casa é volume, não
eficiência**.

### 2.5. Média móvel

Com a janela de 3 temporadas que a monografia declara (o código usava 2):

| Temporada | Diferencial | Média móvel 3 |
|---|---|---|
| 20/21 | −0,071 | 0,263 |
| 21/22 | +0,268 | 0,213 |
| 22/23 | +0,592 | 0,263 |
| 23/24 | +0,411 | 0,424 |
| 24/25 | +0,182 | 0,395 |
| 25/26 | +0,379 | 0,324 |

A tendência suavizada fica em torno de 0,32–0,42 nas últimas temporadas, contra
0,48–0,52 no início do recorte. A leitura de "estabilização em patamar ligeiramente
inferior" se mantém.

### 2.6. Seção 4.5 (mudança de estádio) agora tem dados

Com o recorte estendido a 2009/10:

| Clube | Período | Estádio | Jogos em casa | Dif. pontos |
|---|---|---|---|---|
| **West Ham** | antes | Boleyn Ground (Upton Park) | 114 | **+0,648** |
| | depois | London Stadium | 190 | **+0,347** |
| **Tottenham** | antes | White Hart Lane / Wembley | 185 | **+0,448** |
| | depois | Tottenham Hotspur Stadium | 138 | **+0,414** |

O West Ham perdeu cerca de metade da vantagem de mando após deixar o Upton Park; o
Tottenham praticamente não mudou. É um resultado sugestivo e coerente com a hipótese
da "frieza das arenas modernas" que a seção 4.5 levantava — mas trata-se de dois
clubes, sem controle para as mudanças de elenco e de técnico do mesmo período.
Apresentar como estudo de caso exploratório, não como evidência causal.

O Brentford ficou de fora: subiu para a Premier League em 2021/22 já no Gtech, então
não existe período "antes".

---

## 3. Um problema nos dados que vale registrar na monografia

A verificação automática de quebras de série (`analise.verificar_quebras_de_serie`)
detectou o seguinte:

```
    metrica  temporada  media_anterior   media  variacao_relativa
chutes_alvo       1314           7.118   4.462              0.373
```

A média de chutes no alvo da liga cai **37% de 2012/13 para 2013/14**, enquanto gols
(1,40 → 1,38) e chutes totais (12,57 → 13,44) seguem estáveis. Não é mudança no
futebol: é mudança de critério do provedor, que antes contabilizava finalizações
bloqueadas como chutes no alvo.

**Consequência:** qualquer comparação de HST/AST que cruze 2013/14 é inválida. Sem
essa checagem, o estudo de caso reportaria que o West Ham "perdeu 1,9 chute no alvo
por jogo ao mudar de estádio" — efeito inteiramente artificial. Por isso a coluna
`chutes_alvo_casa` da tabela acima aparece vazia para os dois clubes.

O recorte principal do TCC (2015/16 em diante) está inteiramente depois da quebra e
**não é afetado**. Vale uma nota metodológica na monografia: é o tipo de cuidado que
demonstra domínio da fonte.

---

## 4. Como reproduzir

```bash
pip install -r requirements.txt
python scripts/executar_analise.py
pytest tests/ -q
```

O script escreve `tabelas/*.csv` e `figuras/*.pdf`. Nenhum número da monografia deve
ser copiado à mão de uma saída de célula: quando os dados mudarem, tudo se atualiza
junto.

## 5. O que ainda falta para o TCC2

1. Modelo Poisson/Dixon–Coles com termo de mando, para estimar o fator casa
   controlando por força do adversário — resolve a última lacuna metodológica e
   atende ao "Utilizará Aprendizado de Máquina?" da p.10.
2. Modelo preditivo com validação temporal e os três baselines (sempre-casa,
   histórico, odds do Bet365). Ver `REVISAO_TCC1.md`, seção 6.2, sobre vazamento de
   dados — é o erro mais fácil de cometer aqui.
3. Correções de redação e referências apontadas no PDF da banca.
