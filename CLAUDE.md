# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PAES 2026 Data Explorer - A Streamlit web application for analyzing Chilean university entrance exam (PAES) results. Built with DuckDB for analytics, Pandas for data manipulation, and Plotly for interactive visualizations.

## Commands

```bash
# Install dependencies
uv sync

# Run the web application (localhost:8501)
uv run streamlit run app.py

# Regenerate database from raw data
uv run jupyter execute notebooks/paes_db.ipynb

# Add new dependencies
uv add <package-name>
```

## Architecture

### Database (paes.duckdb)

Read-only DuckDB database with three main tables:
- `resultados_paes` (306K rows) - Student exam scores with columns: `lectora_reg`, `mate1_reg`, `mate2_reg`, `historia_reg`, `ciencias_reg` for current scores, plus `*_inv` variants for winter tests and `*_ant` for previous year
- `establecimientos` (8.9K rows) - Schools with `rbd` as primary key, joined to results
- `comunas` (346 rows) - Geographic hierarchy: comuna → provincia → región

Reference tables: `ref_dependencia` (school types), `ref_rama` (educational branches), `ref_situacion_egreso`, `ref_modulo_ciencias`, `cod_ensenanza`

### Application (app.py)

Single-file Streamlit app with:
- Cached DuckDB connection via `@st.cache_resource`
- Sidebar multi-select filters (region, dependency, branch)
- Three tabs: Summary metrics, Institution rankings, Regional analysis
- Dynamic SQL WHERE clause construction based on filters
- Region ordering uses north-to-south geographic mapping (dict `orden_regiones`)

### Data Pipeline (notebooks/paes_db.ipynb)

Builds database from:
- `data/ArchivoC_Adm2026REG.csv` - Raw PAES results (50 MB)
- `data/Libro_CódigosADM2026_ArchivoC.xlsx` - MINEDUC codebook
- `data/new_schools_list.json` - School registry

## Key Patterns

- Institution queries use `HAVING COUNT(*) >= 5` to filter for statistical significance
- Score columns use Spanish comma decimals, converted during import with `REPLACE` and `NULLIF`
- Visualizations: Plotly Express for simple charts, Graph Objects for customized layouts
- All database queries are read-only; modifications go through the notebook pipeline
