"""Paso 1c: cerrar el diagnostico de Aprender antes de construir nada.

Dos preguntas pendientes:
  1. ¿El bloque de desempeño (ldesemp / mdesemp) cubre a la misma poblacion
     que el cuestionario dentro de su propia base? Si si, se puede normalizar
     todo a proporciones por base y unir las proporciones sin mezclar
     denominadores.
  2. ¿De donde sale la fila con 50,7% de diferencia entre bases? La sospecha
     es que son departamentos con muy pocos estudiantes.
"""

from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
LECTURA = {"sep": ";", "encoding": "latin-1", "dtype": str}
CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]

BASES = {
    "lengua": "ap2024_Desempenos_de_Lengua.csv",
    "matematica": "ap2024_Desempenos_de_Matematica.csv",
    "solo_cc": "ap2024_Solo_CC.csv",
}


def a_numero(serie):
    return pd.to_numeric(
        serie.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )


def cargar_numerico(nombre_archivo):
    df = pd.read_csv(RAW / nombre_archivo, **LECTURA)
    for col in df.columns:
        if col not in CLAVES:
            df[col] = a_numero(df[col])
    return df.sort_values(CLAVES).reset_index(drop=True)


def sumar_bloque(df, prefijo):
    cols = [c for c in df.columns if c.startswith(prefijo)]
    return df[cols].sum(axis=1, min_count=1)


def main():
    dfs = {k: cargar_numerico(v) for k, v in BASES.items()}
    etiqueta = dfs["lengua"][CLAVES].astype(str).agg(" | ".join, axis=1)

    print("=" * 74)
    print("1. ¿EL DESEMPEÑO CUBRE LA MISMA POBLACION QUE EL CUESTIONARIO?")
    print("=" * 74)
    for base, prefijo in [("lengua", "ldesemp_"), ("matematica", "mdesemp_")]:
        df = dfs[base]
        total_cuestionario = sumar_bloque(df, "ap03_")
        total_desempeno = sumar_bloque(df, prefijo)
        brecha = total_cuestionario - total_desempeno
        brecha_pct = brecha / total_cuestionario * 100

        print(f"\n  Base '{base}' (bloque {prefijo}):")
        print(f"    total cuestionario (ap03): {total_cuestionario.sum():>12,.1f}")
        print(f"    total desempeño          : {total_desempeno.sum():>12,.1f}")
        print(f"    diferencia nacional      : {brecha.sum():>12,.1f} "
              f"({brecha.sum() / total_cuestionario.sum() * 100:.2f}%)")
        print(f"    filas donde coinciden (±0.5): "
              f"{(brecha.abs() < 0.5).sum():,} de {len(df):,}")
        print(f"    brecha por fila -> mediana: {brecha_pct.median():.2f}% | "
              f"p90: {brecha_pct.quantile(0.9):.2f}% | "
              f"max: {brecha_pct.max():.2f}%")

    print()
    print("=" * 74)
    print("2. LOS OUTLIERS: ¿SON DEPARTAMENTOS CHICOS?")
    print("=" * 74)
    totales = pd.DataFrame({n: sumar_bloque(d, "ap03_") for n, d in dfs.items()})
    totales["clave"] = etiqueta
    totales["dif_pct"] = (
        (totales[list(BASES)].max(axis=1) - totales[list(BASES)].min(axis=1))
        / totales[list(BASES)].max(axis=1) * 100
    )
    totales["tamano"] = totales[list(BASES)].max(axis=1)

    print("\n  Las 8 filas con mayor discrepancia entre bases:")
    peores = totales.nlargest(8, "dif_pct")[
        ["clave", "lengua", "matematica", "solo_cc", "dif_pct", "tamano"]
    ]
    print(peores.to_string(index=False, float_format=lambda x: f"{x:,.1f}"))

    print("\n  Discrepancia segun el tamaño de la fila:")
    cortes = [0, 25, 50, 100, 250, 500, 1_000, 1_000_000]
    etiquetas = ["<25", "25-50", "50-100", "100-250", "250-500",
                 "500-1000", ">1000"]
    totales["tramo"] = pd.cut(totales["tamano"], bins=cortes, labels=etiquetas)
    resumen = totales.groupby("tramo", observed=True).agg(
        filas=("dif_pct", "size"),
        dif_mediana=("dif_pct", "median"),
        dif_max=("dif_pct", "max"),
    )
    print(resumen.to_string(float_format=lambda x: f"{x:,.2f}"))

    print("\n  Cuantos estudiantes viven en las filas mas ruidosas:")
    ruidosas = totales[totales["dif_pct"] > 10]
    print(f"    filas con discrepancia >10%: {len(ruidosas):,} de {len(totales):,} "
          f"({len(ruidosas) / len(totales):.1%})")
    print(f"    estudiantes que representan: {ruidosas['tamano'].sum():,.0f} de "
          f"{totales['tamano'].sum():,.0f} "
          f"({ruidosas['tamano'].sum() / totales['tamano'].sum():.2%})")


if __name__ == "__main__":
    main()
