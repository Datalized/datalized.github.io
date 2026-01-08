---
title: PAES 2026 - Ranking
toc: true
---

# Ranking de Establecimientos

```js
import { initializeTWind } from "./components/tailwind.js";
const tw = initializeTWind({ invalidation });

const escuelas = await FileAttachment("data/escuelas-ranking.json").json();
const filtros = await FileAttachment("data/filtros.json").json();
```

<div class="${tw`bg-gradient-to-br from-amber-100 to-amber-50 border-l-4 border-amber-500 py-3 px-4 rounded-r-lg mb-6 text-sm w-full`}">
<strong>Nota metodológica</strong>: El DEMRE advierte que la PAES no fue diseñada para medir calidad educativa de establecimientos. Los rankings reflejan principalmente el nivel socioeconómico.
</div>

<div class="${tw`flex flex-wrap gap-x-8 gap-y-6 items-end p-5 bg-slate-100 rounded-xl mb-6`}">

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

</div>

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
  columns: ["rank_nacional", "rank_comuna", "establecimiento", "dependencia", "comuna", "cantidad", "prom_lect_mate", "en_top10"],
  header: {
    rank_nacional: "#",
    rank_comuna: "# Comuna",
    establecimiento: "Establecimiento",
    dependencia: "Dependencia",
    comuna: "Comuna",
    cantidad: "Est.",
    prom_lect_mate: "Prom. L+M",
    en_top10: "Top 10%"
  },
  sort: false
})
```
