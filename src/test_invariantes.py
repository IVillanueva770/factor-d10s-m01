"""Verificacion del pipeline: las propiedades que TIENEN que valer siempre.

Cada assert de este archivo es una conclusion que se midio en algun paso del
analisis. Si mañana alguien toca el pipeline y rompe una, el script falla en
vez de producir un dataset silenciosamente mal.

Correr con:  python src/test_invariantes.py

Regla al agregar cosas: si en el analisis se afirma algo sobre los datos,
ese algo se convierte en un assert aca. Una afirmacion sin assert es una
afirmacion que ya nadie va a volver a chequear.
"""

import sys
import unicodedata
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW = BASE_DIR / "data" / "raw"
DOCS = RAW / "documentacion"
INTERIM = BASE_DIR / "data" / "interim"
PROCESADO = BASE_DIR / "data" / "processed"

CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]

resultados = []


def verificar(nombre, condicion, detalle=""):
    resultados.append((bool(condicion), nombre, detalle))


def a_numero(serie):
    return pd.to_numeric(
        serie.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce")


def normalizar(texto):
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().replace(",", " ").split())


def cargar_aprender(nombre):
    df = pd.read_csv(RAW / nombre, sep=";", encoding="latin-1", dtype=str)
    for c in df.columns:
        if c not in CLAVES:
            df[c] = a_numero(df[c])
    return df.sort_values(CLAVES).reset_index(drop=True)


# ---------------------------------------------------------------- APRENDER
lengua = cargar_aprender("ap2024_Desempenos_de_Lengua.csv")
matematica = cargar_aprender("ap2024_Desempenos_de_Matematica.csv")

verificar("el CSV crudo de Aprender tiene 1.175 filas",
          len(lengua) == 1175, f"{len(lengua)}")
verificar("las claves territoriales no se repiten",
          lengua.duplicated(subset=CLAVES).sum() == 0)
verificar("Lengua y Matematica describen las mismas filas",
          lengua[CLAVES].equals(matematica[CLAVES]))


def total(df, prefijo):
    return df[[c for c in df.columns if c.startswith(prefijo)]].sum(axis=1)


totales = {p: total(lengua, p).sum()
           for p in ("ap03_", "sobreedad_", "NSE_nivel_", "repitencia_")}
verificar("todos los bloques censales dan el mismo total de estudiantes",
          len(set(round(v, 2) for v in totales.values())) == 1,
          f"{totales}")
verificar("el total nacional es 540.040",
          round(totales["ap03_"]) == 540040, f"{totales['ap03_']:,.1f}")
verificar("el desempeño cubre la misma poblacion que el cuestionario",
          (total(lengua, "ldesemp_") - total(lengua, "ap03_")).abs().max() < 0.5)
verificar("no hay supresion de celdas chicas (existen valores menores a 2)",
          (lengua.select_dtypes("number").stack() < 2).sum() > 0)

# ------------------------------------------------- TABLA DE PROPORCIONES
prop = pd.read_csv(INTERIM / "aprender_2024_proporciones.csv")
bloques = sorted({c.split("__")[0] for c in prop.columns if "__" in c
                  and not c.startswith("cob__")})
# La invariante real: cada bloque suma 1, o no tiene dato para esa fila.
# Cualquier otra cosa (sumar 0.6, sumar 1.3) es un defecto de construccion.
for b in bloques:
    cols = [c for c in prop.columns if c.startswith(f"{b}__")]
    suma = prop[cols].sum(axis=1)
    sin_dato = prop[cols].isna().all(axis=1)
    raras = ~(suma.between(0.999, 1.001) | sin_dato)
    verificar(f"el bloque '{b}' suma 1 o no tiene dato",
              raras.sum() == 0, f"{raras.sum()} filas mal formadas")

sin_dato_por_bloque = pd.concat(
    [prop[[c for c in prop.columns if c.startswith(f"{b}__")]].isna().all(axis=1)
     for b in bloques], axis=1)
verificar("no quedan filas vacias en todos los bloques a la vez",
          not sin_dato_por_bloque.all(axis=1).any(),
          f"{sin_dato_por_bloque.all(axis=1).sum()} filas fantasma")
verificar("la tabla tiene 1.174 filas (1.175 menos la fila sin datos)",
          len(prop) == 1174, f"{len(prop)}")

verificar("no quedo ninguna columna con nombre ambiguo",
          set(c for c in prop.columns if "__" not in c) ==
          {*CLAVES, "estudiantes", "flag_discrepancia_bases"})
verificar("hay una columna de cobertura por cada bloque",
          len([c for c in prop.columns if c.startswith("cob__")]) == len(bloques))

# --------------------------------------------------------------------- EPH
eph = pd.read_parquet(INTERIM / "eph_3t2025_unida.parquet")
verificar("la EPH no perdio ni duplico personas al unir con hogares",
          len(eph) == 44946, f"{len(eph):,}")
verificar("toda persona tiene su hogar", eph["IV1"].notna().all())
verificar("CODUSU solo NO alcanza como clave (hay viviendas multi-hogar)",
          eph.groupby("CODUSU")["NRO_HOGAR"].nunique().gt(1).sum() > 0)
verificar("el periodo es 3er trimestre 2025",
          set(eph["ANO4"]) == {2025} and set(eph["TRIMESTRE"]) == {3})

# --------------------------------------------------------- PUENTE Y EPH AGG
puente = pd.read_csv(DOCS / "aglomerado_provincia.csv")
verificar("los 32 aglomerados tienen provincia asignada",
          set(eph["AGLOMERADO"]) <= set(puente["aglomerado"]))
verificar("solo 2 aglomerados cruzan provincia",
          puente["cruza_provincias"].sum() == 2)

indicadores = pd.read_csv(INTERIM / "eph_indicadores_provincia.csv")
verificar("hay indicadores para las 24 jurisdicciones",
          len(indicadores) == 24, f"{len(indicadores)}")
cols_prop = [c for c in indicadores.columns
             if c.startswith("eph_") and "ipcf" not in c
             and "casos" not in c and "aglomerados" not in c]
fuera_de_rango = ((indicadores[cols_prop] < 0) |
                  (indicadores[cols_prop] > 1)).sum().sum()
verificar("todo indicador de proporcion cae entre 0 y 1",
          fuera_de_rango == 0, f"{fuera_de_rango} valores fuera")

ba = indicadores.loc[indicadores["provincia"] == "Buenos Aires",
                     "eph_ipcf_mediano"].item()
verificar("el ingreso se pondera con PONDIH y no con PONDERA",
          ba > 300_000,
          f"Buenos Aires: {ba:,.0f} (con PONDERA daba 140.250)")

# --------------------------------------------------------- DATASET MAESTRO
maestro = pd.read_csv(PROCESADO / "dataset_maestro_inicial.csv")
verificar("el maestro conserva las 1.174 filas utiles",
          len(maestro) == 1174, f"{len(maestro)}")
verificar("ninguna fila quedo sin contexto socioeconomico",
          maestro[[c for c in maestro.columns
                   if c.startswith("eph_")]].notna().any(axis=1).all())

cols_eph = [c for c in maestro.columns if c.startswith("eph_")]
verificar("el contexto de la EPH no se mezclo entre provincias",
          maestro.groupby("jurisdiccion")[cols_eph].nunique().max().max() == 1)
verificar("las jurisdicciones del maestro son las 24 de Aprender",
          maestro["jurisdiccion"].nunique() == 24)
verificar("la cantidad de estudiantes se conserva",
          round(maestro["estudiantes"].sum()) == 540040)

# ------------------------------------------------------------------ REPORTE
print("=" * 74)
print("VERIFICACION DE INVARIANTES DEL PIPELINE")
print("=" * 74)
fallaron = 0
for ok, nombre, detalle in resultados:
    marca = "OK  " if ok else "FALLA"
    extra = f"  ({detalle})" if detalle and not ok else ""
    print(f"  [{marca}] {nombre}{extra}")
    fallaron += not ok

print()
print(f"  {len(resultados) - fallaron} de {len(resultados)} verificaciones pasaron")
sys.exit(1 if fallaron else 0)
