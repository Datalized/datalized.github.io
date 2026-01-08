# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PAES 2026 Data Explorer - A data visualization project for analyzing Chilean university entrance exam (PAES) results. Two implementations:
- **Streamlit app** (`app.py`) - Interactive Python web app with server-side DuckDB
- **Observable Framework** (`src/`) - Static site with precomputed JSON data for GitHub Pages

## Commands

### Streamlit (Python)

```bash
# Install Python dependencies
uv sync

# Run the Streamlit app (localhost:8501)
uv run streamlit run app.py

# Regenerate database from raw data
uv run jupyter execute notebooks/paes_db.ipynb

# Add new Python dependencies
uv add <package-name>
```

### Observable Framework (JavaScript)

```bash
# Install Node dependencies
npm install

# Development server (localhost:3000)
npm run dev

# Build static site to dist/
npm run build

# Clean data loader cache
rm -rf .observablehq/cache/
```

Note: `npm run dev/build` automatically uses the uv virtualenv via `PATH=.venv/bin:$PATH` in package.json, so Python data loaders can import duckdb.

## Architecture

### Database (paes.duckdb)

Read-only DuckDB database with main tables:
- `resultados_paes` (306K rows) - Student exam scores with columns: `lectora_reg`, `mate1_reg`, `mate2_reg`, `historia_reg`, `ciencias_reg` for current scores, plus `*_inv` variants for winter tests and `*_ant` for previous year
- `establecimientos` (12K rows) - Schools from MINEDUC directory with `rbd` as primary key, includes:
  - Geographic coordinates: `latitud`, `longitud` (for nearby schools feature)
  - Enrollment by level: `mat_parvulario`, `mat_basica`, `mat_media_hc`, `mat_media_tp`, `mat_total`
  - Administrative info: `cod_depe`, `cod_depe2`, `rural`, `convenio_pie`, `pace`
- `comunas` (346 rows) - Geographic hierarchy: comuna → provincia → región

Reference tables: `ref_dependencia` (PAES classification), `ref_dependencia_mineduc` (COD_DEPE), `ref_dependencia_mineduc2` (COD_DEPE2 grouped), `ref_rama`, `ref_situacion_egreso`, `ref_modulo_ciencias`, `ref_orientacion_religiosa`, `ref_estado_establecimiento`, `cod_ensenanza`

### Streamlit App (app.py)

Single-file Streamlit app with:
- Cached DuckDB connection via `@st.cache_resource`
- Sidebar multi-select filters (region, dependency, branch)
- Five tabs: Summary metrics, Institution rankings, Search Institution, Regional analysis, Gap Analysis
- Dynamic SQL WHERE clause construction based on filters
- Region ordering uses north-to-south geographic mapping (dict `ORDEN_REGIONES`)
- `calcular_distancia_km()` function for Haversine distance calculation (nearby schools feature)

Search Institution tab features:
- Text search with filtered selectbox for school selection
- Individual student scatter plot (Math vs Reading scores)
- Nearby schools comparison using lat/lon coordinates (within 10km radius)
- Fallback to same-comuna comparison when coordinates unavailable

### Observable Framework (src/)

Static site with three pages:
- `src/index.md` - Ranking (homepage)
- `src/crema.md` - La Crema (Top 10% analysis)
- `src/ficha.md` - La Ficha (school search)

Data loaders in `src/data/` (Python scripts that query DuckDB at build time):
- `escuelas-ranking.json.py` - School rankings with metrics
- `brechas-top10.json.py` - Top 10% analysis data
- `filtros.json.py` - Filter options for selectors

Config: `observablehq.config.js` sets `base: "/paes2026/"` for GitHub Pages deployment.

### Data Pipeline (notebooks/paes_db.ipynb)

Builds database from:
- `data/ArchivoC_Adm2026REG.csv` - Raw PAES results (50 MB)
- `data/Libro_CódigosADM2026_ArchivoC.xlsx` - MINEDUC codebook
- `data/20250926_Directorio_Oficial_EE_2025_*.csv` - MINEDUC Official School Directory (with lat/lon, enrollment, etc.)

## Deployment

### Streamlit (Community Cloud)

- `requirements.txt` contains production dependencies (without jupyter/openpyxl dev tools)
- `paes.duckdb` must be committed to git (excluded from .gitignore via negation)
- After regenerating database with notebook, commit the new `paes.duckdb`

### Observable Framework (GitHub Pages)

- Run `npm run build` to generate static files in `dist/`
- Data loaders execute at build time, generating JSON from DuckDB
- Deploys via GitHub Actions (see `docs/migrate-webapp.md` for workflow)

## Key Patterns

- Institution queries use `HAVING COUNT(*) >= 5` to filter for statistical significance
- Score columns use Spanish comma decimals, converted during import with `REPLACE` and `NULLIF`
- Official filters for matching DEMRE statistics: `puntaje_nem > 0`, `rindio_anterior = false`, `situacion_egreso = 1`
- All database queries are read-only; modifications go through the notebook pipeline
- Consistent color scheme for dependency types defined in `COLORES_DEPENDENCIA` dict
