---
title: PAES 2026 - Metodología
toc: true
style: styles.css
head: |
  <link rel="canonical" href="https://public.datalized.cl/paes-2026/metodologia">
  <meta name="description" content="Metodología y fuentes de datos del análisis PAES 2026. Documentación técnica sobre la extracción, procesamiento y filtros aplicados.">
  <meta property="og:title" content="PAES 2026 - Metodología">
  <meta property="og:description" content="Metodología y fuentes de datos del análisis PAES 2026.">
  <meta property="og:url" content="https://public.datalized.cl/paes-2026/metodologia">
  <meta property="og:type" content="website">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-G4W566JJXE"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-G4W566JJXE');</script>
---

# Metodología y Datos

Este proyecto analiza los resultados de la **PAES 2026** (Prueba de Acceso a la Educación Superior) de Chile. Aquí documentamos las fuentes de datos, el proceso de extracción y los criterios de filtrado aplicados.

## Qué es la PAES

La **PAES** es el instrumento de evaluación utilizado en Chile para el ingreso a la educación superior, administrado por el **DEMRE** (Departamento de Evaluación, Medición y Registro Educacional) de la Universidad de Chile.

### Pruebas evaluadas

| Prueba | Tipo | Descripción |
|--------|------|-------------|
| **Competencia Lectora** | Obligatoria | Comprensión de lectura y análisis textual |
| **Matemática 1 (M1)** | Obligatoria | Matemática básica |
| **Matemática 2 (M2)** | Electiva | Matemática avanzada |
| **Ciencias** | Electiva | Biología, Física o Química |
| **Historia y Cs. Sociales** | Electiva | Historia, geografía y ciencias sociales |

### Escala de puntajes

- **Mínimo**: 100 puntos
- **Máximo**: 1000 puntos
- **Promedio teórico**: 500 puntos

## Fuentes de datos

Los datos provienen de dos fuentes oficiales del Estado de Chile:

| Fuente | Descripción | Enlace |
|--------|-------------|--------|
| **DEMRE** | Resultados PAES 2026 (306,022 postulantes) | [portal-transparencia.demre.cl](https://portal-transparencia.demre.cl/portal-base-datos) |
| **MINEDUC** | Directorio de Establecimientos 2025 (~12,000 colegios) | [datosabiertos.mineduc.cl](https://datosabiertos.mineduc.cl/directorio-de-establecimientos-educacionales/) |

## Pipeline de datos

El proceso de extracción y transformación sigue este flujo:

```
raw-data/           →  Notebook (Jupyter)  →  paes.duckdb  →  Data Loaders  →  JSON
(CSV, Excel)           (Python + DuckDB)      (Base datos)    (Python)         (Web)
```

### Datasets generados

| Tabla | Registros | Descripción |
|-------|-----------|-------------|
| `resultados_paes` | 306,022 | Puntajes y datos de cada postulante |
| `establecimientos` | ~12,000 | Colegios con ubicación, matrícula, dependencia |
| `comunas` | 346 | Regiones, provincias y comunas de Chile |

## Filtros aplicados

Para calcular rankings y estadísticas, aplicamos los **criterios oficiales del DEMRE** que excluyen casos especiales:

### Filtro principal (WHERE_OFICIAL)

```sql run=false
WHERE puntaje_nem > 0          -- Tiene NEM válido
  AND puntaje_ranking > 0      -- Tiene ranking válido
  AND mate1_reg > 0            -- Rindió Matemática 1
  AND lectora_reg > 0          -- Rindió Competencia Lectora
  AND rindio_anterior = false  -- Primera vez que rinde
  AND situacion_egreso = 1     -- Alumno regular nacional
```

### Por qué estos filtros

| Filtro | Razón |
|--------|-------|
| `puntaje_nem > 0` | Excluye postulantes sin notas de enseñanza media |
| `rindio_anterior = false` | Solo postulantes del proceso actual (no repitentes) |
| `situacion_egreso = 1` | Solo egresados regulares (excluye validación de estudios y extranjeros) |

### Filtro de significancia estadística

Para rankings de establecimientos:

```sql run=false
HAVING COUNT(*) >= 5  -- Mínimo 5 estudiantes por establecimiento
```

Esto evita que colegios con muy pocos postulantes aparezcan en posiciones extremas del ranking por azar estadístico.

## Cálculo del Top 10%

El umbral del **Top 10%** se calcula sobre el promedio de Competencia Lectora y Matemática 1:

```sql run=false
PERCENTILE_CONT(0.9) WITHIN GROUP (
  ORDER BY (lectora_reg + mate1_reg) / 2
)
```

## Advertencias importantes

<div class="warning" label="Limitaciones de los rankings">

El **DEMRE advierte explícitamente** que la PAES no fue diseñada para medir la calidad educativa de los establecimientos. Los rankings basados en promedios PAES presentan sesgos importantes:

- **Sesgo socioeconómico**: ~70% de los resultados se explican por nivel socioeconómico familiar
- **No miden valor agregado**: Un colegio con estudiantes de alto NSE puede tener promedios altos sin aportar valor educativo
- **Autoselección**: Los colegios selectivos filtran estudiantes antes del egreso

</div>

## Referencias

- [DEMRE - Portal de Transparencia](https://portal-transparencia.demre.cl/)
- [MINEDUC - Datos Abiertos](https://datosabiertos.mineduc.cl/)
- [CIPER - El ranking del privilegio](https://www.ciperchile.cl/2026/01/06/el-ranking-del-privilegio/)
