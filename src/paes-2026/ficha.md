---
title: Ficha colegios - Buscar Establecimiento
toc: false
style: styles.css
head: |
  <link rel="canonical" href="https://public.datalized.cl/paes-2026/ficha">
  <meta name="description" content="Busca cualquier establecimiento educacional y explora su desempeño en la PAES 2026. Promedios, distribución de puntajes y comparación comunal.">
  <meta property="og:title" content="PAES 2026 - Ficha colegios">
  <meta property="og:description" content="Busca y compara el desempeño de establecimientos en la PAES 2026.">
  <meta property="og:url" content="https://public.datalized.cl/paes-2026/ficha">
  <meta property="og:type" content="website">
---

```js
const escuelas = FileAttachment("data/escuelas-ranking.json").json();
const filtros = FileAttachment("data/filtros.json").json();
import { rankBadge, depBadge, scoreValue, top10Indicator, rankingAlign } from "./components/tableFormatters.js";
```

```js
const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};

// Leer parámetro RBD de la URL (después de que escuelas esté cargado)
const urlParams = new URLSearchParams(window.location.search);
const rbdParam = urlParams.get('rbd');
const rbdSeleccionado = rbdParam ? parseInt(rbdParam) : null;
const escuelaPreseleccionada = rbdSeleccionado ? escuelas.find(d => d.rbd === rbdSeleccionado) : null;
```

```js
// Si hay una escuela preseleccionada, mostrar su ficha
if (escuelaPreseleccionada) {
  const e = escuelaPreseleccionada;

  display(html`
    <nav style="margin-bottom: 1rem; font-size: 0.875rem;">
      <a href="./ficha" style="color: var(--datalized-teal);">← Volver al directorio</a>
    </nav>
  `);

  display(html`
    <div class="school-header" style="border-left: 4px solid ${colores[e.dependencia]}">
      <h1 style="margin-bottom: 0.5rem; font-size: 1.75rem;">${e.establecimiento}</h1>
      <div class="school-meta">
        <span><strong>RBD:</strong> ${e.rbd}</span>
        <span><strong>Comuna:</strong> ${e.comuna}</span>
        <span><strong>Región:</strong> ${e.region}</span>
        <span><strong>Dependencia:</strong> ${e.dependencia}</span>
        <span><strong>Estudiantes:</strong> ${e.cantidad}</span>
      </div>
    </div>
  `);

  display(html`<h2 class="section-title">Promedios por Prueba</h2>`);
  display(html`<p>Los promedios de puntajes obtenidos por los estudiantes del establecimiento en las pruebas obligatorias. El promedio Lectora + Matemática (L+M) es el indicador principal utilizado para el ranking.</p>`);

  display(html`
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Ranking Nacional</h3>
        <span class="value">#${e.rank_nacional}</span>
        <small>de ${escuelas.length.toLocaleString()}</small>
      </div>
      <div class="stat-card">
        <h3>Ranking Comunal</h3>
        <span class="value">#${e.rank_comuna}</span>
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

  display(html`<h2 class="section-title">Distribución de Puntajes</h2>`);
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
    display(html`<h2 class="section-title">Comparación con otros establecimientos en ${e.comuna}</h2>`);
    display(html`<p>Este gráfico compara el promedio Lectora + Matemática del establecimiento seleccionado (destacado en color verde) con otros establecimientos de la misma comuna.</p>`);

    const comparacion = [e, ...cercanas];
    display(html`
      <figure>
        <div class="plot-container">
          ${resize((width) => Plot.plot({
            width,
            marginLeft: Math.min(250, width * 0.4),
            marginRight: 50,
            height: Math.max(280, comparacion.length * 28),
            style: {fontSize: "11px"},
            y: {label: null},
            x: {axis: null},
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
              Plot.text(comparacion, {
                y: "establecimiento",
                x: "prom_lect_mate",
                text: d => d.prom_lect_mate,
                dx: 5,
                textAnchor: "start",
                fontSize: 10,
                fill: "currentColor"
              })
            ]
          }))}
        </div>
        <figcaption><strong>Figura 1:</strong> Comparación de promedios Lectora + Matemática con establecimientos de la misma comuna (barra verde = establecimiento actual)</figcaption>
      </figure>
    `);

    display(html`<h3>Tabla comparativa</h3>`);
    display(Inputs.table(comparacion.sort((a, b) => b.prom_lect_mate - a.prom_lect_mate), {
      columns: ["rank_comuna", "establecimiento", "dependencia", "prom_lect_mate", "cantidad", "en_top10", "rank_nacional"],
      header: {
        rank_comuna: html`<span title="Ranking dentro de la comuna">#</span>`,
        establecimiento: html`<span title="Haz clic para ver la ficha detallada">Establecimiento</span>`,
        dependencia: html`<span title="Tipo de administración del establecimiento">Dependencia</span>`,
        prom_lect_mate: html`<span title="Promedio en Competencia Lectora y Matemática 1">Prom. L+M</span>`,
        cantidad: html`<span title="Cantidad de estudiantes que rindieron la PAES">Est.</span>`,
        en_top10: html`<span title="Estudiantes en el Top 10% nacional">Top 10%</span>`,
        rank_nacional: html`<span title="Ranking nacional por promedio"># Nac.</span>`
      },
      format: {
        rank_comuna: d => rankBadge(d),
        rank_nacional: d => rankBadge(d),
        establecimiento: (d, i, data) => html`<a href="?rbd=${data[i].rbd}" class="school-name" style="color: var(--datalized-teal);">${d}</a>`,
        dependencia: d => depBadge(d),
        prom_lect_mate: d => d,
        en_top10: (d, i, data) => top10Indicator(d, data[i].cantidad)
      },
      width: {
        rank_comuna: 40,
        establecimiento: 160,
        dependencia: 100,
        prom_lect_mate: 70,
        cantidad: 50,
        en_top10: 60,
        rank_nacional: 50
      },
      rows: 100,
      height: 'auto',
      align: rankingAlign,
      select: false
    }));
  }
}
```

```js
// Si no hay escuela preseleccionada, mostrar el directorio
if (!escuelaPreseleccionada) {
  display(html`<h1>Directorio de Establecimientos</h1>`);
  display(html`<p>Busca cualquier establecimiento educacional y accede a su ficha detallada con desempeño en la PAES 2026. Haz clic en el nombre del establecimiento para ver promedios por prueba, distribución de puntajes y comparación comunal.</p>`);
}
```

<div class="filters">

```js
const busquedaTexto = escuelaPreseleccionada ? "" : view(Inputs.text({
  placeholder: "Escribe el nombre del establecimiento...",
  label: "Buscar"
}));

const regionSel = escuelaPreseleccionada ? null : view(Inputs.select(
  [null, ...filtros.regiones],
  {label: "Región", format: d => d ? d.nombre : "Todas"}
));

const depSel = escuelaPreseleccionada ? null : view(Inputs.select(
  [null, ...filtros.dependencias],
  {label: "Dependencia", format: d => d ? d.nombre : "Todas"}
));
```

</div>

```js
if (!escuelaPreseleccionada) {
  const escuelasFiltradas = escuelas.filter(d => {
    const matchBusqueda = !busquedaTexto ||
      d.establecimiento.toLowerCase().includes(busquedaTexto.toLowerCase()) ||
      d.comuna?.toLowerCase().includes(busquedaTexto.toLowerCase());
    const matchRegion = !regionSel || d.cod_region === regionSel.codigo;
    const matchDependencia = !depSel || d.dependencia === depSel.nombre;
    return matchBusqueda && matchRegion && matchDependencia;
  });

  display(html`<p style="color: var(--datalized-gray-light); margin-bottom: 1rem;">Mostrando <strong>${escuelasFiltradas.length.toLocaleString()}</strong> de ${escuelas.length.toLocaleString()} establecimientos</p>`);

  display(Inputs.table(escuelasFiltradas, {
    columns: ["rank_nacional", "establecimiento", "dependencia", "prom_lect_mate", "comuna", "region", "cantidad"],
    header: {
      rank_nacional: html`<span title="Ranking nacional por promedio Lectora + Matemática">#</span>`,
      establecimiento: html`<span title="Haz clic para ver la ficha detallada">Establecimiento</span>`,
      dependencia: html`<span title="Tipo de administración del establecimiento">Dependencia</span>`,
      prom_lect_mate: html`<span title="Promedio en Competencia Lectora y Matemática 1">Prom. L+M</span>`,
      comuna: html`<span title="Comuna donde se ubica el establecimiento">Comuna</span>`,
      region: html`<span title="Región del país">Región</span>`,
      cantidad: html`<span title="Cantidad de estudiantes que rindieron la PAES">Est.</span>`
    },
    format: {
      rank_nacional: d => rankBadge(d),
      establecimiento: (d, i, data) => html`<a href="?rbd=${data[i].rbd}" class="school-name" style="text-decoration: none; color: var(--datalized-teal);">${d}</a>`,
      dependencia: d => depBadge(d),
      prom_lect_mate: d => scoreValue(d)
    },
    width: {
      rank_nacional: 40,
      establecimiento: 180,
      dependencia: 110,
      prom_lect_mate: 80,
      comuna: 100,
      region: 120,
      cantidad: 50
    },
    rows: 20,
    align: {
      rank_nacional: "center",
      cantidad: "right",
      prom_lect_mate: "right"
    },
    select: false
  }));
}
```
