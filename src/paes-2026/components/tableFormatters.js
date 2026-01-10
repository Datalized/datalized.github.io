// Helpers para formatear celdas de Inputs.table
// Retornan elementos HTML para usar con la opción `format`

import { html } from "npm:htl";

export function rankBadge(rank) {
    const cls = rank === 1 ? "gold" : rank === 2 ? "silver" : rank === 3 ? "bronze" : "normal";
    return html`<span class="rank-badge ${cls}">${rank}</span>`;
}

export function depBadge(dep) {
    const clsMap = {
        "Particular Pagado": "particular-pagado",
        "Particular Subvencionado": "particular-subvencionado",
        "Municipal": "municipal",
        "SLEP": "slep",
        "Serv. Local Educación": "slep",
        "Administración Delegada": "admin-delegada",
        "Corp. Administración Delegada": "admin-delegada"
    };
    const cls = clsMap[dep] || "particular-subvencionado";
    const shortMap = {
        "Particular Subvencionado": "Part. Subv.",
        "Particular Pagado": "Part. Pagado",
        "Administración Delegada": "Adm. Deleg.",
        "Corp. Administración Delegada": "Corp. Adm. Deleg.",
        "Serv. Local Educación": "SLEP"
    };
    const short = shortMap[dep] || dep;
    return html`<span class="dep-badge ${cls}">${short}</span>`;
}

export function scoreValue(score) {
    if (score == null || isNaN(score)) return html`<span class="score-value">-</span>`;
    const cls = score >= 850 ? "excellent" : score >= 750 ? "good" : score >= 650 ? "moderate" : "normal";
    return html`<span class="score-value ${cls}">${score.toLocaleString("es-CL", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}</span>`;
}

export function top10Indicator(value, total) {
    const pct = total > 0 ? (value / total) * 100 : 0;
    const cls = pct >= 50 ? "excellent" : pct >= 25 ? "good" : pct >= 10 ? "moderate" : "low";
    return html`<div class="top10-indicator">
    <div class="top10-bar"><div class="top10-bar-fill ${cls}" style="width: ${Math.min(pct, 100)}%"></div></div>
    <span class="top10-value">${value}</span>
  </div>`;
}

// Configuración común de formato para tablas de ranking
export const rankingFormat = {
    rank_nacional: d => rankBadge(d),
    rank_comuna: d => rankBadge(d),
    establecimiento: d => html`<span class="school-name">${d}</span>`,
    dependencia: d => depBadge(d),
    prom_lect_mate: d => d
};

// Configuración común de alineación
export const rankingAlign = {
    rank_nacional: "center",
    rank_comuna: "center",
    rank_top10: "center",
    cantidad: "right",
    prom_lect_mate: "right",
    en_top10: "right",
    estudiantes_top10: "right",
    total_estudiantes: "right"
};

// Headers de tabla con tooltips explicativos
export const tableHeaders = {
    rbd: html`<span title="Rol Base de Datos del establecimiento">RBD</span>`,
    rank_nacional: html`<span title="Ranking nacional por promedio Lectora + Matemática">#</span>`,
    rank_comuna: html`<span title="Ranking dentro de la comuna"># Com.</span>`,
    rank_top10: html`<span title="Ranking por cantidad de estudiantes en Top 10%">#</span>`,
    establecimiento: html`<span title="Nombre del establecimiento educacional">Establecimiento</span>`,
    dependencia: html`<span title="Tipo de administración del establecimiento">Dependencia</span>`,
    prom_lect_mate: html`<span title="Promedio en Competencia Lectora y Matemática 1">Prom. L+M</span>`,
    prom_lectora: html`<span title="Promedio en Competencia Lectora">Prom. Lectora</span>`,
    prom_mate1: html`<span title="Promedio en Matemática 1">Prom. Mate 1</span>`,
    comuna: html`<span title="Comuna donde se ubica el establecimiento">Comuna</span>`,
    region: html`<span title="Región del país">Región</span>`,
    cantidad: html`<span title="Cantidad de estudiantes que rindieron la PAES">Est.</span>`,
    en_top10: html`<span title="Estudiantes en el Top 10% nacional">Top 10%</span>`,
    estudiantes_top10: html`<span title="Cantidad de estudiantes en el Top 10% nacional">Top 10%</span>`,
    total_estudiantes: html`<span title="Total de estudiantes que rindieron la PAES">Total</span>`,
    // Stats por prueba
    n: html`<span title="Cantidad de estudiantes que rindieron la prueba">Rindieron</span>`,
    promedio: html`<span title="Puntaje promedio obtenido">Promedio</span>`,
    desviacion: html`<span title="Desviación estándar de los puntajes">Desv. Est.</span>`,
    mediana: html`<span title="Percentil 50: valor central de la distribución">Mediana</span>`,
    p25: html`<span title="Percentil 25: 25% obtuvo este puntaje o menos">P25</span>`,
    p75: html`<span title="Percentil 75: 75% obtuvo este puntaje o menos">P75</span>`,
    p90: html`<span title="Percentil 90: umbral del Top 10%">P90</span>`,
    puntaje_maximo: html`<span title="Estudiantes que obtuvieron puntaje nacional (1000 pts)">Con 1000 pts</span>`
};
