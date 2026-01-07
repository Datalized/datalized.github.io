# PAES 2026 - Explorador de Datos

Aplicación para explorar y analizar los resultados de la **PAES** (Prueba de Acceso a la Educación Superior) de Chile, proceso de admisión 2026.

## Descripción

Este proyecto contiene:
- Base de datos DuckDB con resultados PAES 2026
- Aplicación Streamlit interactiva para explorar los datos
- Notebooks Jupyter para procesamiento de datos

## Contexto: El debate sobre rankings educativos

Esta aplicación incluye un **Análisis de Brechas Educativas** que responde a la discusión pública sobre cómo interpretar los resultados PAES.

### El problema de los rankings tradicionales

Los rankings de "mejores colegios" basados en promedios PAES son cuestionados por:

- **Sesgo socioeconómico**: ~70% de los resultados se explican por nivel socioeconómico familiar, no por calidad educativa
- **Invisibilización del talento público**: El 55% de los estudiantes del Top 10% nacional NO viene de colegios particulares pagados
- **Validez cuestionada**: El DEMRE [advierte oficialmente](https://demre.cl/noticias/2025-01-10-consulta-resultados-por-colegios-actualizada) que la PAES no fue diseñada para medir calidad de establecimientos

### Referencias

- **[@elaval - Análisis PAES 2026](https://elaval.github.io/PAES-2026/)**: Análisis crítico de rankings tradicionales
- **[CIPER - El ranking del privilegio](https://www.ciperchile.cl/2026/01/06/el-ranking-del-privilegio/)**: Crítica estructural a los rankings
- **[U. Chile - Valor agregado en educación](https://brunner.cl/2010/08/valor-agregado-por-diferentes-tipos-de-colegios-en-chile/)**: Metodología de valor agregado
- **[U. Chile - Desigualdad y rankings](https://ingenieria.uchile.cl/noticias/202460/sobre-desigualdad-rankings-y-educacion-publica)**: Perspectiva académica

### Métricas alternativas implementadas

Esta app incluye:
- **Comparación contextualizada**: Comparar establecimientos solo del mismo tipo de dependencia
- **Distribución del Top 10%**: ¿De dónde vienen realmente los mejores estudiantes?
- **Box plots por dependencia**: Distribución completa de puntajes, no solo promedios
- **Brechas regionales**: Diferencias entre educación pública y privada por región

## Datos

| Dataset | Registros | Descripción |
|---------|-----------|-------------|
| `resultados_paes` | 306,022 | Puntajes y datos de postulantes |
| `establecimientos` | ~12,000 | Colegios con ubicación geográfica (lat/lon), matrícula, dependencia |
| `comunas` | 346 | Regiones, provincias y comunas |
| `cod_ensenanza` | 26 | Códigos MINEDUC de enseñanza |

**Tablas de referencia:** `ref_dependencia` (clasificación PAES), `ref_dependencia_mineduc` (COD_DEPE, 6 categorías), `ref_dependencia_mineduc2` (COD_DEPE2, 5 categorías agrupadas), `ref_rama`, `ref_situacion_egreso`, `ref_modulo_ciencias`, `ref_orientacion_religiosa`, `ref_estado_establecimiento`

### Nueva información de establecimientos (MINEDUC 2025)

La tabla `establecimientos` ahora incluye datos del [Directorio Oficial de Establecimientos del MINEDUC](https://datosabiertos.mineduc.cl/directorio-de-establecimientos-educacionales/):

- **Geolocalización**: Latitud y longitud para búsqueda de colegios cercanos
- **Matrícula**: Por nivel educativo (parvulario, básica, media HC/TP)
- **Dependencia detallada**: COD_DEPE (6 categorías) y COD_DEPE2 (5 categorías agrupadas)
- **Programas**: Convenio PIE, Programa PACE
- **Características**: Ruralidad, orientación religiosa, costos (matrícula y mensualidad)

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
- Análisis por establecimiento (ranking general + comparación contextualizada)
- **Buscar Establecimiento**: Búsqueda individual de colegios con:
  - Scatter plot de resultados individuales (Matemática vs Lectora)
  - Datos agregados del establecimiento
  - Colegios cercanos basados en geolocalización
- Análisis por región
- **Análisis de brechas educativas**: distribución del talento, box plots por dependencia, origen del Top 10%

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
├── requirements.txt        # Dependencias para Streamlit Cloud
├── CLAUDE.md               # Instrucciones para Claude Code
├── LICENSE                 # Licencia MIT
├── data/
│   ├── ArchivoC_Adm2026REG.csv                          # Resultados PAES (DEMRE)
│   ├── Libro_CódigosADM2026_ArchivoC.xlsx               # Libro de códigos (DEMRE)
│   ├── 20250926_Directorio_Oficial_EE_2025_20250430_WEB.csv  # Directorio establecimientos (MINEDUC)
│   └── ER_Directorio_Oficial_EE_WEB.pdf                 # Esquema del directorio
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
| MINEDUC | [datosabiertos.mineduc.cl](https://datosabiertos.mineduc.cl/directorio-de-establecimientos-educacionales/) | Directorio Oficial de Establecimientos 2025 |
| DEMRE | Libro de Códigos ADM2026 | Códigos y comunas |

## Tecnologías

- [DuckDB](https://duckdb.org/) - Base de datos analítica
- [Streamlit](https://streamlit.io/) - Framework de aplicaciones web
- [streamlit-searchbox](https://github.com/m-wrzr/streamlit-searchbox) - Componente de búsqueda con autocompletado
- [Plotly](https://plotly.com/) - Visualizaciones interactivas
- [uv](https://docs.astral.sh/uv/) - Gestor de paquetes Python

## Licencia

MIT

---

Hecho con ❤️ por [Datalized](https://datalized.cl/)
