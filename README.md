# Datalized Public

Datos públicos de Chile, visualizados y analizados. Exploraciones interactivas de información oficial para entender mejor nuestro país.

🌐 **[public.datalized.cl](https://public.datalized.cl)**

## Proyectos

### PAES 2026

Análisis de resultados de la **PAES** (Prueba de Acceso a la Educación Superior) de Chile, proceso de admisión 2026.

**Funcionalidades:**
- **Ranking de Establecimientos**: Ordenar por promedio, cantidad de estudiantes o presencia en Top 10%
- **Top 10%**: ¿De dónde vienen los mejores estudiantes? Análisis por dependencia
- **Ficha colegios**: Búsqueda individual de establecimientos con comparación comunal

**Datos:**
| Dataset | Registros | Descripción |
|---------|-----------|-------------|
| `resultados_paes` | 306,022 | Puntajes y datos de postulantes |
| `establecimientos` | ~12,000 | Colegios con ubicación, matrícula, dependencia |
| `comunas` | 346 | Regiones, provincias y comunas |

## Contexto: Rankings educativos

Los rankings de "mejores colegios" basados en promedios PAES son cuestionados:

- **Sesgo socioeconómico**: ~70% de los resultados se explican por nivel socioeconómico familiar
- **Invisibilización del talento público**: El 55% del Top 10% NO viene de particulares pagados
- **Validez cuestionada**: El DEMRE advierte que la PAES no mide calidad de establecimientos

### Referencias

- [@elaval - Análisis PAES 2026](https://elaval.github.io/PAES-2026/)
- [CIPER - El ranking del privilegio](https://www.ciperchile.cl/2026/01/06/el-ranking-del-privilegio/)
- [U. Chile - Desigualdad y rankings](https://ingenieria.uchile.cl/noticias/202460/sobre-desigualdad-rankings-y-educacion-publica)

## Tecnología

- [Observable Framework](https://observablehq.com/framework/) - Sitio estático con data loaders
- [DuckDB](https://duckdb.org/) - Base de datos analítica
- [Observable Plot](https://observablehq.com/plot/) - Visualizaciones

## Desarrollo

```bash
# Instalar dependencias
npm install
uv sync

# Desarrollo (localhost:3000)
npm run dev

# Build para producción
npm run build

# Regenerar base de datos
uv run jupyter execute notebooks/paes-2026/raw-data.ipynb
```

## Estructura

```
├── src/
│   ├── index.md              # Landing page
│   └── paes-2026/            # Proyecto PAES
│       ├── index.md          # Ranking
│       ├── top.md            # Top 10%
│       ├── ficha.md          # Búsqueda
│       └── data/             # Data loaders (Python)
├── notebooks/
│   └── paes-2026/
│       └── raw-data.ipynb    # Genera paes.duckdb
├── raw-data/                 # Datos fuente (no en git)
└── paes.duckdb               # Base de datos compilada
```

## Fuentes de Datos

| Fuente | URL | Descripción |
|--------|-----|-------------|
| DEMRE | [portal-transparencia.demre.cl](https://portal-transparencia.demre.cl/portal-base-datos) | Resultados PAES 2026 |
| MINEDUC | [datosabiertos.mineduc.cl](https://datosabiertos.mineduc.cl/directorio-de-establecimientos-educacionales/) | Directorio de Establecimientos |

## Licencia

MIT

---

Hecho con datos por [Datalized](https://datalized.cl/)
