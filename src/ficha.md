---
title: La Ficha - Buscar Establecimiento
toc: false
---

# La Ficha: Buscar Establecimiento

```js
const escuelas = await FileAttachment("data/escuelas-ranking.json").json();

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};
```

<div class="search-box">

```js
const busqueda = view(Inputs.search(escuelas, {
  placeholder: "Buscar establecimiento por nombre o comuna...",
  columns: ["establecimiento", "comuna"],
  format: d => `${d.establecimiento} - ${d.comuna}`
}));
```

</div>

```js
if (busqueda.length > 0) {
  const e = busqueda[0];
  const rankNacional = escuelas.findIndex(x => x.rbd === e.rbd) + 1;

  display(html`
    <div class="school-header" style="border-left: 4px solid ${colores[e.dependencia]}">
      <h2 class="school-name">${e.establecimiento}</h2>
      <div class="school-meta">
        <span class="meta-item"><strong>Comuna:</strong> ${e.comuna}</span>
        <span class="meta-item"><strong>Región:</strong> ${e.region}</span>
        <span class="meta-item"><strong>Dependencia:</strong> ${e.dependencia}</span>
        <span class="meta-item"><strong>Estudiantes:</strong> ${e.cantidad}</span>
      </div>
    </div>
  `);

  display(html`
    <div class="grid grid-cols-4 metrics-grid">
      <div class="card metric-card">
        <h3>Ranking Nacional</h3>
        <span class="big">#${rankNacional}</span>
        <small class="metric-sub">de ${escuelas.length.toLocaleString()}</small>
      </div>
      <div class="card metric-card">
        <h3>Prom. Lectora</h3>
        <span class="big">${e.prom_lectora}</span>
      </div>
      <div class="card metric-card">
        <h3>Prom. Mate 1</h3>
        <span class="big">${e.prom_mate1}</span>
      </div>
      <div class="card metric-card">
        <h3>Prom. L+M</h3>
        <span class="big highlight">${e.prom_lect_mate}</span>
      </div>
    </div>
  `);

  display(html`
    <div class="grid grid-cols-4 metrics-grid">
      <div class="card metric-card">
        <h3>Percentil 25</h3>
        <span class="big">${e.p25}</span>
      </div>
      <div class="card metric-card">
        <h3>Mediana</h3>
        <span class="big">${e.mediana}</span>
      </div>
      <div class="card metric-card">
        <h3>Percentil 75</h3>
        <span class="big">${e.p75}</span>
      </div>
      <div class="card metric-card">
        <h3>En Top 10%</h3>
        <span class="big">${e.en_top10}</span>
        <small class="metric-sub">${e.cantidad > 0 ? Math.round(e.en_top10 / e.cantidad * 100) : 0}%</small>
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
      columns: ["establecimiento", "dependencia", "cantidad", "prom_lect_mate", "en_top10"],
      header: {
        establecimiento: "Establecimiento",
        dependencia: "Dependencia",
        cantidad: "Est.",
        prom_lect_mate: "Prom. L+M",
        en_top10: "Top 10%"
      }
    }));
  }
}
```
