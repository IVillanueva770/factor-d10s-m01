"""Paso 3: cargar la EPH y unir Hogares con Personas.

La consigna pide unir las dos tablas por CODUSU. Antes de unirlas hay que
mirar si esa clave alcanza, porque un CODUSU puede tener mas de un hogar
(NRO_HOGAR) y en ese caso unir solo por CODUSU multiplicaria filas.

Los xlsx tardan casi un minuto en abrir. Se cachean en parquet la primera vez.
"""

import zipfile
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW = BASE_DIR / "data" / "raw"
INTERIM = BASE_DIR / "data" / "interim"


def cargar_eph(nombre_en_zip):
    """Lee la hoja del zip, cacheando en parquet para no repetir el costo."""
    cache = INTERIM / f"{Path(nombre_en_zip).stem}.parquet"
    if cache.exists():
        return pd.read_parquet(cache)
    with zipfile.ZipFile(RAW / "eph3t.zip") as z:
        df = pd.read_excel(z.open(nombre_en_zip))
    INTERIM.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cache, index=False)
    return df


def main():
    hogar = cargar_eph("usu_hogar_T325.xlsx")
    personas = cargar_eph("usu_individual_T325.xlsx")

    print("=" * 74)
    print("1. QUE TRAE CADA TABLA")
    print("=" * 74)
    print(f"  hogares : {len(hogar):>7,} filas x {hogar.shape[1]:>3} columnas")
    print(f"  personas: {len(personas):>7,} filas x {personas.shape[1]:>3} columnas")
    print(f"  periodo : ANO4={hogar['ANO4'].unique()} "
          f"TRIMESTRE={hogar['TRIMESTRE'].unique()}")

    print()
    print("=" * 74)
    print("2. ¿ALCANZA CODUSU COMO CLAVE?")
    print("=" * 74)
    print(f"  CODUSU unicos en hogar   : {hogar['CODUSU'].nunique():>7,} "
          f"(filas: {len(hogar):,})")
    print(f"  CODUSU duplicados en hogar: "
          f"{hogar['CODUSU'].duplicated().sum():>7,}")
    print(f"  CODUSU+NRO_HOGAR unicos  : "
          f"{hogar[['CODUSU', 'NRO_HOGAR']].drop_duplicates().shape[0]:>7,}")
    multi = hogar.groupby("CODUSU")["NRO_HOGAR"].nunique()
    print(f"  viviendas con mas de un hogar: {(multi > 1).sum():,}")
    print("  -> la clave correcta es CODUSU + NRO_HOGAR, no CODUSU solo")

    print()
    print("=" * 74)
    print("3. ¿TODAS LAS PERSONAS TIENEN SU HOGAR, Y AL REVES?")
    print("=" * 74)
    claves_h = set(map(tuple, hogar[["CODUSU", "NRO_HOGAR"]].values))
    claves_p = set(map(tuple, personas[["CODUSU", "NRO_HOGAR"]].values))
    print(f"  hogares            : {len(claves_h):>7,}")
    print(f"  hogares en personas: {len(claves_p):>7,}")
    print(f"  personas sin hogar : {len(claves_p - claves_h):>7,}")
    print(f"  hogares sin personas: {len(claves_h - claves_p):>7,}")

    print()
    print("=" * 74)
    print("4. EL JOIN")
    print("=" * 74)
    eph = personas.merge(hogar, on=["CODUSU", "NRO_HOGAR"], how="left",
                         suffixes=("", "_hog"), validate="many_to_one")
    print(f"  filas antes del join : {len(personas):,}")
    print(f"  filas despues        : {len(eph):,}")
    print(f"  personas sin match   : {eph['IV1'].isna().sum():,}")
    print("  (validate='many_to_one' garantiza que no se multiplicaron filas)")

    duplicadas = [c for c in personas.columns
                  if c in hogar.columns and c not in ("CODUSU", "NRO_HOGAR")]
    print(f"  columnas presentes en ambas tablas: {duplicadas}")
    for col in duplicadas:
        if f"{col}_hog" in eph.columns:
            iguales = (eph[col] == eph[f"{col}_hog"]).mean()
            print(f"    {col:12s} coinciden en {iguales:.1%} de las filas")

    print()
    print("=" * 74)
    print("5. LA POBLACION QUE NOS INTERESA (12 a 18 años)")
    print("=" * 74)
    adolescentes = eph[eph["CH06"].between(12, 18)]
    print(f"  personas 12-18: {len(adolescentes):,} de {len(eph):,} "
          f"({len(adolescentes) / len(eph):.1%})")
    print(f"  ponderadas    : {adolescentes['PONDERA'].sum():,.0f} personas")
    print(f"  aglomerados   : {adolescentes['AGLOMERADO'].nunique()} de "
          f"{eph['AGLOMERADO'].nunique()}")

    INTERIM.mkdir(parents=True, exist_ok=True)
    eph.to_parquet(INTERIM / "eph_3t2025_unida.parquet", index=False)
    print(f"\n  guardado: data/interim/eph_3t2025_unida.parquet "
          f"({len(eph):,} x {eph.shape[1]})")


if __name__ == "__main__":
    main()
