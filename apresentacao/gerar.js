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
  { text: "Orientador: Prof. Dr. Francisco Pereira Junior", options: { breakLine: true } },
  { text: "Bacharelado em Engenharia de Computação", options: {} },
], { isTextBox: true, x: X, y: 4.46, w: 9.3, h: 1.3, margin: 0,
     fontSize: 16, color: TINTA, lineSpacingMultiple: 1.2, objectName: "capa-autoria" });
s.addText("Campus Cornélio Procópio · 2026", {
  isTextBox: true, x: X, y: 5.74, w: 9.3, h: 0.34, margin: 0,
  fontSize: 13, color: SUAVE, objectName: "capa-local" });
s.addNotes("Bom dia. Vou apresentar a análise do Fator Casa na Premier League, cobrindo 11 temporadas e 4.180 partidas.");

// ═══════════════════════ 2. Roteiro ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Abertura" });
titulo(s, "Roteiro");
const roteiro = [
  ["Contexto e problema", "O fenômeno e por que revisitá-lo"],
  ["Método e dados", "CRISP-DM, 11 temporadas, 4.180 partidas"],
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
s.addNotes("Cinco blocos. A parte central são os resultados e a modelagem.");

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
s.addNotes("Cada mecanismo deixa uma assinatura empírica diferente. Arbitragem aparece em cartões; familiaridade e logística, em volume ofensivo. Isso vai permitir separá-los mais adiante.");

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
s.addNotes("A pergunta tem duas partes: a magnitude e os mecanismos. O quinto objetivo é o que entrou agora, no TCC 2.");

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
s.addNotes("O TCC 1 cobriu as três primeiras fases. Modelagem e Avaliação entraram agora.");
// ═══════════════════════ 6. Rigor dos dados ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Método" });
titulo(s, "Reprodutibilidade e integridade dos dados");
s.addText("A fonte reescreve periodicamente seus arquivos. Sem controle, duas execuções em datas distintas produzem números diferentes sem qualquer aviso.", {
  isTextBox: true, x: X, y: 1.62, w: W, h: 0.5, margin: 0,
  fontSize: 15, color: CINZA, objectName: "rigor-intro" });
cartao(s, { x: X, y: 2.3, w: 5.25, h: 1.72, numero: 1,
  titulo: "Manifesto com SHA-256",
  corpo: "Procedência e resumo criptográfico de cada arquivo são registrados. Qualquer divergência interrompe a execução." });
cartao(s, { x: X + 5.55, y: 2.3, w: 5.25, h: 1.72, numero: 2,
  titulo: "Falha alta, nunca silenciosa",
  corpo: "Erro de coleta interrompe o processamento, em vez de gerar um conjunto parcial sem aviso." });
s.addShape(pres.ShapeType.roundRect, { x: X, y: 4.2, w: W, h: 1.72, rectRadius: 0.08,
  fill: { color: NAVY }, line: { color: NAVY }, objectName: "quebra-fundo" });
s.addText("Quebra de série detectada automaticamente", {
  isTextBox: true, x: X + 0.4, y: 4.42, w: W - 0.8, h: 0.34, margin: 0,
  fontSize: 16, bold: true, color: AMARELO, objectName: "quebra-tit" });
s.addText("A média de finalizações no alvo da liga cai 37% entre 2012/13 e 2013/14, enquanto gols e finalizações totais permanecem estáveis. Não é mudança no jogo: é mudança de critério do provedor. Comparações dessa variável que atravessem 2013/14 são inválidas.", {
  isTextBox: true, x: X + 0.4, y: 4.82, w: W - 0.8, h: 0.96, margin: 0,
  fontSize: 14, color: "FFFFFF", lineSpacingMultiple: 1.1, objectName: "quebra-corpo" });
s.addNotes("Esse achado é metodológico, mas importa: sem ele, o estudo de caso dos estádios reportaria uma queda de quase dois chutes no alvo que seria artefato da planilha.");

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
s.addNotes("O teste binomial é condicionado aos jogos decididos. A nula do TCC 1 era uniforme entre os três resultados, o que seria rejeitado mesmo num mundo sem fator casa.");

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
s.addNotes("A conclusão qualitativa do TCC 1 se mantém, mas os valores mudaram: antes eram 33,3% e 32,1%, inflados por um filtro que removia justamente as partidas de conversão zero.");

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
s.addNotes("A conclusão 5.2 da monografia do TCC 1 cai. Não há evidência de que o Big Six dependa menos do mando.");
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
s.addNotes("Este é o achado que substitui a comparação com o Big Six, e aponta na direção contrária à intuição.");

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
s.addNotes("Numa temporada completa o calendário é balanceado, então o controle por adversário importa menos. Ele se torna decisivo nos recortes menores, como os 92 jogos sem público de 2019/20.");

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
s.addNotes("Importante não afirmar queda. 2022/23 está no mesmo patamar de 2016/17. A temporada 2024/25 é um achado novo, sem explicação evidente, e está nos trabalhos futuros.");
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
s.addNotes("Aqui é essencial não afirmar demais. O TCC 1 dizia que o experimento natural isolava o público como variável causal central. Isso não se sustenta no contraste intratemporada.");

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
s.addNotes("Este é o achado mais original do trabalho: os dois mecanismos se separam empiricamente.");

// ═══════════════════════ 15. Preditivo: desenho ═══════════════════════
s = pres.addSlide({ masterName: "CONTEUDO", sectionTitle: "Modelagem" });
titulo(s, "Modelagem preditiva: o risco antes do resultado");
s.addShape(pres.ShapeType.roundRect, { x: X, y: 1.62, w: W, h: 1.12, rectRadius: 0.08,
  fill: { color: NAVY }, line: { color: NAVY }, objectName: "vaz-fundo" });
s.addText("Finalizações, escanteios e faltas só existem depois do apito final. Usá-las como variáveis explicativas produziria acurácia alta e um trabalho errado.",
  { isTextBox: true, x: X + 0.4, y: 1.74, w: W - 0.8, h: 0.9, margin: 0,
    fontSize: 16, bold: true, color: "FFFFFF", valign: "middle", lineSpacingMultiple: 1.1,
    objectName: "vaz-texto" });
cartao(s, { x: X, y: 2.96, w: 3.45, h: 2.1, numero: 1,
  titulo: "Features pré-jogo",
  corpo: "Rating Elo, forma recente, forma por mando, dias de descanso, rodada e regime de público." });
cartao(s, { x: X + 3.68, y: 2.96, w: 3.45, h: 2.1, numero: 2,
  titulo: "Trava experimental",
  corpo: "Altera o placar de uma partida, reconstrói tudo e exige que nenhuma feature daquela partida se mova." });
cartao(s, { x: X + 7.36, y: 2.96, w: 3.44, h: 2.1, numero: 3,
  titulo: "Validação temporal",
  corpo: "Para prever uma temporada, o treino usa apenas partidas anteriores. Todos os modelos reajustam sobre o mesmo histórico." });
s.addText("Um contra-teste exige que as partidas seguintes mudem, para impedir que o primeiro seja satisfeito trivialmente.",
  { isTextBox: true, x: X, y: 5.26, w: W, h: 0.4, margin: 0,
    fontSize: 13, italic: true, color: SUAVE, objectName: "vaz-nota" });
s.addNotes("A ausência de vazamento não é declaração: é verificada por teste automatizado.");
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
s.addNotes("É a justificativa empírica para adotar log-loss como métrica principal, e não acurácia. Um modelo mais complexo perdendo para um mais simples, com a razão visível na calibração.");

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
s.addNotes("Duas conclusões do TCC 1 mudaram. Isso foi explicitado na monografia, com os números antigos e novos lado a lado.");

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
s.addNotes("A 2024/25 é a questão mais interessante em aberto — apareceu ao ajustar o modelo por temporada e não estava visível no diferencial bruto.");

// ═══════════════════════ 19. Encerramento ═══════════════════════
s = pres.addSlide({ masterName: "SECAO", sectionTitle: "Fechamento" });
s.addText("Obrigado", { isTextBox: true, x: X, y: 2.5, w: 8.6, h: 1.0, margin: 0,
  fontSize: 52, bold: true, color: NAVY, objectName: "fim-titulo" });
s.addShape(pres.ShapeType.rect, { x: X, y: 3.66, w: 1.5, h: 0.055,
  fill: { color: AMARELO }, line: { color: AMARELO }, objectName: "fim-marca" });
s.addText("Matheus Ferreira Alphonse dos Anjos", {
  isTextBox: true, x: X, y: 3.96, w: 8.6, h: 0.36, margin: 0,
  fontSize: 17, bold: true, color: TINTA, objectName: "fim-autor" });
s.addText("Orientador: Prof. Dr. Francisco Pereira Junior", {
  isTextBox: true, x: X, y: 4.32, w: 8.6, h: 0.34, margin: 0,
  fontSize: 15, color: CINZA, objectName: "fim-orientador" });
s.addText("Código, dados e documentação: github.com/matheustm29/TCC2", {
  isTextBox: true, x: X, y: 5.0, w: 8.6, h: 0.34, margin: 0,
  fontSize: 13, color: SUAVE, objectName: "fim-repo" });
s.addNotes("Fico à disposição para as perguntas da banca.");

// ═══════════════════════ gravação ═══════════════════════
const SAIDA = path.join(DIR, "TCC2_Defesa.pptx");
pres.writeFile({ fileName: SAIDA }).then(async () => {
  const { applyTheme } = require("/root/.claude/skills/synced/7ce4da26-8ba6-4b98-83a6-29f1f2f4c6d4_824aeafc-07d5-4c65-9478-a848f0bee219/pptx/scripts/apply_theme.js");
  await applyTheme(SAIDA, THEME);
  console.log("gerado:", SAIDA);
});
