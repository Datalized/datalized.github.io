#!/usr/bin/env python3
"""Ranking de escuelas con métricas completas."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

WHERE_OFICIAL = """
    r.puntaje_nem > 0 AND r.puntaje_ranking > 0
    AND r.mate1_reg > 0 AND r.lectora_reg > 0
    AND r.rindio_anterior = false AND r.situacion_egreso = 1
"""

# Calcular umbral top 10%
p90 = con.execute(f"""
    SELECT PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY (lectora_reg + mate1_reg)/2)
    FROM resultados_paes r WHERE {WHERE_OFICIAL}
""").fetchone()[0]

result = con.execute(f"""
    SELECT
        e.rbd,
        e.nombre as establecimiento,
        d.descripcion as dependencia,
        c.cod_region,
        c.region,
        c.comuna,
        e.latitud,
        e.longitud,
        COUNT(*) as cantidad,
        ROUND(AVG(r.lectora_reg), 1) as prom_lectora,
        ROUND(AVG(r.mate1_reg), 1) as prom_mate1,
        ROUND((AVG(r.lectora_reg) + AVG(r.mate1_reg)) / 2, 1) as prom_lect_mate,
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p25,
        ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as mediana,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY (r.lectora_reg + r.mate1_reg)/2), 0) as p75,
        SUM(CASE WHEN (r.lectora_reg + r.mate1_reg)/2 >= {p90} THEN 1 ELSE 0 END) as en_top10
    FROM resultados_paes r
    JOIN establecimientos e ON r.rbd = e.rbd
    JOIN ref_dependencia d ON r.dependencia = d.codigo
    LEFT JOIN comunas c ON r.cod_comuna = c.cod_comuna
    WHERE {WHERE_OFICIAL}
    GROUP BY e.rbd, e.nombre, d.descripcion, c.cod_region, c.region, c.comuna, e.latitud, e.longitud
    HAVING COUNT(*) >= 5
    ORDER BY prom_lect_mate DESC
""").fetchall()

# Agregar ranking nacional (ya viene ordenado por prom_lect_mate DESC)
data = [
    {
        "rbd": r[0], "establecimiento": r[1], "dependencia": r[2],
        "cod_region": r[3], "region": r[4], "comuna": r[5],
        "lat": r[6], "lon": r[7], "cantidad": r[8],
        "prom_lectora": r[9], "prom_mate1": r[10], "prom_lect_mate": r[11],
        "p25": r[12], "mediana": r[13], "p75": r[14], "en_top10": r[15],
        "rank_nacional": i + 1
    }
    for i, r in enumerate(result)
]

# Calcular ranking por comuna
por_comuna = {}
for e in data:
    comuna = e["comuna"]
    if comuna not in por_comuna:
        por_comuna[comuna] = []
    por_comuna[comuna].append(e)

for escuelas in por_comuna.values():
    escuelas.sort(key=lambda x: x["rank_nacional"])
    for i, e in enumerate(escuelas):
        e["rank_comuna"] = i + 1

json.dump(data, sys.stdout)
