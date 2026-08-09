"""Auditoria: ¿los NaN de Aprender son ceros o valores suprimidos?

Importa porque en 06 se hizo fillna(0) al calcular proporciones. Si los NaN
fueran supresiones por confidencialidad, ese fillna convertiria "dato oculto"
en "no hay nadie", justo en las categorias mas chicas.
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]

BLOQUES = ["ap03_", "sobreedad_", "repitencia_", "NSE_nivel_", "clima_",
           "migracion_", "ap19_", "ap27_", "ldesemp_"]
NO_RESPUESTA = {"Blanco", "No_disponible", "Multimarca", "No_corresponde",
                "_Blanco", "_No_disponible"}


def a_numero(s):
    return pd.to_numeric(
        s.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce")


df = pd.read_csv(RAW / "ap2024_Desempenos_de_Lengua.csv", sep=";",
                 encoding="latin-1", dtype=str)
for c in df.columns:
    if c not in CLAVES:
        df[c] = a_numero(df[c])

total_fila = df[[c for c in df.columns if c.startswith("ap03_")]].sum(axis=1)

print("=" * 72)
print("TEST 1: ¿cada bloque suma el total de la fila?")
print("=" * 72)
for b in BLOQUES:
    cols = [c for c in df.columns if c.startswith(b)]
    suma = df[cols].sum(axis=1)
    dif = (suma - total_fila).abs()
    print(f"  {b:14s} filas que cierran (±0.5): {(dif < 0.5).sum():>5,}/{len(df):,}"
          f" | brecha max: {dif.max():.2f}")

print()
print("=" * 72)
print("TEST 2: ¿hay un piso en los valores? (supresion de celdas chicas)")
print("=" * 72)
cols_validas = [c for c in df.columns
                if any(c.startswith(b) for b in BLOQUES)
                and c.split("_", 1)[-1] not in NO_RESPUESTA]
valores = df[cols_validas].stack()
print(f"  valores no nulos: {len(valores):,}")
print(f"  minimo: {valores.min():.4f} | p1: {valores.quantile(.01):.3f} | "
      f"mediana: {valores.median():.1f}")
for umbral in (1, 2, 3, 5):
    n = (valores < umbral).sum()
    print(f"  valores menores a {umbral}: {n:>6,} ({n/len(valores):.2%})")

print()
print("=" * 72)
print("TEST 3: las categorias raras (¿NaN = cero?)")
print("=" * 72)
for col in ["ap03_X", "repitencia_Repitió_2_veces_o_más",
            "sobreedad_3_años_o_más_de_sobreedad_20_años_o_más_30Jun",
            "ap19_No_hay_libros_en_formato_papel"]:
    if col in df.columns:
        s = df[col]
        print(f"  {col[:52]:54s} NaN: {s.isna().sum():>5,}/{len(s):,} "
              f"| suma: {s.sum():>10,.1f}")

print()
print("=" * 72)
print("TEST 4: ¿donde se concentran los NaN?")
print("=" * 72)
nr = [c for c in df.columns if any(c.startswith(b) for b in BLOQUES)
      and c.split("_", 1)[-1] in NO_RESPUESTA]
print(f"  columnas de no-respuesta (Blanco/No_disp/Multimarca): {len(nr)}")
print(f"    celdas NaN: {df[nr].isna().sum().sum():,} de {df[nr].size:,} "
      f"({df[nr].isna().sum().sum()/df[nr].size:.1%})")
print(f"  columnas de respuesta valida: {len(cols_validas)}")
print(f"    celdas NaN: {df[cols_validas].isna().sum().sum():,} de "
      f"{df[cols_validas].size:,} "
      f"({df[cols_validas].isna().sum().sum()/df[cols_validas].size:.1%})")
