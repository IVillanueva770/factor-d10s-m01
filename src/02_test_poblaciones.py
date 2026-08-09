"""Paso 1b: ¿por qué las tres bases de Aprender difieren en las mismas celdas?

Hipotesis: cada base cuenta una poblacion distinta de estudiantes (los que
rindieron Lengua, los que rindieron Matematica, los que completaron el
cuestionario complementario). Si es cierta, el total de estudiantes por fila
tiene que diferir entre bases, y no se pueden pegar columnas de una al lado
de otra sin mezclar denominadores.

El test: sumar todas las categorias de una misma pregunta da el total de
estudiantes de esa fila. Se hace con varias preguntas distintas y se comparan
los totales entre bases.
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

# Preguntas cuyas categorias, sumadas, cubren a toda la poblacion.
BLOQUES_TOTALIZADORES = ["ap03_", "sobreedad_", "NSE_nivel_", "repitencia_"]


def a_numero(serie):
    """Convierte texto con coma decimal a float. Los blancos quedan en NaN.

    Los CSV del Ministerio traen las celdas vacias como un espacio en blanco,
    lo que fuerza a pandas a leer toda la columna como texto.
    """
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


def total_por_bloque(df, prefijo):
    cols = [c for c in df.columns if c.startswith(prefijo)]
    return df[cols].sum(axis=1, min_count=1), len(cols)


def main():
    dfs = {k: cargar_numerico(v) for k, v in BASES.items()}

    print("=" * 74)
    print("A. LA CARGA NUMERICA, ¿FUNCIONO?")
    print("=" * 74)
    lengua = dfs["lengua"]
    numericas = lengua.select_dtypes("number").columns
    print(f"  columnas numericas: {len(numericas):,} de {lengua.shape[1]:,}")
    print(f"  columnas que quedaron como texto: "
          f"{sorted(set(lengua.columns) - set(numericas) - set(CLAVES))}")
    celdas = lengua[numericas].size
    vacias = lengua[numericas].isna().sum().sum()
    print(f"  celdas vacias: {vacias:,} de {celdas:,} ({vacias / celdas:.1%})")

    print()
    print("=" * 74)
    print("B. ¿CADA BLOQUE DE PREGUNTA DA EL MISMO TOTAL DENTRO DE UNA BASE?")
    print("=" * 74)
    for prefijo in BLOQUES_TOTALIZADORES:
        total, n_cols = total_por_bloque(lengua, prefijo)
        print(f"  {prefijo:14s} ({n_cols:>2} categorias) -> "
              f"total nacional: {total.sum():>12,.1f}")

    print()
    print("=" * 74)
    print("C. EL TEST: ¿DIFIEREN LOS TOTALES ENTRE BASES?")
    print("=" * 74)
    totales = pd.DataFrame({
        nombre: total_por_bloque(df, "ap03_")[0] for nombre, df in dfs.items()
    })
    totales.insert(0, "clave", lengua[CLAVES].astype(str).agg(" | ".join, axis=1))

    print("  Total de estudiantes por base (suma de las categorias de ap03, sexo):")
    for nombre in BASES:
        print(f"    {nombre:12s} {totales[nombre].sum():>12,.1f}")

    iguales = (
        totales["lengua"].round(4).eq(totales["matematica"].round(4))
        & totales["lengua"].round(4).eq(totales["solo_cc"].round(4))
    )
    print()
    print(f"  Filas donde las tres bases dan el MISMO total: "
          f"{iguales.sum():,} de {len(totales):,}")
    print(f"  Filas donde difieren: {(~iguales).sum():,} de {len(totales):,}")

    dif = totales.loc[~iguales].copy()
    if not dif.empty:
        dif["dif_max_%"] = (
            (dif[["lengua", "matematica", "solo_cc"]].max(axis=1)
             - dif[["lengua", "matematica", "solo_cc"]].min(axis=1))
            / dif[["lengua", "matematica", "solo_cc"]].max(axis=1) * 100
        )
        print()
        print("  Muestra de filas que difieren:")
        print(dif.head(8).to_string(index=False,
                                    float_format=lambda x: f"{x:,.1f}"))
        print()
        print(f"  Diferencia porcentual entre bases (sobre {len(dif):,} filas):")
        print(f"    mediana: {dif['dif_max_%'].median():.2f}%")
        print(f"    promedio: {dif['dif_max_%'].mean():.2f}%")
        print(f"    maxima:  {dif['dif_max_%'].max():.2f}%")

    print()
    print("=" * 74)
    print("D. ¿QUIEN ES LA POBLACION MAS GRANDE?")
    print("=" * 74)
    for nombre in BASES:
        gana = (totales[nombre] >= totales[list(BASES)].max(axis=1) - 1e-6).sum()
        print(f"  {nombre:12s} es la base con MAS estudiantes en "
              f"{gana:,} de {len(totales):,} filas")


if __name__ == "__main__":
    main()
