# Migración a Aplicación Web con DuckDB-WASM

Este documento describe cómo migrar la aplicación PAES 2026 Explorer de Streamlit a una aplicación web estática usando DuckDB-WASM y Observable Framework.

## Resumen Ejecutivo

| Aspecto | Actual (Streamlit) | Propuesto (Observable Framework) |
|---------|-------------------|----------------------------------|
| Backend | Python + Streamlit Cloud | Sin backend (estático) |
| Base de datos | DuckDB (34 MB) | DuckDB-WASM + Parquet |
| Hosting | Streamlit Community Cloud | GitHub Pages (gratis) |
| Rendimiento | Queries en servidor | Queries en navegador (instantáneo) |
| Costo | Gratis (limitado) | Gratis (ilimitado) |

## ¿Por qué migrar?

### Ventajas de DuckDB-WASM + Observable Framework

1. **Rendimiento instantáneo**: Los datos se precomputan en build time y se envían como archivos estáticos
2. **Sin servidor**: No hay costos de hosting ni límites de concurrencia
3. **Privacidad**: Los datos nunca salen del navegador del usuario
4. **Escalabilidad**: GitHub Pages puede manejar millones de usuarios
5. **Interactividad**: Mosaic permite visualizaciones interactivas con millones de puntos

### Limitaciones actuales de Streamlit

- Límites de memoria y conexiones en Streamlit Cloud
- Latencia en cada interacción (round-trip al servidor)
- Dependencia de un servicio externo

---

## Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────────────┐
│                      BUILD TIME (GitHub Actions)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   paes.duckdb ──► Data Loaders (Python/DuckDB CLI)              │
│                          │                                       │
│                          ▼                                       │
│              ┌──────────────────────┐                           │
│              │  Archivos Parquet    │                           │
│              │  optimizados         │                           │
│              │  - resumen.parquet   │                           │
│              │  - escuelas.parquet  │                           │
│              │  - regiones.parquet  │                           │
│              │  - brechas.parquet   │                           │
│              └──────────────────────┘                           │
│                          │                                       │
│                          ▼                                       │
│              Observable Framework Build                          │
│                          │                                       │
│                          ▼                                       │
│                    dist/ (estático)                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RUNTIME (Navegador)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Usuario ──► GitHub Pages ──► HTML/JS/Parquet                  │
│                                     │                            │
│                                     ▼                            │
│                           ┌─────────────────┐                   │
│                           │  DuckDB-WASM    │                   │
│                           │  (en navegador) │                   │
│                           └─────────────────┘                   │
│                                     │                            │
│                                     ▼                            │
│                           ┌─────────────────┐                   │
│                           │ Mosaic vgplot   │                   │
│                           │ Visualizaciones │                   │
│                           └─────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tecnologías Clave

### 1. DuckDB-WASM

[DuckDB-WASM](https://github.com/duckdb/duckdb-wasm) es la versión WebAssembly de DuckDB que corre completamente en el navegador.

**Características:**
- Ejecuta SQL completo en el cliente
- Soporta Parquet, CSV, JSON, Arrow
- Compatible con Chrome, Firefox, Safari
- Basado en DuckDB v1.4.3

**Ejemplo básico:**
```javascript
import * as duckdb from '@duckdb/duckdb-wasm';

const db = await duckdb.instantiate();
const conn = await db.connect();

// Cargar Parquet remoto
await conn.query(`
  CREATE TABLE resultados AS
  SELECT * FROM read_parquet('https://example.com/data.parquet')
`);

// Ejecutar queries
const result = await conn.query(`
  SELECT dependencia, AVG(lectora_reg) as promedio
  FROM resultados
  GROUP BY dependencia
`);
```

**Recursos:**
- [Documentación oficial](https://duckdb.org/docs/stable/clients/wasm/overview)
- [NPM Package](https://www.npmjs.com/package/@duckdb/duckdb-wasm)
- [Shell interactivo](https://shell.duckdb.org)

### 2. Observable Framework

[Observable Framework](https://observablehq.com/framework/) es un generador de sitios estáticos optimizado para aplicaciones de datos.

**Características:**
- Soporte nativo para DuckDB-WASM
- Data loaders para precomputar datos en build time
- Markdown con bloques de código reactivos
- Deploy a GitHub Pages

**Instalación:**
```bash
# Crear nuevo proyecto
npx @observablehq/framework create paes-explorer

# Estructura del proyecto
paes-explorer/
├── src/
│   ├── index.md           # Página principal
│   ├── data/
│   │   ├── resumen.parquet.py    # Data loader
│   │   └── escuelas.parquet.sh   # Data loader
│   └── components/
│       └── charts.js
├── observablehq.config.js
└── package.json
```

**Recursos:**
- [Getting Started](https://observablehq.com/framework/getting-started)
- [Data Loaders](https://observablehq.com/framework/data-loaders)
- [Deploying](https://observablehq.com/framework/deploying)

### 3. Data Loaders (Build Time)

Los data loaders ejecutan durante el build para generar archivos estáticos optimizados.

**¿Por qué usarlos?**
- Precomputan agregaciones pesadas
- Optimizan el tamaño de los datos
- No exponen la base de datos completa
- Cachean resultados entre builds

**Ejemplo: `src/data/resumen.parquet.py`**
```python
#!/usr/bin/env python3
"""Data loader que genera resumen de PAES por dependencia."""
import duckdb
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

# Query con agregaciones precomputadas
result = con.execute("""
    SELECT
        d.descripcion as dependencia,
        COUNT(*) as total,
        ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
        ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
        ROUND(PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY r.lectora_reg), 0) as p10_lectora,
        ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY r.lectora_reg), 0) as p90_lectora
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE r.lectora_reg > 0 AND r.mate1_reg > 0
    GROUP BY d.descripcion
""").arrow()

# Escribir a stdout como Parquet
import pyarrow.parquet as pq
pq.write_table(result, sys.stdout.buffer)
```

**Ejemplo: `src/data/escuelas.parquet.sh`**
```bash
#!/bin/bash
# Data loader usando DuckDB CLI para escuelas con top performers

duckdb paes.duckdb -c "
COPY (
    SELECT
        e.nombre,
        e.nom_comuna,
        d.descripcion as dependencia,
        COUNT(*) as estudiantes,
        ROUND(AVG((r.lectora_reg + r.mate1_reg)/2), 1) as promedio
    FROM resultados_paes r
    JOIN establecimientos e ON r.rbd = e.rbd
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE r.lectora_reg > 0 AND r.mate1_reg > 0
    GROUP BY e.nombre, e.nom_comuna, d.descripcion
    HAVING COUNT(*) >= 5
    ORDER BY promedio DESC
    LIMIT 1000
) TO '/dev/stdout' (FORMAT PARQUET);
"
```

### 4. Mosaic para Visualizaciones Interactivas

[Mosaic](https://idl.uw.edu/mosaic/) permite crear visualizaciones interactivas vinculadas a DuckDB.

**Características:**
- Cross-filtering entre múltiples gráficos
- Soporta millones de puntos de datos
- API declarativa similar a Observable Plot
- Actualización en tiempo real

**Ejemplo con vgplot:**
```javascript
import { vgplot, loadParquet, coordinator } from "@uwdata/vgplot";

// Cargar datos
await loadParquet("resultados", FileAttachment("data/resultados.parquet"));

// Crear visualización con cross-filter
vgplot.plot({
  marks: [
    vgplot.dot(
      vgplot.from("resultados"),
      {
        x: "lectora_reg",
        y: "mate1_reg",
        fill: "dependencia",
        r: 2,
        opacity: 0.5
      }
    )
  ],
  width: 800,
  height: 600
});
```

**Recursos:**
- [Mosaic + Observable Framework](https://idl.uw.edu/mosaic-framework-example/)
- [vgplot API](https://idl.uw.edu/mosaic/vgplot/)

---

## Plan de Migración

### Fase 1: Configuración del Proyecto

```bash
# 1. Crear proyecto Observable Framework
npx @observablehq/framework create paes-explorer
cd paes-explorer

# 2. Instalar dependencias
npm install @uwdata/vgplot @duckdb/duckdb-wasm

# 3. Copiar base de datos
cp ../paes.duckdb .
```

**Estructura propuesta:**
```
paes-explorer/
├── src/
│   ├── index.md                    # Tab: Resumen
│   ├── establecimientos.md         # Tab: Por Establecimiento
│   ├── buscar.md                   # Tab: Buscar Establecimiento
│   ├── regiones.md                 # Tab: Por Región
│   ├── brechas.md                  # Tab: Análisis de Brechas
│   ├── data/
│   │   ├── resumen.parquet.py
│   │   ├── dependencias.parquet.py
│   │   ├── escuelas-top.parquet.py
│   │   ├── regiones.parquet.py
│   │   ├── comunas.parquet.py
│   │   ├── brechas.parquet.py
│   │   └── ref-tables.json.py      # Tablas de referencia
│   └── components/
│       ├── filters.js              # Filtros del sidebar
│       └── charts.js               # Componentes de gráficos
├── paes.duckdb                     # Base de datos fuente
├── observablehq.config.js
└── package.json
```

### Fase 2: Data Loaders

Crear data loaders para cada sección de la aplicación:

#### `src/data/resumen.parquet.py`
```python
#!/usr/bin/env python3
"""Estadísticas generales para la página de resumen."""
import duckdb
import sys
import pyarrow.parquet as pq

con = duckdb.connect("paes.duckdb", read_only=True)

# Estadísticas por dependencia con distribución
result = con.execute("""
    SELECT
        d.descripcion as dependencia,
        COUNT(*) as total,
        COUNT(r.lectora_reg) as rindieron_lectora,
        COUNT(r.mate1_reg) as rindieron_mate1,
        ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
        ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
        ROUND(AVG(r.puntaje_nem), 1) as prom_nem,
        ROUND(STDDEV(r.lectora_reg), 1) as std_lectora,
        ROUND(STDDEV(r.mate1_reg), 1) as std_mate1
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE r.puntaje_nem > 0
      AND r.puntaje_ranking > 0
      AND r.mate1_reg > 0
      AND r.lectora_reg > 0
      AND r.rindio_anterior = false
      AND r.situacion_egreso = 1
    GROUP BY d.descripcion
    ORDER BY total DESC
""").arrow()

pq.write_table(result, sys.stdout.buffer)
```

#### `src/data/histograma-lectora.parquet.py`
```python
#!/usr/bin/env python3
"""Datos para histograma de puntajes Lectora por dependencia."""
import duckdb
import sys
import pyarrow.parquet as pq

con = duckdb.connect("paes.duckdb", read_only=True)

# Muestra estratificada para histograma (máx 50k puntos)
result = con.execute("""
    SELECT
        d.descripcion as dependencia,
        r.lectora_reg as puntaje
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE r.lectora_reg IS NOT NULL
      AND r.puntaje_nem > 0
      AND r.rindio_anterior = false
      AND r.situacion_egreso = 1
    USING SAMPLE 50000
""").arrow()

pq.write_table(result, sys.stdout.buffer)
```

#### `src/data/escuelas-ranking.parquet.py`
```python
#!/usr/bin/env python3
"""Top escuelas con métricas completas."""
import duckdb
import sys
import pyarrow.parquet as pq

con = duckdb.connect("paes.duckdb", read_only=True)

result = con.execute("""
    WITH p90_nacional AS (
        SELECT PERCENTILE_CONT(0.9) WITHIN GROUP
               (ORDER BY (lectora_reg + mate1_reg)/2) as umbral
        FROM resultados_paes
        WHERE puntaje_nem > 0 AND rindio_anterior = false AND situacion_egreso = 1
    )
    SELECT
        e.rbd,
        e.nombre as establecimiento,
        d.descripcion as dependencia,
        c.region,
        c.comuna,
        COUNT(*) as cantidad,
        ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
        ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
        ROUND((AVG(r.lectora_reg) + AVG(r.mate1_reg)) / 2, 1) as prom_lect_mate,
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p25,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p75,
        SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= (SELECT umbral FROM p90_nacional)
            THEN 1 ELSE 0 END) as en_top10,
        ROUND(AVG(r.puntaje_nem), 1) as prom_nem
    FROM resultados_paes r
    JOIN establecimientos e ON r.rbd = e.rbd
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
    WHERE r.puntaje_nem > 0
      AND r.rindio_anterior = false
      AND r.situacion_egreso = 1
      AND r.lectora_reg IS NOT NULL
      AND r.mate1_reg IS NOT NULL
    GROUP BY e.rbd, e.nombre, d.descripcion, c.region, c.comuna
    HAVING COUNT(*) >= 5
    ORDER BY prom_lect_mate DESC
""").arrow()

pq.write_table(result, sys.stdout.buffer)
```

### Fase 3: Páginas Markdown

#### `src/index.md` (Resumen)
```markdown
---
title: PAES 2026 - Explorador de Datos
toc: false
---

# PAES 2026 - Explorador de Datos

Análisis de resultados de la Prueba de Acceso a la Educación Superior de Chile.

```js
// Cargar datos precomputados
const resumen = await FileAttachment("data/resumen.parquet").parquet();
const histLectora = await FileAttachment("data/histograma-lectora.parquet").parquet();
```

## Métricas Generales

```js
// Calcular totales
const totales = resumen.reduce((acc, d) => ({
  total: acc.total + d.total,
  rindieron_lectora: acc.rindieron_lectora + d.rindieron_lectora,
  rindieron_mate1: acc.rindieron_mate1 + d.rindieron_mate1
}), {total: 0, rindieron_lectora: 0, rindieron_mate1: 0});

const promLectora = resumen.reduce((acc, d) => acc + d.prom_lectora * d.total, 0) / totales.total;
const promMate1 = resumen.reduce((acc, d) => acc + d.prom_mate1 * d.total, 0) / totales.total;
```

<div class="grid grid-cols-4">
  <div class="card">
    <h2>Total Postulantes</h2>
    <span class="big">${totales.total.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Rindieron Lectora</h2>
    <span class="big">${totales.rindieron_lectora.toLocaleString()}</span>
  </div>
  <div class="card">
    <h2>Prom. Lectora</h2>
    <span class="big">${promLectora.toFixed(1)}</span>
  </div>
  <div class="card">
    <h2>Prom. Matemática 1</h2>
    <span class="big">${promMate1.toFixed(1)}</span>
  </div>
</div>

## Distribución por Dependencia

```js
Plot.plot({
  marginLeft: 150,
  marks: [
    Plot.barX(resumen, {
      y: "dependencia",
      x: "total",
      fill: "dependencia",
      sort: {y: "-x"}
    }),
    Plot.ruleX([0])
  ]
})
```

## Histograma de Puntajes Lectora

```js
Plot.plot({
  marks: [
    Plot.rectY(histLectora,
      Plot.binX({y: "count"}, {x: "puntaje", fill: "dependencia", thresholds: 50})
    ),
    Plot.ruleY([0])
  ],
  color: {legend: true}
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
const escuelas = await FileAttachment("data/escuelas-ranking.parquet").parquet();
```

```js
// Selector de escuela
const escuelaSeleccionada = view(Inputs.search(escuelas, {
  placeholder: "Buscar establecimiento...",
  columns: ["establecimiento", "comuna"],
  format: d => `${d.establecimiento} - ${d.comuna}`
}));
```

```js
// Mostrar info si hay selección
if (escuelaSeleccionada.length > 0) {
  const escuela = escuelaSeleccionada[0];
  display(html`
    <div class="card">
      <h2>${escuela.establecimiento}</h2>
      <p><strong>Comuna:</strong> ${escuela.comuna}</p>
      <p><strong>Región:</strong> ${escuela.region}</p>
      <p><strong>Dependencia:</strong> ${escuela.dependencia}</p>
      <p><strong>Estudiantes:</strong> ${escuela.cantidad}</p>
      <p><strong>Promedio Lectora+Mate:</strong> ${escuela.prom_lect_mate}</p>
    </div>
  `);
}
```
```

### Fase 4: Configuración de Deploy

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
  // Para GitHub Pages sin dominio custom
  base: "/paes2026/"
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

      # Instalar DuckDB CLI para data loaders .sh
      - name: Install DuckDB CLI
        run: |
          wget https://github.com/duckdb/duckdb/releases/download/v1.1.1/duckdb_cli-linux-amd64.zip
          unzip duckdb_cli-linux-amd64.zip
          chmod +x duckdb
          sudo mv duckdb /usr/local/bin/

      # Instalar dependencias Python
      - name: Install Python dependencies
        run: |
          pip install duckdb pyarrow pandas

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

## Consideraciones de Optimización

### Tamaño de Archivos Parquet

El archivo `paes.duckdb` actual tiene 34 MB. Para optimizar:

1. **Precomputar agregaciones**: En lugar de enviar 306K filas, enviar resúmenes
2. **Filtrar columnas**: Solo incluir columnas necesarias para cada vista
3. **Comprimir**: Parquet tiene compresión nativa (snappy, zstd)
4. **Particionar**: Dividir en múltiples archivos pequeños

**Estimación de tamaños:**
| Dataset | Filas | Tamaño estimado |
|---------|-------|-----------------|
| Resumen por dependencia | 5 | < 1 KB |
| Histograma (muestra 50k) | 50,000 | ~500 KB |
| Escuelas ranking | ~3,000 | ~200 KB |
| Regiones/comunas | ~400 | ~20 KB |
| Datos individuales (muestra) | 50,000 | ~2 MB |

**Total estimado**: ~3-5 MB vs 34 MB original

### Optimización de Parquet para DuckDB-WASM

```python
# Usar row_group_size pequeño para mejor rendimiento en WASM
pq.write_table(
    result,
    sys.stdout.buffer,
    compression='zstd',
    row_group_size=10000  # Importante para DuckDB-WASM
)
```

### Caching de Data Loaders

Observable Framework cachea automáticamente los outputs de data loaders en `.observablehq/cache/`. Para forzar regeneración:

```bash
# Invalidar cache de un loader específico
touch src/data/resumen.parquet.py

# O limpiar todo el cache
rm -rf .observablehq/cache/
```

---

## Migración de Funcionalidades

### Mapeo de Componentes Streamlit → Observable

| Streamlit | Observable Framework |
|-----------|---------------------|
| `st.metric()` | Card con CSS |
| `st.dataframe()` | `Inputs.table()` |
| `st.plotly_chart()` | `Plot.plot()` o Mosaic vgplot |
| `st.sidebar` | Layout con CSS Grid |
| `st.multiselect()` | `Inputs.select()` con multiple |
| `st.tabs()` | Páginas separadas |
| `st_searchbox()` | `Inputs.search()` |

### Filtros Reactivos

En Observable, los filtros se manejan con SQL dinámico en el cliente:

```javascript
// Filtro de región
const regionSel = view(Inputs.select(regiones, {
  multiple: true,
  label: "Región"
}));

// Query reactivo con DuckDB-WASM
const datosFiltrados = await sql`
  SELECT * FROM escuelas
  WHERE ${regionSel.length === 0} OR region IN (${regionSel})
`;
```

---

## Alternativas Consideradas

### 1. React + duckdb-wasm-kit

**Pros:**
- Mayor control sobre UI
- Ecosistema rico de componentes
- TypeScript nativo

**Contras:**
- Más código boilerplate
- Sin data loaders nativos
- Requiere configurar build pipeline

**Recursos:**
- [duckdb-wasm-kit](https://github.com/holdenmatt/duckdb-wasm-kit)

### 2. Svelte + Observable Plot

**Pros:**
- Bundle pequeño
- Sintaxis reactiva simple
- Buen rendimiento

**Contras:**
- Menor ecosistema
- Sin soporte nativo para DuckDB

### 3. Vanilla JS + Vite

**Pros:**
- Sin dependencias de framework
- Máximo control
- Bundle mínimo

**Contras:**
- Más trabajo manual
- Sin data loaders

### Recomendación

**Observable Framework** es la mejor opción porque:
1. Soporte nativo para DuckDB-WASM
2. Data loaders para precomputar en build time
3. Integración con Mosaic para visualizaciones masivas
4. Deploy simple a GitHub Pages
5. Markdown-first para documentación

---

## Cronograma Sugerido

### Semana 1: Setup
- [ ] Crear proyecto Observable Framework
- [ ] Configurar data loaders básicos
- [ ] Migrar página de Resumen

### Semana 2: Funcionalidades Core
- [ ] Migrar rankings de establecimientos
- [ ] Implementar búsqueda de escuelas
- [ ] Agregar filtros reactivos

### Semana 3: Visualizaciones Avanzadas
- [ ] Integrar Mosaic para scatter plots
- [ ] Implementar análisis de brechas
- [ ] Optimizar rendimiento

### Semana 4: Deploy y Polish
- [ ] Configurar GitHub Actions
- [ ] Deploy a GitHub Pages
- [ ] Testing y ajustes finales

---

## Referencias

### DuckDB-WASM
- [GitHub Repository](https://github.com/duckdb/duckdb-wasm)
- [Official Documentation](https://duckdb.org/docs/stable/clients/wasm/overview)
- [NPM Package](https://www.npmjs.com/package/@duckdb/duckdb-wasm)
- [Interactive Shell](https://shell.duckdb.org)

### Observable Framework
- [Official Site](https://observablehq.com/framework/)
- [Getting Started](https://observablehq.com/framework/getting-started)
- [Data Loaders Guide](https://observablehq.com/framework/data-loaders)
- [DuckDB Integration](https://observablehq.com/framework/lib/duckdb)
- [Deploying to GitHub Pages](https://observablehq.com/framework/deploying)

### Mosaic
- [Mosaic Project](https://idl.uw.edu/mosaic/)
- [vgplot API](https://idl.uw.edu/mosaic/vgplot/)
- [Framework Examples](https://idl.uw.edu/mosaic-framework-example/)
- [GitHub Repository](https://github.com/uwdata/mosaic)

### Ejemplos de Referencia
- [NYC Taxi Rides (1M records)](https://idl.uw.edu/mosaic-framework-example/)
- [Observable Web Latency (7M requests)](https://idl.uw.edu/mosaic-framework-example/observable-latency)
- [DuckDB Data Loader Example](https://observablehq.observablehq.cloud/framework-example-loader-duckdb/)
