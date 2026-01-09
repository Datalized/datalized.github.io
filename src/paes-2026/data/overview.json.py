#!/usr/bin/env python3
"""Estadísticas generales del dataset PAES 2026 (sin filtros)."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

# === KPIs GENERALES (sin filtros) ===

# Total de postulantes
total_postulantes = con.execute("SELECT COUNT(*) FROM resultados_paes").fetchone()[0]

# Total de establecimientos con postulantes
total_establecimientos = con.execute("""
    SELECT COUNT(DISTINCT rbd) FROM resultados_paes WHERE rbd IS NOT NULL
""").fetchone()[0]

# Postulantes por prueba rendida
postulantes_por_prueba = con.execute("""
    SELECT
        'Lectora' as prueba, COUNT(lectora_reg) as total FROM resultados_paes WHERE lectora_reg > 0
    UNION ALL
    SELECT 'Matemática 1', COUNT(mate1_reg) FROM resultados_paes WHERE mate1_reg > 0
    UNION ALL
    SELECT 'Matemática 2', COUNT(mate2_reg) FROM resultados_paes WHERE mate2_reg > 0
    UNION ALL
    SELECT 'Historia', COUNT(historia_reg) FROM resultados_paes WHERE historia_reg > 0
    UNION ALL
    SELECT 'Ciencias', COUNT(ciencias_reg) FROM resultados_paes WHERE ciencias_reg > 0
""").fetchall()

# === ESTADÍSTICAS POR PRUEBA ===

pruebas = [
    ('lectora_reg', 'Competencia Lectora'),
    ('mate1_reg', 'Matemática 1'),
    ('mate2_reg', 'Matemática 2'),
    ('historia_reg', 'Historia y Cs. Sociales'),
    ('ciencias_reg', 'Ciencias')
]

stats_pruebas = []
for col, nombre in pruebas:
    stats = con.execute(f"""
        SELECT
            COUNT({col}) as n,
            ROUND(AVG({col}), 1) as promedio,
            ROUND(STDDEV({col}), 1) as desviacion,
            MIN({col}) as minimo,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {col}) as p25,
            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY {col}) as mediana,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {col}) as p75,
            PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY {col}) as p90,
            MAX({col}) as maximo,
            SUM(CASE WHEN {col} = 1000 THEN 1 ELSE 0 END) as puntaje_maximo
        FROM resultados_paes
        WHERE {col} > 0
    """).fetchone()

    stats_pruebas.append({
        "prueba": nombre,
        "columna": col,
        "n": stats[0],
        "promedio": stats[1],
        "desviacion": stats[2],
        "minimo": stats[3],
        "p25": round(stats[4]) if stats[4] else None,
        "mediana": round(stats[5]) if stats[5] else None,
        "p75": round(stats[6]) if stats[6] else None,
        "p90": round(stats[7]) if stats[7] else None,
        "maximo": stats[8],
        "puntaje_maximo": stats[9],
    })

# === DISTRIBUCIÓN POR DEPENDENCIA ===

distribucion_dependencia = []
for col, nombre in pruebas:
    dist = con.execute(f"""
        SELECT
            d.descripcion as dependencia,
            COUNT({col}) as n,
            ROUND(AVG({col}), 1) as promedio,
            ROUND(STDDEV({col}), 1) as desviacion,
            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY {col}) as mediana
        FROM resultados_paes r
        JOIN ref_dependencia d ON r.dependencia = d.codigo
        WHERE {col} > 0
        GROUP BY d.descripcion
        ORDER BY promedio DESC
    """).fetchall()

    for row in dist:
        distribucion_dependencia.append({
            "prueba": nombre,
            "dependencia": row[0].title(),
            "n": row[1],
            "promedio": row[2],
            "desviacion": row[3],
            "mediana": round(row[4]) if row[4] else None
        })

# === DISTRIBUCIÓN POR RAMA EDUCACIONAL ===

distribucion_rama = con.execute("""
    SELECT
        CASE
            WHEN rama LIKE 'H%' THEN 'Humanista-Científico'
            WHEN rama LIKE 'T%' THEN 'Técnico-Profesional'
            ELSE 'Otro'
        END as tipo_rama,
        COUNT(*) as n,
        ROUND(AVG(lectora_reg), 1) as prom_lectora,
        ROUND(AVG(mate1_reg), 1) as prom_mate1
    FROM resultados_paes
    WHERE lectora_reg > 0 AND mate1_reg > 0
    GROUP BY tipo_rama
    ORDER BY n DESC
""").fetchall()

# === HISTOGRAMAS DE PUNTAJES ===

histogramas = []
for col, nombre in pruebas:
    # Obtener histograma
    hist = con.execute(f"""
        SELECT
            FLOOR({col} / 50) * 50 as rango_inicio,
            COUNT(*) as frecuencia
        FROM resultados_paes
        WHERE {col} > 0
        GROUP BY rango_inicio
        ORDER BY rango_inicio
    """).fetchall()

    # Obtener promedio y P90 para esta prueba
    stats = con.execute(f"""
        SELECT
            ROUND(AVG({col}), 0) as promedio,
            ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY {col}), 0) as p90
        FROM resultados_paes
        WHERE {col} > 0
    """).fetchone()

    histogramas.append({
        "prueba": nombre,
        "promedio": int(stats[0]),
        "p90": int(stats[1]),
        "datos": [{"rango": int(r[0]), "frecuencia": r[1]} for r in hist]
    })

# === TOP 10 PUNTAJES MÁXIMOS ===

puntajes_maximos = con.execute("""
    SELECT
        'Lectora' as prueba,
        COUNT(lectora_reg) as total,
        SUM(CASE WHEN lectora_reg = 1000 THEN 1 ELSE 0 END) as con_1000,
        ROUND(100.0 * SUM(CASE WHEN lectora_reg = 1000 THEN 1 ELSE 0 END) / COUNT(lectora_reg), 3) as pct
    FROM resultados_paes WHERE lectora_reg > 0
    UNION ALL
    SELECT 'Matemática 1', COUNT(mate1_reg),
        SUM(CASE WHEN mate1_reg = 1000 THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN mate1_reg = 1000 THEN 1 ELSE 0 END) / COUNT(mate1_reg), 3)
    FROM resultados_paes WHERE mate1_reg > 0
    UNION ALL
    SELECT 'Matemática 2', COUNT(mate2_reg),
        SUM(CASE WHEN mate2_reg = 1000 THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN mate2_reg = 1000 THEN 1 ELSE 0 END) / COUNT(mate2_reg), 3)
    FROM resultados_paes WHERE mate2_reg > 0
    UNION ALL
    SELECT 'Historia', COUNT(historia_reg),
        SUM(CASE WHEN historia_reg = 1000 THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN historia_reg = 1000 THEN 1 ELSE 0 END) / COUNT(historia_reg), 3)
    FROM resultados_paes WHERE historia_reg > 0
    UNION ALL
    SELECT 'Ciencias', COUNT(ciencias_reg),
        SUM(CASE WHEN ciencias_reg = 1000 THEN 1 ELSE 0 END),
        ROUND(100.0 * SUM(CASE WHEN ciencias_reg = 1000 THEN 1 ELSE 0 END) / COUNT(ciencias_reg), 3)
    FROM resultados_paes WHERE ciencias_reg > 0
""").fetchall()

# === RESULTADO FINAL ===

result = {
    "kpis": {
        "total_postulantes": total_postulantes,
        "total_establecimientos": total_establecimientos,
    },
    "postulantes_por_prueba": [
        {"prueba": r[0], "total": r[1]} for r in postulantes_por_prueba
    ],
    "stats_pruebas": stats_pruebas,
    "distribucion_dependencia": distribucion_dependencia,
    "distribucion_rama": [
        {"rama": r[0], "n": r[1], "prom_lectora": r[2], "prom_mate1": r[3]}
        for r in distribucion_rama
    ],
    "histogramas": histogramas,
    "puntajes_maximos": [
        {"prueba": r[0], "total": r[1], "con_1000": r[2], "pct": r[3]}
        for r in puntajes_maximos
    ]
}

json.dump(result, sys.stdout)
