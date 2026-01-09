---
title: PAES 2026 - Ranking
toc: true
style: styles.css
head: |
  <link rel="canonical" href="https://public.datalized.cl/paes-2026/ranking">
  <meta name="description" content="Ranking de establecimientos educacionales chilenos según resultados PAES 2026. Filtra por región, comuna y dependencia.">
  <meta property="og:title" content="PAES 2026 - Ranking de Establecimientos">
  <meta property="og:description" content="Ranking de establecimientos educacionales chilenos según resultados PAES 2026.">
  <meta property="og:url" content="https://public.datalized.cl/paes-2026/ranking">
  <meta property="og:type" content="website">
---

# Ranking de Establecimientos

```js
import { rankBadge, depBadge, scoreValue, top10Indicator, rankingAlign } from "./components/tableFormatters.js";

const escuelas = FileAttachment("data/escuelas-ranking.json").json();
const filtros = FileAttachment("data/filtros.json").json();
```



<div class="filters">

```js
const regionSel = view(Inputs.select(
  [null, ...filtros.regiones],
  {label: "Región", format: d => d ? d.nombre : "Todas", size: 3}
));

const comunaSel = view(Inputs.select(
  [null, ...filtros.comunas],
  {label: "Comuna", format: d => d ? d.nombre : "Todas"}
));

const depSel = view(Inputs.select(
  [null, ...filtros.dependencias],
  {label: "Dependencia", format: d => d ? d.nombre : "Todas"}
));

const orden = view(Inputs.radio(
  ["Promedio", "Estudiantes", "Top 10%"],
  {value: "Promedio", label: "Ordenar por"}
));
```

</div>

<div class="warning" label="Nota metodológica">
  El DEMRE advierte que la PAES no fue diseñada para medir calidad educativa de establecimientos.
</div>

```js
const topN = 100;
// Filtrar y ordenar
let datos = escuelas
  .filter(e => !regionSel || e.cod_region === regionSel.codigo)
  .filter(e => !comunaSel || e.cod_comuna === comunaSel.codigo)
  .filter(e => !depSel || e.dependencia === depSel.nombre);

if (orden === "Promedio") datos.sort((a, b) => b.prom_lect_mate - a.prom_lect_mate);
else if (orden === "Estudiantes") datos.sort((a, b) => b.cantidad - a.cantidad);
else datos.sort((a, b) => b.en_top10 - a.en_top10);

datos = datos.slice(0, topN);
```

```js
Inputs.table(datos, {
  columns: ["rank_nacional", "establecimiento", "dependencia", "prom_lect_mate", "comuna", "cantidad", "en_top10", "rank_comuna"],
  header: {
    rank_nacional: html`<span title="Ranking nacional por promedio Lectora + Matemática">#</span>`,
    establecimiento: html`<span title="Nombre del establecimiento educacional">Establecimiento</span>`,
    dependencia: html`<span title="Tipo de administración del establecimiento">Dependencia</span>`,
    prom_lect_mate: html`<span title="Promedio de puntajes en Competencia Lectora y Matemática 1">Prom. L+M</span>`,
    comuna: html`<span title="Comuna donde se ubica el establecimiento">Comuna</span>`,
    cantidad: html`<span title="Cantidad de estudiantes que rindieron la PAES">Est.</span>`,
    en_top10: html`<span title="Estudiantes en el Top 10% nacional">Top 10%</span>`,
    rank_comuna: html`<span title="Ranking dentro de la comuna"># Com.</span>`
  },
  format: {
    rank_nacional: d => rankBadge(d),
    rank_comuna: d => rankBadge(d),
    establecimiento: d => html`<span class="school-name">${d}</span>`,
    dependencia: d => depBadge(d),
    prom_lect_mate: d => d,
    en_top10: (d, i, data) => data[i].cantidad,
    comuna: d => d
  },
  align: rankingAlign,
  width: {
    rank_nacional: 40,
    establecimiento: 180,
    dependencia: 110,
    prom_lect_mate: 80,
    comuna: 100,
    cantidad: 60,
    en_top10: 60,
    rank_comuna: 50
  },
  rows: 30,
  select: false,
  sort: false
})
```
