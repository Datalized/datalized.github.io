# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Datalized Public** - A multi-project data visualization platform for Chilean public data, available at `public.datalized.cl`. Built with Observable Framework for static site generation.

### Projects

- **PAES 2026** (`src/paes-2026/`) - Chilean university entrance exam results analysis

## Commands

```bash
# Install dependencies
npm install && uv sync

# Development server (localhost:3000)
npm run dev

# Build static site to dist/
npm run build

# Clean build artifacts and cache
npm run clean

# Regenerate PAES database from raw data
uv run jupyter execute notebooks/paes-2026/raw-data.ipynb
```

Note: `npm run dev/build` automatically uses the uv virtualenv via `PATH=.venv/bin:$PATH` in package.json, so Python data loaders can import duckdb.

## Architecture

```
├── raw-data/              # Raw CSV/Excel files (not in git)
├── notebooks/             # Jupyter notebooks → build DuckDB
│   └── paes-2026/raw-data.ipynb
├── paes.duckdb            # Built database (committed to git)
├── src/                   # Observable Framework source
│   └── paes-2026/
│       ├── data/*.py      # Python data loaders → JSON at build time
│       └── components/    # Reusable JS modules
└── dist/                  # Built static site (not in git)
```

**Data flow**: `raw-data/` → Notebook → `paes.duckdb` → Data loaders → JSON → Observable pages

## PAES 2026 Project

### Database (paes.duckdb)

Main tables:
- `resultados_paes` (306K rows) - Student exam scores: `lectora_reg`, `mate1_reg`, `mate2_reg`, `historia_reg`, `ciencias_reg` (plus `*_inv` for winter tests, `*_ant` for previous year)
- `establecimientos` (12K rows) - Schools with `rbd` primary key, includes: `latitud`/`longitud`, enrollment (`mat_parvulario`, `mat_basica`, `mat_media_hc`, `mat_media_tp`, `mat_total`), admin (`cod_depe`, `cod_depe2`, `rural`, `convenio_pie`, `pace`)
- `comunas` (346 rows) - Geographic hierarchy: comuna → provincia → región

Reference tables: `ref_dependencia`, `ref_dependencia_mineduc`, `ref_dependencia_mineduc2`, `ref_rama`, `ref_situacion_egreso`, `ref_modulo_ciencias`, `ref_orientacion_religiosa`, `ref_estado_establecimiento`, `cod_ensenanza`

### Key Query Patterns

**Official DEMRE filter** (used in all data loaders):
```sql
WHERE r.puntaje_nem > 0 AND r.puntaje_ranking > 0
  AND r.mate1_reg > 0 AND r.lectora_reg > 0
  AND r.rindio_anterior = false AND r.situacion_egreso = 1
```

**Statistical significance**: `HAVING COUNT(*) >= 5` (minimum students per school)

**Score conversions**: Spanish comma decimals converted with `REPLACE` and `NULLIF` during import

**Region ordering**: North-to-south geographic mapping via `ORDEN_REGIONES` dict

### Data Loaders

Located in `src/paes-2026/data/`:
- `escuelas-ranking.json.py` - School rankings with percentiles and Top 10% counts
- `brechas-top10.json.py` - Top 10% analysis by dependency type
- `filtros.json.py` - Filter options for UI selectors

## Deployment

- GitHub Actions workflow builds on push to main → GitHub Pages
- Data loaders execute at build time, generating JSON from DuckDB
- `paes.duckdb` must be committed (negated in .gitignore)
- After regenerating database, commit the new `paes.duckdb`

## Observable Framework Reference

Full documentation: [`docs/observable.md`](docs/observable.md)

### Quick Reference

**Data loading**:
```js
const data = FileAttachment("paes-2026/data/escuelas-ranking.json").json();
```

**Reactive inputs**:
```js
const region = view(Inputs.select(regiones, {label: "Región:", value: "Metropolitana"}));
```

**Dashboard layouts**:
```html
<div class="grid grid-cols-4">
  <div class="card"><h2>Título</h2>Contenido</div>
</div>
```

**Theme variables**: `--theme-foreground`, `--theme-background`, `--theme-foreground-focus`, `--theme-foreground-muted`
