# Migración a Aplicación Web Estática con Observable Framework

Este documento describe cómo migrar la aplicación PAES 2026 Explorer de Streamlit a una aplicación web estática usando Observable Framework.

## Resumen Ejecutivo

| Aspecto | Actual (Streamlit) | Propuesto (Observable Framework) |
|---------|-------------------|----------------------------------|
| Backend | Python + Streamlit Cloud | Sin backend (100% estático) |
| Base de datos | DuckDB (34 MB) en servidor | Datos precomputados en JSON |
| Secciones | 5 tabs | 3 páginas enfocadas |
| Hosting | Streamlit Community Cloud | GitHub Pages (gratis, ilimitado) |
| Tamaño final | 34 MB + app | ~500 KB total |

## Secciones Post-Migración

| Sección | Descripción | Datos necesarios |
|---------|-------------|------------------|
| **Ranking** | Rankings de establecimientos con filtros | escuelas-ranking.json |
| **El Top 10** | Análisis del Top 10% nacional | brechas-top10.json |
| **La Ficha** | Búsqueda y ficha de establecimiento | escuelas-ranking.json |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                      BUILD TIME (GitHub Actions)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   paes.duckdb ──► Data Loaders (Python + DuckDB)                │
│                          │                                       │
│                          ▼                                       │
│              ┌──────────────────────┐                           │
│              │  Archivos JSON       │                           │
│              │  - escuelas.json     │                           │
│              │  - brechas.json      │                           │
│              │  - filtros.json      │                           │
│              └──────────────────────┘                           │
│                          │                                       │
│                          ▼                                       │
│              Observable Framework Build                          │
│                          │                                       │
│                          ▼                                       │
│                    dist/ (HTML + JS + datos)                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RUNTIME (Navegador)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Usuario ──► GitHub Pages ──► HTML/JS/JSON                     │
│                                     │                            │
│                                     ▼                            │
│                           JavaScript + Observable Plot           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura del Proyecto

```
paes-explorer/
├── src/
│   ├── index.md                    # Ranking (página principal)
│   ├── top.md                    # El Top 10 (Top 10%)
│   ├── ficha.md                    # La Ficha (búsqueda)
│   ├── data/
│   │   ├── escuelas-ranking.json.py
│   │   ├── brechas-top10.json.py
│   │   └── filtros.json.py
│   └── components/
│       └── colors.js
├── paes.duckdb                     # Solo para build
├── observablehq.config.js
└── package.json
```

---

## Data Loaders

### `src/data/escuelas-ranking.json.py`

Usado por **Ranking** y **La Ficha**.

```python
#!/usr/bin/env python3
"""Ranking de escuelas con métricas completas."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

WHERE_OFICIAL = """
    r.puntaje_nem > 0 AND r.puntaje_ranking > 0
    AND r.mate1_reg > 0 AND r.lectora_reg > 0
    AND r.rindio_anterior = false AND r.situacion_egreso = 1
"""

# Calcular umbral top 10%
p90 = con.execute(f"""
    SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2)
    FROM resultados_paes r WHERE {WHERE_OFICIAL}
""").fetchone()[0]

result = con.execute(f"""
    SELECT
        e.rbd,
        e.nombre as establecimiento,
        d.descripcion as dependencia,
        c.cod_region,
        c.region,
        c.comuna,
        e.latitud,
        e.longitud,
        COUNT(*) as cantidad,
        ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
        ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
        ROUND((AVG(r.lectora_reg) + AVG(r.mate1_reg)) / 2, 1) as prom_lect_mate,
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p25,
        ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as mediana,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p75,
        SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) as en_top10
    FROM resultados_paes r
    JOIN establecimientos e ON r.rbd = e.rbd
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
    WHERE {WHERE_OFICIAL}
    GROUP BY e.rbd, e.nombre, d.descripcion, c.cod_region, c.region, c.comuna, e.latitud, e.longitud
    HAVING COUNT(*) >= 5
    ORDER BY prom_lect_mate DESC
""").fetchall()

data = [
    {
        "rbd": r[0], "establecimiento": r[1], "dependencia": r[2],
        "cod_region": r[3], "region": r[4], "comuna": r[5],
        "lat": r[6], "lon": r[7], "cantidad": r[8],
        "prom_lectora": r[9], "prom_mate1": r[10], "prom_lect_mate": r[11],
        "p25": r[12], "mediana": r[13], "p75": r[14], "en_top10": r[15]
    }
    for r in result
]

json.dump(data, sys.stdout)
```

### `src/data/brechas-top10.json.py`

Usado por **El Top 10**.

```python
#!/usr/bin/env python3
"""Datos para análisis del Top 10% nacional."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

WHERE_OFICIAL = """
    r.puntaje_nem > 0 AND r.puntaje_ranking > 0
    AND r.mate1_reg > 0 AND r.lectora_reg > 0
    AND r.rindio_anterior = false AND r.situacion_egreso = 1
"""

# Umbrales
thresholds = con.execute(f"""
    SELECT
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2) as p90,
        PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2) as p80
    FROM resultados_paes r WHERE {WHERE_OFICIAL}
""").fetchone()

p90, p80 = thresholds

# Origen del top 10% por dependencia
origen_top10 = con.execute(f"""
    SELECT
        d.descripcion as dependencia,
        COUNT(*) as estudiantes,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as porcentaje
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE (r.lectora_reg + r.mate1_reg)/2 >= {p90} AND {WHERE_OFICIAL}
    GROUP BY d.descripcion
    ORDER BY estudiantes DESC
""").fetchall()

# Top escuelas con más estudiantes en el top 10%
escuelas_top10 = con.execute(f"""
    SELECT
        e.nombre as establecimiento,
        d.descripcion as dependencia,
        c.comuna,
        COUNT(*) as estudiantes_top10,
        (SELECT COUNT(*) FROM resultados_paes r2
         WHERE r2.rbd = e.rbd AND {WHERE_OFICIAL.replace('r.', 'r2.')}) as total_estudiantes
    FROM resultados_paes r
    JOIN establecimientos e ON r.rbd = e.rbd
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
    WHERE (r.lectora_reg + r.mate1_reg)/2 >= {p90} AND {WHERE_OFICIAL}
    GROUP BY e.rbd, e.nombre, d.descripcion, c.comuna
    ORDER BY estudiantes_top10 DESC
    LIMIT 100
""").fetchall()

# Probabilidad de top 10% por dependencia
prob_top10 = con.execute(f"""
    SELECT
        d.descripcion as dependencia,
        COUNT(*) as total,
        SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) as en_top10,
        ROUND(100.0 * SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_top10
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE {WHERE_OFICIAL}
    GROUP BY d.descripcion
    ORDER BY pct_top10 DESC
""").fetchall()

# Total en top 10%
total_top10 = con.execute(f"""
    SELECT COUNT(*) FROM resultados_paes r
    WHERE (r.lectora_reg + r.mate1_reg)/2 >= {p90} AND {WHERE_OFICIAL}
""").fetchone()[0]

result = {
    "umbrales": {"p90": round(p90, 0), "p80": round(p80, 0)},
    "total_top10": total_top10,
    "origen_top10": [
        {"dependencia": r[0], "estudiantes": r[1], "porcentaje": r[2]}
        for r in origen_top10
    ],
    "escuelas_top10": [
        {"establecimiento": r[0], "dependencia": r[1], "comuna": r[2],
         "estudiantes_top10": r[3], "total_estudiantes": r[4]}
        for r in escuelas_top10
    ],
    "prob_top10": [
        {"dependencia": r[0], "total": r[1], "en_top10": r[2], "pct_top10": r[3]}
        for r in prob_top10
    ]
}

json.dump(result, sys.stdout)
```

### `src/data/filtros.json.py`

Opciones para selectores.

```python
#!/usr/bin/env python3
"""Opciones para los selectores de filtros."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

# Orden geográfico norte-sur
ORDEN_REGIONES = {
    15: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 13: 7, 6: 8,
    7: 9, 16: 10, 8: 11, 9: 12, 14: 13, 10: 14, 11: 15, 12: 16
}

regiones = con.execute("""
    SELECT DISTINCT cod_region, region FROM comunas ORDER BY cod_region
""").fetchall()
regiones_ordenadas = sorted(regiones, key=lambda r: ORDEN_REGIONES.get(r[0], 99))

dependencias = con.execute("SELECT codigo, descripcion FROM ref_dependencia ORDER BY codigo").fetchall()

result = {
    "regiones": [{"codigo": r[0], "nombre": r[1]} for r in regiones_ordenadas],
    "dependencias": [{"codigo": r[0], "nombre": r[1]} for r in dependencias]
}

json.dump(result, sys.stdout)
```

---

## Páginas

### `src/index.md` (Ranking)

```markdown
---
title: PAES 2026 - Ranking
toc: false
---

# Ranking de Establecimientos

```js
const escuelas = await FileAttachment("data/escuelas-ranking.json").json();
const filtros = await FileAttachment("data/filtros.json").json();

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};
```

<div class="note">
💡 <strong>Nota metodológica</strong>: El DEMRE advierte que la PAES no fue diseñada para medir calidad educativa de establecimientos. Los rankings reflejan principalmente el nivel socioeconómico.
</div>

```js
const regionSel = view(Inputs.select(
  [null, ...filtros.regiones],
  {label: "Región", format: d => d ? d.nombre : "Todas"}
));

const depSel = view(Inputs.select(
  [null, ...filtros.dependencias],
  {label: "Dependencia", format: d => d ? d.nombre : "Todas"}
));

const orden = view(Inputs.radio(
  ["Mejor promedio", "Más estudiantes", "Más en Top 10%"],
  {value: "Mejor promedio", label: "Ordenar por"}
));

const topN = view(Inputs.range([10, 100], {value: 30, step: 10, label: "Mostrar"}));
```

```js
// Filtrar y ordenar
let datos = escuelas
  .filter(e => !regionSel || e.cod_region === regionSel.codigo)
  .filter(e => !depSel || e.dependencia === depSel.nombre);

if (orden === "Mejor promedio") datos.sort((a, b) => b.prom_lect_mate - a.prom_lect_mate);
else if (orden === "Más estudiantes") datos.sort((a, b) => b.cantidad - a.cantidad);
else datos.sort((a, b) => b.en_top10 - a.en_top10);

datos = datos.slice(0, topN);
```

```js
Inputs.table(datos, {
  columns: ["establecimiento", "dependencia", "comuna", "cantidad", "prom_lect_mate", "en_top10"],
  header: {
    establecimiento: "Establecimiento",
    dependencia: "Dependencia",
    comuna: "Comuna",
    cantidad: "Estudiantes",
    prom_lect_mate: "Prom. L+M",
    en_top10: "Top 10%"
  },
  sort: false
})
```

```js
Plot.plot({
  marginLeft: 280,
  height: Math.max(400, datos.length * 22),
  marks: [
    Plot.barX(datos, {
      y: "establecimiento",
      x: "prom_lect_mate",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```
```

### `src/top.md` (El Top 10)

```markdown
---
title: El Top 10 - Top 10%
toc: false
---

# El Top 10: ¿De dónde viene el Top 10%?

```js
const data = await FileAttachment("data/brechas-top10.json").json();

const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};
```

<div class="grid grid-cols-3">
  <div class="card">
    <h2>Umbral Top 10%</h2>
    <span class="big">${data.umbrales.p90} pts</span>
  </div>
  <div class="card">
    <h2>Umbral Top 20%</h2>
    <span class="big">${data.umbrales.p80} pts</span>
  </div>
  <div class="card">
    <h2>Estudiantes en Top 10%</h2>
    <span class="big">${data.total_top10.toLocaleString()}</span>
  </div>
</div>

## Origen del Top 10% por Dependencia

```js
const pctNoPagado = data.origen_top10
  .filter(d => d.dependencia !== 'Particular Pagado')
  .reduce((sum, d) => sum + d.porcentaje, 0);
```

<div class="tip">
<strong>${pctNoPagado.toFixed(1)}%</strong> del Top 10% NO viene de colegios particulares pagados
</div>

```js
Plot.plot({
  marginLeft: 200,
  height: 250,
  marks: [
    Plot.barX(data.origen_top10, {
      y: "dependencia",
      x: "estudiantes",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.text(data.origen_top10, {
      y: "dependencia",
      x: "estudiantes",
      text: d => `${d.porcentaje}%`,
      dx: 5,
      textAnchor: "start"
    }),
    Plot.ruleX([0])
  ]
})
```

## Probabilidad de estar en el Top 10% según Dependencia

```js
Plot.plot({
  marginLeft: 200,
  height: 250,
  marks: [
    Plot.barX(data.prob_top10, {
      y: "dependencia",
      x: "pct_top10",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.text(data.prob_top10, {
      y: "dependencia",
      x: "pct_top10",
      text: d => `${d.pct_top10}%`,
      dx: 5,
      textAnchor: "start"
    }),
    Plot.ruleX([0])
  ],
  x: {label: "% de estudiantes en Top 10%"}
})
```

## Escuelas con más estudiantes en el Top 10%

```js
Inputs.table(data.escuelas_top10.slice(0, 30), {
  columns: ["establecimiento", "dependencia", "comuna", "estudiantes_top10", "total_estudiantes"],
  header: {
    establecimiento: "Establecimiento",
    dependencia: "Dependencia",
    comuna: "Comuna",
    estudiantes_top10: "En Top 10%",
    total_estudiantes: "Total Est."
  }
})
```

```js
Plot.plot({
  height: 500,
  marginLeft: 280,
  marks: [
    Plot.barX(data.escuelas_top10.slice(0, 25), {
      y: "establecimiento",
      x: "estudiantes_top10",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```
```

### `src/ficha.md` (La Ficha)

```markdown
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
```

---

## Configuración

### `observablehq.config.js`

```javascript
export default {
  title: "PAES 2026",
  pages: [
    {name: "Ranking", path: "/"},
    {name: "El Top 10", path: "/top"},
    {name: "La Ficha", path: "/ficha"}
  ],
  theme: "light",
  base: "/paes2026/"
};
```

### `.github/workflows/deploy.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        run: pip install duckdb

      - run: npm ci
      - run: npm run build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

---

## Estimación de Tamaños

| Archivo | Contenido | Tamaño estimado |
|---------|-----------|-----------------|
| escuelas-ranking.json | ~3,000 escuelas | ~400 KB |
| brechas-top10.json | Top 10% + 100 escuelas | ~50 KB |
| filtros.json | Regiones + dependencias | ~3 KB |

**Total**: ~450 KB (vs 34 MB original)

---

## Comandos

```bash
# Crear proyecto
npx @observablehq/framework create paes-explorer

# Desarrollo local
npm run dev

# Build
npm run build

# Limpiar cache de data loaders
rm -rf .observablehq/cache/
```

---

## Referencias

- [Observable Framework](https://observablehq.com/framework/)
- [Data Loaders](https://observablehq.com/framework/data-loaders)
- [Observable Plot](https://observablehq.com/plot/)
- [Observable Inputs](https://observablehq.com/framework/inputs)
- [Deploying to GitHub Pages](https://observablehq.com/framework/deploying)
