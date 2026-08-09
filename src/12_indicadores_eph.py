"""Paso 5: indicadores socioeconomicos por provincia, a partir de la EPH.

Todos los codigos de variable estan verificados contra el documento oficial del
INDEC que quedo guardado en data/raw/documentacion/. Ninguno se escribio de
memoria; el detalle de cada uno esta en DEFINICIONES, que ademas se exporta
como parte del diccionario de variables del entregable.

Todo se calcula PONDERADO. Los microdatos de la EPH son una muestra: sin
aplicar PONDERA, cada encuestado pesaria igual y los aglomerados chicos
quedarian sobrerrepresentados.
"""

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS = BASE_DIR / "data" / "raw" / "documentacion"
INTERIM = BASE_DIR / "data" / "interim"

FUENTE = ("INDEC, EPH 3er trimestre 2025. Codigos verificados en "
          "data/raw/documentacion/EPH_diseno_reg_t414.pdf")

DEFINICIONES = {
    "eph_no_asiste_12_18":
        "% de personas de 12 a 18 años que no asiste a un establecimiento "
        "educativo (CH10 = 2 'no asiste pero asistio' o 3 'nunca asistio'). "
        "Es el proxy mas directo de abandono escolar disponible en la EPH.",
    "eph_ipcf_mediano":
        "Mediana del ingreso per capita familiar (IPCF) de las personas de la "
        "provincia, en pesos del trimestre. Ponderada por PONDIH (el "
        "ponderador de ingresos del hogar) y NO por PONDERA: el 27,5% de las "
        "personas tiene IPCF=0 por no declarar ingresos, y el INDEC ya las "
        "marca poniendoles PONDIH=0 (coincide en el 98,8% de los casos). "
        "Usando PONDERA esas personas entran con peso completo y un cero que "
        "no es un ingreso sino una no respuesta: asi Buenos Aires daba la "
        "mediana mas baja del pais (140.250) porque el 47,4% de la muestra de "
        "Partidos del GBA no declara ingresos.",
    "eph_sin_dato_ingreso":
        "% de personas sin dato de ingreso (PONDIH = 0). Es el denominador "
        "que falta del indicador anterior: sin esto no se sabe sobre que "
        "fraccion de la provincia se calculo la mediana.",
    "eph_hacinamiento_critico":
        "% de personas en hogares con mas de 3 personas por habitacion de uso "
        "exclusivo (IX_TOT / II1 > 3). Umbral estandar de hacinamiento critico.",
    "eph_agua_fuera_vivienda":
        "% de personas en hogares cuya agua no llega por cañeria dentro de la "
        "vivienda (IV6 = 2 o 3).",
    "eph_desocupacion":
        "Desocupados sobre poblacion economicamente activa "
        "(ESTADO = 2 / (ESTADO = 1 o 2)). Excluye inactivos y menores de 10, "
        "que tienen codigos propios (3 y 4).",
    "eph_adultos_sin_secundaria":
        "% de personas de 25 años o mas que no completo el secundario "
        "(NIVEL_ED 1, 2, 3 o 7).",
    "eph_adolescentes_ocupados":
        "% de personas de 12 a 18 años que estan ocupadas (ESTADO = 1).",
}


def mediana_ponderada(valores, pesos):
    """Mediana teniendo en cuenta el ponderador de cada observacion."""
    orden = np.argsort(valores)
    v, p = np.asarray(valores)[orden], np.asarray(pesos)[orden]
    acumulado = np.cumsum(p)
    if acumulado[-1] == 0:
        return np.nan
    return v[np.searchsorted(acumulado, acumulado[-1] / 2)]


def proporcion_ponderada(mascara, pesos):
    """Fraccion ponderada de True dentro de la poblacion considerada."""
    total = pesos.sum()
    return (pesos[mascara].sum() / total) if total else np.nan


def indicadores_de(grupo):
    peso = grupo["PONDERA"]

    ado = grupo[grupo["CH06"].between(12, 18)]
    pea = grupo[grupo["ESTADO"].isin([1, 2])]
    adultos = grupo[grupo["CH06"] >= 25]
    con_ingreso = grupo[grupo["PONDIH"] > 0]
    hogares = grupo.drop_duplicates(subset=["CODUSU", "NRO_HOGAR"])

    personas_por_cuarto = grupo["IX_TOT"] / grupo["II1"].replace(0, np.nan)

    return pd.Series({
        "eph_no_asiste_12_18":
            proporcion_ponderada(ado["CH10"].isin([2, 3]), ado["PONDERA"]),
        "eph_ipcf_mediano":
            mediana_ponderada(con_ingreso["IPCF"].values,
                              con_ingreso["PONDIH"].values),
        "eph_sin_dato_ingreso":
            proporcion_ponderada(grupo["PONDIH"] == 0, peso),
        "eph_hacinamiento_critico":
            proporcion_ponderada(personas_por_cuarto > 3, peso),
        "eph_agua_fuera_vivienda":
            proporcion_ponderada(grupo["IV6"].isin([2, 3]), peso),
        "eph_desocupacion":
            proporcion_ponderada(pea["ESTADO"] == 2, pea["PONDERA"]),
        "eph_adultos_sin_secundaria":
            proporcion_ponderada(adultos["NIVEL_ED"].isin([1, 2, 3, 7]),
                                 adultos["PONDERA"]),
        "eph_adolescentes_ocupados":
            proporcion_ponderada(ado["ESTADO"] == 1, ado["PONDERA"]),
        # Denominadores: van en la tabla para que nadie use un indicador sin
        # saber sobre cuantos casos se calculo.
        "eph_casos_personas": len(grupo),
        "eph_casos_hogares": len(hogares),
        "eph_casos_12_18": len(ado),
        "eph_aglomerados": grupo["AGLOMERADO"].nunique(),
    })


def main():
    eph = pd.read_parquet(INTERIM / "eph_3t2025_unida.parquet")
    puente = pd.read_csv(DOCS / "aglomerado_provincia.csv")

    eph = eph.merge(puente[["aglomerado", "provincia", "cruza_provincias"]],
                    left_on="AGLOMERADO", right_on="aglomerado", how="left",
                    validate="many_to_one")
    assert eph["provincia"].notna().all(), "Hay aglomerados sin provincia"

    tabla = eph.groupby("provincia").apply(indicadores_de, include_groups=False)
    tabla = tabla.reset_index()

    for col in ("eph_casos_personas", "eph_casos_hogares", "eph_casos_12_18",
                "eph_aglomerados"):
        tabla[col] = tabla[col].astype(int)

    tabla.to_csv(INTERIM / "eph_indicadores_provincia.csv", index=False,
                 encoding="utf-8")
    pd.DataFrame({"variable": DEFINICIONES.keys(),
                  "definicion": DEFINICIONES.values(),
                  "fuente": FUENTE}).to_csv(
        INTERIM / "eph_diccionario.csv", index=False, encoding="utf-8")

    print("=" * 90)
    print("INDICADORES SOCIOECONOMICOS POR PROVINCIA (EPH 3T 2025)")
    print("=" * 90)
    vista = tabla.set_index("provincia")[[
        "eph_no_asiste_12_18", "eph_adolescentes_ocupados",
        "eph_adultos_sin_secundaria", "eph_hacinamiento_critico",
        "eph_desocupacion", "eph_ipcf_mediano", "eph_sin_dato_ingreso",
        "eph_casos_12_18",
    ]].sort_values("eph_no_asiste_12_18", ascending=False)
    with pd.option_context("display.width", 200):
        print(vista.to_string(float_format=lambda x: f"{x:,.3f}"))

    print()
    print(f"  provincias: {len(tabla)}")
    print(f"  archivo: data/interim/eph_indicadores_provincia.csv")
    print(f"  diccionario: data/interim/eph_diccionario.csv")


if __name__ == "__main__":
    main()
