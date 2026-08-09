"""Paso 1d: el join real es lengua + matematica. ¿Cuanto difieren entre si?

solo_cc queda descartada (es la base del cuestionario complementario, con su
propio factor de expansion). Falta cuantificar la discrepancia del par que si
vamos a unir.
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
LECTURA = {"sep": ";", "encoding": "latin-1", "dtype": str}
CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]


def a_numero(serie):
    return pd.to_numeric(
        serie.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )


def cargar(nombre):
    df = pd.read_csv(RAW / nombre, **LECTURA)
    for col in df.columns:
        if col not in CLAVES:
            df[col] = a_numero(df[col])
    return df.sort_values(CLAVES).reset_index(drop=True)


lengua = cargar("ap2024_Desempenos_de_Lengua.csv")
matematica = cargar("ap2024_Desempenos_de_Matematica.csv")

tot_l = lengua[[c for c in lengua.columns if c.startswith("ap03_")]].sum(axis=1)
tot_m = matematica[[c for c in matematica.columns if c.startswith("ap03_")]].sum(axis=1)

dif = (tot_l - tot_m).abs() / tot_l.replace(0, pd.NA) * 100

print("=" * 70)
print("LENGUA vs MATEMATICA (el par que vamos a unir)")
print("=" * 70)
print(f"  total nacional lengua    : {tot_l.sum():>12,.1f}")
print(f"  total nacional matematica: {tot_m.sum():>12,.1f}")
print(f"  diferencia nacional      : {abs(tot_l.sum() - tot_m.sum()):>12,.1f} "
      f"({abs(tot_l.sum() - tot_m.sum()) / tot_l.sum() * 100:.4f}%)")
print()
print(f"  discrepancia por fila -> mediana: {dif.median():.2f}%")
print(f"                           p90    : {dif.quantile(0.90):.2f}%")
print(f"                           p99    : {dif.quantile(0.99):.2f}%")
print(f"                           maxima : {dif.max():.2f}%")
print()
for umbral in (1, 5, 10):
    n = (dif > umbral).sum()
    print(f"  filas con discrepancia >{umbral:>2}%: {n:>4,} de {len(dif):,} "
          f"({n / len(dif):.1%})")

peores = pd.DataFrame({
    "clave": lengua[CLAVES].astype(str).agg(" | ".join, axis=1),
    "lengua": tot_l,
    "matematica": tot_m,
    "dif_%": dif,
}).nlargest(5, "dif_%")
print()
print("  Las 5 peores:")
print(peores.to_string(index=False, float_format=lambda x: f"{x:,.1f}"))
