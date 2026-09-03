"""Paso 4b: el puente geografico entre Aprender y la EPH.

Aprender llega a departamento dentro de 24 jurisdicciones. La EPH llega a
aglomerado (32). No comparten ninguna clave, asi que el unico nivel donde las
dos fuentes se pueden encontrar es la PROVINCIA.

Este script no decide nada por su cuenta: lee la tabla de correspondencia de
data/raw/documentacion/aglomerado_provincia.csv (editable, revisable, con los
casos dudosos marcados) y mide que tan bien queda cubierta cada provincia.
"""

import unicodedata
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS = BASE_DIR / "data" / "raw" / "documentacion"
INTERIM = BASE_DIR / "data" / "interim"


def normalizar(texto):
    """Compara nombres de provincia sin depender de tildes ni mayusculas."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    )
    return sin_tildes.strip().lower()


def main():
    puente = pd.read_csv(DOCS / "aglomerado_provincia.csv")
    nombres = pd.read_csv(DOCS / "aglomerados_indec.csv")
    puente = puente.merge(nombres, on="aglomerado", validate="one_to_one")

    eph = pd.read_parquet(INTERIM / "eph_3t2025_unida.parquet")
    aprender = pd.read_csv(INTERIM / "aprender_2024_proporciones.csv")

    print("=" * 74)
    print("1. LA TABLA DE CORRESPONDENCIA CUBRE TODOS LOS AGLOMERADOS")
    print("=" * 74)
    faltan = set(eph["AGLOMERADO"]) - set(puente["aglomerado"])
    print(f"  aglomerados en la EPH sin provincia asignada: {faltan or 'ninguno'}")
    print(f"  aglomerados marcados como dudosos: "
          f"{puente['cruza_provincias'].sum()} "
          f"({list(puente.loc[puente['cruza_provincias'], 'aglomerado'])})")

    print()
    print("=" * 74)
    print("2. ¿LAS PROVINCIAS DE LAS DOS FUENTES SE CORRESPONDEN?")
    print("=" * 74)
    prov_eph = {normalizar(p) for p in puente["provincia"]}
    prov_aprender = {normalizar(j) for j in aprender["jurisdiccion"].unique()}

    print(f"  jurisdicciones en Aprender: {len(prov_aprender)}")
    print(f"  provincias con aglomerado EPH: {len(prov_eph)}")

    solo_aprender = prov_aprender - prov_eph
    solo_eph = prov_eph - prov_aprender
    print(f"\n  En Aprender pero sin aglomerado EPH ({len(solo_aprender)}):")
    for p in sorted(solo_aprender):
        print(f"    - {p}")
    print(f"\n  Con aglomerado EPH pero no en Aprender ({len(solo_eph)}):")
    for p in sorted(solo_eph):
        print(f"    - {p}")

    print()
    print("=" * 74)
    print("3. CUANTOS AGLOMERADOS SOSTIENEN A CADA PROVINCIA")
    print("=" * 74)
    eph = eph.merge(puente[["aglomerado", "provincia"]],
                    left_on="AGLOMERADO", right_on="aglomerado", how="left",
                    validate="many_to_one")
    resumen = eph.groupby("provincia").agg(
        aglomerados=("AGLOMERADO", "nunique"),
        personas=("CODUSU", "size"),
        ponderadas=("PONDERA", "sum"),
    ).sort_values("ponderadas", ascending=False)
    resumen["% muestra"] = resumen["ponderadas"] / resumen["ponderadas"].sum()

    adolescentes = eph[eph["CH06"].between(12, 18)]
    resumen["casos_12_18"] = adolescentes.groupby("provincia").size()
    print(resumen.to_string(float_format=lambda x: f"{x:,.1f}"))

    print()
    print("  Provincias con menos de 100 adolescentes encuestados:")
    flacas = resumen[resumen["casos_12_18"] < 100]
    print(f"    {len(flacas)} de {len(resumen)}: "
          f"{list(flacas.index) if len(flacas) else 'ninguna'}")

    print()
    print("=" * 74)
    print("4. PESO DE LOS DOS CASOS DUDOSOS")
    print("=" * 74)
    dudosos = eph[eph["AGLOMERADO"].isin([38, 93])]
    print(f"  personas: {len(dudosos):,} de {len(eph):,} "
          f"({len(dudosos) / len(eph):.2%})")
    print(f"  ponderadas: {dudosos['PONDERA'].sum():,.0f} de "
          f"{eph['PONDERA'].sum():,.0f} "
          f"({dudosos['PONDERA'].sum() / eph['PONDERA'].sum():.2%})")
    for cod in (38, 93):
        sub = eph[eph["AGLOMERADO"] == cod]
        prov = puente.loc[puente["aglomerado"] == cod, "provincia"].item()
        ado = sub[sub["CH06"].between(12, 18)]
        print(f"    aglomerado {cod} -> {prov}: {len(sub):,} personas "
              f"({sub['PONDERA'].sum():,.0f} ponderadas), "
              f"{len(ado):,} adolescentes 12-18")

    puente.to_csv(INTERIM / "puente_aglomerado_provincia.csv", index=False,
                  encoding="utf-8")


if __name__ == "__main__":
    main()
