---
title: PAES 2026 - Ranking
toc: true
style: styles.css
---

# Ranking de Establecimientos

```js
const escuelas = FileAttachment("data/escuelas-ranking.json").json();
const filtros = FileAttachment("data/filtros.json").json();
```

<div class="warning" label="Nota metodológica">
El DEMRE advierte que la PAES no fue diseñada para medir calidad educativa de establecimientos. Los rankings reflejan principalmente el nivel socioeconómico.
</div>

<div class="filters">

```js
const regionSel = view(Inputs.select(
  [null, ...filtros.regiones],
  {label: "Región", format: d => d ? d.nombre : "Todas"}
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
  .filter(e => !comunaSel || e.cod_comuna === comunaSel.codigo)
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
  width: {
    rank_nacional: 10,
    rank_comuna: 10,
    cantidad: 30,
    prom_lect_mate: 80,
    en_top10: 80,
    dependencia: 120,
    comuna: 100
  },
  height: 'auto',
  sort: false 
})
```
