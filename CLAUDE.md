# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Datalized Public** - A multi-project data visualization platform for Chilean public data, available at `public.datalized.cl`. Built with Observable Framework for static site generation.

### Projects

- **PAES 2026** (`src/paes-2026/`) - Chilean university entrance exam results analysis

## Directory Structure

```
├── raw-data/              # Raw data files (not in git)
│   └── paes-2026/         # PAES 2026 source data
├── notebooks/             # Jupyter notebooks for data processing
│   └── paes-2026/
│       └── raw-data.ipynb # Builds paes.duckdb from raw CSV files
├── src/                   # Observable Framework source
│   ├── index.md           # Main landing page
│   └── paes-2026/         # PAES 2026 project
│       ├── index.md       # Ranking page
│       ├── top.md         # Top 10% analysis
│       ├── ficha.md       # School search
│       ├── data/          # Python data loaders
│       └── components/    # Reusable JS components
├── paes.duckdb            # Built database (committed to git)
└── observablehq.config.js # Observable Framework config
```

## Commands

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

### Python (Data Processing)

```bash
# Install Python dependencies
uv sync

# Regenerate PAES database from raw data
uv run jupyter execute notebooks/paes-2026/raw-data.ipynb

# Add new Python dependencies
uv add <package-name>
```

## PAES 2026 Project

### Database (paes.duckdb)

Read-only DuckDB database with main tables:
- `resultados_paes` (306K rows) - Student exam scores with columns: `lectora_reg`, `mate1_reg`, `mate2_reg`, `historia_reg`, `ciencias_reg` for current scores, plus `*_inv` variants for winter tests and `*_ant` for previous year
- `establecimientos` (12K rows) - Schools from MINEDUC directory with `rbd` as primary key, includes:
  - Geographic coordinates: `latitud`, `longitud`
  - Enrollment by level: `mat_parvulario`, `mat_basica`, `mat_media_hc`, `mat_media_tp`, `mat_total`
  - Administrative info: `cod_depe`, `cod_depe2`, `rural`, `convenio_pie`, `pace`
- `comunas` (346 rows) - Geographic hierarchy: comuna → provincia → región

Reference tables: `ref_dependencia`, `ref_dependencia_mineduc`, `ref_dependencia_mineduc2`, `ref_rama`, `ref_situacion_egreso`, `ref_modulo_ciencias`, `ref_orientacion_religiosa`, `ref_estado_establecimiento`, `cod_ensenanza`

### Data Loaders

Located in `src/paes-2026/data/` (Python scripts that query DuckDB at build time):
- `escuelas-ranking.json.py` - School rankings with metrics
- `brechas-top10.json.py` - Top 10% analysis data
- `filtros.json.py` - Filter options for selectors

### Raw Data Sources

Located in `raw-data/paes-2026/`:
- `ArchivoC_Adm2026REG.csv` - Raw PAES results (50 MB)
- `Libro_CódigosADM2026_ArchivoC.xlsx` - MINEDUC codebook
- `20250926_Directorio_Oficial_EE_2025_*.csv` - MINEDUC Official School Directory

## Deployment

### Observable Framework (GitHub Pages / public.datalized.cl)

- Run `npm run build` to generate static files in `dist/`
- Data loaders execute at build time, generating JSON from DuckDB
- `paes.duckdb` must be committed to git (excluded from .gitignore via negation)
- After regenerating database with notebook, commit the new `paes.duckdb`

## Key Patterns

- Institution queries use `HAVING COUNT(*) >= 5` to filter for statistical significance
- Score columns use Spanish comma decimals, converted during import with `REPLACE` and `NULLIF`
- Official filters for matching DEMRE statistics: `puntaje_nem > 0`, `rindio_anterior = false`, `situacion_egreso = 1`
- All database queries are read-only; modifications go through the notebook pipeline
- Region ordering uses north-to-south geographic mapping (dict `ORDEN_REGIONES`)
