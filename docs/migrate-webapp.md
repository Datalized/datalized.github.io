# Migración a Aplicación Web Estática con Observable Framework

Este documento describe cómo migrar la aplicación PAES 2026 Explorer de Streamlit a una aplicación web estática usando Observable Framework.

## Resumen Ejecutivo

| Aspecto | Actual (Streamlit) | Propuesto (Observable Framework) |
|---------|-------------------|----------------------------------|
| Backend | Python + Streamlit Cloud | Sin backend (100% estático) |
| Base de datos | DuckDB (34 MB) en servidor | Datos precomputados en JSON/Parquet |
| Procesamiento | Queries en cada request | Todo precomputado en build time |
| Hosting | Streamlit Community Cloud | GitHub Pages (gratis, ilimitado) |
| Tamaño final | 34 MB + app | ~3-5 MB total |

## ¿Por qué migrar?

### Ventajas de Observable Framework

1. **Carga instantánea**: Datos precomputados = sin esperas
2. **Sin servidor**: GitHub Pages es gratis e ilimitado
3. **Escalabilidad infinita**: CDN global, sin límites de concurrencia
4. **Mantenimiento cero**: Sin base de datos que mantener en producción
5. **SEO friendly**: HTML estático indexable

### Limitaciones actuales de Streamlit

- Límites de memoria y conexiones en Streamlit Cloud
- Latencia en cada interacción (round-trip al servidor)
- Base de datos debe estar disponible en runtime

---

## Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────────┐
│                      BUILD TIME (GitHub Actions)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   paes.duckdb ──► Data Loaders (Python + DuckDB)                │
│                          │                                       │
│                          ▼                                       │
│              ┌──────────────────────┐                           │
│              │  Archivos estáticos  │                           │
│              │  - resumen.json      │                           │
│              │  - escuelas.json     │                           │
│              │  - histograma.json   │                           │
│              │  - regiones.json     │                           │
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
│                           ┌─────────────────┐                   │
│                           │  JavaScript     │                   │
│                           │  (filtros,      │                   │
│                           │   ordenamiento) │                   │
│                           └─────────────────┘                   │
│                                     │                            │
│                                     ▼                            │
│                           ┌─────────────────┐                   │
│                           │ Observable Plot │                   │
│                           │ Visualizaciones │                   │
│                           └─────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Punto clave**: DuckDB solo se usa en **build time** para generar los datos. En el navegador solo hay JavaScript puro y Observable Plot.

---

## Tecnologías

### 1. Observable Framework

[Observable Framework](https://observablehq.com/framework/) es un generador de sitios estáticos para aplicaciones de datos.

**Características:**
- Data loaders que ejecutan en build time (Python, R, Shell, etc.)
- Markdown reactivo con bloques de código JavaScript
- Observable Plot integrado para visualizaciones
- Deploy directo a GitHub Pages

**Instalación:**
```bash
# Crear proyecto
npx @observablehq/framework create paes-explorer
cd paes-explorer

# Estructura
paes-explorer/
├── src/
│   ├── index.md              # Página principal
│   ├── data/
│   │   └── resumen.json.py   # Data loader (genera JSON)
│   └── components/
├── observablehq.config.js
└── package.json
```

### 2. Data Loaders (Build Time con DuckDB)

Los data loaders son scripts que generan archivos estáticos durante el build. Pueden usar cualquier lenguaje.

**Ventajas:**
- Precomputan todas las agregaciones pesadas
- El usuario recibe datos listos para mostrar
- La base de datos nunca se expone al público
- Cache automático entre builds

**Convención de nombres:**
```
resumen.json.py    → genera → resumen.json
escuelas.csv.py    → genera → escuelas.csv
histograma.json.sh → genera → histograma.json
```

### 3. Observable Plot (Visualizaciones)

[Observable Plot](https://observablehq.com/plot/) es una librería de visualización declarativa incluida en Framework.

```javascript
Plot.plot({
  marks: [
    Plot.barY(data, {x: "categoria", y: "valor", fill: "grupo"})
  ]
})
```

---

## Plan de Migración

### Estructura del Proyecto

```
paes-explorer/
├── src/
│   ├── index.md                    # Resumen
│   ├── establecimientos.md         # Rankings
│   ├── buscar.md                   # Buscar escuela
│   ├── regiones.md                 # Análisis regional
│   ├── brechas.md                  # Análisis de brechas
│   ├── data/
│   │   ├── resumen.json.py
│   │   ├── dependencias.json.py
│   │   ├── escuelas-ranking.json.py
│   │   ├── histograma-lectora.json.py
│   │   ├── histograma-mate.json.py
│   │   ├── regiones.json.py
│   │   ├── comunas-top.json.py
│   │   ├── brechas-top10.json.py
│   │   └── filtros.json.py         # Opciones para selectores
│   └── components/
│       └── colors.js               # Paleta de colores
├── paes.duckdb                     # Solo para build
├── observablehq.config.js
└── package.json
```

### Data Loaders

#### `src/data/resumen.json.py`
```python
#!/usr/bin/env python3
"""Estadísticas generales para la página de resumen."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

# Filtros oficiales (mismos que app.py)
WHERE_OFICIAL = """
    r.puntaje_nem > 0
    AND r.puntaje_ranking > 0
    AND r.mate1_reg > 0
    AND r.lectora_reg > 0
    AND r.rindio_anterior = false
    AND r.situacion_egreso = 1
"""

# Totales generales
totales = con.execute(f"""
    SELECT
        COUNT(*) as total,
        COUNT(lectora_reg) as rindieron_lectora,
        COUNT(mate1_reg) as rindieron_mate1,
        ROUND(AVG(lectora_reg), 1) as prom_lectora,
        ROUND(AVG(mate1_reg), 1) as prom_mate1,
        ROUND(AVG(puntaje_nem), 1) as prom_nem
    FROM resultados_paes r
    WHERE {WHERE_OFICIAL}
""").fetchone()

# Por dependencia
por_dependencia = con.execute(f"""
    SELECT
        d.descripcion as dependencia,
        COUNT(*) as cantidad,
        ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
        ROUND(AVG(r.mate1_reg), 1) as prom_mate1
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE {WHERE_OFICIAL}
    GROUP BY d.descripcion
    ORDER BY cantidad DESC
""").fetchall()

# Por rama
por_rama = con.execute(f"""
    SELECT
        rm.descripcion as rama,
        COUNT(*) as cantidad
    FROM resultados_paes r
    JOIN ref_rama rm ON r.rama = rm.codigo
    WHERE {WHERE_OFICIAL}
    GROUP BY rm.descripcion
    ORDER BY cantidad DESC
""").fetchall()

result = {
    "totales": {
        "total": totales[0],
        "rindieron_lectora": totales[1],
        "rindieron_mate1": totales[2],
        "prom_lectora": totales[3],
        "prom_mate1": totales[4],
        "prom_nem": totales[5]
    },
    "por_dependencia": [
        {"dependencia": r[0], "cantidad": r[1], "prom_lectora": r[2], "prom_mate1": r[3]}
        for r in por_dependencia
    ],
    "por_rama": [
        {"rama": r[0], "cantidad": r[1]}
        for r in por_rama
    ]
}

json.dump(result, sys.stdout)
```

#### `src/data/histograma-lectora.json.py`
```python
#!/usr/bin/env python3
"""Datos pre-binneados para histograma de Lectora."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

WHERE_OFICIAL = """
    r.puntaje_nem > 0 AND r.rindio_anterior = false AND r.situacion_egreso = 1
"""

# Pre-calcular bins del histograma (evita enviar 200k+ puntos)
result = con.execute(f"""
    SELECT
        d.descripcion as dependencia,
        FLOOR(r.lectora_reg / 20) * 20 as bin_start,
        COUNT(*) as count
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE {WHERE_OFICIAL} AND r.lectora_reg IS NOT NULL
    GROUP BY d.descripcion, FLOOR(r.lectora_reg / 20) * 20
    ORDER BY bin_start
""").fetchall()

data = [
    {"dependencia": r[0], "bin": r[1], "count": r[2]}
    for r in result
]

json.dump(data, sys.stdout)
```

#### `src/data/escuelas-ranking.json.py`
```python
#!/usr/bin/env python3
"""Ranking de escuelas con métricas completas."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

WHERE_OFICIAL = """
    r.puntaje_nem > 0 AND r.rindio_anterior = false AND r.situacion_egreso = 1
    AND r.lectora_reg IS NOT NULL AND r.mate1_reg IS NOT NULL
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
        COUNT(*) as cantidad,
        ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
        ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
        ROUND((AVG(r.lectora_reg) + AVG(r.mate1_reg)) / 2, 1) as prom_lect_mate,
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p25,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p75,
        SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) as en_top10
    FROM resultados_paes r
    JOIN establecimientos e ON r.rbd = e.rbd
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
    WHERE {WHERE_OFICIAL}
    GROUP BY e.rbd, e.nombre, d.descripcion, c.cod_region, c.region, c.comuna
    HAVING COUNT(*) >= 5
    ORDER BY prom_lect_mate DESC
""").fetchall()

data = [
    {
        "rbd": r[0], "establecimiento": r[1], "dependencia": r[2],
        "cod_region": r[3], "region": r[4], "comuna": r[5],
        "cantidad": r[6], "prom_lectora": r[7], "prom_mate1": r[8],
        "prom_lect_mate": r[9], "p25": r[10], "p75": r[11], "en_top10": r[12]
    }
    for r in result
]

json.dump(data, sys.stdout)
```

#### `src/data/filtros.json.py`
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
ramas = con.execute("SELECT codigo, descripcion FROM ref_rama ORDER BY codigo").fetchall()

result = {
    "regiones": [{"codigo": r[0], "nombre": r[1]} for r in regiones_ordenadas],
    "dependencias": [{"codigo": r[0], "nombre": r[1]} for r in dependencias],
    "ramas": [{"codigo": r[0], "nombre": r[1]} for r in ramas]
}

json.dump(result, sys.stdout)
```

### Páginas Markdown

#### `src/index.md` (Resumen)
```markdown
---
title: PAES 2026 - Explorador de Datos
toc: false
---

# PAES 2026 - Explorador de Datos

Análisis de resultados de la Prueba de Acceso a la Educación Superior de Chile.

```js
const resumen = await FileAttachment("data/resumen.json").json();
const histLectora = await FileAttachment("data/histograma-lectora.json").json();
```

## Métricas Generales

<div class="grid grid-cols-6">
  <div class="card">
    <h2>Total Postulantes</h2>
    <span class="big">${resumen.totales.total.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Rindieron Lectora</h2>
    <span class="big">${resumen.totales.rindieron_lectora.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Rindieron Mate 1</h2>
    <span class="big">${resumen.totales.rindieron_mate1.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Prom. Lectora</h2>
    <span class="big">${resumen.totales.prom_lectora}</span>
  </div>
  <div class="card">
    <h2>Prom. Matemática 1</h2>
    <span class="big">${resumen.totales.prom_mate1}</span>
  </div>
  <div class="card">
    <h2>Prom. NEM</h2>
    <span class="big">${resumen.totales.prom_nem}</span>
  </div>
</div>

## Distribución por Dependencia

<div class="grid grid-cols-2">
<div>

```js
const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};

Plot.plot({
  marginLeft: 180,
  height: 300,
  marks: [
    Plot.barX(resumen.por_dependencia, {
      y: "dependencia",
      x: "cantidad",
      fill: d => colores[d.dependencia],
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```

</div>
<div>

```js
Plot.plot({
  height: 300,
  marks: [
    Plot.arc(resumen.por_rama, {
      value: "cantidad",
      label: "rama",
      innerRadius: 50
    })
  ]
})
```

</div>
</div>

## Distribución de Puntajes PAES

```js
Plot.plot({
  height: 400,
  color: {legend: true, domain: Object.keys(colores), range: Object.values(colores)},
  marks: [
    Plot.rectY(histLectora, {
      x: "bin",
      y: "count",
      fill: "dependencia",
      interval: 20
    }),
    Plot.ruleY([0])
  ]
})
```
```

#### `src/establecimientos.md` (Rankings)
```markdown
---
title: Análisis por Establecimiento
---

# Análisis por Establecimiento

```js
const escuelas = await FileAttachment("data/escuelas-ranking.json").json();
const filtros = await FileAttachment("data/filtros.json").json();
```

<div class="note">
💡 <strong>Nota metodológica</strong>: El DEMRE advierte que la PAES no fue diseñada para medir calidad educativa. Los rankings reflejan principalmente el nivel socioeconómico.
</div>

```js
// Filtros
const regionSel = view(Inputs.select(
  [null, ...filtros.regiones],
  {label: "Región", format: d => d ? d.nombre : "Todas"}
));

const depSel = view(Inputs.select(
  [null, ...filtros.dependencias],
  {label: "Dependencia", format: d => d ? d.nombre : "Todas"}
));

const topN = view(Inputs.range([10, 100], {value: 20, step: 10, label: "Mostrar"}));
```

```js
// Filtrar datos
const escuelasFiltradas = escuelas
  .filter(e => !regionSel || e.cod_region === regionSel.codigo)
  .filter(e => !depSel || e.dependencia === depSel.nombre)
  .slice(0, topN);
```

```js
Inputs.table(escuelasFiltradas, {
  columns: ["establecimiento", "dependencia", "region", "cantidad", "prom_lect_mate", "en_top10"],
  header: {
    establecimiento: "Establecimiento",
    dependencia: "Dependencia",
    region: "Región",
    cantidad: "Estudiantes",
    prom_lect_mate: "Promedio L+M",
    en_top10: "En Top 10%"
  }
})
```

```js
const colores = {
  'Particular Pagado': '#E63946',
  'Particular Subvencionado': '#457B9D',
  'Municipal': '#2A9D8F',
  'Serv. Local Educación': '#E9C46A',
  'Corp. Administración Delegada': '#9B5DE5'
};

Plot.plot({
  marginLeft: 250,
  height: Math.max(400, escuelasFiltradas.length * 25),
  marks: [
    Plot.barX(escuelasFiltradas.slice(0, 20), {
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

#### `src/buscar.md` (Buscar Establecimiento)
```markdown
---
title: Buscar Establecimiento
---

# Buscar Establecimiento

```js
const escuelas = await FileAttachment("data/escuelas-ranking.json").json();
```

```js
const busqueda = view(Inputs.search(escuelas, {
  placeholder: "Buscar establecimiento...",
  columns: ["establecimiento", "comuna"],
  format: d => `${d.establecimiento} - ${d.comuna}`
}));
```

```js
if (busqueda.length > 0) {
  const escuela = busqueda[0];
  display(html`
    <div class="card" style="max-width: 600px">
      <h2>${escuela.establecimiento}</h2>
      <div class="grid grid-cols-2">
        <div><strong>Comuna:</strong> ${escuela.comuna}</div>
        <div><strong>Región:</strong> ${escuela.region}</div>
        <div><strong>Dependencia:</strong> ${escuela.dependencia}</div>
        <div><strong>Estudiantes:</strong> ${escuela.cantidad}</div>
      </div>
      <hr>
      <div class="grid grid-cols-3">
        <div class="card">
          <h3>Prom. Lectora</h3>
          <span class="big">${escuela.prom_lectora}</span>
        </div>
        <div class="card">
          <h3>Prom. Mate 1</h3>
          <span class="big">${escuela.prom_mate1}</span>
        </div>
        <div class="card">
          <h3>Prom. L+M</h3>
          <span class="big">${escuela.prom_lect_mate}</span>
        </div>
      </div>
      <p><strong>Estudiantes en Top 10% nacional:</strong> ${escuela.en_top10}</p>
    </div>
  `);

  // Escuelas cercanas (misma comuna)
  const cercanas = escuelas
    .filter(e => e.comuna === escuela.comuna && e.rbd !== escuela.rbd)
    .slice(0, 10);

  if (cercanas.length > 0) {
    display(html`<h3>Otros establecimientos en ${escuela.comuna}</h3>`);
    display(Inputs.table(cercanas, {
      columns: ["establecimiento", "dependencia", "cantidad", "prom_lect_mate"]
    }));
  }
}
```
```

### Configuración

#### `observablehq.config.js`
```javascript
export default {
  title: "PAES 2026 Explorer",
  pages: [
    {name: "Resumen", path: "/"},
    {name: "Por Establecimiento", path: "/establecimientos"},
    {name: "Buscar", path: "/buscar"},
    {name: "Por Región", path: "/regiones"},
    {name: "Análisis de Brechas", path: "/brechas"}
  ],
  theme: "light",
  base: "/paes2026/"  // Para GitHub Pages
};
```

#### `.github/workflows/deploy.yml`
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

| Dataset | Filas | Tamaño estimado |
|---------|-------|-----------------|
| resumen.json | 1 | < 1 KB |
| histograma-lectora.json | ~400 bins | ~15 KB |
| histograma-mate.json | ~400 bins | ~15 KB |
| escuelas-ranking.json | ~3,000 | ~400 KB |
| regiones.json | ~16 | ~2 KB |
| comunas-top.json | ~100 | ~5 KB |
| brechas.json | ~100 | ~10 KB |
| filtros.json | ~50 | ~3 KB |

**Total estimado**: ~500 KB vs 34 MB original (reducción del 98%)

---

## Limitaciones del Enfoque Simplificado

### Lo que NO se puede hacer sin DuckDB-WASM:

1. **Queries SQL arbitrarios en el cliente**: Los datos deben pre-calcularse
2. **Filtros combinados dinámicos**: Requiere pre-generar todas las combinaciones o filtrar arrays en JS
3. **Datos a nivel individual**: Solo agregaciones precomputadas

### Soluciones:

| Funcionalidad | Solución |
|---------------|----------|
| Filtros por región | Pre-incluir `cod_region` y filtrar en JS |
| Filtros por dependencia | Pre-incluir `dependencia` y filtrar en JS |
| Búsqueda de escuela | `Inputs.search()` sobre array completo |
| Scatter plot individual | Usar muestra representativa (~5k puntos) |

### Cuándo SÍ necesitarías DuckDB-WASM:

- Queries SQL complejos definidos por el usuario
- Datasets >10MB que no quieres enviar completos
- Joins dinámicos entre múltiples tablas
- Análisis exploratorio ad-hoc

---

## Migración de Componentes

| Streamlit | Observable Framework |
|-----------|---------------------|
| `st.metric()` | `<div class="card">` con CSS |
| `st.dataframe()` | `Inputs.table()` |
| `st.plotly_chart()` | `Plot.plot()` |
| `st.sidebar` | Filtros inline con `view()` |
| `st.multiselect()` | `Inputs.select({multiple: true})` |
| `st.tabs()` | Páginas separadas (navegación) |
| `st_searchbox()` | `Inputs.search()` |
| `st.slider()` | `Inputs.range()` |
| `st.checkbox()` | `Inputs.toggle()` |

---

## Comandos Útiles

```bash
# Desarrollo local
npm run dev

# Build para producción
npm run build

# Ver build localmente
npm run preview

# Limpiar cache de data loaders
rm -rf .observablehq/cache/

# Forzar re-ejecución de un loader
touch src/data/resumen.json.py
```

---

## Referencias

### Observable Framework
- [Sitio oficial](https://observablehq.com/framework/)
- [Getting Started](https://observablehq.com/framework/getting-started)
- [Data Loaders](https://observablehq.com/framework/data-loaders)
- [Deploying](https://observablehq.com/framework/deploying)

### Observable Plot
- [Documentación](https://observablehq.com/plot/)
- [Galería de ejemplos](https://observablehq.com/@observablehq/plot-gallery)

### Observable Inputs
- [Documentación](https://observablehq.com/framework/inputs)

### Ejemplos de Referencia
- [Framework Examples](https://github.com/observablehq/framework/tree/main/examples)
- [Mosaic + Framework (si necesitas DuckDB-WASM)](https://idl.uw.edu/mosaic-framework-example/)
