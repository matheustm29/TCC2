# Roteiro da defesa

Falas slide a slide. Tempo estimado: **27 minutos e 35 segundos**,
sem contar perguntas.

O mesmo texto está nas notas de apresentador do `.pptx`, visível no modo
apresentador do PowerPoint.

Para encaixar em 20 minutos, pule os slides 9 e 13, marcados abaixo. Isso
tira cerca de dois minutos e meio sem quebrar o fio da argumentação.

---

## Slide 1 — Capa

*40s*

Bom dia. Meu nome é Matheus Ferreira Alphonse dos Anjos, sou aluno de Engenharia de Computação aqui no câmpus Cornélio Procópio, e vou apresentar meu trabalho de conclusão de curso, orientado pelo professor Francisco Pereira Junior.

O tema é o Fator Casa na Premier League. Aquela ideia que todo torcedor conhece, de que jogar em casa dá vantagem. A pergunta que eu quis responder é se isso ainda se sustenta nos números, e por quê. O recorte são onze temporadas e 4.180 partidas.

---

## Slide 2 — Roteiro

*30s*

A apresentação tem cinco blocos.

Começo pelo contexto e pelo problema. Depois mostro como o trabalho foi construído, que é a parte de método e implementação. O miolo são os resultados descritivos e a modelagem, que é onde estão os achados. E fecho com as conclusões, as limitações e o que fica para continuar.

---

## Slide 3 — O Fator Casa e seus mecanismos

*75s*

O Fator Casa é documentado na literatura desde pelo menos 1992, com Courneya e Carron. A definição é simples: equipes mandantes obtêm, de forma consistente, resultados melhores do que as visitantes.

O que não é simples é o porquê. A literatura aponta quatro mecanismos. O apoio da torcida, que motiva o mandante e pressiona o visitante. A familiaridade com o ambiente: o gramado, as dimensões do campo, o clima. O desgaste da viagem para quem joga fora. E o viés de arbitragem, a ideia de que o árbitro é influenciado pela pressão do público.

Guardem esses quatro, porque eles não são intercambiáveis. Cada um deixa uma marca diferente nos dados. Arbitragem aparece em cartões. Familiaridade e logística aparecem em volume de jogo. É justamente isso que vai permitir separá-los mais adiante.

---

## Slide 4 — Problema de pesquisa e objetivos

*75s*

A pergunta central tem duas partes: quanto vale o mando de campo hoje, e quais desses mecanismos realmente o sustentam.

Para responder, defini cinco objetivos. Quantificar a magnitude, mas com intervalo de confiança e tamanho de efeito, não só p-valor. Verificar se o fenômeno é igual para todos os clubes. Olhar a evolução no tempo. Avaliar o papel do público, separando-o das outras coisas que mudaram no mesmo período.

E o quinto, que é o que entrou nesta etapa: estimar o mando com um modelo que controle a força do adversário, e avaliar modelos preditivos.

---

## Slide 5 — Método e dados

*75s*

O trabalho segue o CRISP-DM, com a análise feita em Python.

Os dados vêm do portal Football-Data.co.uk: são 4.180 partidas, onze temporadas, de 2015/16 a 2025/26, com 22 variáveis por partida.

No TCC 1 eu cobri as três primeiras fases do CRISP-DM. Modelagem e Avaliação são a contribuição desta etapa.

E uma observação sobre o número da direita, os 81 testes automatizados. Eu volto nele no próximo slide, porque foi a mudança mais importante entre as duas etapas.

---

## Slide 6 — A solução computacional em camadas

*110s*

O TCC 1 era um notebook único: coleta, tratamento, cálculo e texto no mesmo arquivo. Isso tornou possível um erro que eu só descobri na apresentação, e que eu mostro daqui a pouco. A reformulação partiu desse diagnóstico.

Hoje o processamento é um pacote Python de sete módulos, em camadas, como vocês veem no diagrama. Cada camada consome a anterior e entrega para a seguinte por arquivo em disco, não por estado compartilhado em memória. É isso que permite testar cada etapa isoladamente.

À direita, três decisões que vieram de problemas reais. Primeira: cada arquivo baixado tem procedência e resumo SHA-256 registrados num manifesto. A fonte reescreve os arquivos de tempos em tempos, e sem isso duas execuções em datas diferentes produziriam números diferentes sem nenhum aviso.

Segunda: erro de coleta interrompe a execução. Antes, uma falha de rede gerava um conjunto parcial e a análise seguia normalmente.

A terceira é um achado. Existe uma rotina que detecta quebra de série nos dados, e ela encontrou uma queda de 37% nas finalizações no alvo entre 2012/13 e 2013/14, enquanto gols e finalizações totais ficaram estáveis. Não foi o jogo que mudou, foi o critério de registro do provedor. Sem essa detecção, o estudo de caso sobre mudança de estádio reportaria uma queda que seria artefato de planilha.

E a linha de baixo vale dizer em voz alta: nenhum número desta apresentação foi digitado à mão. Todos saem de tabelas e figuras geradas por código.

---

## Slide 7 — Como o código é verificado

*110s*

Essa é a parte que eu considero a contribuição de Computação mais forte do trabalho.

Testar software científico tem uma dificuldade específica, que a literatura chama de problema do oráculo: o programa foi escrito justamente para calcular algo que ninguém sabe de antemão. Não existe gabarito para comparar.

Eu usei duas estratégias. A primeira é gerar dados sintéticos. Em vez de testar o estimador contra dados reais, eu gero partidas a partir do próprio modelo, com um valor de gama que eu escolhi, e verifico se o ajuste consegue recuperar esse valor.

Foi assim que eu encontrei um defeito no meu próprio código. O intervalo de confiança que eu calculava cobria o valor verdadeiro em 83% das simulações, quando deveria cobrir em 95%. Ou seja, eu estava subestimando a incerteza em cerca de um quarto. Troquei o método de cálculo e a cobertura foi para 97,5%.

A segunda estratégia é o teste de propriedade. Aqui eu não afirmo qual é o valor certo. Eu afirmo uma relação que precisa valer: se eu alterar o placar de uma partida, nenhuma variável explicativa daquela mesma partida pode mudar. É a linha de código que está aí embaixo. É a forma executável de provar que não há vazamento de dados, e eu volto nesse conceito na parte preditiva.

---

## Slide 8 — A vantagem existe

*90s*

Indo para os resultados. A vantagem existe, e com folga de confiança.

Das partidas que terminam com vencedor, 58,09% são vitórias do mandante, com intervalo entre 56,35 e 59,81. Em pontos, são 0,37 ponto a mais por jogo.

Mas aqui vem a primeira correção em relação ao TCC 1. O d de Cohen é 0,143, o que classifica o efeito como pequeno. Com 4.180 partidas, qualquer diferença modesta produz p-valor baixo. Significância não é magnitude.

O TCC 1 descrevia a assimetria como contundente, e isso não se sustenta. O fenômeno é consistente e sistemático, mas de magnitude moderada. A correção aqui é de interpretação, não de cálculo.

---

## Slide 9 — Volume de oportunidades

*70s  ·  *cortável se o tempo for 20 min**

E como essa vantagem se manifesta? Não por eficiência.

As taxas de conversão de finalização no alvo em gol são praticamente iguais: 32,6% para o mandante e 31,8% para o visitante, com intervalos que quase se sobrepõem.

O que muda é o volume. O mandante produz mais finalizações no alvo e mais escanteios em todas as temporadas do recorte, como o gráfico mostra.

Então o Fator Casa é uma questão de criar mais oportunidades, não de aproveitá-las melhor.

---

## Slide 10 — Correção: Big Six

*120s*

Esse é o slide que eu mais queria mostrar, porque é a correção de um erro meu.

No TCC 1 eu comparei o Big Six com os demais clubes e encontrei uma diferença enorme, com p menor que 0,001. O cálculo agregava, para cada partida, os pontos do mandante numa coluna e os do visitante na outra, e separava pelo rótulo do mandante.

O problema é que a segunda coluna é o visitante daquela mesma partida. Quando eu olhava a linha do Big Six, a coluna de fora não era o Big Six jogando fora. Eram os adversários do Big Six. Eu estava comparando dois grupos diferentes.

Com a unidade de análise correta, que é o clube e não a partida, o diferencial do Big Six cai de 1,397 para 0,418, o dos demais sobe de menos 0,070 para 0,366, e a diferença entre os grupos vira 0,051, com p de 0,351. Não há diferença estatisticamente significativa.

E havia dois indícios na própria saída do TCC 1 que eu não vi na época. O Big Six aparecia com 0,701 ponto fora de casa, quando a tabela por clube mostrava o Manchester City com 2,05. E os demais clubes apareciam melhores fora do que em casa, o que não faz sentido nenhum.

A conclusão 5.2 da monografia anterior cai.

---

## Slide 11 — Times de cima dependem mais

*90s*

Refeita a pergunta da forma correta, aparece um achado que contraria a intuição.

Em vez de usar um grupo fixo de clubes, eu segmentei por posição final, recalculada a cada temporada. As seis primeiras colocadas obtêm 0,450 ponto de vantagem em casa. O meio da tabela, 0,349. As seis últimas, 0,319.

Ou seja, os times de cima dependem mais do mando, não menos. E o gradiente é ordenado, aparecendo igual em gols, finalizações no alvo e escanteios, o que reduz a chance de ser artefato de uma métrica específica.

Tem um detalhe que reforça. Existe efeito de teto trabalhando contra o G6: ele já faz 1,73 ponto por jogo fora de casa, então sobra 1,27 de margem até o máximo de três. O Z6 tem 2,28 de margem. Mesmo com menos espaço para crescer, o G6 cresce mais.

---

## Slide 12 — Por que um modelo

*100s*

Até aqui eu usei médias de pontos, e elas têm duas limitações. A primeira é que pontos são limitados a três por partida, o que comprime a vantagem das equipes fortes, como acabamos de ver. A segunda é que a média não vem com medida de incerteza, e não controla quem o time enfrentou.

Por isso eu ajustei o modelo de Dixon e Coles, de 1997. Ele modela os gols de cada lado como variáveis de Poisson, com parâmetros de ataque e defesa para cada clube, e um parâmetro de mando compartilhado, que é o gama.

Como o gama é estimado junto com a força de todos os clubes, ele mede a vantagem já descontada a qualidade do adversário. E como a escala é multiplicativa, o valor é comparável entre clubes de patamares diferentes.

O resultado é um acréscimo de 21,7% nos gols esperados atribuível ao mando. Eu implementei esse modelo do zero, e foi ele que passou pela validação por recuperação de parâmetro que mencionei: 40 simulações com gama conhecido, cobertura de 97,5%.

---

## Slide 13 — Gama por temporada

*80s  ·  *cortável se o tempo for 20 min**

Com o modelo ajustado temporada a temporada, dá para olhar a evolução.

Duas temporadas têm intervalo de confiança contendo o zero, ou seja, sem vantagem detectável. A primeira é 2020/21, que todo mundo espera. A segunda é 2024/25, que não tem relação com a pandemia e que eu não consigo explicar. É um achado novo, e ficou nos trabalhos futuros.

Mas o ponto mais importante do slide é o que não dá para afirmar. Os intervalos da maioria das temporadas se sobrepõem, e 2022/23 está no mesmo patamar de 2016/17. O padrão compatível com os dados é variabilidade alta em torno de um nível estável, com dois vales. Não é uma tendência de queda contínua.

---

## Slide 14 — O público explica a queda?

*110s*

Agora o público. A literatura trata o período de portões fechados como experimento natural, e o TCC 1 seguiu essa linha. Mas há um problema de desenho.

Comparar 2020/21 com as temporadas anteriores confunde o efeito da torcida com tudo o mais que mudou: pré-temporada encurtada, calendário congestionado, número de substituições, desfalques por infecção.

O contraste limpo está dentro de 2019/20, porque ali os mesmos elencos jogaram com e sem público, no mesmo calendário e no mesmo regulamento. São 92 jogos sem público e 288 com público.

E o resultado é esse: sem público, 0,457 ponto de vantagem. Com público, 0,438. A vantagem não caiu. Se mudou alguma coisa, foi ligeiramente para cima. O p-valor é 0,952 no contraste descritivo e 0,680 no modelo ajustado. A inversão do Fator Casa acontece só em 2020/21.

Uma ressalva de alcance, que eu faço questão de dizer: o intervalo de 2019/20 ainda contém o valor estimado no agregado. Os dados não excluem o efeito do público. O que eles mostram é que a evidência de que o público explica a queda repousa sobre uma única temporada atípica.

---

## Slide 15 — Arbitragem e resultado se dissociam

*110s*

E aqui está o achado mais original do trabalho. Ele aparece quando se olha a coluna de cartões amarelos junto com a de pontos.

Em 2019/20 com público, o mandante recebe 0,247 cartão a menos que o visitante. É o viés disciplinar que a literatura descreve. Nas partidas sem público da mesma temporada, esse viés desaparece: o diferencial vai para mais 0,033, praticamente zero. Em 2020/21, também sem público, fica em 0,034.

Ou seja, tirar a torcida realmente muda o comportamento da arbitragem. Isso é consistente com a literatura recente.

Mas olhem a coluna da direita. Na mesma temporada de 2019/20, enquanto o viés de cartões sumiu, a vantagem em pontos ficou igual: 0,438 com público, 0,457 sem.

Os dois efeitos não caminham juntos. A torcida influencia a arbitragem, mas não é por esse caminho que se produz a vantagem em resultados. Isso importa porque os dois mecanismos costumam ser tratados como um só.

---

## Slide 16 — Modelagem preditiva: desenho

*90s*

A última parte é a modelagem preditiva, e ela começa por um cuidado.

As estatísticas de finalização, escanteio e falta só existem depois do apito final. Se eu usar essas colunas para prever o resultado, eu consigo acurácia alta e um trabalho errado. É o erro mais comum nesse tipo de trabalho.

Então as variáveis são todas anteriores ao apito inicial: rating Elo, forma recente, forma específica por mando, dias de descanso, rodada e regime de público. E a ausência de vazamento não é uma declaração minha, é verificada pelo teste que eu mostrei. Tem um contra-teste junto, exigindo que as partidas seguintes mudem, para o primeiro não passar por acidente.

Do lado direito está o protocolo de validação. Cada linha é uma temporada avaliada, e a janela de treino só contém temporadas anteriores. Dentro da temporada de teste, o histórico cresce a cada dez partidas e todos os modelos reajustam juntos. Isso é deliberado: se só um deles reestimasse ao longo da temporada, eu estaria medindo o protocolo, e não o modelo.

---

## Slide 17 — O modelo estatístico superou

*100s*

E o resultado foi esse. O modelo estatístico, o Dixon-Coles, teve o melhor log-loss, 0,9762, à frente da regressão logística e bem à frente do gradient boosting.

O caso do gradient boosting merece atenção. Ele tem acurácia de 50,7%, melhor que a frequência base, e mesmo assim log-loss pior.

A curva de calibração explica. Quando ele prevê 94% de chance, acerta 81% das vezes. Ele empurra as probabilidades para os extremos, o que ajuda na acurácia, porque ali basta acertar a classe mais provável, e é punido com severidade pelo log-loss, que olha a probabilidade atribuída.

Isso é a justificativa empírica para eu ter adotado log-loss como métrica principal. Em problemas probabilísticos, acurácia sozinha engana.

---

## Slide 18 — Conclusões

*90s*

Fechando.

O que se mantém: a vantagem do mandante existe e é robusta, 21,7% a mais de gols já descontada a força do adversário, e ela se manifesta por volume de oportunidades, não por eficiência.

O que mudou em relação ao TCC 1: o Big Six não depende menos do mando, a diferença não é significativa; times de cima dependem mais, num gradiente ordenado por posição final; e o público não explica a queda de 2020/21 quando o contraste é feito dentro da mesma temporada.

E o achado novo, que está em destaque: o viés de arbitragem e a vantagem em resultados se dissociam. O primeiro desaparece sem público já em 2019/20, enquanto o segundo permanece. A torcida influencia a arbitragem, mas esse não é o mecanismo central do Fator Casa.

---

## Slide 19 — Limitações e trabalhos futuros

*70s*

As limitações principais.

O modelo estima um gama comum para a liga inteira, então eu não consigo dizer se um clube específico depende mais do mando que outro. Faltam variáveis de contexto que a literatura aponta como relevantes: distância de viagem, horário da partida, ocupação do estádio. Não foi possível fazer o contraste intratemporada em 2020/21, porque nenhuma partida daquela temporada teve público pleno.

E não houve comparação com as probabilidades do mercado de apostas, que seria a referência externa mais exigente. As rotinas estão implementadas e testadas, mas as colunas de cotação não estavam disponíveis no acervo coletado. É a continuidade mais imediata, junto com estimar o mando por clube com modelos hierárquicos e investigar a temporada 2024/25.

---

## Slide 20 — Encerramento

*20s*

É isso. Obrigado pela atenção, e fico à disposição para as perguntas.

---
