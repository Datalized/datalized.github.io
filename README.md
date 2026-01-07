# PAES 2026 - Explorador de Datos

Aplicación para explorar y analizar los resultados de la **PAES** (Prueba de Acceso a la Educación Superior) de Chile, proceso de admisión 2026.

## Descripción

Este proyecto contiene:
- Base de datos DuckDB con resultados PAES 2026
- Aplicación Streamlit interactiva para explorar los datos
- Notebooks Jupyter para procesamiento de datos

## Datos

| Dataset | Registros | Descripción |
|---------|-----------|-------------|
| `resultados_paes` | 306,022 | Puntajes y datos de postulantes |
| `establecimientos` | 8,977 | Colegios (RBD, nombre, ubicación) |
| `comunas` | 346 | Regiones, provincias y comunas |
| `cod_ensenanza` | 26 | Códigos MINEDUC de enseñanza |

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/rarce/paes2026.git
cd paes2026

# Instalar dependencias (requiere uv)
uv sync

# Generar base de datos
cd notebooks
uv run jupyter execute paes_db.ipynb
cd ..

# Ejecutar aplicación
uv run streamlit run app.py
```

## Uso

### Aplicación Web

```bash
uv run streamlit run app.py
```

Abre http://localhost:8501 en tu navegador.

**Funcionalidades:**
- Resumen general con métricas y gráficos
- Análisis por establecimiento (ranking de colegios)
- Análisis por región
- Explorador SQL interactivo

### Jupyter Notebook

```bash
uv run jupyter notebook notebooks/paes_db.ipynb
```

## Estructura del Proyecto

```
paes2026/
├── app.py                  # Aplicación Streamlit
├── paes.duckdb             # Base de datos DuckDB
├── pyproject.toml          # Dependencias del proyecto
├── data/
│   ├── ArchivoC_Adm2026REG.csv           # Resultados PAES
│   ├── Libro_CódigosADM2026_ArchivoC.xlsx # Libro de códigos
│   └── new_schools_list.json              # Establecimientos
├── docs/
│   └── paes.md             # Documentación sobre la PAES
└── notebooks/
    └── paes_db.ipynb       # Notebook para crear la BD
```

## Esquema de Base de Datos

### Tabla Principal: `resultados_paes`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | VARCHAR | Identificador único del postulante |
| `rbd` | INTEGER | RBD del establecimiento |
| `dependencia` | INTEGER | 1=Part.Pagado, 2=Part.Subv, 3=Municipal, 4=SLE |
| `rama` | VARCHAR | H1-H4 (humanista), T1-T5 (técnico) |
| `puntaje_nem` | INTEGER | Puntaje NEM (100-1000) |
| `puntaje_ranking` | INTEGER | Puntaje Ranking (100-1000) |
| `lectora_reg` | INTEGER | Competencia Lectora Regular |
| `mate1_reg` | INTEGER | Matemática 1 Regular |
| `mate2_reg` | INTEGER | Matemática 2 Regular |
| `historia_reg` | INTEGER | Historia y Cs. Sociales Regular |
| `ciencias_reg` | INTEGER | Ciencias Regular |

Ver [docs/paes.md](docs/paes.md) para más detalles sobre la PAES.

## Fuentes de Datos

| Fuente | URL | Descripción |
|--------|-----|-------------|
| DEMRE | [portal-transparencia.demre.cl](https://portal-transparencia.demre.cl/portal-base-datos) | Resultados PAES 2026 |
| GitHub Gist | [taylordowns2000](https://gist.github.com/taylordowns2000/5a45618a8e53359bf8a82eea65a51c03) | Establecimientos educacionales |
| DEMRE | Libro de Códigos ADM2026 | Códigos y comunas |

## Tecnologías

- [DuckDB](https://duckdb.org/) - Base de datos analítica
- [Streamlit](https://streamlit.io/) - Framework de aplicaciones web
- [Plotly](https://plotly.com/) - Visualizaciones interactivas
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes Python

## Licencia

MIT

---

Hecho con ❤️ por [Datalized](https://datalized.cl/)
