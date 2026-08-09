"""Paso 1: entender qué son realmente las tres bases de Aprender 2024.

Antes de unir nada hay que responder tres preguntas:
  1. ¿Las tres bases describen las mismas filas? (mismas claves territoriales)
  2. ¿Las columnas del cuestionario están repetidas idénticas en las tres?
  3. ¿Qué aporta cada una que las otras no tengan?

De la respuesta depende si hay que unir (merge) o apilar (concat), que son
cosas distintas y dan resultados distintos.
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# Los CSV del Ministerio vienen en formato europeo: separador ';', encoding
# latin-1 y coma decimal. Sin declararlo, pandas devuelve una sola columna.
LECTURA = {"sep": ";", "encoding": "latin-1", "decimal": ","}

CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]

BASES = {
    "lengua": "ap2024_Desempenos_de_Lengua.csv",
    "matematica": "ap2024_Desempenos_de_Matematica.csv",
    "solo_cc": "ap2024_Solo_CC.csv",
}


def cargar(nombre_archivo):
    return pd.read_csv(RAW / nombre_archivo, **LECTURA)


def main():
    dfs = {k: cargar(v) for k, v in BASES.items()}

    print("=" * 70)
    print("1. FORMA DE CADA BASE")
    print("=" * 70)
    for nombre, df in dfs.items():
        print(f"  {nombre:12s} {df.shape[0]:>6,} filas x {df.shape[1]:>5,} columnas")

    print()
    print("=" * 70)
    print("2. ¿LAS TRES DESCRIBEN LAS MISMAS FILAS?")
    print("=" * 70)
    claves = {k: set(map(tuple, df[CLAVES].values)) for k, df in dfs.items()}
    base = claves["lengua"]
    for nombre, s in claves.items():
        print(f"  {nombre:12s} {len(s):>6,} claves unicas | "
              f"iguales a lengua: {s == base}")
    print(f"  interseccion de las tres: {len(base & claves['matematica'] & claves['solo_cc']):,}")
    print(f"  claves duplicadas dentro de lengua: "
          f"{dfs['lengua'].duplicated(subset=CLAVES).sum()}")

    print()
    print("=" * 70)
    print("3. ¿QUE COLUMNAS COMPARTEN Y CUALES SON PROPIAS?")
    print("=" * 70)
    cols = {k: set(df.columns) for k, df in dfs.items()}
    comunes = cols["lengua"] & cols["matematica"] & cols["solo_cc"]
    print(f"  columnas comunes a las tres: {len(comunes):,}")
    for nombre, c in cols.items():
        propias = c - comunes
        print(f"  propias de {nombre:12s}: {len(propias):>3}  {sorted(propias)}")

    print()
    print("=" * 70)
    print("4. LAS COLUMNAS COMPARTIDAS, ¿TIENEN LOS MISMOS VALORES?")
    print("=" * 70)
    # Ordenamos por las claves para comparar fila a fila con la misma referencia.
    a = dfs["lengua"].sort_values(CLAVES).reset_index(drop=True)
    b = dfs["matematica"].sort_values(CLAVES).reset_index(drop=True)
    c = dfs["solo_cc"].sort_values(CLAVES).reset_index(drop=True)

    muestra = sorted(comunes - set(CLAVES))
    iguales_lm, distintas_lm = [], []
    for col in muestra:
        if a[col].equals(b[col]):
            iguales_lm.append(col)
        else:
            distintas_lm.append(col)
    print(f"  lengua vs matematica -> identicas: {len(iguales_lm):,} | "
          f"distintas: {len(distintas_lm):,}")
    print(f"    ejemplos de distintas: {distintas_lm[:8]}")

    iguales_lc = sum(1 for col in muestra if a[col].equals(c[col]))
    print(f"  lengua vs solo_cc    -> identicas: {iguales_lc:,} | "
          f"distintas: {len(muestra) - iguales_lc:,}")

    if distintas_lm:
        col = distintas_lm[0]
        comparacion = pd.DataFrame({
            "clave": a[CLAVES].astype(str).agg(" | ".join, axis=1),
            "lengua": a[col],
            "matematica": b[col],
            "solo_cc": c[col],
        })
        print()
        print(f"  Mirando de cerca '{col}' (primeras 5 filas):")
        print(comparacion.head().to_string(index=False))


if __name__ == "__main__":
    main()
