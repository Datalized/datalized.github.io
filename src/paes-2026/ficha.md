---
title: La Ficha - Buscar Establecimiento
toc: false
style: styles.css
---

# La Ficha: Buscar Establecimiento

```js
const escuelas = FileAttachment("data/escuelas-ranking.json").json();
import { rankBadge, depBadge, scoreValue, top10Indicator, rankingAlign } from "./components/tableFormatters.js";

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};
```

<div class="filters">

```js
// Crear opciones para el datalist
const opciones = escuelas.map(d => `${d.establecimiento} - ${d.comuna}`);

const busquedaTexto = view(Inputs.text({
  placeholder: "Escribe el nombre del establecimiento...",
  datalist: opciones,
  label: "Buscar establecimiento"
}));
```

</div>

```js
// Buscar la escuela que coincide con el texto
const escuelaSeleccionada = escuelas.find(d =>
  `${d.establecimiento} - ${d.comuna}` === busquedaTexto
);
```

```js
if (escuelaSeleccionada) {
  const e = escuelaSeleccionada;

  display(html`
    <div class="school-header" style="border-left: 4px solid ${colores[e.dependencia]}">
      <h2>${e.establecimiento}</h2>
      <div class="school-meta">
        <span><strong>Comuna:</strong> ${e.comuna}</span>
        <span><strong>Región:</strong> ${e.region}</span>
        <span><strong>Dependencia:</strong> ${e.dependencia}</span>
        <span><strong>Estudiantes:</strong> ${e.cantidad}</span>
      </div>
    </div>
  `);

  display(html`
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Ranking Nacional</h3>
        <span class="value">#${e.rank_nacional}</span>
        <small>de ${escuelas.length.toLocaleString()}</small>
      </div>
      <div class="stat-card">
        <h3>Prom. Lectora</h3>
        <span class="value">${e.prom_lectora}</span>
      </div>
      <div class="stat-card">
        <h3>Prom. Mate 1</h3>
        <span class="value">${e.prom_mate1}</span>
      </div>
      <div class="stat-card">
        <h3>Prom. L+M</h3>
        <span class="value highlight">${e.prom_lect_mate}</span>
      </div>
    </div>
  `);

  display(html`
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Percentil 25</h3>
        <span class="value">${e.p25}</span>
      </div>
      <div class="stat-card">
        <h3>Mediana</h3>
        <span class="value">${e.mediana}</span>
      </div>
      <div class="stat-card">
        <h3>Percentil 75</h3>
        <span class="value">${e.p75}</span>
      </div>
      <div class="stat-card">
        <h3>En Top 10%</h3>
        <span class="value">${e.en_top10}</span>
        <small>${e.cantidad > 0 ? Math.round(e.en_top10 / e.cantidad * 100) : 0}%</small>
      </div>
    </div>
  `);

  const cercanas = escuelas
    .filter(x => x.comuna === e.comuna && x.rbd !== e.rbd)
    .slice(0, 10);

  if (cercanas.length > 0) {
    display(html`<h3 class="section-title">Comparación con otros establecimientos en ${e.comuna}</h3>`);

    const comparacion = [e, ...cercanas];
    display(resize((width) => Plot.plot({
      width,
      marginLeft: Math.min(250, width * 0.4),
      height: Math.max(280, comparacion.length * 28),
      style: {fontSize: "11px"},
      y: {label: null},
      marks: [
        Plot.barX(comparacion, {
          y: "establecimiento",
          x: "prom_lect_mate",
          fill: d => d.rbd === e.rbd ? "#1e293b" : colores[d.dependencia],
          sort: {y: "-x"},
          tip: true
        }),
        Plot.ruleX([0])
      ],
      x: {label: "Promedio Lectora + Matemática"}
    })));

    display(Inputs.table(cercanas, {
      columns: ["rank_nacional", "rank_comuna", "establecimiento", "dependencia", "cantidad", "prom_lect_mate", "en_top10"],
      header: {
        rank_nacional: "# Nac.",
        rank_comuna: "# Com.",
        establecimiento: "Establecimiento",
        dependencia: "Dependencia",
        cantidad: "Est.",
        prom_lect_mate: "Prom. L+M",
        en_top10: "Top 10%"
      },
      format: {
        rank_nacional: d => rankBadge(d),
        rank_comuna: d => rankBadge(d),
        establecimiento: d => html`<span class="school-name">${d}</span>`,
        dependencia: d => depBadge(d),
        prom_lect_mate: d => scoreValue(d),
        en_top10: (d, i, data) => top10Indicator(d, data[i].cantidad)
      },
      align: rankingAlign,
      select: false
    }));
  }
}
```
