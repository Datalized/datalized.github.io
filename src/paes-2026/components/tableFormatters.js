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
