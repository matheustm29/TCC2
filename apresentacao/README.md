# Apresentação de defesa

`TCC2_Defesa.pptx` — 19 slides, 16:9, com o fundo institucional do campus.
Cada slide traz nota de apresentador (painel "Anotações" do PowerPoint).

## Estrutura

| Slides | Bloco |
|---|---|
| 1–2 | Capa e roteiro |
| 3–4 | Contexto, problema e objetivos |
| 5–6 | Método, dados e integridade |
| 7–10 | Resultados descritivos |
| 11–16 | Modelagem (Dixon-Coles e preditivo) |
| 17–19 | Conclusões, limitações e encerramento |

## Como regerar

O arquivo `.pptx` é gerado por script, não editado à mão. Para refazer
após alterar texto ou figura:

```bash
npm install pptxgenjs
node gerar.js
```

As figuras vêm de `figuras/`, na raiz do repositório, produzidas por
`scripts/executar_analise.py` e `scripts/executar_modelagem.py`;
`fundo.jpg` é o fundo institucional fornecido pela universidade.

## Duas versões do deck

```bash
node gerar.js                 # TCC2_Defesa.pptx, com a fala nas notas
SEM_NOTAS=1 node gerar.js     # TCC2_Defesa_sem_notas.pptx, para compartilhar
```

As notas de apresentador trazem o texto falado de cada slide, escrito em
primeira pessoa. Ele serve ao modo apresentador do PowerPoint e não faz
sentido num arquivo enviado a terceiros, daí a segunda versão.
