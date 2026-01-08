---
title: La Crema - Top 10%
toc: false
---

# La Crema: ¿De dónde viene el Top 10%?

```js
const data = await FileAttachment("data/brechas-top10.json").json();

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Umbral Top 10%</h2>
    <span class="big">${data.umbrales.p90} pts</span>
  </div>
  <div class="card">
    <h2>Umbral Top 20%</h2>
    <span class="big">${data.umbrales.p80} pts</span>
  </div>
  <div class="card">
    <h2>Estudiantes en Top 10%</h2>
    <span class="big">${data.total_top10.toLocaleString()}</span>
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
Plot.plot({
  marginLeft: 200,
  height: 250,
  marks: [
    Plot.barX(data.origen_top10, {
      y: "dependencia",
      x: "estudiantes",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.text(data.origen_top10, {
      y: "dependencia",
      x: "estudiantes",
      text: d => `${d.porcentaje}%`,
      dx: 5,
      textAnchor: "start"
    }),
    Plot.ruleX([0])
  ]
})
```

## Probabilidad de estar en el Top 10% según Dependencia

```js
Plot.plot({
  marginLeft: 200,
  height: 250,
  marks: [
    Plot.barX(data.prob_top10, {
      y: "dependencia",
      x: "pct_top10",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.text(data.prob_top10, {
      y: "dependencia",
      x: "pct_top10",
      text: d => `${d.pct_top10}%`,
      dx: 5,
      textAnchor: "start"
    }),
    Plot.ruleX([0])
  ],
  x: {label: "% de estudiantes en Top 10%"}
})
```

## Escuelas con más estudiantes en el Top 10%

```js
Inputs.table(data.escuelas_top10.slice(0, 30), {
  columns: ["establecimiento", "dependencia", "comuna", "estudiantes_top10", "total_estudiantes"],
  header: {
    establecimiento: "Establecimiento",
    dependencia: "Dependencia",
    comuna: "Comuna",
    estudiantes_top10: "En Top 10%",
    total_estudiantes: "Total Est."
  }
})
```

```js
Plot.plot({
  height: 500,
  marginLeft: 280,
  marks: [
    Plot.barX(data.escuelas_top10.slice(0, 25), {
      y: "establecimiento",
      x: "estudiantes_top10",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```
