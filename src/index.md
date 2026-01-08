---
title: PAES 2026 - Ranking
toc: false
---

# Ranking de Establecimientos

```js
const escuelas = await FileAttachment("data/escuelas-ranking.json").json();
const filtros = await FileAttachment("data/filtros.json").json();

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};
```

<div class="note">
<strong>Nota metodológica</strong>: El DEMRE advierte que la PAES no fue diseñada para medir calidad educativa de establecimientos. Los rankings reflejan principalmente el nivel socioeconómico.
</div>

```js
const regionSel = view(Inputs.select(
  [null, ...filtros.regiones],
  {label: "Región", format: d => d ? d.nombre : "Todas"}
));

const depSel = view(Inputs.select(
  [null, ...filtros.dependencias],
  {label: "Dependencia", format: d => d ? d.nombre : "Todas"}
));

const orden = view(Inputs.radio(
  ["Mejor promedio", "Más estudiantes", "Más en Top 10%"],
  {value: "Mejor promedio", label: "Ordenar por"}
));

const topN = view(Inputs.range([10, 100], {value: 30, step: 10, label: "Mostrar"}));
```

```js
// Filtrar y ordenar
let datos = escuelas
  .filter(e => !regionSel || e.cod_region === regionSel.codigo)
  .filter(e => !depSel || e.dependencia === depSel.nombre);

if (orden === "Mejor promedio") datos.sort((a, b) => b.prom_lect_mate - a.prom_lect_mate);
else if (orden === "Más estudiantes") datos.sort((a, b) => b.cantidad - a.cantidad);
else datos.sort((a, b) => b.en_top10 - a.en_top10);

datos = datos.slice(0, topN);
```

```js
Inputs.table(datos, {
  columns: ["establecimiento", "dependencia", "comuna", "cantidad", "prom_lect_mate", "en_top10"],
  header: {
    establecimiento: "Establecimiento",
    dependencia: "Dependencia",
    comuna: "Comuna",
    cantidad: "Estudiantes",
    prom_lect_mate: "Prom. L+M",
    en_top10: "Top 10%"
  },
  sort: false
})
```

```js
Plot.plot({
  marginLeft: 280,
  height: Math.max(400, datos.length * 22),
  marks: [
    Plot.barX(datos, {
      y: "establecimiento",
      x: "prom_lect_mate",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```
