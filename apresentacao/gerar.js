const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const DIR = __dirname;
const FUNDO = path.join(DIR, "fundo.jpg");
// As figuras são as mesmas geradas pelos scripts de análise, em `figuras/`
// na raiz do repositório; `fig/` local serve apenas a cópias de trabalho.
const DIR_FIG = fs.existsSync(path.join(DIR, "fig"))
  ? path.join(DIR, "fig")
  : path.join(DIR, "..", "figuras");
const fig = (n) => path.join(DIR_FIG, n);

// Paleta institucional, amostrada do próprio fundo fornecido.
const NAVY = "17252E";
const AMARELO = "FECF07";
const TINTA = "2B3A45";
const CINZA = "5A6670";
const SUAVE = "8A949C";
const AZUL = "2A78D6";
const LARANJA = "EB6834";
const CARTAO = "F1F4F7";

// Área segura: o bloco navy ocupa o canto superior direito e a marca
// institucional o rodapé. Conteúdo entre y 0,80" e 6,40"; x até 11,6".
const X = 0.8, W = 10.8;
const Y_TIT = 0.72, Y_TOP = 1.75, Y_BOT = 6.35;

const THEME = {
  name: "UTFPR TCC",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: NAVY, lt1: "FFFFFF", dk2: TINTA, lt2: CARTAO,
    accent1: NAVY, accent2: AMARELO, accent3: AZUL,
    accent4: LARANJA, accent5: CINZA, accent6: SUAVE,
    hlink: AZUL, folHlink: CINZA,
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Matheus Ferreira Alphonse dos Anjos";
pres.title = "Analise estatistica e quantitativa do Fator Casa na Premier League";

const C = pres.SchemeColor;

// SEM_NOTAS=1 gera uma cópia sem as notas de apresentador, para compartilhar.
// As notas trazem a fala da defesa, escrita em primeira pessoa, que não faz
// sentido num arquivo enviado a terceiros.
const SEM_NOTAS = process.env.SEM_NOTAS === "1";
function notas(slide, texto) { if (!SEM_NOTAS) slide.addNotes(texto); }

pres.defineSlideMaster({
  title: "CAPA",
  background: { path: FUNDO },
  objects: [],
});

pres.defineSlideMaster({
  title: "CONTEUDO",
  background: { path: FUNDO },
  objects: [
    { placeholder: { options: {
      name: "title", type: "title", x: X, y: Y_TIT, w: W, h: 0.78,
      fontSize: 30, bold: true, color: NAVY, align: "left", valign: "middle", margin: 0 }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "SECAO",
  background: { path: FUNDO },
  objects: [],
});

// ───────────────────────────── helpers ─────────────────────────────

/** Número grande com rótulo embaixo. */
function stat(s, { x, y, w, numero, rotulo, cor = NAVY, tamanho = 46 }) {
  s.addText(numero, {
    isTextBox: true, x, y, w, h: 0.78, margin: 0,
    fontSize: tamanho, bold: true, color: cor, align: "left", valign: "bottom",
    objectName: `stat-num-${rotulo.slice(0, 18)}`,
  });
  s.addText(rotulo, {
    isTextBox: true, x, y: y + 0.80, w, h: 0.62, margin: 0,
    fontSize: 13, color: CINZA, align: "left", valign: "top",
    objectName: `stat-rot-${rotulo.slice(0, 18)}`,
  });
}

/** Cartão com tinta suave, título e corpo. */
function cartao(s, { x, y, w, h, titulo, corpo, numero }) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.08, fill: { color: CARTAO }, line: { color: CARTAO },
    objectName: `cartao-${titulo.slice(0, 18)}`,
  });
  let yt = y + 0.26;
  if (numero !== undefined) {
    s.addShape(pres.ShapeType.ellipse, {
      x: x + 0.26, y: y + 0.24, w: 0.44, h: 0.44,
      fill: { color: NAVY }, line: { color: NAVY },
      objectName: `bolha-${titulo.slice(0, 14)}`,
    });
    s.addText(String(numero), {
      isTextBox: true, x: x + 0.26, y: y + 0.24, w: 0.44, h: 0.44, margin: 0,
      fontSize: 15, bold: true, color: "FFFFFF", align: "center", valign: "middle",
      objectName: `bolha-num-${titulo.slice(0, 14)}`,
    });
  }
  const xt = numero !== undefined ? x + 0.86 : x + 0.3;
  const wt = w - (numero !== undefined ? 1.16 : 0.6);
  s.addText(titulo, {
    isTextBox: true, x: xt, y: yt, w: wt, h: 0.38, margin: 0,
    fontSize: 16, bold: true, color: NAVY, valign: "middle",
    objectName: `cartao-tit-${titulo.slice(0, 14)}`,
  });
  s.addText(corpo, {
    isTextBox: true, x: x + 0.3, y: yt + 0.46, w: w - 0.6, h: h - (yt - y) - 0.62,
    margin: 0, fontSize: 13.5, color: CINZA, valign: "top", lineSpacingMultiple: 1.12,
    objectName: `cartao-corpo-${titulo.slice(0, 14)}`,
  });
}

/** Lista com marcadores. */
function lista(s, itens, { x, y, w, h, tamanho = 16, espaco = 9 }) {
  s.addText(
    itens.map((t, i) => ({
      text: t, options: { bullet: { indent: 18 }, breakLine: i < itens.length - 1 },
    })),
    { isTextBox: true, x, y, w, h, margin: 0, fontSize: tamanho, color: TINTA,
      valign: "top", paraSpaceAfter: espaco, lineSpacingMultiple: 1.1, objectName: "lista" }
  );
}

function titulo(s, texto) {
  s.addText(texto, { placeholder: "title" });
}

function legenda(s, texto, y = Y_BOT - 0.02) {
  s.addText(texto, {
    isTextBox: true, x: X, y, w: W, h: 0.3, margin: 0,
    fontSize: 11, italic: true, color: SUAVE, objectName: "legenda",
  });
}

// ═══════════════════════ 1. Capa ═══════════════════════
pres.addSection({ title: "Abertura" });
let s = pres.addSlide({ masterName: "CAPA", sectionTitle: "Abertura" });
s.addText("ANÁLISE ESTATÍSTICA E QUANTITATIVA DO FATOR CASA NA PREMIER LEAGUE NA ERA MODERNA", {
  isTextBox: true, x: X, y: 1.65, w: 9.3, h: 1.9, margin: 0,
  fontSize: 34, bold: true, color: NAVY, lineSpacingMultiple: 1.04, objectName: "capa-titulo",
});
s.addShape(pres.ShapeType.rect, { x: X, y: 3.72, w: 1.5, h: 0.055,
  fill: { color: AMARELO }, line: { color: AMARELO }, objectName: "capa-marca" });
s.addText("Trabalho de Conclusão de Curso 2", {
  isTextBox: true, x: X, y: 3.98, w: 9.3, h: 0.34, margin: 0,
  fontSize: 15, color: CINZA, objectName: "capa-tipo" });
s.addText([
  { text: "Matheus Ferreira Alphonse dos Anjos", options: { bold: true, breakLine: true } },
  { text: "Orientador: Prof. Francisco Pereira Junior", options: { breakLine: true } },
  { text: "Bacharelado em Engenharia de Computação", options: {} },
], { isTextBox: true, x: X, y: 4.46, w: 9.3, h: 1.3, margin: 0,
     fontSize: 16, color: TINTA, lineSpacingMultiple: 1.2, objectName: "capa-autoria" });
s.addText("Campus Cornélio Procópio · 2026", {
  isTextBox: true, x: X, y: 5.74, w: 9.3, h: 0.34, margin: 0,
  fontSize: 13, color: SUAVE, objectName: "capa-local" });
notas(s, "Bom dia. Eu sou o Matheus, de Engenharia de Computação, e vou apresentar meu trabalho de conclusão, orientado pelo professor Francisco.\n\nO tema é o Fator Casa: a ideia de que jogar em casa dá vantagem. Eu quis saber se isso ainda aparece nos números, e por quê. Onze temporadas da Premier League, 4.180 jogos.");

// ═══════════════════════ 2. Roteiro ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Abertura" });
titulo(s, "Roteiro");
const roteiro = [
  ["Contexto e problema", "O fenômeno e por que revisitá-lo"],
  ["Método e implementação", "CRISP-DM, pipeline em camadas e verificação"],
  ["Resultados descritivos", "Magnitude, heterogeneidade e público"],
  ["Modelagem", "Poisson bivariado e modelos preditivos"],
  ["Conclusões", "Achados, limitações e continuidade"],
];
roteiro.forEach(([t, d], i) => {
  const y = Y_TOP + i * 0.88;
  s.addShape(pres.ShapeType.ellipse, { x: X, y, w: 0.5, h: 0.5,
    fill: { color: i === 0 ? NAVY : CARTAO }, line: { color: i === 0 ? NAVY : CARTAO },
    objectName: `rot-bolha-${i}` });
  s.addText(String(i + 1), { isTextBox: true, x: X, y, w: 0.5, h: 0.5, margin: 0,
    fontSize: 16, bold: true, color: i === 0 ? "FFFFFF" : NAVY, align: "center", valign: "middle",
    objectName: `rot-num-${i}` });
  s.addText(t, { isTextBox: true, x: X + 0.78, y: y - 0.02, w: 4.0, h: 0.34, margin: 0,
    fontSize: 17, bold: true, color: NAVY, valign: "middle", objectName: `rot-t-${i}` });
  s.addText(d, { isTextBox: true, x: X + 0.78, y: y + 0.26, w: 7.6, h: 0.3, margin: 0,
    fontSize: 13.5, color: CINZA, valign: "middle", objectName: `rot-d-${i}` });
});
notas(s, "São cinco blocos: o problema, como eu construí o trabalho, os resultados, a modelagem e as conclusões.");

// ═══════════════════════ 3. O fenômeno ═══════════════════════
pres.addSection({ title: "Contexto" });
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Contexto" });
titulo(s, "O Fator Casa e seus mecanismos");
s.addText("Vantagem estatística consistente das equipes mandantes, documentada desde Courneya e Carron (1992). A literatura atribui o fenômeno a quatro mecanismos distintos:", {
  isTextBox: true, x: X, y: 1.62, w: W, h: 0.56, margin: 0,
  fontSize: 15, color: CINZA, lineSpacingMultiple: 1.1, objectName: "intro-mec" });
const mec = [
  ["Apoio da torcida", "Motivação dos mandantes e pressão sobre os visitantes."],
  ["Familiaridade", "Conhecimento do gramado, das dimensões e do clima local."],
  ["Logística de viagem", "Desgaste físico e mental imposto ao visitante."],
  ["Viés de arbitragem", "Pressão sobre as decisões em lances cruciais."],
];
mec.forEach(([t, d], i) => {
  cartao(s, { x: X + (i % 2) * 5.5, y: 2.4 + Math.floor(i / 2) * 1.85,
              w: 5.25, h: 1.62, titulo: t, corpo: d, numero: i + 1 });
});
notas(s, "Que o mandante leva vantagem, todo mundo sabe, e a literatura mede isso desde os anos 90. A pergunta interessante é por quê.\n\nCostuma-se apontar quatro causas: a torcida, a familiaridade com o campo, o cansaço da viagem de quem joga fora, e o árbitro, que seria influenciado pela pressão da arquibancada.\n\nGuardem essas quatro, porque elas deixam marcas diferentes nos dados. Árbitro aparece em cartão. Familiaridade e viagem aparecem no volume de jogo. É isso que vai permitir separar uma da outra mais para frente.");

// ═══════════════════════ 4. Problema e objetivos ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Contexto" });
titulo(s, "Problema de pesquisa e objetivos");
s.addShape(pres.ShapeType.roundRect, { x: X, y: 1.62, w: W, h: 1.16, rectRadius: 0.08,
  fill: { color: NAVY }, line: { color: NAVY }, objectName: "pergunta-fundo" });
s.addText("Até que ponto o mando de campo ainda é estatisticamente determinante na era moderna, e quais mecanismos sustentam essa vantagem?", {
  isTextBox: true, x: X + 0.4, y: 1.72, w: W - 0.8, h: 0.96, margin: 0,
  fontSize: 18, bold: true, color: "FFFFFF", valign: "middle", lineSpacingMultiple: 1.08,
  objectName: "pergunta" });
s.addText("Objetivos específicos", { isTextBox: true, x: X, y: 3.16, w: W, h: 0.34,
  margin: 0, fontSize: 16, bold: true, color: NAVY, objectName: "obj-tit" });
lista(s, [
  "Quantificar a magnitude da vantagem, com intervalos de confiança e tamanho de efeito",
  "Verificar se equipes de diferentes faixas da tabela se comportam da mesma forma",
  "Identificar tendência temporal do fenômeno",
  "Avaliar o papel do público, distinguindo-o de outras mudanças do período",
  "Estimar o mando por modelo que controle a força do adversário e avaliar modelos preditivos",
], { x: X, y: 3.66, w: W, h: 2.5, tamanho: 16 });
notas(s, "A pergunta tem duas partes: quanto vale jogar em casa hoje, e qual dessas causas sustenta a vantagem.\n\nDaí saíram cinco objetivos. Medir o tamanho da vantagem. Ver se ela é igual para todos os clubes. Olhar se mudou ao longo do tempo. Avaliar o peso da torcida, separando-a das outras coisas que mudaram na pandemia. E o último, que entrou nesta etapa: usar um modelo que desconte a força do adversário.");

// ═══════════════════════ 5. Método e dados ═══════════════════════
pres.addSection({ title: "Método" });
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Método" });
titulo(s, "Método e dados");
s.addText("Metodologia CRISP-DM, com análise em Python. Dados do portal Football-Data.co.uk, cobrindo o recorte completo de 11 temporadas.", {
  isTextBox: true, x: X, y: 1.62, w: W, h: 0.5, margin: 0,
  fontSize: 15, color: CINZA, objectName: "met-intro" });
stat(s, { x: X, y: 2.42, w: 2.6, numero: "4.180", rotulo: "partidas analisadas" });
stat(s, { x: X + 2.85, y: 2.42, w: 2.6, numero: "11", rotulo: "temporadas\n2015/16 a 2025/26" });
stat(s, { x: X + 5.7, y: 2.42, w: 2.6, numero: "22", rotulo: "variáveis por partida" });
stat(s, { x: X + 8.4, y: 2.42, w: 2.4, numero: "81", rotulo: "testes automatizados" });
s.addText("Fases executadas", { isTextBox: true, x: X, y: 4.3, w: W, h: 0.34, margin: 0,
  fontSize: 16, bold: true, color: NAVY, objectName: "fases-tit" });
const fases = ["Entendimento\ndo negócio", "Entendimento\ndos dados", "Preparação\ndos dados", "Modelagem", "Avaliação"];
fases.forEach((f, i) => {
  const x = X + i * 2.18;
  s.addShape(pres.ShapeType.roundRect, { x, y: 4.78, w: 2.0, h: 0.86, rectRadius: 0.06,
    fill: { color: i >= 3 ? NAVY : CARTAO }, line: { color: i >= 3 ? NAVY : CARTAO },
    objectName: `fase-${i}` });
  s.addText(f, { isTextBox: true, x, y: 4.78, w: 2.0, h: 0.86, margin: 0,
    fontSize: 12.5, bold: i >= 3, color: i >= 3 ? "FFFFFF" : TINTA, align: "center", valign: "middle",
    objectName: `fase-t-${i}` });
});
s.addText("As duas últimas fases são a contribuição desta etapa", {
  isTextBox: true, x: X, y: 5.74, w: W, h: 0.3, margin: 0,
  fontSize: 12, italic: true, color: SUAVE, objectName: "fases-nota" });
notas(s, "Segui o CRISP-DM, que é um roteiro padrão de projetos de dados, e fiz tudo em Python. São 4.180 partidas, onze temporadas, 22 informações por jogo.\n\nNo TCC 1 eu tinha coberto as três primeiras etapas. Modelagem e avaliação entraram agora.\n\nE guardem o número da direita, 81 testes, porque é o assunto do próximo slide.");
// ═══════════════════════ 6. A solução computacional ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Método" });
titulo(s, "A solução computacional em camadas");
s.addText("O TCC 1 era um notebook único. Hoje é um pacote Python de sete módulos, com fronteiras explícitas entre as etapas e 81 testes automatizados.", {
  isTextBox: true, x: X, y: 1.6, w: W, h: 0.5, margin: 0,
  fontSize: 15, color: CINZA, objectName: "arq-intro" });
s.addImage({ path: fig("arquitetura_pipeline.png"), x: X, y: 2.18, w: 3.85, h: 4.1,
  objectName: "fig-arquitetura" });

const rigor = [
  ["Manifesto com SHA-256",
   "Procedência e resumo criptográfico de cada arquivo. Qualquer divergência interrompe a execução."],
  ["Falha alta, nunca silenciosa",
   "Erro de coleta interrompe o processamento, em vez de gerar um conjunto parcial sem aviso."],
  ["Quebra de série detectada sozinha",
   "Finalizações no alvo caem 37% entre 2012/13 e 2013/14. Não é o jogo que mudou, é o critério do provedor."],
];
rigor.forEach(([t, d], i) => {
  const y = 2.18 + i * 1.42;
  cartao(s, { x: X + 4.25, y, w: 6.55, h: 1.26, numero: i + 1, titulo: t, corpo: d });
});
s.addText("Nenhum número desta apresentação foi copiado à mão: todos saem de tabelas e figuras geradas por código.",
  { isTextBox: true, x: X, y: 6.4, w: W, h: 0.34, margin: 0,
    fontSize: 12.5, italic: true, color: SUAVE, objectName: "arq-nota" });
notas(s, "O TCC 1 era um arquivo só, onde coleta, cálculo e texto se misturavam. Foi isso que permitiu um erro que eu só descobri na apresentação, e que eu mostro daqui a pouco.\n\nHoje é um programa dividido em camadas, como no diagrama. Cada camada entrega para a seguinte por arquivo em disco, e é isso que permite testar cada pedaço separadamente.\n\nÀ direita, três decisões que vieram de problemas reais. Cada arquivo baixado tem uma assinatura digital guardada, porque o site muda os arquivos de tempos em tempos, e sem isso duas execuções em dias diferentes dariam números diferentes, sem avisar. Se a coleta falha, o programa para. Antes ele seguia com dados pela metade. E a terceira é um achado. Eu tenho uma rotina que procura mudanças estranhas nos dados, e ela encontrou uma: as finalizações no alvo caem 37% de uma temporada para a outra, em 2013, enquanto os gols ficam iguais. Não foi o futebol que mudou, foi o critério de quem anota.\n\nE a frase de baixo: nenhum número desta apresentação foi digitado à mão.");

// ═══════════════════════ 6b. Verificação ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Método" });
titulo(s, "Como o código é verificado");
s.addShape(pres.ShapeType.roundRect, { x: X, y: 1.6, w: W, h: 1.0, rectRadius: 0.08,
  fill: { color: NAVY }, line: { color: NAVY }, objectName: "ver-fundo" });
s.addText("O programa calcula algo que ninguém conhece de antemão. Não existe resposta certa para comparar com a saída.",
  { isTextBox: true, x: X + 0.4, y: 1.7, w: W - 0.8, h: 0.8, margin: 0,
    fontSize: 16, bold: true, color: "FFFFFF", valign: "middle", objectName: "ver-texto" });
cartao(s, { x: X, y: 2.82, w: 5.25, h: 2.2, numero: 1,
  titulo: "Dados sintéticos",
  corpo: "Gerar partidas a partir do próprio modelo, com γ conhecido, e exigir que o ajuste o recupere." });
cartao(s, { x: X + 5.55, y: 2.82, w: 5.25, h: 2.2, numero: 2,
  titulo: "Teste de propriedade",
  corpo: "Não afirma o valor certo. Afirma uma relação: alterar o placar de uma partida não pode mudar as variáveis daquela partida." });
s.addShape(pres.ShapeType.roundRect, { x: X, y: 5.22, w: 7.0, h: 1.1, rectRadius: 0.06,
  fill: { color: CARTAO }, line: { color: CARTAO }, objectName: "ver-cod-fundo" });
s.addText([
  { text: "assert", options: { color: AZUL, bold: true } },
  { text: " antes[feature] == depois[feature], ", options: { color: TINTA } },
  { text: '"VAZAMENTO"', options: { color: LARANJA } },
], { isTextBox: true, x: X + 0.3, y: 5.42, w: 6.4, h: 0.3, margin: 0,
     fontSize: 13, fontFace: "Courier New", objectName: "ver-codigo" });
s.addText("tests/test_preditivo.py", {
  isTextBox: true, x: X + 0.3, y: 5.78, w: 6.4, h: 0.28, margin: 0,
  fontSize: 11, color: SUAVE, fontFace: "Courier New", objectName: "ver-codigo-fonte" });
stat(s, { x: X + 7.6, y: 5.08, w: 3.2, numero: "83 → 97,5%",
  rotulo: "cobertura do intervalo, antes e depois\nde trocar o cálculo do erro padrão",
  cor: LARANJA, tamanho: 28 });
notas(s, "Essa é a parte que eu considero a maior contribuição de Computação do trabalho.\n\nTestar um programa científico tem uma dificuldade própria: ele foi escrito justamente para calcular algo que ninguém sabe de antemão. Não existe gabarito para conferir.\n\nEntão eu usei dois caminhos. O primeiro é inventar dados. Em vez de testar com jogos reais, eu gero jogos falsos a partir do próprio modelo, com um valor de vantagem que eu mesmo escolhi, e verifico se o programa encontra aquele valor de volta. Foi assim que eu descobri um erro meu. A minha margem de erro acertava o valor verdadeiro em 83% das vezes, quando deveria acertar em 95%. Eu estava dizendo ter mais certeza do que de fato tinha. Troquei a forma de calcular e foi para 97,5%.\n\nO segundo caminho é testar uma regra, em vez de um número. Eu digo o seguinte: se eu mudar o placar de um jogo, nenhuma informação usada para prever aquele mesmo jogo pode mudar. É a linha de código aí embaixo. É assim que eu provo que o modelo não está espiando o resultado.");

// ═══════════════════════ 7. A vantagem existe ═══════════════════════
pres.addSection({ title: "Resultados" });
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Resultados" });
titulo(s, "A vantagem existe — e é menor do que se supõe");
stat(s, { x: X, y: 1.78, w: 3.3, numero: "58,09%", rotulo: "das partidas decididas\nterminam com vitória do mandante\nIC 95%: [56,35; 59,81]" });
stat(s, { x: X + 3.7, y: 1.78, w: 3.3, numero: "+0,37", rotulo: "ponto por jogo de vantagem\nIC 95%: [0,29; 0,45]" });
stat(s, { x: X + 7.4, y: 1.78, w: 3.4, numero: "0,143", rotulo: "d de Cohen\nefeito pequeno", cor: LARANJA });
s.addShape(pres.ShapeType.roundRect, { x: X, y: 4.1, w: W, h: 1.78, rectRadius: 0.08,
  fill: { color: CARTAO }, line: { color: CARTAO }, objectName: "efeito-fundo" });
s.addText("Significância não é magnitude", {
  isTextBox: true, x: X + 0.4, y: 4.3, w: W - 0.8, h: 0.34, margin: 0,
  fontSize: 16, bold: true, color: NAVY, objectName: "efeito-tit" });
s.addText("Com 4.180 partidas, p-valores reduzidos são esperados mesmo para diferenças modestas. O tamanho de efeito classifica o fenômeno como pequeno: consistente e sistemático, porém de magnitude moderada. O TCC 1 descrevia a assimetria como contundente — a correção aqui é de interpretação, não de cálculo.",
  { isTextBox: true, x: X + 0.4, y: 4.7, w: W - 0.8, h: 1.0, margin: 0,
    fontSize: 14, color: CINZA, lineSpacingMultiple: 1.12, objectName: "efeito-corpo" });
notas(s, "Indo para os resultados. A vantagem existe, com folga. Dos jogos que têm vencedor, 58% terminam com vitória do mandante. Em pontos, são 0,37 ponto a mais por jogo.\n\nMas aqui vem a primeira correção em relação ao TCC 1. O tamanho desse efeito é pequeno. Com 4.180 jogos, qualquer diferencinha fica estatisticamente significativa, e significativo não quer dizer grande. O TCC 1 dizia que a assimetria era contundente, e isso não se sustenta. O fenômeno é constante, mas modesto.");

// ═══════════════════════ 8. Volume, não eficiência ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Resultados" });
titulo(s, "Volume de oportunidades, não eficiência");
s.addImage({ path: fig("volume_ofensivo.png"), x: X, y: 1.68, w: 7.1, h: 2.67,
  objectName: "fig-volume" });
stat(s, { x: X + 7.5, y: 1.72, w: 3.3, numero: "32,6%", rotulo: "conversão do mandante", tamanho: 38 });
stat(s, { x: X + 7.5, y: 3.08, w: 3.3, numero: "31,8%", rotulo: "conversão do visitante", tamanho: 38 });
s.addText("As taxas de conversão de finalizações no alvo em gols são praticamente equivalentes, com intervalos de confiança que quase se sobrepõem. O diferencial vem do volume: mandantes produzem mais finalizações no alvo e mais escanteios em todas as temporadas do recorte.",
  { isTextBox: true, x: X, y: 4.62, w: W, h: 0.9, margin: 0,
    fontSize: 15, color: CINZA, lineSpacingMultiple: 1.12, objectName: "conv-texto" });
legenda(s, "Fonte: autoria própria (2026).", 5.6);
notas(s, "E de onde vem essa vantagem? Não de eficiência. O mandante transforma chute em gol praticamente na mesma taxa do visitante, 32,6 contra 31,8 por cento.\n\nO que muda é o volume. São dois painéis: chutes no alvo à esquerda, escanteios à direita. A linha do mandante fica por cima da do visitante nas onze temporadas, sem nenhuma exceção. A vantagem é de volume, não de pontaria.");

// ═══════════════════════ 9. Correção do Big Six ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Resultados" });
titulo(s, "Correção: a comparação entre Big Six e demais clubes");
s.addText("O cálculo agregava, para cada partida, os pontos do mandante e os do visitante. Como a segunda coluna é o visitante daquela mesma partida, o que se media não era o Big Six fora de casa, e sim seus adversários.",
  { isTextBox: true, x: X, y: 1.6, w: W, h: 0.6, margin: 0,
    fontSize: 15, color: CINZA, lineSpacingMultiple: 1.1, objectName: "bs-intro" });
const linhas = [
  ["", "TCC 1", "Corrigido"],
  ["Diferencial do Big Six", "+1,397", "+0,418"],
  ["Diferencial dos demais", "−0,070", "+0,366"],
  ["Diferença entre grupos", "—", "+0,051"],
  ["p-valor", "< 0,001", "0,351"],
  ["Unidade de análise", "1.254 partidas", "28 clubes"],
];
s.addTable(
  linhas.map((l, i) => l.map((c, j) => ({
    text: c,
    options: {
      bold: i === 0 || j === 0, fontSize: 14,
      color: i === 0 ? "FFFFFF" : (j === 2 ? NAVY : TINTA),
      fill: { color: i === 0 ? NAVY : (i % 2 ? "FFFFFF" : CARTAO) },
      align: j === 0 ? "left" : "center", valign: "middle",
    },
  }))),
  { x: X, y: 2.36, w: 7.0, colW: [3.0, 2.0, 2.0], rowH: 0.42,
    border: { type: "solid", color: "FFFFFF", pt: 1 }, objectName: "bs-tabela" }
);
s.addShape(pres.ShapeType.roundRect, { x: X + 7.4, y: 2.36, w: 3.4, h: 2.52, rectRadius: 0.08,
  fill: { color: NAVY }, line: { color: NAVY }, objectName: "bs-licao-fundo" });
s.addText("O aprendizado", { isTextBox: true, x: X + 7.7, y: 2.6, w: 2.8, h: 0.32, margin: 0,
  fontSize: 15, bold: true, color: AMARELO, objectName: "bs-licao-tit" });
s.addText("O teste aparentava poder por contar partidas, quando a hipótese era sobre clubes. Com a unidade correta, não há diferença estatisticamente significativa entre os grupos.",
  { isTextBox: true, x: X + 7.7, y: 3.02, w: 2.8, h: 1.7, margin: 0,
    fontSize: 13.5, color: "FFFFFF", lineSpacingMultiple: 1.12, objectName: "bs-licao-corpo" });
s.addText("Dois indícios estavam na própria saída do TCC 1: o Big Six aparecia com 0,701 ponto fora, quando a tabela por clube registrava Man City com 2,05; e os demais clubes apareciam melhores fora do que em casa.",
  { isTextBox: true, x: X, y: 5.06, w: 7.0, h: 0.86, margin: 0,
    fontSize: 13, italic: true, color: SUAVE, lineSpacingMultiple: 1.1, objectName: "bs-indicios" });
notas(s, "Esse slide é o que eu mais queria mostrar, porque é a correção de um erro meu.\n\nNo TCC 1 eu comparei os seis grandes com o resto da liga e achei uma diferença enorme. O cálculo somava, para cada jogo, os pontos do mandante de um lado e os do visitante do outro, e separava pelo nome do mandante.\n\nO problema é que o visitante daquele jogo não é o mesmo time. Quando eu olhava a linha dos seis grandes, a coluna de fora de casa não era os seis grandes jogando fora. Eram os adversários deles. Eu estava comparando dois grupos diferentes e chamando de um só.\n\nRefazendo a conta por clube, e não por jogo, a diferença entre os grupos desaparece. O p-valor sai de menos de 0,001 para 0,35.\n\nE tinha um sinal na minha própria saída que eu não enxerguei: os times menores apareciam melhores fora do que em casa, o que não existe. Uma das conclusões do TCC 1 cai por aqui.");
// ═══════════════════════ 10. Por faixa de classificação ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Resultados" });
titulo(s, "Times de cima dependem mais do mando, não menos");
s.addImage({ path: fig("fator_casa_por_faixa.png"), x: X, y: 1.66, w: 6.0, h: 3.8,
  objectName: "fig-faixa" });
s.addText("O gradiente é monotônico e se repete em gols, finalizações no alvo e escanteios. A faixa é recalculada a cada temporada, pela posição final — não por um grupo fixo de clubes.",
  { isTextBox: true, x: X + 6.4, y: 1.72, w: 4.4, h: 1.0, margin: 0,
    fontSize: 14.5, color: CINZA, lineSpacingMultiple: 1.12, objectName: "faixa-texto" });
const faixas = [["G6 (1º a 6º)", "0,450", NAVY], ["Meio (7º a 14º)", "0,349", CINZA], ["Z6 (15º a 20º)", "0,319", SUAVE]];
faixas.forEach(([n, v, cor], i) => {
  const y = 2.92 + i * 0.62;
  s.addText(n, { isTextBox: true, x: X + 6.4, y, w: 2.6, h: 0.4, margin: 0,
    fontSize: 14.5, color: TINTA, valign: "middle", objectName: `fx-n-${i}` });
  s.addText(v, { isTextBox: true, x: X + 9.0, y, w: 1.8, h: 0.4, margin: 0,
    fontSize: 19, bold: true, color: cor, align: "right", valign: "middle", objectName: `fx-v-${i}` });
});
s.addShape(pres.ShapeType.roundRect, { x: X + 6.4, y: 4.86, w: 4.4, h: 1.06, rectRadius: 0.08,
  fill: { color: CARTAO }, line: { color: CARTAO }, objectName: "teto-fundo" });
s.addText("E o efeito de teto atua contra o G6: ele já faz 1,73 ponto fora, restando 1,27 de margem, contra 2,28 do Z6.",
  { isTextBox: true, x: X + 6.7, y: 5.0, w: 3.8, h: 0.8, margin: 0,
    fontSize: 13, color: NAVY, lineSpacingMultiple: 1.1, objectName: "teto-texto" });
legenda(s, "Fonte: autoria própria (2026).", 5.62);
notas(s, "Refeita a pergunta do jeito certo, aparece um resultado que contraria a intuição.\n\nEm vez de usar um grupo fixo de clubes, eu separei por posição final, recalculada a cada temporada. Os seis primeiros ganham 0,450 ponto por jogar em casa. O meio da tabela, 0,349. Os seis últimos, 0,319.\n\nOs times de cima dependem mais do mando, não menos. E a ordem se repete em gols, em chutes no alvo e em escanteios, o que torna difícil ser coincidência.\n\nTem um detalhe que reforça. Os times de cima já fazem 1,73 ponto por jogo fora de casa, então sobra pouco espaço para crescer. Mesmo assim, crescem mais.");

// ═══════════════════════ 11. Por que um modelo ═══════════════════════
pres.addSection({ title: "Modelagem" });
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Modelagem" });
titulo(s, "Por que um modelo, e não mais uma média");
s.addText("Médias de pontos são limitadas a três por partida, o que comprime a vantagem das equipes fortes, e não vêm acompanhadas de medida de incerteza. O modelo de Dixon e Coles (1997) estima ataque e defesa de cada clube e o mando como parâmetro compartilhado.",
  { isTextBox: true, x: X, y: 1.6, w: W, h: 0.74, margin: 0,
    fontSize: 15, color: CINZA, lineSpacingMultiple: 1.12, objectName: "mod-intro" });
s.addShape(pres.ShapeType.roundRect, { x: X, y: 2.62, w: 6.3, h: 1.3, rectRadius: 0.08,
  fill: { color: CARTAO }, line: { color: CARTAO }, objectName: "eq-fundo" });
s.addText([
  { text: "λ", options: { italic: true } }, { text: "casa", options: { subscript: true } },
  { text: "  =  exp( μ + ataque", options: {} }, { text: "i", options: { subscript: true } },
  { text: " − defesa", options: {} }, { text: "j", options: { subscript: true } },
  { text: " + γ )", options: {} },
], { isTextBox: true, x: X + 0.35, y: 2.82, w: 5.6, h: 0.42, margin: 0,
     fontSize: 17, color: NAVY, valign: "middle", objectName: "eq-casa" });
s.addText([
  { text: "λ", options: { italic: true } }, { text: "fora", options: { subscript: true } },
  { text: "  =  exp( μ + ataque", options: {} }, { text: "j", options: { subscript: true } },
  { text: " − defesa", options: {} }, { text: "i", options: { subscript: true } },
  { text: " )", options: {} },
], { isTextBox: true, x: X + 0.35, y: 3.3, w: 5.6, h: 0.42, margin: 0,
     fontSize: 17, color: NAVY, valign: "middle", objectName: "eq-fora" });
stat(s, { x: X + 6.9, y: 2.56, w: 3.9, numero: "+21,7%", rotulo: "de gols atribuíveis ao mando\nγ = 0,1967 · IC [0,1605; 0,2329]" });
lista(s, [
  "γ é estimado junto com a força de todos os clubes: mede a vantagem já descontada a qualidade do adversário",
  "A escala é multiplicativa, portanto comparável entre clubes de patamares distintos",
  "Validado por recuperação de parâmetro: 40 simulações com γ conhecido, cobertura de 97,5%",
], { x: X, y: 4.44, w: W, h: 1.8, tamanho: 15, espaco: 16 });
notas(s, "Até aqui eu usei média de pontos, e ela tem dois limites. Pontos param em três por jogo, então o teto atrapalha justamente os times fortes. E a média não diz nada sobre quem o time enfrentou.\n\nPor isso eu usei o modelo de Dixon e Coles, de 1997. Ele estima o ataque e a defesa de cada clube e, junto com isso, um número que representa o mando de campo. Como esse número sai calculado junto com a força de todo mundo, ele já vem descontado da qualidade do adversário.\n\nO resultado: jogar em casa vale 21,7% a mais de gols esperados. Eu programei esse modelo do zero, e foi nele que apliquei o teste de dados inventados.");

// ═══════════════════════ 12. γ por temporada ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Modelagem" });
titulo(s, "O fator casa ajustado, temporada a temporada");
s.addImage({ path: fig("mando_ajustado_por_temporada.png"), x: X, y: 1.66, w: 7.3, h: 4.11,
  objectName: "fig-gamma" });
cartao(s, { x: X + 7.7, y: 1.66, w: 3.1, h: 2.0,
  titulo: "2020/21", corpo: "γ = 0,007\nIC [−0,115; 0,129]\n\nSem vantagem detectável." });
cartao(s, { x: X + 7.7, y: 3.77, w: 3.1, h: 2.0,
  titulo: "2024/25", corpo: "γ = 0,063\nIC [−0,055; 0,180]\n\nSem relação com a pandemia.\nQuestão em aberto." });
legenda(s, "Os intervalos da maioria das temporadas se sobrepõem: o padrão é variabilidade alta em torno de um nível estável, com dois vales — não uma tendência monotônica de queda.", 5.9);
notas(s, "Rodando o modelo temporada a temporada, dá para olhar a evolução. Cada ponto é uma temporada, e a barra é a margem de erro.\n\nDuas temporadas encostam no zero, ou seja, sem vantagem nenhuma: 2020/21, que todo mundo espera, e 2024/25, que eu não consigo explicar e deixei como trabalho futuro.\n\nMas o mais importante aqui é o que não dá para afirmar. Repare que quase todas as barras se cruzam, e que 2022/23 está na mesma altura de 2016/17. Não existe queda contínua. É oscilação em torno do mesmo patamar.");
// ═══════════════════════ 13. O público ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Modelagem" });
titulo(s, "O público explica a queda de 2020/21?");
s.addImage({ path: fig("contraste_publico.png"), x: X, y: 1.62, w: 6.5, h: 2.94,
  objectName: "fig-publico" });
s.addShape(pres.ShapeType.roundRect, { x: X + 6.9, y: 1.66, w: 3.9, h: 2.86, rectRadius: 0.08,
  fill: { color: NAVY }, line: { color: NAVY }, objectName: "pub-fundo" });
s.addText("O contraste decisivo", { isTextBox: true, x: X + 7.2, y: 1.88, w: 3.3, h: 0.32,
  margin: 0, fontSize: 15, bold: true, color: AMARELO, objectName: "pub-tit" });
s.addText("Dentro da temporada 2019/20 — mesmos elencos, mesmo calendário, mesmo regulamento:",
  { isTextBox: true, x: X + 7.2, y: 2.26, w: 3.3, h: 0.62, margin: 0,
    fontSize: 13, color: "FFFFFF", lineSpacingMultiple: 1.1, objectName: "pub-sub" });
[["Sem público", "+0,457", "92 jogos"], ["Com público", "+0,438", "288 jogos"]].forEach(([n, v, j], i) => {
  const y = 2.98 + i * 0.62;
  s.addText(n, { isTextBox: true, x: X + 7.2, y, w: 1.6, h: 0.5, margin: 0,
    fontSize: 13.5, color: "FFFFFF", valign: "middle", objectName: `pub-n-${i}` });
  s.addText(v, { isTextBox: true, x: X + 8.7, y, w: 1.0, h: 0.5, margin: 0,
    fontSize: 18, bold: true, color: AMARELO, align: "right", valign: "middle", objectName: `pub-v-${i}` });
  s.addText(j, { isTextBox: true, x: X + 9.8, y, w: 0.9, h: 0.5, margin: 0,
    fontSize: 11, color: SUAVE, align: "right", valign: "middle", objectName: `pub-j-${i}` });
});
s.addText("A vantagem não caiu com a ausência de torcida (p = 0,952 no contraste descritivo; p = 0,680 no modelo ajustado). A inversão ocorre apenas em 2020/21, temporada que diferiu das anteriores também em pré-temporada, calendário e número de substituições.",
  { isTextBox: true, x: X, y: 4.76, w: W, h: 0.86, margin: 0,
    fontSize: 14.5, color: CINZA, lineSpacingMultiple: 1.12, objectName: "pub-conclusao" });
legenda(s, "Alcance da conclusão: o intervalo de 2019/20 ainda contém o valor estimado no agregado — os dados não excluem o efeito, mas mostram que a evidência repousa sobre uma única temporada atípica.", 5.72);
notas(s, "Agora a torcida. A literatura trata os jogos de portão fechado como um experimento natural, e o TCC 1 seguiu essa linha. Só que tem um problema.\n\nComparar 2020/21 com os anos anteriores mistura o efeito da torcida com tudo o mais que mudou: pré-temporada curta, calendário apertado, mais substituições, jogadores afastados por contágio.\n\nA comparação limpa está dentro de 2019/20. Ali os mesmos elencos jogaram com e sem público, no mesmo campeonato: 92 jogos sem torcida e 288 com torcida.\n\nE o resultado é esse. Sem público, 0,457 de vantagem. Com público, 0,438. Não caiu. Se mudou, foi um pouquinho para cima. A inversão acontece só em 2020/21.\n\nUma ressalva que eu faço questão de dizer: isso não prova que a torcida não importa. O que mostra é que a prova de que ela importa está apoiada numa única temporada muito atípica.");

// ═══════════════════════ 14. A dissociação ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Modelagem" });
titulo(s, "Achado: arbitragem e resultado se dissociam");
s.addText("A coluna de cartões amarelos permite uma distinção que o diferencial de pontos, isoladamente, não permitiria.",
  { isTextBox: true, x: X, y: 1.6, w: W, h: 0.4, margin: 0,
    fontSize: 15, color: CINZA, objectName: "diss-intro" });
const diss = [
  ["2019/20\ncom público", "−0,247", "+0,438", CARTAO, TINTA],
  ["2019/20\nsem público", "+0,033", "+0,457", NAVY, "FFFFFF"],
  ["2020/21\nsem público", "+0,034", "−0,119", NAVY, "FFFFFF"],
];
s.addText("Cenário", { isTextBox: true, x: X, y: 2.2, w: 3.0, h: 0.34, margin: 0,
  fontSize: 13, bold: true, color: SUAVE, objectName: "diss-h0" });
s.addText("Diferencial de cartões", { isTextBox: true, x: X + 3.2, y: 2.2, w: 3.4, h: 0.34,
  margin: 0, fontSize: 13, bold: true, color: SUAVE, align: "center", objectName: "diss-h1" });
s.addText("Diferencial de pontos", { isTextBox: true, x: X + 6.9, y: 2.2, w: 3.4, h: 0.34,
  margin: 0, fontSize: 13, bold: true, color: SUAVE, align: "center", objectName: "diss-h2" });
diss.forEach(([n, c, p, fundo, tinta], i) => {
  const y = 2.62 + i * 0.96;
  s.addShape(pres.ShapeType.roundRect, { x: X, y, w: 10.3, h: 0.84, rectRadius: 0.06,
    fill: { color: fundo }, line: { color: fundo }, objectName: `diss-r-${i}` });
  s.addText(n, { isTextBox: true, x: X + 0.3, y, w: 2.8, h: 0.84, margin: 0,
    fontSize: 13.5, bold: true, color: tinta, valign: "middle", objectName: `diss-n-${i}` });
  s.addText(c, { isTextBox: true, x: X + 3.2, y, w: 3.4, h: 0.84, margin: 0,
    fontSize: 20, bold: true, color: i === 0 ? NAVY : AMARELO, align: "center", valign: "middle",
    objectName: `diss-c-${i}` });
  s.addText(p, { isTextBox: true, x: X + 6.9, y, w: 3.4, h: 0.84, margin: 0,
    fontSize: 20, bold: true, color: tinta, align: "center", valign: "middle",
    objectName: `diss-p-${i}` });
});
s.addText("O viés disciplinar favorável ao mandante desaparece sem público já em 2019/20 — mesma temporada em que a vantagem em pontos permaneceu inalterada. A torcida parece influenciar a arbitragem, mas esse viés não é o mecanismo que sustenta a vantagem em resultados.",
  { isTextBox: true, x: X, y: 5.56, w: W, h: 0.74, margin: 0,
    fontSize: 14.5, color: NAVY, bold: true, lineSpacingMultiple: 1.12, objectName: "diss-conc" });
notas(s, "E aqui está o achado mais original do trabalho. Ele aparece quando se olha cartão amarelo junto com ponto.\n\nEm 2019/20, com torcida, o mandante leva 0,247 cartão a menos que o visitante. É o favorecimento do árbitro que a literatura descreve. Nos jogos sem torcida da mesma temporada, isso some: vai para praticamente zero. Em 2020/21, também sem torcida, a mesma coisa.\n\nOu seja, tirar a torcida realmente muda o comportamento do árbitro.\n\nMas olhem a coluna da direita. Na mesma temporada, enquanto o favorecimento no cartão sumiu, a vantagem em pontos ficou igual.\n\nOs dois não andam juntos. A torcida mexe com o árbitro, mas não é por aí que nasce a vantagem no placar. Isso importa porque as duas coisas costumam ser tratadas como uma só.");

// ═══════════════════════ 15. Preditivo: desenho ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Modelagem" });
titulo(s, "Modelagem preditiva: o risco antes do resultado");
s.addShape(pres.ShapeType.roundRect, { x: X, y: 1.62, w: W, h: 1.12, rectRadius: 0.08,
  fill: { color: NAVY }, line: { color: NAVY }, objectName: "vaz-fundo" });
s.addText("Finalizações, escanteios e faltas só existem depois do apito final. Usá-las como variáveis explicativas produziria acurácia alta e um trabalho errado.",
  { isTextBox: true, x: X + 0.4, y: 1.74, w: W - 0.8, h: 0.9, margin: 0,
    fontSize: 16, bold: true, color: "FFFFFF", valign: "middle", lineSpacingMultiple: 1.1,
    objectName: "vaz-texto" });
cartao(s, { x: X, y: 2.9, w: 6.1, h: 1.5, numero: 1,
  titulo: "Features pré-jogo",
  corpo: "Rating Elo, forma recente, forma por mando, dias de descanso, rodada e regime de público." });
cartao(s, { x: X, y: 4.52, w: 6.1, h: 1.5, numero: 2,
  titulo: "Trava experimental",
  corpo: "Altera o placar de uma partida, reconstrói tudo e exige que nenhuma feature daquela partida se mova." });
s.addImage({ path: fig("validacao_temporal.png"), x: X + 6.45, y: 2.9, w: 4.35, h: 3.36,
  objectName: "fig-walkforward" });
s.addText("Um contra-teste exige que as partidas seguintes mudem, para impedir que o primeiro seja satisfeito trivialmente.",
  { isTextBox: true, x: X, y: 6.15, w: 6.1, h: 0.4, margin: 0,
    fontSize: 12.5, italic: true, color: SUAVE, objectName: "vaz-nota" });
notas(s, "A última parte é prever resultados, e ela começa com um cuidado.\n\nChute, escanteio e falta só existem depois que o jogo acaba. Se eu usar isso para prever o jogo, eu acerto muito e o trabalho está errado. É o erro mais comum nesse tipo de estudo.\n\nEntão eu só uso informação que existe antes do apito: a força de cada time, o desempenho nos últimos cinco jogos, dias de descanso, rodada e se tinha público.\n\nDo lado direito está o desenho da validação. Para prever uma temporada, o modelo só enxerga temporadas anteriores. Dentro da temporada, ele vai aprendendo a cada dez jogos, e todos os modelos aprendem no mesmo ritmo.");
// ═══════════════════════ 16. Preditivo: resultados ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Modelagem" });
titulo(s, "O modelo estatístico superou os de aprendizado de máquina");
const modelos = [
  ["Dixon-Coles", "0,9762", "53,6%", true],
  ["Regressão logística", "0,9880", "53,6%", false],
  ["Frequência base", "1,0669", "44,0%", false],
  ["Gradient boosting", "1,0807", "50,7%", false],
];
s.addText("Modelo", { isTextBox: true, x: X, y: 1.66, w: 3.2, h: 0.3, margin: 0,
  fontSize: 12.5, bold: true, color: SUAVE, objectName: "pred-h0" });
s.addText("Log-loss", { isTextBox: true, x: X + 3.3, y: 1.66, w: 1.5, h: 0.3, margin: 0,
  fontSize: 12.5, bold: true, color: SUAVE, align: "right", objectName: "pred-h1" });
s.addText("Acurácia", { isTextBox: true, x: X + 4.95, y: 1.66, w: 1.4, h: 0.3, margin: 0,
  fontSize: 12.5, bold: true, color: SUAVE, align: "right", objectName: "pred-h2" });
modelos.forEach(([n, l, a, destaque], i) => {
  const y = 2.02 + i * 0.66;
  s.addShape(pres.ShapeType.roundRect, { x: X, y, w: 6.35, h: 0.56, rectRadius: 0.05,
    fill: { color: destaque ? NAVY : CARTAO }, line: { color: destaque ? NAVY : CARTAO },
    objectName: `pred-r-${i}` });
  s.addText(n, { isTextBox: true, x: X + 0.25, y, w: 3.0, h: 0.56, margin: 0,
    fontSize: 14, bold: destaque, color: destaque ? "FFFFFF" : TINTA, valign: "middle",
    objectName: `pred-n-${i}` });
  s.addText(l, { isTextBox: true, x: X + 3.3, y, w: 1.5, h: 0.56, margin: 0,
    fontSize: 15, bold: true, color: destaque ? AMARELO : TINTA, align: "right", valign: "middle",
    objectName: `pred-l-${i}` });
  s.addText(a, { isTextBox: true, x: X + 4.95, y, w: 1.15, h: 0.56, margin: 0,
    fontSize: 14, color: destaque ? "FFFFFF" : CINZA, align: "right", valign: "middle",
    objectName: `pred-a-${i}` });
});
s.addImage({ path: fig("preditivo_calibracao.png"), x: X + 6.75, y: 1.62, w: 4.05, h: 3.79,
  objectName: "fig-calib" });
s.addShape(pres.ShapeType.roundRect, { x: X, y: 4.76, w: 6.35, h: 1.3, rectRadius: 0.08,
  fill: { color: CARTAO }, line: { color: CARTAO }, objectName: "calib-fundo" });
s.addText("O gradient boosting tem acurácia melhor que a frequência base e log-loss pior. A calibração explica: quando prevê 94%, acerta 81%. Ele empurra as probabilidades para os extremos, o que eleva a acurácia e penaliza severamente o log-loss.",
  { isTextBox: true, x: X + 0.3, y: 4.9, w: 5.75, h: 1.04, margin: 0,
    fontSize: 13.5, color: NAVY, lineSpacingMultiple: 1.12, objectName: "calib-texto" });
s.addText("Fonte: autoria própria (2026).", {
  isTextBox: true, x: X + 6.75, y: 5.46, w: 4.05, h: 0.28, margin: 0,
  fontSize: 11, italic: true, color: SUAVE, objectName: "legenda" });
notas(s, "E o resultado foi esse. O modelo estatístico ganhou dos modelos de aprendizado de máquina.\n\nO caso mais interessante é o último da tabela. Ele acerta mais jogos que o palpite mais simples e, ainda assim, fica em último lugar na métrica principal.\n\nO gráfico explica. Quando ele diz que o mandante tem 94% de chance, o mandante ganha 81% das vezes. Ele exagera na confiança. Para acertar quem ganha, isso até ajuda, porque basta apontar o favorito. Mas se você leva a sério a probabilidade que ele deu, ele erra feio.\n\nPor isso eu não avaliei por acerto, e sim por uma métrica que olha a probabilidade.");

// ═══════════════════════ 17. Conclusões ═══════════════════════
pres.addSection({ title: "Fechamento" });
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Fechamento" });
titulo(s, "Conclusões");
s.addText("O que se mantém", { isTextBox: true, x: X, y: 1.66, w: 5.1, h: 0.32, margin: 0,
  fontSize: 15, bold: true, color: NAVY, objectName: "conc-h1" });
lista(s, [
  "A vantagem do mandante existe e é robusta: +21,7% de gols, já descontada a força do adversário",
  "O fenômeno é volume de oportunidades, não eficiência de finalização",
], { x: X, y: 2.06, w: 5.1, h: 1.5, tamanho: 14 });
s.addText("O que mudou", { isTextBox: true, x: X + 5.6, y: 1.66, w: 5.2, h: 0.32, margin: 0,
  fontSize: 15, bold: true, color: NAVY, objectName: "conc-h2" });
lista(s, [
  "O Big Six não depende menos do mando — a diferença não é significativa",
  "Times de cima dependem mais, em gradiente monotônico por posição final",
  "O público não explica a queda de 2020/21 no contraste intratemporada",
], { x: X + 5.6, y: 2.06, w: 5.2, h: 2.0, tamanho: 14 });
s.addShape(pres.ShapeType.roundRect, { x: X, y: 4.1, w: W, h: 1.5, rectRadius: 0.08,
  fill: { color: NAVY }, line: { color: NAVY }, objectName: "achado-fundo" });
s.addText("Achado novo", { isTextBox: true, x: X + 0.4, y: 4.28, w: W - 0.8, h: 0.3, margin: 0,
  fontSize: 14, bold: true, color: AMARELO, objectName: "achado-tit" });
s.addText("O viés de arbitragem e a vantagem em resultados se dissociam: o primeiro desaparece sem público já em 2019/20, enquanto o segundo permanece. A torcida influencia a arbitragem, mas esse não é o mecanismo central do Fator Casa.",
  { isTextBox: true, x: X + 0.4, y: 4.64, w: W - 0.8, h: 0.82, margin: 0,
    fontSize: 15, color: "FFFFFF", lineSpacingMultiple: 1.12, objectName: "achado-corpo" });
notas(s, "Fechando.\n\nO que se mantém: jogar em casa dá vantagem, 21,7% a mais de gols já descontado o adversário, e ela vem de criar mais oportunidades, não de aproveitá-las melhor.\n\nO que mudou em relação ao TCC 1: os seis grandes não dependem menos do mando, na verdade são os times de cima que dependem mais, e a torcida não explica a queda de 2020/21 quando a comparação é feita direito.\n\nE o achado novo, em destaque: o favorecimento do árbitro e a vantagem no placar se separam. O primeiro some sem torcida, o segundo continua. A torcida mexe com a arbitragem, mas não é esse o motor do Fator Casa.");

// ═══════════════════════ 18. Limitações e futuros ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Fechamento" });
titulo(s, "Limitações e trabalhos futuros");
s.addText("Limitações", { isTextBox: true, x: X, y: 1.66, w: 5.1, h: 0.32, margin: 0,
  fontSize: 15, bold: true, color: NAVY, objectName: "lim-h" });
lista(s, [
  "Parâmetro de mando único para toda a liga, não estimado por clube",
  "Ausência de variáveis de contexto: distância de viagem, horário e ocupação do estádio",
  "Não foi possível construir o contraste intratemporada em 2020/21",
  "Sem comparação com as probabilidades implícitas no mercado de apostas",
], { x: X, y: 2.12, w: 5.1, h: 3.5, tamanho: 15, espaco: 16 });
s.addText("Trabalhos futuros", { isTextBox: true, x: X + 5.6, y: 1.66, w: 5.2, h: 0.32, margin: 0,
  fontSize: 15, bold: true, color: NAVY, objectName: "fut-h" });
lista(s, [
  "Estimar o mando por clube com modelos hierárquicos e encolhimento",
  "Incorporar distância de deslocamento e ocupação do estádio",
  "Comparar com as odds de mercado como referência externa",
  "Estender a outras ligas europeias",
  "Investigar a temporada 2024/25, cujo parâmetro próximo de zero não tem explicação evidente",
], { x: X + 5.6, y: 2.12, w: 5.2, h: 3.5, tamanho: 15, espaco: 16 });
notas(s, "As limitações. O modelo usa um único valor de mando para a liga inteira, então eu não sei dizer se um clube específico depende mais do que outro. Faltam dados de contexto: distância de viagem, horário do jogo, quanto o estádio encheu. E não deu para fazer a comparação limpa dentro de 2020/21, porque nenhum jogo daquele ano teve público.\n\nFicou de fora a comparação com as cotações das casas de apostas, que seria a referência mais dura. O código está pronto, mas os dados de cotação não vieram na base. É a continuação mais imediata.");

// ═══════════════════════ 19. Encerramento ═══════════════════════
s = pres.addSlide({ masterName: "SECAO", sectionTitle: "Fechamento" });
s.addText("Obrigado", { isTextBox: true, x: X, y: 2.5, w: 8.6, h: 1.0, margin: 0,
  fontSize: 52, bold: true, color: NAVY, objectName: "fim-titulo" });
s.addShape(pres.ShapeType.rect, { x: X, y: 3.66, w: 1.5, h: 0.055,
  fill: { color: AMARELO }, line: { color: AMARELO }, objectName: "fim-marca" });
s.addText("Matheus Ferreira Alphonse dos Anjos", {
  isTextBox: true, x: X, y: 3.96, w: 8.6, h: 0.36, margin: 0,
  fontSize: 17, bold: true, color: TINTA, objectName: "fim-autor" });
s.addText("Orientador: Prof. Francisco Pereira Junior", {
  isTextBox: true, x: X, y: 4.32, w: 8.6, h: 0.34, margin: 0,
  fontSize: 15, color: CINZA, objectName: "fim-orientador" });
s.addText("Código, dados e documentação: github.com/matheustm29/TCC2", {
  isTextBox: true, x: X, y: 5.0, w: 8.6, h: 0.34, margin: 0,
  fontSize: 13, color: SUAVE, objectName: "fim-repo" });
notas(s, "É isso. Obrigado, e fico à disposição.");

// ═══════════════════════ gravação ═══════════════════════
const SAIDA = path.join(DIR, SEM_NOTAS ? "TCC2_Defesa_sem_notas.pptx" : "TCC2_Defesa.pptx");
pres.writeFile({ fileName: SAIDA }).then(async () => {
  const { applyTheme } = require("/root/.claude/skills/synced/7ce4da26-8ba6-4b98-83a6-29f1f2f4c6d4_824aeafc-07d5-4c65-9478-a848f0bee219/pptx/scripts/apply_theme.js");
  await applyTheme(SAIDA, THEME);
  console.log("gerado:", SAIDA);
});
