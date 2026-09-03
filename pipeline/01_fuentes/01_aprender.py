"""Paso 2: construir la tabla de Aprender 2024 lista para integrar.

Que hace:
  1. Carga la base de Lengua (cuestionario + desempeño en Lengua) y la de
     Matematica (solo para tomar su bloque de desempeño).
  2. Selecciona los bloques de preguntas relevantes para abandono escolar.
  3. Convierte los conteos ponderados a PROPORCIONES dentro de cada fila,
     usando como denominador las respuestas validas del bloque.
  4. Guarda ademas, por bloque, la COBERTURA (que fraccion de los estudiantes
     de la fila quedo representada), que es el indicador de calidad del dato.

Por que proporciones y no conteos: las bases vienen expandidas por un factor
de ponderacion propio de cada cuestionario (lo dice el documento metodologico
del Ministerio). Los conteos de bases distintas no son comparables entre si;
las proporciones dentro de cada base si.
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
RAW = BASE_DIR / "data" / "raw"
INTERIM = BASE_DIR / "data" / "interim"

CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]

# Categorias que no son respuestas reales: no van al numerador ni al
# denominador. Ojo: en las bases 2024 vienen SIEMPRE vacias (10.575 de
# 10.575 celdas), asi que no sirven para medir no respuesta. Para eso esta
# la cobertura.
NO_RESPUESTA = {"Blanco", "No_disponible", "Multimarca", "No_corresponde",
                "_Blanco", "_No_disponible"}

# Bloque de columnas -> nombre humano. El bloque se identifica por el prefijo
# del nombre de columna; las categorias salen del sufijo.
BLOQUES = {
    "ap03_": "sexo",
    "ap12_": "tamano_hogar",
    "ap19_": "libros_hogar",
    "ap24_": "asistio_jardin",
    "ap27_": "inasistencias",
    "ap31_": "horas_estudio",
    "edadA_junio2024_": "edad",
    "sobreedad_": "sobreedad",
    "repitencia_": "repitencia",
    "migracion_": "migracion",
    "clima_": "clima_escolar",
    "NSE_nivel_": "nse",
    "Nivel_Ed_Madre_": "educ_madre",
    "Nivel_Ed_Padre_": "educ_padre",
}

# Excluido a proposito: "Nivel_Ed_Persona_Resp_" (educacion del referente).
# Es una variable CONDICIONAL, solo aplica cuando el referente no es la
# madre ni el padre: cubre el 16,6% de los estudiantes (mediana) y hasta
# un 1,7% en el peor departamento. Sus proporciones no describen a la
# poblacion sino a un subconjunto autoseleccionado. Se retoma en el TP2
# como indicador de "no convive con los padres", que es su lectura util.

BLOQUE_DESEMPENO_LENGUA = "ldesemp_"
BLOQUE_DESEMPENO_MATEMATICA = "mdesemp_"

# Bloque que sirve para contar el total de estudiantes de la fila. Cualquiera
# de los totalizadores sirve: ya verificamos que todos dan el mismo total.
BLOQUE_TOTAL = "ap03_"


def a_numero(serie):
    """Texto con coma decimal -> float. Blancos (' ') quedan NaN."""
    return pd.to_numeric(
        serie.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )


def normalizar_nombre(texto):
    """'De_21_a_50_libros' -> 'de_21_a_50_libros' (sin tildes, snake_case)."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    limpio = re.sub(r"[^0-9a-zA-Z]+", "_", sin_tildes).strip("_").lower()
    return re.sub(r"_+", "_", limpio)


def cargar(nombre_archivo):
    df = pd.read_csv(RAW / nombre_archivo, sep=";", encoding="latin-1",
                     dtype=str)
    for col in df.columns:
        if col not in CLAVES:
            df[col] = a_numero(df[col])
    return df.sort_values(CLAVES).reset_index(drop=True)


def proporciones_del_bloque(df, prefijo, nombre_humano, total_fila):
    """Convierte un bloque de conteos en proporciones sobre quienes respondieron.

    Devuelve (DataFrame de proporciones, Series de cobertura del bloque).

    Sobre los NaN: se tratan como cero. Verificado en src/07_auditar_nan.py,
    no es un supuesto comodo. El valor minimo de toda la matriz es 1,0000 y hay
    2.140 valores por debajo de 2, asi que el Ministerio NO suprime celdas
    chicas (un umbral de supresion las habria borrado). Y en los bloques
    censales el total cierra exacto aun con NaN presentes, lo que solo puede
    pasar si el NaN vale cero.

    Sobre la cobertura: reemplaza a una tasa de no respuesta que daba 0,00% en
    los 17 bloques. Daba cero por construccion, porque las columnas Blanco /
    No_disponible / Multimarca estan vacias en el 100% de sus 10.575 celdas.
    La cobertura mide lo mismo por el otro lado (que fraccion de los
    estudiantes de la fila quedo representado en el bloque) y si varia: 100%
    en los bloques completos, 84,8% de mediana en clima escolar.
    """
    columnas = [c for c in df.columns if c.startswith(prefijo)]
    validas = [c for c in columnas if c[len(prefijo):] not in NO_RESPUESTA]

    respondieron = df[validas].sum(axis=1, min_count=1)

    proporciones = pd.DataFrame({
        f"{nombre_humano}__{normalizar_nombre(c[len(prefijo):])}":
            df[c].fillna(0) / respondieron
        for c in validas
    })
    cobertura = (respondieron / total_fila).rename(f"cob__{nombre_humano}")
    return proporciones, cobertura


def main():
    lengua = cargar("ap2024_Desempenos_de_Lengua.csv")
    matematica = cargar("ap2024_Desempenos_de_Matematica.csv")

    # Guarda de integridad: las dos bases tienen que describir las mismas
    # filas, en el mismo orden, antes de tomar columnas de una y de la otra.
    assert lengua[CLAVES].equals(matematica[CLAVES]), \
        "Las claves de Lengua y Matematica no coinciden fila a fila"

    # Filas sin ningun dato: el Ministerio publica la clave territorial con
    # las 1.031 columnas vacias. Medido: 1 fila (Chaco / GENERAL DONOVAN /
    # Estatal / Rural), 0 estudiantes. No es no respuesta, es una fila que no
    # tiene nada atras, y arrastrarla ensucia cualquier promedio.
    datos = lengua.drop(columns=CLAVES)
    vacias = datos.isna().all(axis=1)
    if vacias.any():
        print(f"  descartadas {vacias.sum()} fila(s) sin ningun dato:")
        for _, f in lengua.loc[vacias, CLAVES].iterrows():
            print(f"    {' / '.join(f.astype(str))}")
        lengua = lengua[~vacias].reset_index(drop=True)
        matematica = matematica[~vacias.values].reset_index(drop=True)

    salida = lengua[CLAVES].copy()
    salida["estudiantes"] = lengua[
        [c for c in lengua.columns if c.startswith(BLOQUE_TOTAL)]
    ].sum(axis=1, min_count=1)

    total_l = salida["estudiantes"]
    total_m = matematica[
        [c for c in matematica.columns if c.startswith(BLOQUE_TOTAL)]
    ].sum(axis=1, min_count=1)

    coberturas = {}
    for prefijo, nombre in BLOQUES.items():
        props, cob = proporciones_del_bloque(lengua, prefijo, nombre, total_l)
        salida = pd.concat([salida, props], axis=1)
        coberturas[nombre] = cob

    props_l, cob_l = proporciones_del_bloque(
        lengua, BLOQUE_DESEMPENO_LENGUA, "desemp_lengua", total_l)
    props_m, cob_m = proporciones_del_bloque(
        matematica, BLOQUE_DESEMPENO_MATEMATICA, "desemp_matematica", total_m)
    salida = pd.concat([salida, props_l, props_m], axis=1)
    coberturas["desemp_lengua"] = cob_l
    coberturas["desemp_matematica"] = cob_m

    cobertura = pd.DataFrame(coberturas).add_prefix("cob__")
    salida = pd.concat([salida, cobertura], axis=1)

    # NO hay flag binario de cobertura, a proposito. Se probaron umbrales de
    # 90% a 50% y la cantidad de filas marcadas baja de forma continua (68% /
    # 51% / 39% / 31% / 25% / 14% / 8%), sin ningun escalon: no existe una cola
    # separable de filas "malas". Cualquier corte seria arbitrario y le
    # impondria esa decision, invisible, a quien use la tabla. Quedan las
    # columnas cob__* continuas y cada analisis elige y justifica su corte.

    # Bandera de las filas donde las dos bases discrepan mas de 10%: no se
    # eliminan, se marcan, para poder excluirlas en analisis sensibles.
    salida["flag_discrepancia_bases"] = (
        (salida["estudiantes"] - total_m).abs() / salida["estudiantes"] > 0.10
    )

    INTERIM.mkdir(parents=True, exist_ok=True)
    destino = INTERIM / "aprender_2024_proporciones.csv"
    salida.to_csv(destino, index=False, encoding="utf-8")

    print("=" * 74)
    print("TABLA DE APRENDER 2024 CONSTRUIDA")
    print("=" * 74)
    print(f"  archivo: {destino.relative_to(BASE_DIR)}")
    print(f"  filas: {len(salida):,} | columnas: {salida.shape[1]:,}")
    print(f"  estudiantes representados: {salida['estudiantes'].sum():,.0f}")
    print(f"  filas marcadas por discrepancia entre bases: "
          f"{salida['flag_discrepancia_bases'].sum()}")

    print()
    print("  Verificacion: cada bloque de proporciones debe sumar 1 por fila")
    todos = dict(BLOQUES)
    todos[BLOQUE_DESEMPENO_LENGUA] = "desemp_lengua"
    todos[BLOQUE_DESEMPENO_MATEMATICA] = "desemp_matematica"
    # Ojo con la version anterior de este chequeo: aceptaba como validas las
    # filas que sumaban 1 Y TAMBIEN las que sumaban 0 o quedaban vacias, o sea
    # que se perdonaba a si mismo los casos que no cumplian. Ahora se separan:
    # suman 1 (correcto), sin dato (informativo) y raras (defecto real).
    for nombre in todos.values():
        cols = [c for c in salida.columns if c.startswith(f"{nombre}__")]
        suma = salida[cols].sum(axis=1)
        sin_dato = salida[cols].isna().all(axis=1)
        uno = suma.between(0.999, 1.001)
        raras = ~(uno | sin_dato)
        print(f"    {nombre:20s} {len(cols):>2} cols | suman 1: {uno.sum():>5,} "
              f"| sin dato: {sin_dato.sum():>3,} | RARAS: {raras.sum()}")
        assert raras.sum() == 0, f"{nombre}: {raras.sum()} filas mal formadas"

    print()
    print("  Distribucion de la cobertura (peor bloque de cada fila):")
    peor = cobertura.min(axis=1)
    for u in (0.90, 0.80, 0.70, 0.60, 0.50):
        n = (peor < u).sum()
        print(f"    filas con algun bloque <{u:.0%}: {n:>5,} ({n / len(salida):>5.1%})")
    print()
    print("  Cobertura por bloque (que fraccion de la fila quedo representada):")
    for nombre, serie in sorted(coberturas.items(), key=lambda x: x[1].median()):
        print(f"    {nombre:20s} mediana {serie.median():>6.1%} | "
              f"min {serie.min():>6.1%}")


if __name__ == "__main__":
    main()
