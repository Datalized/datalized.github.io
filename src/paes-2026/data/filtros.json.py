#!/usr/bin/env python3
"""Opciones para los selectores de filtros."""
import duckdb
import json
import sys

con = duckdb.connect("paes.duckdb", read_only=True)

# Orden geográfico norte-sur
ORDEN_REGIONES = {
    15: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 13: 7, 6: 8,
    7: 9, 16: 10, 8: 11, 9: 12, 14: 13, 10: 14, 11: 15, 12: 16
}

regiones = con.execute("""
    SELECT DISTINCT cod_region, region FROM comunas ORDER BY cod_region
""").fetchall()
regiones_ordenadas = sorted(regiones, key=lambda r: ORDEN_REGIONES.get(r[0], 99))

comunas = con.execute("""
    SELECT cod_comuna, comuna FROM comunas ORDER BY comuna
""").fetchall()

dependencias = con.execute("SELECT codigo, descripcion FROM ref_dependencia ORDER BY codigo").fetchall()

result = {
    "regiones": [{"codigo": r[0], "nombre": r[1].title()} for r in regiones_ordenadas],
    "comunas": [{"codigo": r[0], "nombre": r[1].title()} for r in comunas],
    "dependencias": [{"codigo": r[0], "nombre": r[1].title()} for r in dependencias]
}

json.dump(result, sys.stdout)
