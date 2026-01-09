---
title: Top 10 - Top 10%
toc: false
style: styles.css
head: |
  <link rel="canonical" href="https://public.datalized.cl/paes-2026/top">
  <meta name="description" content="Análisis del Top 10% de puntajes PAES 2026. Descubre de qué tipos de establecimientos provienen los mejores resultados.">
  <meta property="og:title" content="PAES 2026 - Top 10%">
  <meta property="og:description" content="Análisis del Top 10% de puntajes PAES 2026 por tipo de establecimiento.">
  <meta property="og:url" content="https://public.datalized.cl/paes-2026/top">
  <meta property="og:type" content="website">
---

# Top 10


Una mirada rápida a quiénes concentran el **Top 10%** de puntajes en la PAES y cómo varía esa presencia según **dependencia** del establecimiento.


```js
const data = FileAttachment("data/brechas-top10.json").json();
const escuelasRanking = FileAttachment("data/escuelas-ranking.json").json();
import { rankBadge, depBadge, rankingAlign } from "./components/tableFormatters.js";

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};
```

```js
// Crear mapa de ranking nacional desde datos precalculados
const rankNacionalMap = new Map(escuelasRanking.map(e => [e.establecimiento, e.rank_nacional]));

// Agregar ranking a escuelas_top10
const escuelasTop10 = data.escuelas_top10.map((e, i) => ({
  ...e,
  rank_top10: i + 1,
  rank_nacional: rankNacionalMap.get(e.establecimiento) || '-'
}));

// colegios con estudiantes en el top 10%
const colegiosTop10Set = new Set(escuelasTop10.filter(e => e.estudiantes_top10 > 0).map(e => e.establecimiento));
const totalColegiosTop10 = colegiosTop10Set.size;

```

<div class="stats-grid">
  <div class="stat-card">
    <h2>Umbral Top 10%</h2>
    <span class="value">${data.umbrales.p90} pts</span>
  </div>
  <div class="stat-card">
    <h2>Umbral Top 20%</h2>
    <span class="value">${data.umbrales.p80} pts</span>
  </div>
  <div class="stat-card">
    <h2>Estudiantes en Top 10%</h2>
    <span class="value">${data.total_top10.toLocaleString()}</span>
  </div>
  <div class="stat-card">
    <h2>Colegios con estudiantes en Top 10%</h2>
    <span class="value">${totalColegiosTop10.toLocaleString()}</span>
  </div>
</div>

## Origen del Top 10% por Dependencia

Este gráfico muestra *de qué tipo de establecimiento* provienen los estudiantes que están en el Top 10% (en valores absolutos y con el porcentaje sobre el total del Top 10%).


```js
const pctNoPagado = data.origen_top10
  .filter(d => d.dependencia !== 'Particular Pagado')
  .reduce((sum, d) => sum + d.porcentaje, 0);
```

<div class="tip">
<strong>${pctNoPagado.toFixed(1)}%</strong> del Top 10% NO viene de colegios particulares pagados
</div>

<figure>
  <div class="plot-container">
    ${resize((width) => Plot.plot({
      width,
      marginLeft: Math.max(150, Math.min(200, width * 0.4)),
      height: 220,
      style: {fontSize: width < 500 ? "10px" : "12px"},
      y: {label: null},
      x: {label: "Número de estudiantes"},
      marks: [
        Plot.barX(data.origen_top10, {
          y: "dependencia",
          x: "estudiantes",
          fill: d => colores[d.dependencia],
          sort: {y: "-x"},
          tip: {
            format: {
              y: true,
              x: d => `${d.toLocaleString()} estudiantes (${data.origen_top10.find(item => item.estudiantes === d)?.porcentaje}%)`
            }
          }
        }),
        Plot.text(data.origen_top10, {
          y: "dependencia",
          x: "estudiantes",
          text: d => `${d.porcentaje}%`,
          dx: 5,
          textAnchor: "start",
          fontSize: 11,
          fill: "currentColor"
        }),
        Plot.ruleX([0])
      ]
    }))}
  </div>
  <figcaption><strong>Figura 1:</strong> Composición del Top 10% por tipo de establecimiento (valores absolutos y porcentajes)</figcaption>
</figure>

## Escuelas con más estudiantes en el Top 10%

Ranking de establecimientos por **cantidad de estudiantes en Top 10%**. El “ranking nacional” corresponde al ranking general del proyecto (no solo Top 10%).



```js
Inputs.table(escuelasTop10.slice(0, 100), {
  columns: ["rank_top10", "establecimiento", "dependencia", "estudiantes_top10", "comuna", "total_estudiantes", "rank_nacional"],
  header: {
    rank_top10: "#",
    establecimiento: "Establecimiento",
    dependencia: "Dependencia",
    estudiantes_top10: "Top 10%",
    comuna: "Comuna",
    total_estudiantes: "Total",
    rank_nacional: "# Nac."
  },
  format: {
    rank_top10: d => rankBadge(d),
    rank_nacional: d => rankBadge(d),
    establecimiento: d => html`<span class="school-name">${d}</span>`,
    dependencia: d => depBadge(d)
  },
  align: rankingAlign,
  width: {
    rank_top10: 40,
    establecimiento: 180,
    dependencia: 110,
    estudiantes_top10: 70,
    comuna: 100,
    total_estudiantes: 60,
    rank_nacional: 50
  },
  height: 'auto',
  select: false
})
```
