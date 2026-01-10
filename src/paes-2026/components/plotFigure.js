// Componente para figuras con gráficos Plot
// Envuelve gráficos en estructura semántica con caption

import { html } from "npm:htl";

/**
 * Crea una figura con plot-container y figcaption
 * @param {Function} plotFn - Función que recibe width y retorna un Plot
 * @param {string} caption - Texto del caption (puede incluir HTML)
 * @param {Object} options - Opciones adicionales
 * @param {number} options.number - Número de figura (ej: 1 para "Figura 1:")
 * @returns {HTMLElement} Elemento figure con el gráfico
 */
export function plotFigure(plotFn, caption, options = {}) {
  const { number } = options;
  const prefix = number ? `<strong>Figura ${number}:</strong> ` : "";

  return html`<figure>
    <div class="plot-container">
      ${resize((width) => plotFn(width))}
    </div>
    <figcaption>${html([prefix + caption])}</figcaption>
  </figure>`;
}

/**
 * Crea una figura simple (sin resize) con plot-container y figcaption
 * @param {HTMLElement} plot - Elemento del gráfico ya renderizado
 * @param {string} caption - Texto del caption
 * @param {Object} options - Opciones adicionales
 * @param {number} options.number - Número de figura
 * @returns {HTMLElement} Elemento figure con el gráfico
 */
export function staticFigure(plot, caption, options = {}) {
  const { number } = options;
  const prefix = number ? `<strong>Figura ${number}:</strong> ` : "";

  return html`<figure>
    <div class="plot-container">
      ${plot}
    </div>
    <figcaption>${html([prefix + caption])}</figcaption>
  </figure>`;
}
