# Pendências da revisão

Observações do orientador e notas próprias, com o estado de cada uma.

Atualizado em 09/11/2026.

---

## Resolvidas

### Imagem do CRISP-DM

Referência indicada: <https://www.dataviking.com.br/post/crisp-dm-e-util-mesmo>

O orientador observou que a seta azul de recomeço deveria envolver todas as
fases, e não apenas o retorno ao entendimento do negócio, para dar o caráter
incremental de todo o processo. A Figura 1 foi redesenhada com anel externo em
torno das seis fases, no sentido do fluxo. O texto da Seção 2.2 passou a
explicar o anel.

### Números do texto com referência à origem

Os 18 parágrafos do Capítulo 4 que citavam valores sem dizer de onde vinham
agora nomeiam a tabela ou a figura correspondente.

### Trechos de código

Três listagens no Capítulo 3, no float `sourcecode` do próprio modelo:

* Listagem 1, encadeamento das etapas em `executar_analise.py`;
* Listagem 2, teste de ausência de vazamento;
* Listagem 3, conversão de datas.

### Pipeline explicado com código

A Listagem 1 acompanha a Figura 2 na Seção 3.1.1. O diagrama mostra as camadas e
a listagem mostra a chamada de cada etapa.

### Exemplo concreto de caso de teste

Pedido do orientador na Seção 3.1.4. Atendido pela Listagem 2.

### "até a banca"

Trocado por "na apresentação do TCC 1", conforme confirmado.

### Referência cruzada da tabela de testes

O rótulo `tab:testes` estava definido duas vezes, na metodologia e nos
resultados, e a referência da Seção 3.1.4 apontava para a tabela errada. O
rótulo da metodologia passou a ser `tab:testes-automatizados`.

---

## Em aberto

### Fundamentação teórica da área de Computação

O Capítulo 2 não tem seção de fundamentos de Computação. O conteúdo
computacional está todo no Capítulo 3, que descreve o que foi feito, não o que a
literatura diz. Falta base para pipeline de dados, reprodutibilidade em pesquisa
computacional, teste automatizado de software científico e aprendizado
supervisionado.

Pendente de decisão: vale combinar com o orientador antes de escrever.
