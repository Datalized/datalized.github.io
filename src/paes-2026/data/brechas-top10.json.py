#!/usr/bin/env python3
"""Datos para análisis del Top 10% nacional."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

WHERE_OFICIAL = """
    r.puntaje_nem > 0 AND r.puntaje_ranking > 0
    AND r.mate1_reg > 0 AND r.lectora_reg > 0
    AND r.rindio_anterior = false AND r.situacion_egreso = 1
"""

# Umbrales
thresholds = con.execute(f"""
    SELECT
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2) as p90,
        PERCENTILE_CONT(0.8) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2) as p80
    FROM resultados_paes r WHERE {WHERE_OFICIAL}
""").fetchone()

p90, p80 = thresholds

# Origen del top 10% por dependencia
origen_top10 = con.execute(f"""
    SELECT
        d.descripcion as dependencia,
        COUNT(*) as estudiantes,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as porcentaje
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE (r.lectora_reg + r.mate1_reg)/2 >= {p90} AND {WHERE_OFICIAL}
    GROUP BY d.descripcion
    ORDER BY estudiantes DESC
""").fetchall()

# Top escuelas con más estudiantes en el top 10%
escuelas_top10 = con.execute(f"""
    SELECT
        e.nombre as establecimiento,
        d.descripcion as dependencia,
        c.comuna,
        COUNT(*) as estudiantes_top10,
        (SELECT COUNT(*) FROM resultados_paes r2
         WHERE r2.rbd = e.rbd AND {WHERE_OFICIAL.replace('r.', 'r2.')}) as total_estudiantes
    FROM resultados_paes r
    JOIN establecimientos e ON r.rbd = e.rbd
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
    WHERE (r.lectora_reg + r.mate1_reg)/2 >= {p90} AND {WHERE_OFICIAL}
    GROUP BY e.rbd, e.nombre, d.descripcion, c.comuna
    ORDER BY estudiantes_top10 DESC
""").fetchall()

# Probabilidad de top 10% por dependencia
prob_top10 = con.execute(f"""
    SELECT
        d.descripcion as dependencia,
        COUNT(*) as total,
        SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) as en_top10,
        ROUND(100.0 * SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) / COUNT(*), 1) as pct_top10
    FROM resultados_paes r
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    WHERE {WHERE_OFICIAL}
    GROUP BY d.descripcion
    ORDER BY pct_top10 DESC
""").fetchall()

# Total en top 10%
total_top10 = con.execute(f"""
    SELECT COUNT(*) FROM resultados_paes r
    WHERE (r.lectora_reg + r.mate1_reg)/2 >= {p90} AND {WHERE_OFICIAL}
""").fetchone()[0]

result = {
    "umbrales": {"p90": round(p90, 0), "p80": round(p80, 0)},
    "total_top10": total_top10,
    "origen_top10": [
        {"dependencia": r[0].title(), "estudiantes": r[1], "porcentaje": r[2]}
        for r in origen_top10
    ],
    "escuelas_top10": [
        {"establecimiento": r[0].title(), "dependencia": r[1].title(), "comuna": r[2].title(),
         "estudiantes_top10": r[3], "total_estudiantes": r[4]}
        for r in escuelas_top10
    ],
    "prob_top10": [
        {"dependencia": r[0].title(), "total": r[1], "en_top10": r[2], "pct_top10": r[3]}
        for r in prob_top10
    ]
}

json.dump(result, sys.stdout)
