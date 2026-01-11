#!/usr/bin/env python3
"""Distribución de puntajes por establecimiento - histogramas pre-computados."""
import duckdb
import json
import sys
from collections import defaultdict

con = duckdb.connect("paes.duckdb", read_only=True)

WHERE_OFICIAL = """
    r.puntaje_nem > 0 AND r.puntaje_ranking > 0
    AND r.mate1_reg > 0 AND r.lectora_reg > 0
    AND r.rindio_anterior = false AND r.situacion_egreso = 1
"""

BIN_SIZE = 20  # Bins de 20 puntos

# Obtener puntajes individuales agrupados por rbd
result = con.execute(f"""
    SELECT
        rbd,
        (FLOOR((lectora_reg + mate1_reg) / 2.0 / {BIN_SIZE}) * {BIN_SIZE})::INTEGER as bin_lm,
        (FLOOR(lectora_reg / {BIN_SIZE}) * {BIN_SIZE})::INTEGER as bin_l,
        (FLOOR(mate1_reg / {BIN_SIZE}) * {BIN_SIZE})::INTEGER as bin_m,
        COUNT(*) as cnt
    FROM resultados_paes r
    WHERE {WHERE_OFICIAL}
    GROUP BY rbd, bin_lm, bin_l, bin_m
    ORDER BY rbd, bin_lm
""").fetchall()

# Agrupar por rbd
data = defaultdict(lambda: {"lm": defaultdict(int), "l": defaultdict(int), "m": defaultdict(int)})

for row in result:
    rbd, bin_lm, bin_l, bin_m, cnt = row
    if rbd is None:
        continue
    rbd_str = str(rbd)
    data[rbd_str]["lm"][bin_lm] += cnt
    data[rbd_str]["l"][bin_l] += cnt
    data[rbd_str]["m"][bin_m] += cnt

# Convertir a listas ordenadas [[bin, cnt], ...]
output = {}
for rbd, hists in data.items():
    output[rbd] = {
        "lm": sorted([[b, c] for b, c in hists["lm"].items()]),
        "l": sorted([[b, c] for b, c in hists["l"].items()]),
        "m": sorted([[b, c] for b, c in hists["m"].items()])
    }

json.dump(output, sys.stdout)
