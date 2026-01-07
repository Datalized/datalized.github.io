# PAES - Prueba de Acceso a la Educación Superior (Chile)

## Descripción General

La **PAES** (Prueba de Acceso a la Educación Superior) es el instrumento de evaluación utilizado en Chile para el ingreso a la educación superior. Reemplazó a la antigua PSU (Prueba de Selección Universitaria) a partir del proceso de admisión 2023.

Es administrada por el **DEMRE** (Departamento de Evaluación, Medición y Registro Educacional) de la Universidad de Chile.

## Estructura de Pruebas (Admisión 2026)

### Pruebas Obligatorias

| Prueba | Descripción |
|--------|-------------|
| **Competencia Lectora** | Evalúa comprensión de lectura y habilidades de análisis textual |
| **Competencia Matemática 1 (M1)** | Matemática básica, obligatoria para todos los postulantes |

### Pruebas Electivas

| Prueba | Descripción |
|--------|-------------|
| **Competencia Matemática 2 (M2)** | Matemática avanzada. Obligatoria para ciertas carreras (pondera mínimo 5%) |
| **Ciencias** | Incluye Biología, Física y Química |
| **Historia y Ciencias Sociales** | Contenidos de historia, geografía y ciencias sociales |

## Características Principales

- **Sin descuento por errores**: Las respuestas incorrectas no restan puntaje
- **Dos niveles de matemática**: Permite evaluar mejor las competencias según el área de postulación
- **Modalidades**: PAES Regular (diciembre) y PAES Invierno (julio)

## Escala de Puntajes

| Concepto | Rango |
|----------|-------|
| Puntaje mínimo | 100 |
| Puntaje máximo | 1000 |
| Promedio teórico | 500 |

## Factores de Selección

El proceso de admisión considera múltiples factores:

1. **NEM** (Notas de Enseñanza Media): Promedio de notas convertido a escala 100-1000
2. **Ranking**: Posición relativa del estudiante en su establecimiento
3. **Puntajes PAES**: Resultados de las pruebas rendidas
4. **Ponderaciones**: Cada carrera define los pesos de cada factor

## Fechas Clave - Admisión 2026

| Evento | Fecha |
|--------|-------|
| Rendición PAES Regular | 1-3 diciembre 2025 |
| Publicación de resultados | 5 enero 2026 (08:00 hrs) |
| Apertura postulaciones | 5 enero 2026 (09:00 hrs) |
| Cierre postulaciones | 8 enero 2026 (13:00 hrs) |

### Horarios de Rendición
- Jornada mañana: 09:00 hrs
- Jornada tarde: 15:00 hrs

## Costos de Inscripción (2025)

| Cantidad de pruebas | Costo (CLP) |
|---------------------|-------------|
| 1 prueba | $16.650 |
| 2 pruebas | $30.475 |
| 3+ pruebas | $44.300 |

> **Nota**: Al inscribir M1, se puede inscribir M2 sin costo adicional.

## Estructura de Datos para Base de Datos

### Tabla: `estudiantes`
```sql
CREATE TABLE estudiantes (
    id INTEGER PRIMARY KEY,
    rut VARCHAR(12) UNIQUE,
    nombres VARCHAR(100),
    apellido_paterno VARCHAR(50),
    apellido_materno VARCHAR(50),
    fecha_nacimiento DATE,
    sexo CHAR(1),  -- 'M' o 'F'
    region_id INTEGER,
    comuna_id INTEGER,
    establecimiento_id INTEGER
);
```

### Tabla: `establecimientos`
```sql
CREATE TABLE establecimientos (
    id INTEGER PRIMARY KEY,
    rbd INTEGER UNIQUE,  -- Rol Base de Datos del establecimiento
    nombre VARCHAR(200),
    tipo VARCHAR(50),  -- Municipal, Particular Subvencionado, Particular Pagado
    region_id INTEGER,
    comuna_id INTEGER
);
```

### Tabla: `resultados_paes`
```sql
CREATE TABLE resultados_paes (
    id INTEGER PRIMARY KEY,
    estudiante_id INTEGER,
    proceso_admision INTEGER,  -- Ej: 2026
    puntaje_nem DECIMAL(5,2),
    puntaje_ranking DECIMAL(5,2),
    puntaje_competencia_lectora INTEGER,
    puntaje_matematica_1 INTEGER,
    puntaje_matematica_2 INTEGER,
    puntaje_ciencias INTEGER,
    puntaje_historia INTEGER,
    fecha_rendicion DATE,
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
);
```

### Tabla: `postulaciones`
```sql
CREATE TABLE postulaciones (
    id INTEGER PRIMARY KEY,
    estudiante_id INTEGER,
    proceso_admision INTEGER,
    preferencia INTEGER,  -- 1 a 10
    universidad_id INTEGER,
    carrera_id INTEGER,
    puntaje_ponderado DECIMAL(6,2),
    estado VARCHAR(20),  -- SELECCIONADO, LISTA_ESPERA, NO_SELECCIONADO
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
);
```

### Tabla: `carreras`
```sql
CREATE TABLE carreras (
    id INTEGER PRIMARY KEY,
    codigo INTEGER,
    nombre VARCHAR(200),
    universidad_id INTEGER,
    sede VARCHAR(100),
    vacantes INTEGER,
    ponderacion_nem DECIMAL(4,2),
    ponderacion_ranking DECIMAL(4,2),
    ponderacion_lectora DECIMAL(4,2),
    ponderacion_m1 DECIMAL(4,2),
    ponderacion_m2 DECIMAL(4,2),
    ponderacion_ciencias DECIMAL(4,2),
    ponderacion_historia DECIMAL(4,2),
    puntaje_corte_anterior INTEGER
);
```

## Fuentes de Datos

- **DEMRE**: [demre.cl](https://demre.cl) - Informes técnicos y resultados
- **Acceso Mineduc**: [acceso.mineduc.cl](https://acceso.mineduc.cl) - Portal oficial de postulaciones
- **Datos Abiertos**: [datos.gob.cl](https://datos.gob.cl) - Datasets públicos

## Referencias

- Departamento de Evaluación, Medición y Registro Educacional (DEMRE), Universidad de Chile
- Ministerio de Educación de Chile (MINEDUC)
