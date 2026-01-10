---
title: PAES 2026 - Exploración de Datos
toc: false
style: styles.css
head: |
  <link rel="canonical" href="https://public.datalized.cl/paes-2026/">
  <meta name="description" content="Exploración del dataset PAES 2026. Estadísticas generales, distribuciones por prueba y análisis por dependencia.">
  <meta property="og:title" content="PAES 2026 - Exploración de Datos">
  <meta property="og:description" content="Exploración del dataset PAES 2026 con estadísticas y distribuciones.">
  <meta property="og:url" content="https://public.datalized.cl/paes-2026/">
  <meta property="og:type" content="website">
---

# Exploración del Dataset PAES 2026

Una mirada general a los datos de la **PAES 2026** (Prueba de Acceso a la Educación Superior) de Chile. Estos datos incluyen a todos los postulantes, sin aplicar los filtros metodológicos usados en el ranking.

```js
const data = FileAttachment("data/overview.json").json();

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};
```

## Indicadores Generales

<div class="stats-grid">
  <div class="stat-card">
    <h2>Total Postulantes</h2>
    <span class="value">${data.kpis.total_postulantes.toLocaleString("es-CL")}</span>
  </div>
  <div class="stat-card">
    <h2>Establecimientos</h2>
    <span class="value">${data.kpis.total_establecimientos.toLocaleString("es-CL")}</span>
  </div>
  <div class="stat-card">
    <h2>Puntaje Máximo</h2>
    <span class="value">1000</span>
    <small>Escala 100-1000</small>
  </div>
  <div class="stat-card">
    <h2>Pruebas Obligatorias</h2>
    <span class="value">2</span>
    <small>Lectora + Matemática 1</small>
  </div>
</div>

## Postulantes por Prueba

<figure>
  <div class="plot-container">
    ${resize((width) => Plot.plot({
      width,
      marginLeft: Math.min(120, width * 0.25),
      marginRight: 60,
      height: 200,
      style: {fontSize: "12px"},
      x: {axis: null},
      y: {label: null},
      marks: [
        Plot.barX(data.postulantes_por_prueba, {
          y: "prueba",
          x: "total",
          fill: "#457B9D",
          sort: {y: "-x"},
          tip: true
        }),
        Plot.text(data.postulantes_por_prueba, {
          y: "prueba",
          x: "total",
          text: d => d.total.toLocaleString("es-CL"),
          dx: 5,
          textAnchor: "start",
          fontSize: 11,
          fill: "currentColor"
        })
      ]
    }))}
  </div>
  <figcaption><strong>Figura 1:</strong> Cantidad de postulantes que rindieron cada prueba PAES 2026</figcaption>
</figure>

## Estadísticas por Prueba

```js
Inputs.table(data.stats_pruebas, {
  columns: ["prueba", "n", "promedio", "desviacion", "p25", "mediana", "p75", "p90", "puntaje_maximo"],
  header: {
    prueba: html`<span title="Nombre de la prueba PAES">Prueba</span>`,
    n: html`<span title="Cantidad de estudiantes que rindieron la prueba">Rindieron</span>`,
    promedio: html`<span title="Puntaje promedio obtenido">Promedio</span>`,
    desviacion: html`<span title="Desviación estándar de los puntajes">Desv. Est.</span>`,
    p25: html`<span title="Percentil 25: 25% obtuvo este puntaje o menos">P25</span>`,
    mediana: html`<span title="Percentil 50: valor central de la distribución">Mediana</span>`,
    p75: html`<span title="Percentil 75: 75% obtuvo este puntaje o menos">P75</span>`,
    p90: html`<span title="Percentil 90: umbral del Top 10%">P90</span>`,
    puntaje_maximo: html`<span title="Estudiantes que obtuvieron puntaje nacional (1000 pts)">Con 1000 pts</span>`
  },
  format: {
    n: d => d.toLocaleString("es-CL"),
    puntaje_maximo: d => d.toLocaleString("es-CL")
  },
  width: {
    prueba: 160,
    n: 90,
    puntaje_maximo: 90
  },
  select: false
})
```

## Puntajes Perfectos (1000 puntos)

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Estudiantes con puntaje nacional</h3>
    <figure>
      <div class="plot-container">
        ${resize((width) => Plot.plot({
          width,
          marginLeft: Math.min(120, width * 0.3),
          marginRight: 80,
          height: 200,
          style: {fontSize: "12px"},
          x: {axis: null},
          y: {label: null},
          marks: [
            Plot.barX(data.puntajes_maximos.filter(d => d.con_1000 > 0), {
              y: "prueba",
              x: "con_1000",
              fill: "#E63946",
              sort: {y: "-x"},
              tip: true
            }),
            Plot.text(data.puntajes_maximos.filter(d => d.con_1000 > 0), {
              y: "prueba",
              x: "con_1000",
              text: d => `${d.con_1000.toLocaleString("es-CL")} (${d.pct}%)`,
              dx: 5,
              textAnchor: "start",
              fontSize: 10,
              fill: "currentColor"
            })
          ]
        }))}
      </div>
      <figcaption><strong>Figura 2:</strong> Puntajes nacionales por prueba</figcaption>
    </figure>
  </div>
  <div class="card">
    <h3>Detalle puntajes perfectos</h3>
    ${Inputs.table(data.puntajes_maximos, {
      columns: ["prueba", "total", "con_1000", "pct"],
      header: {
        prueba: html`<span title="Nombre de la prueba PAES">Prueba</span>`,
        total: html`<span title="Cantidad de estudiantes que rindieron la prueba">Rindieron</span>`,
        con_1000: html`<span title="Estudiantes con puntaje nacional (1000 pts)">Con 1000</span>`,
        pct: html`<span title="Porcentaje que obtuvo puntaje nacional">% del total</span>`
      },
      format: {
        total: d => d.toLocaleString("es-CL"),
        con_1000: d => d.toLocaleString("es-CL"),
        pct: d => d + "%"
      },
      width: {
        prueba: 120,
        total: 80,
        con_1000: 70,
        pct: 70
      },
      select: false
    })}
  </div>
</div>

## Distribución de Puntajes

```js
const coloresPruebas = {
  'Competencia Lectora': '#457B9D',
  'Matemática 1': '#2A9D8F',
  'Matemática 2': '#E9C46A',
  'Historia y Cs. Sociales': '#E63946',
  'Ciencias': '#9B5DE5'
};
```

<div class="grid grid-cols-2">
  ${data.histogramas.map((h, i) => html`
    <div class="card">
      <h3>${h.prueba}</h3>
      <figure>
        <div class="plot-container">
          ${resize((width) => Plot.plot({
            width,
            height: 180,
            marginBottom: 35,
            style: {fontSize: "11px"},
            x: {label: null, tickFormat: d => d},
            y: {label: null, tickFormat: "s"},
            marks: [
              Plot.rectY(h.datos, {
                x1: "rango",
                x2: d => d.rango + 50,
                y: "frecuencia",
                fill: coloresPruebas[h.prueba] || "#94a3b8",
                fillOpacity: 0.7,
                tip: {
                  format: {
                    x1: d => `${d} - ${d + 49} pts`,
                    y: d => d.toLocaleString("es-CL") + " estudiantes"
                  }
                }
              }),
              Plot.ruleX([h.promedio], {stroke: "var(--theme-foreground)", strokeWidth: 2, strokeDasharray: "4,4"}),
              Plot.ruleX([h.p90], {stroke: "#E63946", strokeWidth: 2}),
              Plot.text([{x: h.promedio, label: `Prom: ${h.promedio}`}], {
                x: "x", y: 0, text: "label", dy: -8, fontSize: 10, fill: "currentColor", textAnchor: "middle"
              }),
              Plot.text([{x: h.p90, label: `Top 10%: ${h.p90}`}], {
                x: "x", y: 0, text: "label", dy: -20, fontSize: 10, fill: "#E63946", textAnchor: "middle"
              }),
              Plot.ruleY([0])
            ]
          }))}
        </div>
        <figcaption>Prom: ${h.promedio} · Top 10%: ${h.p90}+ pts</figcaption>
      </figure>
    </div>
  `)}
</div>

## Promedios por Dependencia

```js
const pruebasSel = ["Competencia Lectora", "Matemática 1", "Matemática 2", "Historia y Cs. Sociales", "Ciencias"];
const pruebaSelect = view(Inputs.radio(pruebasSel, {label: "Prueba:", value: "Competencia Lectora"}));
```

```js
const datosFiltrados = data.distribucion_dependencia.filter(d => d.prueba === pruebaSelect);
```

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Puntaje promedio por dependencia</h3>
    <figure>
      <div class="plot-container">
        ${resize((width) => Plot.plot({
          width,
          marginLeft: Math.min(200, width * 0.45),
          marginRight: 50,
          height: 200,
          style: {fontSize: "12px"},
          x: {axis: null},
          y: {label: null},
          marks: [
            Plot.barX(datosFiltrados, {
              y: "dependencia",
              x: "promedio",
              fill: d => colores[d.dependencia] || "#94a3b8",
              sort: {y: "-x"},
              tip: {
                format: {
                  y: true,
                  x: d => `Promedio: ${d} pts`
                }
              }
            }),
            Plot.text(datosFiltrados, {
              y: "dependencia",
              x: "promedio",
              text: d => d.promedio,
              dx: 5,
              textAnchor: "start",
              fontSize: 11,
              fill: "currentColor"
            })
          ]
        }))}
      </div>
      <figcaption><strong>Figura 5:</strong> ${pruebaSelect}</figcaption>
    </figure>
  </div>
  <div class="card">
    <h3>Detalle por dependencia</h3>
    ${Inputs.table(datosFiltrados, {
      columns: ["dependencia", "n", "promedio", "mediana", "desviacion"],
      header: {
        dependencia: html`<span title="Tipo de administración del establecimiento">Dependencia</span>`,
        n: html`<span title="Cantidad de estudiantes que rindieron">Rindieron</span>`,
        promedio: html`<span title="Puntaje promedio obtenido">Promedio</span>`,
        mediana: html`<span title="Percentil 50: valor central">Mediana</span>`,
        desviacion: html`<span title="Desviación estándar">Desv. Est.</span>`
      },
      format: {
        n: d => d.toLocaleString("es-CL")
      },
      width: {
        dependencia: 140,
        n: 80
      },
      select: false
    })}
  </div>
</div>

## Por Rama Educacional

```js
const ramaMetrica = view(Inputs.radio(["Prom. Lectora", "Prom. Matemática 1"], {label: "Métrica:", value: "Prom. Lectora"}));
```

```js
const ramaData = data.distribucion_rama.map(d => ({
  ...d,
  valor: ramaMetrica === "Prom. Lectora" ? d.prom_lectora : d.prom_mate1
}));
```

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Puntaje promedio por rama</h3>
    <figure>
      <div class="plot-container">
        ${resize((width) => Plot.plot({
          width,
          marginLeft: Math.min(180, width * 0.45),
          marginRight: 50,
          height: 160,
          style: {fontSize: "12px"},
          x: {axis: null},
          y: {label: null},
          marks: [
            Plot.barX(ramaData, {
              y: "rama",
              x: "valor",
              fill: d => d.rama === "Humanista-Científico" ? "#457B9D" : d.rama === "Técnico-Profesional" ? "#2A9D8F" : "#94a3b8",
              sort: {y: "-x"},
              tip: true
            }),
            Plot.text(ramaData, {
              y: "rama",
              x: "valor",
              text: d => d.valor,
              dx: 5,
              textAnchor: "start",
              fontSize: 11,
              fill: "currentColor"
            })
          ]
        }))}
      </div>
      <figcaption><strong>Figura 6:</strong> ${ramaMetrica} por rama educacional</figcaption>
    </figure>
  </div>
  <div class="card">
    <h3>Detalle por rama</h3>
    ${Inputs.table(data.distribucion_rama, {
      columns: ["rama", "n", "prom_lectora", "prom_mate1"],
      header: {
        rama: html`<span title="Rama educacional del establecimiento">Rama</span>`,
        n: html`<span title="Cantidad de estudiantes que rindieron">Rindieron</span>`,
        prom_lectora: html`<span title="Promedio en Competencia Lectora">Prom. Lectora</span>`,
        prom_mate1: html`<span title="Promedio en Matemática 1">Prom. Mate 1</span>`
      },
      format: {
        n: d => d.toLocaleString("es-CL")
      },
      width: {
        rama: 140,
        n: 80
      },
      select: false
    })}
  </div>
</div>

<div class="note">
Estos datos muestran el dataset completo sin los filtros metodológicos aplicados en el <a href="./ranking">ranking</a> y el análisis del <a href="./top">Top 10%</a>. Para entender los criterios de filtrado, consulta la <a href="./metodologia">metodología</a>.
</div>
