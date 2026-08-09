"""Paso 2: inventario de bloques de preguntas de Aprender 2024.

Las columnas se llaman <pregunta>_<categoria de respuesta>. Agrupandolas por
pregunta se reconstruye el cuestionario y se puede identificar cada bloque por
sus opciones de respuesta, sin depender del diccionario (que es de 2022 y usa
otra numeracion).
"""

import re
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]

cols = pd.read_csv(RAW / "ap2024_Desempenos_de_Lengua.csv", sep=";",
                   encoding="latin-1", nrows=0).columns.tolist()

bloques = {}
for c in cols:
    if c in CLAVES:
        continue
    m = re.match(r"^(ap\d+[a-z]?|[A-Za-z_]+?)_(.+)$", c)
    prefijo = m.group(1) if m else c
    bloques.setdefault(prefijo, []).append(m.group(2) if m else "")

print(f"columnas: {len(cols)} | bloques de pregunta: {len(bloques)}\n")
for prefijo, cats in bloques.items():
    utiles = [c for c in cats
              if c not in ("Blanco", "No_disponible", "Multimarca", "No_corresponde")]
    print(f"{prefijo:22s} ({len(cats):>2}) {' / '.join(utiles)[:150]}")
