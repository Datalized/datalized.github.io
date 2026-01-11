// Componente para visualizar distribución de puntajes con histogramas
import { html } from "npm:htl";
import * as Plot from "npm:@observablehq/plot";

const BIN_SIZE = 20;

/**
 * Crea un histograma a partir de bins pre-computados
 * @param {Array} bins - Array de [bin_inicio, cantidad] pares
 * @param {Object} options - Opciones de visualización
 * @param {string} options.title - Título del gráfico
 * @param {string} options.color - Color de las barras
 * @param {number} options.schoolMedian - Mediana del establecimiento (línea vertical)
 * @param {number} options.nationalMedian - Mediana nacional (línea punteada)
 * @param {number} options.p90 - Umbral top 10% (línea roja)
 * @param {function} options.resize - Función resize de Observable
 * @returns {HTMLElement} Elemento figure con el histograma
 */
export function scoreHistogram(bins, options = {}) {
  const {
    title = "Distribución",
    color = "var(--datalized-teal)",
    schoolMedian = null,
    nationalMedian = null,
    p90 = null,
    resize
  } = options;

  if (!bins || bins.length === 0) {
    return html`<div class="note">Sin datos suficientes</div>`;
  }

  const data = bins.map(([bin, count]) => ({ bin, count }));
  const maxCount = Math.max(...data.map(d => d.count));

  const createPlot = (width) => Plot.plot({
    width,
    height: 180,
    marginBottom: 35,
    marginLeft: 40,
    marginRight: 10,
    style: { fontSize: "10px" },
    x: {
      label: "Puntaje",
      tickFormat: d => d,
      ticks: 5
    },
    y: {
      label: "Estudiantes",
      tickFormat: "d",
      domain: [0, maxCount * 1.1]
    },
    marks: [
      Plot.rectY(data, {
        x1: "bin",
        x2: d => d.bin + BIN_SIZE,
        y: "count",
        fill: color,
        fillOpacity: 0.75,
        tip: {
          format: {
            x1: d => `${d} - ${d + BIN_SIZE - 1} pts`,
            y: d => `${d} estudiantes`
          }
        }
      }),
      // Línea de referencia: mediana del establecimiento
      schoolMedian ? Plot.ruleX([schoolMedian], {
        stroke: "var(--datalized-teal)",
        strokeWidth: 2,
        strokeOpacity: 0.9
      }) : null,
      // Línea de referencia: mediana nacional
      nationalMedian ? Plot.ruleX([nationalMedian], {
        stroke: "var(--theme-foreground-muted)",
        strokeWidth: 1.5,
        strokeDasharray: "4,3"
      }) : null,
      // Línea de referencia: umbral top 10%
      p90 ? Plot.ruleX([p90], {
        stroke: "#E63946",
        strokeWidth: 2,
        strokeOpacity: 0.8
      }) : null,
      Plot.ruleY([0])
    ].filter(Boolean)
  });

  return html`
    <figure style="margin: 0;">
      <figcaption style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.85rem;">${title}</figcaption>
      <div class="plot-container">
        ${resize ? resize((width) => createPlot(width)) : createPlot(300)}
      </div>
    </figure>
  `;
}

/**
 * Crea un grid de 3 histogramas para L+M, Lectora y Matemática
 * @param {Object} dist - Objeto con {lm, l, m} arrays de bins
 * @param {Object} escuela - Datos del establecimiento
 * @param {Object} options - Opciones adicionales
 * @param {number} options.p90 - Umbral top 10% nacional
 * @param {number} options.nationalMedian - Mediana nacional
 * @param {function} options.resize - Función resize de Observable
 * @returns {HTMLElement} Grid con los 3 histogramas
 */
export function distribucionHistogramas(dist, escuela, options = {}) {
  const { p90 = 658, nationalMedian = 524, resize } = options;

  return html`
    <div class="grid grid-cols-3">
      <div class="card">
        ${scoreHistogram(dist.lm, {
          title: "Promedio Lectora + Matemática",
          color: "var(--datalized-teal)",
          schoolMedian: escuela.mediana,
          nationalMedian,
          p90,
          resize
        })}
        <small style="color: var(--theme-foreground-muted); font-size: 0.7rem;">
          Verde: mediana escuela · Gris: nacional · Rojo: top 10%
        </small>
      </div>
      <div class="card">
        ${scoreHistogram(dist.l, {
          title: "Competencia Lectora",
          color: "#457B9D",
          schoolMedian: escuela.prom_lectora,
          resize
        })}
      </div>
      <div class="card">
        ${scoreHistogram(dist.m, {
          title: "Matemática 1",
          color: "#2A9D8F",
          schoolMedian: escuela.prom_mate1,
          resize
        })}
      </div>
    </div>
  `;
}

/**
 * Calcula estadísticas adicionales desde los bins
 * @param {Array} bins - Array de [bin_inicio, cantidad]
 * @param {number} p90 - Umbral top 10%
 * @returns {Object} Estadísticas calculadas
 */
export function calcularEstadisticasDistribucion(bins, p90 = 658) {
  if (!bins || bins.length === 0) return null;

  const total = bins.reduce((sum, [_, cnt]) => sum + cnt, 0);
  const enTop10 = bins
    .filter(([bin, _]) => bin >= p90)
    .reduce((sum, [_, cnt]) => sum + cnt, 0);
  const bajo400 = bins
    .filter(([bin, _]) => bin < 400)
    .reduce((sum, [_, cnt]) => sum + cnt, 0);

  return {
    total,
    enTop10,
    pctTop10: total > 0 ? Math.round(enTop10 / total * 100) : 0,
    bajo400,
    pctBajo400: total > 0 ? Math.round(bajo400 / total * 100) : 0
  };
}
