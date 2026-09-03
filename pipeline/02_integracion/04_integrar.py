"""Paso 6: el dataset maestro.

Une la tabla de Aprender (1 fila = departamento x sector x ambito) con los
indicadores socioeconomicos de la EPH agregados a nivel provincia.

La union es de MUCHOS A UNO: cada departamento recibe el contexto de su
provincia. Eso significa que todos los departamentos de una misma provincia
comparten los mismos valores de EPH, que es exactamente lo que la consigna
pide ("incorporando al dataset de Aprender indicadores socioeconomicos
agregados obtenidos a partir de la EPH") y es tambien su principal limitacion.
"""

from pathlib import Path

import pandas as pd

from comun import clave_provincia

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM = BASE_DIR / "data" / "interim"
PROCESADO = BASE_DIR / "data" / "processed"


def main():
    aprender = pd.read_csv(INTERIM / "aprender_2024_proporciones.csv")
    eph = pd.read_csv(INTERIM / "eph_indicadores_provincia.csv")

    aprender["_clave"] = aprender["jurisdiccion"].map(clave_provincia)
    eph["_clave"] = eph["provincia"].map(clave_provincia)

    print("=" * 74)
    print("1. ANTES DE UNIR: ¿LAS CLAVES SE CORRESPONDEN?")
    print("=" * 74)
    solo_a = set(aprender["_clave"]) - set(eph["_clave"])
    solo_e = set(eph["_clave"]) - set(aprender["_clave"])
    print(f"  jurisdicciones de Aprender: {aprender['_clave'].nunique()}")
    print(f"  provincias con indicadores EPH: {eph['_clave'].nunique()}")
    print(f"  sin par en EPH: {sorted(solo_a) or 'ninguna'}")
    print(f"  sin par en Aprender: {sorted(solo_e) or 'ninguna'}")
    if solo_a or solo_e:
        raise SystemExit("Las claves no cierran: revisar antes de unir")

    maestro = aprender.merge(
        eph.drop(columns=["provincia"]), on="_clave", how="left",
        validate="many_to_one",
    ).drop(columns=["_clave"])

    print()
    print("=" * 74)
    print("2. DESPUES DE UNIR")
    print("=" * 74)
    print(f"  filas antes : {len(aprender):,}")
    print(f"  filas despues: {len(maestro):,}  "
          f"(iguales: {len(aprender) == len(maestro)})")
    print(f"  columnas: {aprender.shape[1] - 1} + "
          f"{eph.shape[1] - 2} = {maestro.shape[1]}")
    cols_eph = [c for c in maestro.columns if c.startswith("eph_")]
    print(f"  filas sin contexto EPH: {maestro[cols_eph].isna().all(axis=1).sum()}")
    print(f"  estudiantes representados: {maestro['estudiantes'].sum():,.0f}")

    print()
    print("=" * 74)
    print("3. VERIFICACION: EL CONTEXTO NO SE MEZCLO ENTRE PROVINCIAS")
    print("=" * 74)
    # Dentro de cada jurisdiccion, los valores de EPH tienen que ser identicos
    # en todas sus filas. Si alguno varia, el join asigno mal.
    variacion = maestro.groupby("jurisdiccion")[cols_eph].nunique().max().max()
    print(f"  valores distintos de un indicador EPH dentro de una misma "
          f"jurisdiccion: {variacion} (tiene que ser 1)")
    assert variacion == 1, "El contexto EPH varia dentro de una jurisdiccion"

    print()
    print("=" * 74)
    print("4. CUANTOS ESTUDIANTES DEPENDEN DE CUAN POCOS ENCUESTADOS")
    print("=" * 74)
    riesgo = maestro.groupby("jurisdiccion").agg(
        estudiantes=("estudiantes", "sum"),
        departamentos=("departamento", "nunique"),
        encuestados_12_18=("eph_casos_12_18", "first"),
    )
    riesgo["estudiantes_por_encuestado"] = (
        riesgo["estudiantes"] / riesgo["encuestados_12_18"])
    riesgo = riesgo.sort_values("estudiantes_por_encuestado", ascending=False)
    print(riesgo.head(8).to_string(float_format=lambda x: f"{x:,.0f}"))
    print()
    print(f"  mediana de estudiantes por adolescente encuestado: "
          f"{riesgo['estudiantes_por_encuestado'].median():,.0f}")

    PROCESADO.mkdir(parents=True, exist_ok=True)
    # Se llama "base" y no "inicial" porque esta etapa NO produce el dataset
    # final: falta la armonizacion (etapa 05), que es la que escribe
    # dataset_maestro_inicial.csv. Antes las dos escribian sobre el mismo
    # archivo, y correr la 05 dos veces seguidas le apilaba columnas encima
    # (medido el 2026-09-03: 131 -> 155 sin fallar ni avisar).
    destino = PROCESADO / "dataset_maestro_base.csv"
    maestro.to_csv(destino, index=False, encoding="utf-8")
    print()
    print(f"  GUARDADO: {destino.relative_to(BASE_DIR)}")
    print(f"  {len(maestro):,} filas x {maestro.shape[1]:,} columnas")


if __name__ == "__main__":
    main()
