"""¿Los bloques que no cierran son preguntas condicionadas (skip pattern)?

Si ap27 (cuantas faltas) solo se le pregunta a quien contesto que si en ap26,
la suma de ap27 tiene que coincidir con ap26_Si, no con el total de la fila.
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]


def a_numero(s):
    return pd.to_numeric(
        s.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce")


df = pd.read_csv(RAW / "ap2024_Desempenos_de_Lengua.csv", sep=";",
                 encoding="latin-1", dtype=str)
for c in df.columns:
    if c not in CLAVES:
        df[c] = a_numero(df[c])


def suma(prefijo):
    return df[[c for c in df.columns if c.startswith(prefijo)]].sum(axis=1)


total = suma("ap03_")

print("=" * 72)
print("¿ap27 (faltas) esta condicionada por ap26 (Si/No)?")
print("=" * 72)
print(f"  ap26 categorias: {[c for c in df.columns if c.startswith('ap26_')]}")
ap26_si = df.get("ap26_Sí")
ap27 = suma("ap27_")
print(f"  suma ap26_Si : {ap26_si.sum():>12,.1f}")
print(f"  suma ap27    : {ap27.sum():>12,.1f}")
print(f"  total fila   : {total.sum():>12,.1f}")
dif = (ap27 - ap26_si).abs()
print(f"  filas donde ap27 == ap26_Si (±0.5): {(dif < 0.5).sum():,}/{len(df):,}")

print()
print("=" * 72)
print("COBERTURA REAL DE CADA BLOQUE (suma del bloque / total de la fila)")
print("=" * 72)
for b, nombre in [("ap03_", "sexo"), ("sobreedad_", "sobreedad"),
                  ("repitencia_", "repitencia"), ("NSE_nivel_", "nse"),
                  ("ap19_", "libros"), ("ldesemp_", "desemp_lengua"),
                  ("ap27_", "inasistencias"), ("clima_", "clima_escolar"),
                  ("migracion_", "migracion"), ("ap31_", "horas_estudio"),
                  ("ap12_", "tamano_hogar"), ("ap24_", "jardin"),
                  ("edadA_junio2024_", "edad"), ("Nivel_Ed_Madre_", "educ_madre")]:
    cob = suma(b) / total
    print(f"  {nombre:16s} mediana: {cob.median():>7.1%} | "
          f"min: {cob.min():>6.1%} | max: {cob.max():>6.1%}")
