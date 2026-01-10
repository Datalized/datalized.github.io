// Componente reutilizable para stat-cards
// Crea tarjetas de estadísticas con estilo consistente

import { html } from "npm:htl";

/**
 * Crea una tarjeta de estadística individual
 * @param {string} title - Título de la tarjeta
 * @param {string|number} value - Valor principal a mostrar
 * @param {Object} options - Opciones adicionales
 * @param {string} options.subtitle - Texto pequeño debajo del valor
 * @param {boolean} options.highlight - Si el valor debe tener color destacado
 * @param {string} options.level - Nivel del título: "h2" o "h3" (default: "h3")
 * @returns {HTMLElement} Elemento HTML de la tarjeta
 */
export function statCard(title, value, options = {}) {
  const { subtitle, highlight = false, level = "h3" } = options;
  const valueClass = highlight ? "value highlight" : "value";

  const titleEl = level === "h2"
    ? html`<h2>${title}</h2>`
    : html`<h3>${title}</h3>`;

  return html`<div class="stat-card">
    ${titleEl}
    <span class="${valueClass}">${value}</span>
    ${subtitle ? html`<small>${subtitle}</small>` : ""}
  </div>`;
}

/**
 * Crea un grid de tarjetas de estadísticas
 * @param {Array} cards - Array de configuraciones de tarjetas
 * @param {string} cards[].title - Título de la tarjeta
 * @param {string|number} cards[].value - Valor principal
 * @param {string} cards[].subtitle - Texto pequeño (opcional)
 * @param {boolean} cards[].highlight - Si destacar el valor (opcional)
 * @param {string} cards[].level - Nivel del título (opcional)
 * @returns {HTMLElement} Elemento HTML del grid
 */
export function statsGrid(cards) {
  return html`<div class="stats-grid">
    ${cards.map(card => statCard(card.title, card.value, {
      subtitle: card.subtitle,
      highlight: card.highlight,
      level: card.level
    }))}
  </div>`;
}
