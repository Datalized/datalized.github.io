---
title: La Ficha - Buscar Establecimiento
toc: false
style: styles.css
---

# La Ficha: Buscar Establecimiento

Busca cualquier establecimiento educacional y explora su desempeño en la PAES 2026. Aquí encontrarás métricas clave como promedios por prueba, distribución de puntajes y posición en rankings nacionales y comunales.

Utiliza el buscador para encontrar tu colegio, liceo o escuela de interés.

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

  display(html`<h3 class="section-title">Promedios por Prueba</h3>`);
  display(html`<p>Los promedios de puntajes obtenidos por los estudiantes del establecimiento en las pruebas obligatorias. El promedio Lectora + Matemática (L+M) es el indicador principal utilizado para el ranking.</p>`);

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

  display(html`<h3 class="section-title">Distribución de Puntajes</h3>`);
  display(html`<p>La distribución de puntajes muestra cómo varían los resultados dentro del establecimiento. El percentil 25 indica que el 25% de estudiantes obtuvo ese puntaje o menos, la mediana (percentil 50) representa el valor central, y el percentil 75 muestra que el 75% obtuvo ese puntaje o menos.</p>`);

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
    display(html`<p>Este gráfico compara el promedio Lectora + Matemática del establecimiento seleccionado (destacado en color oscuro) con otros establecimientos de la misma comuna. Permite visualizar el posicionamiento relativo dentro del contexto comunal.</p>`);

    const comparacion = [e, ...cercanas];
    display(html`
      <figure>
        <div class="plot-container">
          ${resize((width) => Plot.plot({
            width,
            marginLeft: Math.min(250, width * 0.4),
            height: Math.max(280, comparacion.length * 28),
            style: {fontSize: "11px"},
            y: {label: null},
            x: {label: "Promedio Lectora + Matemática", grid: true},
            marks: [
              Plot.barX(comparacion, {
                y: "establecimiento",
                x: "prom_lect_mate",
                fill: d => d.rbd === e.rbd ? "var(--datalized-teal)" : "#94a3b8",
                sort: {y: "-x"},
                tip: {
                  format: {
                    y: true,
                    x: d => `${d} puntos promedio`
                  }
                }
              }),
              Plot.ruleX([0])
            ]
          }))}
        </div>
        <figcaption><strong>Figura 1:</strong> Comparación de promedios Lectora + Matemática con establecimientos de la misma comuna (barra verde = establecimiento seleccionado)</figcaption>
      </figure>
    `);

    display(Inputs.table(comparacion.sort((a, b) => b.prom_lect_mate - a.prom_lect_mate), {
      columns: ["rank_nacional", "rank_comuna", "establecimiento", "dependencia", "cantidad", "prom_lect_mate", "en_top10"],
      header: {
        rank_comuna: "# Com.",
        rank_nacional: "# Nac.",
        establecimiento: "Establecimiento",
        dependencia: "Dependencia",
        cantidad: "Est.",
        prom_lect_mate: "Prom. L+M",
        en_top10: "Top 10%"
      },
      format: {
        rank_comuna: d => rankBadge(d),
        rank_nacional: d => rankBadge(d),
        establecimiento: d => html`<span class="school-name">${d}</span>`,
        dependencia: d => depBadge(d),
        prom_lect_mate: d => d,
        en_top10: (d, i, data) => data[i].cantidad
      },
      width: {
        rank_nacional: 40,
        rank_comuna: 60,
        cantidad: 80,
        prom_lect_mate: 80,
        en_top10: 80,
        dependencia: 110,
        comuna: 100
      },
      rows: 100,
      height: 'auto',
      align: rankingAlign,
      select: false
    }));
  }
}
```
