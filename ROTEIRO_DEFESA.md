# Roteiro da defesa

**20 slides · 17 min 52 s estimados.**

Todos os slides entram na sequência, gráficos incluídos. Os dois slides de
gráfico têm fala curta de propósito: a figura faz o trabalho, você só aponta
o que ela mostra.

O mesmo texto está nas notas do `.pptx`, visível no modo apresentador.

---

## 1. Capa

*30s*

Bom dia. Eu sou o Matheus, de Engenharia de Computação, e vou apresentar meu trabalho de conclusão, orientado pelo professor Francisco.

O tema é o Fator Casa: a ideia de que jogar em casa dá vantagem. Eu quis saber se isso ainda aparece nos números, e por quê. Onze temporadas da Premier League, 4.180 jogos.

---

## 2. Roteiro

*9s*

São cinco blocos: o problema, como eu construí o trabalho, os resultados, a modelagem e as conclusões.

---

## 3. O Fator Casa e seus mecanismos

*46s*

Que o mandante leva vantagem, todo mundo sabe, e a literatura mede isso desde os anos 90. A pergunta interessante é por quê.

Costuma-se apontar quatro causas: a torcida, a familiaridade com o campo, o cansaço da viagem de quem joga fora, e o árbitro, que seria influenciado pela pressão da arquibancada.

Guardem essas quatro, porque elas deixam marcas diferentes nos dados. Árbitro aparece em cartão. Familiaridade e viagem aparecem no volume de jogo. É isso que vai permitir separar uma da outra mais para frente.

---

## 4. Problema de pesquisa e objetivos

*39s*

A pergunta tem duas partes: quanto vale jogar em casa hoje, e qual dessas causas sustenta a vantagem.

Daí saíram cinco objetivos. Medir o tamanho da vantagem. Ver se ela é igual para todos os clubes. Olhar se mudou ao longo do tempo. Avaliar o peso da torcida, separando-a das outras coisas que mudaram na pandemia. E o último, que entrou nesta etapa: usar um modelo que desconte a força do adversário.

---

## 5. Método e dados

*30s*

Segui o CRISP-DM, que é um roteiro padrão de projetos de dados, e fiz tudo em Python. São 4.180 partidas, onze temporadas, 22 informações por jogo.

No TCC 1 eu tinha coberto as três primeiras etapas. Modelagem e avaliação entraram agora.

E guardem o número da direita, 81 testes, porque é o assunto do próximo slide.

---

## 6. A solução computacional em camadas

*97s*

O TCC 1 era um arquivo só, onde coleta, cálculo e texto se misturavam. Foi isso que permitiu um erro que eu só descobri na apresentação, e que eu mostro daqui a pouco.

Hoje é um programa dividido em camadas, como no diagrama. Cada camada entrega para a seguinte por arquivo em disco, e é isso que permite testar cada pedaço separadamente.

À direita, três decisões que vieram de problemas reais. Cada arquivo baixado tem uma assinatura digital guardada, porque o site muda os arquivos de tempos em tempos, e sem isso duas execuções em dias diferentes dariam números diferentes, sem avisar. Se a coleta falha, o programa para. Antes ele seguia com dados pela metade. E a terceira é um achado. Eu tenho uma rotina que procura mudanças estranhas nos dados, e ela encontrou uma: as finalizações no alvo caem 37% de uma temporada para a outra, em 2013, enquanto os gols ficam iguais. Não foi o futebol que mudou, foi o critério de quem anota.

E a frase de baixo: nenhum número desta apresentação foi digitado à mão.

---

## 7. Como o código é verificado

*99s*

Essa é a parte que eu considero a maior contribuição de Computação do trabalho.

Testar um programa científico tem uma dificuldade própria: ele foi escrito justamente para calcular algo que ninguém sabe de antemão. Não existe gabarito para conferir.

Então eu usei dois caminhos. O primeiro é inventar dados. Em vez de testar com jogos reais, eu gero jogos falsos a partir do próprio modelo, com um valor de vantagem que eu mesmo escolhi, e verifico se o programa encontra aquele valor de volta. Foi assim que eu descobri um erro meu. A minha margem de erro acertava o valor verdadeiro em 83% das vezes, quando deveria acertar em 95%. Eu estava dizendo ter mais certeza do que de fato tinha. Troquei a forma de calcular e foi para 97,5%.

O segundo caminho é testar uma regra, em vez de um número. Eu digo o seguinte: se eu mudar o placar de um jogo, nenhuma informação usada para prever aquele mesmo jogo pode mudar. É a linha de código aí embaixo. É assim que eu provo que o modelo não está espiando o resultado.

---

## 8. A vantagem existe — e é menor do que se supõe

*43s*

Indo para os resultados. A vantagem existe, com folga. Dos jogos que têm vencedor, 58% terminam com vitória do mandante. Em pontos, são 0,37 ponto a mais por jogo.

Mas aqui vem a primeira correção em relação ao TCC 1. O tamanho desse efeito é pequeno. Com 4.180 jogos, qualquer diferencinha fica estatisticamente significativa, e significativo não quer dizer grande. O TCC 1 dizia que a assimetria era contundente, e isso não se sustenta. O fenômeno é constante, mas modesto.

---

## 9. Volume de oportunidades, não eficiência

*36s*

E de onde vem essa vantagem? Não de eficiência. O mandante transforma chute em gol praticamente na mesma taxa do visitante, 32,6 contra 31,8 por cento.

O que muda é o volume. São dois painéis: chutes no alvo à esquerda, escanteios à direita. A linha do mandante fica por cima da do visitante nas onze temporadas, sem nenhuma exceção. A vantagem é de volume, não de pontaria.

---

## 10. Correção: a comparação entre Big Six e demais clubes

*91s*

Esse slide é o que eu mais queria mostrar, porque é a correção de um erro meu.

No TCC 1 eu comparei os seis grandes com o resto da liga e achei uma diferença enorme. O cálculo somava, para cada jogo, os pontos do mandante de um lado e os do visitante do outro, e separava pelo nome do mandante.

O problema é que o visitante daquele jogo não é o mesmo time. Quando eu olhava a linha dos seis grandes, a coluna de fora de casa não era os seis grandes jogando fora. Eram os adversários deles. Eu estava comparando dois grupos diferentes e chamando de um só.

Refazendo a conta por clube, e não por jogo, a diferença entre os grupos desaparece. O p-valor sai de menos de 0,001 para 0,35.

E tinha um sinal na minha própria saída que eu não enxerguei: os times menores apareciam melhores fora do que em casa, o que não existe. Uma das conclusões do TCC 1 cai por aqui.

---

## 11. Times de cima dependem mais do mando, não menos

*58s*

Refeita a pergunta do jeito certo, aparece um resultado que contraria a intuição.

Em vez de usar um grupo fixo de clubes, eu separei por posição final, recalculada a cada temporada. Os seis primeiros ganham 0,450 ponto por jogar em casa. O meio da tabela, 0,349. Os seis últimos, 0,319.

Os times de cima dependem mais do mando, não menos. E a ordem se repete em gols, em chutes no alvo e em escanteios, o que torna difícil ser coincidência.

Tem um detalhe que reforça. Os times de cima já fazem 1,73 ponto por jogo fora de casa, então sobra pouco espaço para crescer. Mesmo assim, crescem mais.

---

## 12. Por que um modelo, e não mais uma média

*64s*

Até aqui eu usei média de pontos, e ela tem dois limites. Pontos param em três por jogo, então o teto atrapalha justamente os times fortes. E a média não diz nada sobre quem o time enfrentou.

Por isso eu usei o modelo de Dixon e Coles, de 1997. Ele estima o ataque e a defesa de cada clube e, junto com isso, um número que representa o mando de campo. Como esse número sai calculado junto com a força de todo mundo, ele já vem descontado da qualidade do adversário.

O resultado: jogar em casa vale 21,7% a mais de gols esperados. Eu programei esse modelo do zero, e foi nele que apliquei o teste de dados inventados.

---

## 13. O fator casa ajustado, temporada a temporada

*49s*

Rodando o modelo temporada a temporada, dá para olhar a evolução. Cada ponto é uma temporada, e a barra é a margem de erro.

Duas temporadas encostam no zero, ou seja, sem vantagem nenhuma: 2020/21, que todo mundo espera, e 2024/25, que eu não consigo explicar e deixei como trabalho futuro.

Mas o mais importante aqui é o que não dá para afirmar. Repare que quase todas as barras se cruzam, e que 2022/23 está na mesma altura de 2016/17. Não existe queda contínua. É oscilação em torno do mesmo patamar.

---

## 14. O público explica a queda de 2020/21?

*77s*

Agora a torcida. A literatura trata os jogos de portão fechado como um experimento natural, e o TCC 1 seguiu essa linha. Só que tem um problema.

Comparar 2020/21 com os anos anteriores mistura o efeito da torcida com tudo o mais que mudou: pré-temporada curta, calendário apertado, mais substituições, jogadores afastados por contágio.

A comparação limpa está dentro de 2019/20. Ali os mesmos elencos jogaram com e sem público, no mesmo campeonato: 92 jogos sem torcida e 288 com torcida.

E o resultado é esse. Sem público, 0,457 de vantagem. Com público, 0,438. Não caiu. Se mudou, foi um pouquinho para cima. A inversão acontece só em 2020/21.

Uma ressalva que eu faço questão de dizer: isso não prova que a torcida não importa. O que mostra é que a prova de que ela importa está apoiada numa única temporada muito atípica.

---

## 15. Achado: arbitragem e resultado se dissociam

*70s*

E aqui está o achado mais original do trabalho. Ele aparece quando se olha cartão amarelo junto com ponto.

Em 2019/20, com torcida, o mandante leva 0,247 cartão a menos que o visitante. É o favorecimento do árbitro que a literatura descreve. Nos jogos sem torcida da mesma temporada, isso some: vai para praticamente zero. Em 2020/21, também sem torcida, a mesma coisa.

Ou seja, tirar a torcida realmente muda o comportamento do árbitro.

Mas olhem a coluna da direita. Na mesma temporada, enquanto o favorecimento no cartão sumiu, a vantagem em pontos ficou igual.

Os dois não andam juntos. A torcida mexe com o árbitro, mas não é por aí que nasce a vantagem no placar. Isso importa porque as duas coisas costumam ser tratadas como uma só.

---

## 16. Modelagem preditiva: o risco antes do resultado

*61s*

A última parte é prever resultados, e ela começa com um cuidado.

Chute, escanteio e falta só existem depois que o jogo acaba. Se eu usar isso para prever o jogo, eu acerto muito e o trabalho está errado. É o erro mais comum nesse tipo de estudo.

Então eu só uso informação que existe antes do apito: a força de cada time, o desempenho nos últimos cinco jogos, dias de descanso, rodada e se tinha público.

Do lado direito está o desenho da validação. Para prever uma temporada, o modelo só enxerga temporadas anteriores. Dentro da temporada, ele vai aprendendo a cada dez jogos, e todos os modelos aprendem no mesmo ritmo.

---

## 17. O modelo estatístico superou os de aprendizado de máquina

*58s*

E o resultado foi esse. O modelo estatístico ganhou dos modelos de aprendizado de máquina.

O caso mais interessante é o último da tabela. Ele acerta mais jogos que o palpite mais simples e, ainda assim, fica em último lugar na métrica principal.

O gráfico explica. Quando ele diz que o mandante tem 94% de chance, o mandante ganha 81% das vezes. Ele exagera na confiança. Para acertar quem ganha, isso até ajuda, porque basta apontar o favorito. Mas se você leva a sério a probabilidade que ele deu, ele erra feio.

Por isso eu não avaliei por acerto, e sim por uma métrica que olha a probabilidade.

---

## 18. Conclusões

*60s*

Fechando.

O que se mantém: jogar em casa dá vantagem, 21,7% a mais de gols já descontado o adversário, e ela vem de criar mais oportunidades, não de aproveitá-las melhor.

O que mudou em relação ao TCC 1: os seis grandes não dependem menos do mando, na verdade são os times de cima que dependem mais, e a torcida não explica a queda de 2020/21 quando a comparação é feita direito.

E o achado novo, em destaque: o favorecimento do árbitro e a vantagem no placar se separam. O primeiro some sem torcida, o segundo continua. A torcida mexe com a arbitragem, mas não é esse o motor do Fator Casa.

---

## 19. Limitações e trabalhos futuros

*52s*

As limitações. O modelo usa um único valor de mando para a liga inteira, então eu não sei dizer se um clube específico depende mais do que outro. Faltam dados de contexto: distância de viagem, horário do jogo, quanto o estádio encheu. E não deu para fazer a comparação limpa dentro de 2020/21, porque nenhum jogo daquele ano teve público.

Ficou de fora a comparação com as cotações das casas de apostas, que seria a referência mais dura. O código está pronto, mas os dados de cotação não vieram na base. É a continuação mais imediata.

---

## 20. Obrigado

*4s*

É isso. Obrigado, e fico à disposição.

---

## Controle de tempo

| Slide | Tema | Acumulado |
| --- | --- | --- |
| 1 | Capa | 0:29 |
| 2 | Roteiro | 0:38 |
| 3 | O Fator Casa e seus mecanismos | 1:25 |
| 4 | Problema de pesquisa e objetivos | 2:03 |
| 5 | Método e dados | 2:34 |
| 6 | A solução computacional em camadas | 4:11 |
| 7 | Como o código é verificado | 5:50 |
| 8 | A vantagem existe — e é menor do que se supõe | 6:33 |
| 9 | Volume de oportunidades, não eficiência | 7:09 |
| 10 | Correção: a comparação entre Big Six e demais clubes | 8:39 |
| 11 | Times de cima dependem mais do mando, não menos | 9:38 |
| 12 | Por que um modelo, e não mais uma média | 10:42 |
| 13 | O fator casa ajustado, temporada a temporada | 11:31 |
| 14 | O público explica a queda de 2020/21? | 12:48 |
| 15 | Achado: arbitragem e resultado se dissociam | 13:57 |
| 16 | Modelagem preditiva: o risco antes do resultado | 14:58 |
| 17 | O modelo estatístico superou os de aprendizado de máquina | 15:56 |
| 18 | Conclusões | 16:56 |
| 19 | Limitações e trabalhos futuros | 17:48 |
| 20 | Obrigado | 17:52 |

Os marcos para olhar no relógio: **slide 8 em 6:30** (começo dos resultados),
**slide 14 em 11:30** (torcida) e **slide 17 em 15:00**. Se estiver atrasado,
os lugares para encurtar sem perder conteúdo são o slide 6 e o slide 10, que
são os dois mais longos.
