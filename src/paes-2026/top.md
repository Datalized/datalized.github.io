---
title: El Top 10 - Top 10%
toc: false
---

<style>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.stat-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  padding: 1.25rem;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.stat-card h2 {
  font-size: 0.7rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.5rem 0;
}
.stat-card .value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}
</style>

# El Top 10: ¿De dónde viene el Top 10%?

```js
const data = await FileAttachment("data/brechas-top10.json").json();
const escuelasRanking = await FileAttachment("data/escuelas-ranking.json").json();

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};

// Crear mapa de ranking nacional desde datos precalculados
const rankNacionalMap = new Map(escuelasRanking.map(e => [e.establecimiento, e.rank_nacional]));

// Agregar ranking a escuelas_top10
const escuelasTop10 = data.escuelas_top10.map((e, i) => ({
  ...e,
  rank_top10: i + 1,
  rank_nacional: rankNacionalMap.get(e.establecimiento) || '-'
}));
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
</div>

## Origen del Top 10% por Dependencia

```js
const pctNoPagado = data.origen_top10
  .filter(d => d.dependencia !== 'Particular Pagado')
  .reduce((sum, d) => sum + d.porcentaje, 0);
```

<div class="tip">
<strong>${pctNoPagado.toFixed(1)}%</strong> del Top 10% NO viene de colegios particulares pagados
</div>

```js
resize((width) => Plot.plot({
  width,
  marginLeft: Math.min(200, width * 0.35),
  height: 220,
  style: {fontSize: "12px"},
  y: {label: null},
  marks: [
    Plot.barX(data.origen_top10, {
      y: "dependencia",
      x: "estudiantes",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"},
      tip: true
    }),
    Plot.text(data.origen_top10, {
      y: "dependencia",
      x: "estudiantes",
      text: d => `${d.porcentaje}%`,
      dx: 5,
      textAnchor: "start",
      fontSize: 11
    }),
    Plot.ruleX([0])
  ]
}))
```

## Probabilidad de estar en el Top 10% según Dependencia

```js
resize((width) => Plot.plot({
  width,
  marginLeft: Math.min(200, width * 0.35),
  height: 220,
  style: {fontSize: "12px"},
  y: {label: null},
  marks: [
    Plot.barX(data.prob_top10, {
      y: "dependencia",
      x: "pct_top10",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"},
      tip: true
    }),
    Plot.text(data.prob_top10, {
      y: "dependencia",
      x: "pct_top10",
      text: d => `${d.pct_top10}%`,
      dx: 5,
      textAnchor: "start",
      fontSize: 11
    }),
    Plot.ruleX([0])
  ],
  x: {label: "% en Top 10%"}
}))
```

## Escuelas con más estudiantes en el Top 10%

```js
Inputs.table(escuelasTop10.slice(0, 30), {
  columns: ["rank_top10", "rank_nacional", "establecimiento", "dependencia", "comuna", "estudiantes_top10", "total_estudiantes"],
  header: {
    rank_top10: "#Top10",
    rank_nacional: "#",
    establecimiento: "Establecimiento",
    dependencia: "Dependencia",
    comuna: "Comuna",
    estudiantes_top10: "Est. 10%",
    total_estudiantes: "Total Est."
  },
    width: {
    rank_top10: 50,
    rank_nacional: 20,
    estudiantes_top10: 80,
    total_estudiantes: 80,
    en_top10: 80,
    dependencia: 120,
    comuna: 100
  },
})
```

```js
resize((width) => Plot.plot({
  width,
  marginLeft: Math.min(280, width * 0.4),
  height: Math.max(400, escuelasTop10.slice(0, 20).length * 24),
  style: {fontSize: "11px"},
  y: {label: null},
  marks: [
    Plot.barX(escuelasTop10.slice(0, 20), {
      y: "establecimiento",
      x: "estudiantes_top10",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"},
      tip: true
    }),
    Plot.ruleX([0])
  ],
  x: {label: "Estudiantes en Top 10%"}
}))
```
