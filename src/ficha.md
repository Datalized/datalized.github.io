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

```js
const busqueda = view(Inputs.search(escuelas, {
  placeholder: "Buscar establecimiento por nombre o comuna...",
  columns: ["establecimiento", "comuna"],
  format: d => `${d.establecimiento} - ${d.comuna}`
}));
```

```js
if (busqueda.length > 0) {
  const e = busqueda[0];

  // Ranking nacional
  const rankNacional = escuelas.findIndex(x => x.rbd === e.rbd) + 1;

  display(html`
    <div class="card" style="border-left: 4px solid ${colores[e.dependencia]}">
      <h2>${e.establecimiento}</h2>
      <div class="grid grid-cols-2" style="gap: 1rem">
        <div><strong>Comuna:</strong> ${e.comuna}</div>
        <div><strong>Región:</strong> ${e.region}</div>
        <div><strong>Dependencia:</strong> ${e.dependencia}</div>
        <div><strong>Estudiantes:</strong> ${e.cantidad}</div>
      </div>
    </div>
  `);

  display(html`
    <div class="grid grid-cols-4" style="margin-top: 1rem">
      <div class="card">
        <h3>Ranking Nacional</h3>
        <span class="big">#${rankNacional}</span>
        <small>de ${escuelas.length}</small>
      </div>
      <div class="card">
        <h3>Prom. Lectora</h3>
        <span class="big">${e.prom_lectora}</span>
      </div>
      <div class="card">
        <h3>Prom. Mate 1</h3>
        <span class="big">${e.prom_mate1}</span>
      </div>
      <div class="card">
        <h3>Prom. L+M</h3>
        <span class="big">${e.prom_lect_mate}</span>
      </div>
    </div>
  `);

  display(html`
    <div class="grid grid-cols-4" style="margin-top: 1rem">
      <div class="card">
        <h3>Percentil 25</h3>
        <span class="big">${e.p25}</span>
      </div>
      <div class="card">
        <h3>Mediana</h3>
        <span class="big">${e.mediana}</span>
      </div>
      <div class="card">
        <h3>Percentil 75</h3>
        <span class="big">${e.p75}</span>
      </div>
      <div class="card">
        <h3>En Top 10%</h3>
        <span class="big">${e.en_top10}</span>
      </div>
    </div>
  `);

  // Escuelas cercanas (misma comuna)
  const cercanas = escuelas
    .filter(x => x.comuna === e.comuna && x.rbd !== e.rbd)
    .slice(0, 10);

  if (cercanas.length > 0) {
    display(html`<h3 style="margin-top: 2rem">Otros establecimientos en ${e.comuna}</h3>`);

    // Comparación visual
    const comparacion = [e, ...cercanas];
    display(Plot.plot({
      marginLeft: 250,
      height: Math.max(300, comparacion.length * 30),
      marks: [
        Plot.barX(comparacion, {
          y: "establecimiento",
          x: "prom_lect_mate",
          fill: d => d.rbd === e.rbd ? "#000" : colores[d.dependencia],
          sort: {y: "-x"}
        }),
        Plot.ruleX([0])
      ],
      x: {label: "Promedio Lectora + Matemática"}
    }));

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
