"""Paso 7: diccionario de variables y armonizacion entre fuentes.

Son dos de los tres productos que pide la consigna:
  - "Un diccionario de variables con la descripcion y correspondencia entre
     las variables seleccionadas"
  - criterio de aceptacion: "Se armonicen los nombres y categorias
     equivalentes entre ambas fuentes"

El diccionario se GENERA leyendo el dataset maestro, no se escribe a mano. Si
mañana el pipeline agrega o saca una columna, el diccionario la refleja sola.
Lo unico escrito a mano son las descripciones por bloque, que viven en un solo
lugar (BLOQUES) y fallan ruidosamente si aparece un bloque sin documentar.
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM = BASE_DIR / "data" / "interim"
PROCESADO = BASE_DIR / "data" / "processed"

APRENDER = "Pruebas Aprender 2024 (Censal, Secundaria 5-6 año, base Agregada)"
EPH = "EPH INDEC, 3er trimestre 2025 (bases Hogar e Individual)"

# Un renglon por bloque del dataset. 'origen' es la variable tal como viene en
# la fuente; 'justificacion' responde al criterio de aceptacion de la consigna.
BLOQUES = {
    "sexo": dict(
        origen="ap03", fuente=APRENDER, dimension="estudiante",
        descripcion="Sexo que figura en el DNI del estudiante.",
        justificacion="Variable pedida explicitamente por la consigna. Permite "
                      "analizar brechas de genero en trayectoria y desempeño."),
    "edad": dict(
        origen="edadA_junio2024", fuente=APRENDER, dimension="estudiante",
        descripcion="Edad cumplida al 30 de junio de 2024, en tramos.",
        justificacion="Pedida por la consigna. Es la base del calculo de "
                      "sobreedad, que es un antecedente conocido de abandono."),
    "sobreedad": dict(
        origen="sobreedad", fuente=APRENDER, dimension="trayectoria",
        descripcion="Años de atraso respecto de la edad teorica del año que "
                    "cursa (17 años al 30 de junio para 5to/6to).",
        justificacion="Pedida por la consigna y una de las señales de riesgo "
                      "mas directas: el atraso escolar acumulado precede al "
                      "abandono."),
    "repitencia": dict(
        origen="repitencia", fuente=APRENDER, dimension="trayectoria",
        descripcion="Cantidad de veces que repitio de año.",
        justificacion="NO la pide la consigna. Se incorpora por criterio del "
                      "equipo: el Ministerio publica repitencia junto a "
                      "abandono interanual en su dataset Indicadores "
                      "Educativos, lo que sugiere que las trata como la misma "
                      "familia. A VALIDAR empiricamente en el TP2."),
    "migracion": dict(
        origen="migracion", fuente=APRENDER, dimension="hogar",
        descripcion="Configuracion familiar migrante o no migrante.",
        justificacion="NO la pide la consigna. Incorporada por criterio del "
                      "equipo, sin respaldo empirico todavia. A VALIDAR en el "
                      "TP2; si no aporta, se saca."),
    "clima_escolar": dict(
        origen="clima", fuente=APRENDER, dimension="escuela",
        descripcion="Indice de clima escolar construido por el Ministerio "
                    "(bajo / medio / alto).",
        justificacion="NO la pide la consigna. Incorporada por criterio del "
                      "equipo. ATENCION: es el unico bloque con datos "
                      "faltantes (96 de 1.174 filas sin dato, cobertura "
                      "mediana 87,3%). A VALIDAR en el TP2."),
    "nse": dict(
        origen="NSE_nivel", fuente=APRENDER, dimension="hogar",
        descripcion="Quintil de nivel socioeconomico del estudiante, calculado "
                    "por el Ministerio (Q1 el mas bajo, Q5 el mas alto).",
        justificacion="Pedida por la consigna. Es el resumen socioeconomico que "
                      "la propia fuente construye, y sirve de contraste contra "
                      "los indicadores que trajimos de la EPH."),
    "educ_madre": dict(
        origen="Nivel_Ed_Madre", fuente=APRENDER, dimension="hogar",
        descripcion="Maximo nivel educativo alcanzado por la madre.",
        justificacion="Pedida por la consigna. El nivel educativo materno es "
                      "de los predictores mas usados del rendimiento."),
    "educ_padre": dict(
        origen="Nivel_Ed_Padre", fuente=APRENDER, dimension="hogar",
        descripcion="Maximo nivel educativo alcanzado por el padre.",
        justificacion="Pedida por la consigna. Se conserva pese a tener "
                      "cobertura menor que la de la madre (90,4% contra 100%): "
                      "ese hueco es en si mismo informacion sobre la "
                      "composicion del hogar."),
    "tamano_hogar": dict(
        origen="ap12", fuente=APRENDER, dimension="hogar",
        descripcion="Cantidad de personas con las que vive el estudiante.",
        justificacion="Pedida por la consigna ('tamaño del hogar'). Se eligio "
                      "ap12 y no ap11 porque su categoria 'Vivo solo' delata "
                      "que cuenta personas del hogar. ap11 quedo SIN "
                      "IDENTIFICAR: mismas opciones sin esa categoria."),
    "libros_hogar": dict(
        origen="ap19", fuente=APRENDER, dimension="hogar",
        descripcion="Cantidad de libros en papel en el hogar, en tramos.",
        justificacion="Pedida por la consigna. Es un proxy clasico de capital "
                      "cultural del hogar."),
    "horas_estudio": dict(
        origen="ap31", fuente=APRENDER, dimension="estudiante",
        descripcion="Horas semanales dedicadas a estudiar o hacer tarea fuera "
                    "del horario escolar.",
        justificacion="Pedida por la consigna."),
    "inasistencias": dict(
        origen="ap27", fuente=APRENDER, dimension="trayectoria",
        descripcion="Cantidad de faltas en el año, en tramos.",
        justificacion="Pedida por la consigna. El ausentismo es el paso previo "
                      "observable al abandono."),
    "asistio_jardin": dict(
        origen="ap24", fuente=APRENDER, dimension="trayectoria",
        descripcion="Si asistio al jardin de infantes y desde que sala.",
        justificacion="NO la pide la consigna. Incorporada por criterio del "
                      "equipo como marcador de trayectoria temprana. A VALIDAR "
                      "en el TP2."),
    "desemp_lengua": dict(
        origen="ldesemp", fuente=APRENDER, dimension="desempeño",
        descripcion="Nivel de desempeño en Lengua (por debajo del basico / "
                    "basico / satisfactorio / avanzado).",
        justificacion="Pedida por la consigna. Es una de las dos variables de "
                      "resultado de la evaluacion."),
    "educ_madre_arm": dict(
        origen="Nivel_Ed_Madre (recodificada)", fuente=APRENDER,
        dimension="hogar",
        descripcion="Maximo nivel educativo COMPLETADO por la madre, en la "
                    "escala comun de 4 niveles acordada con la EPH.",
        justificacion="Cumple el criterio de aceptacion de armonizar las "
                      "categorias equivalentes entre fuentes. Habilita "
                      "comparar contra eph_educ_adultos__*, que es la unica "
                      "validacion empirica que tenemos del puente geografico "
                      "(correlacion 0,674 entre ambas)."),
    "educ_padre_arm": dict(
        origen="Nivel_Ed_Padre (recodificada)", fuente=APRENDER,
        dimension="hogar",
        descripcion="Maximo nivel educativo COMPLETADO por el padre, en la "
                    "escala comun de 4 niveles.",
        justificacion="Idem educ_madre_arm."),
    "desemp_matematica": dict(
        origen="mdesemp", fuente=APRENDER, dimension="desempeño",
        descripcion="Nivel de desempeño en Matematica.",
        justificacion="Pedida por la consigna. Se toma de la base de "
                      "Matematica, que tiene su propio factor de expansion."),
}

# Variables que existen en las dos fuentes y hay que poder leer juntas.
ARMONIZACION = [
    dict(concepto="Nivel educativo de adultos del hogar",
         en_aprender="Nivel_Ed_Madre_* / Nivel_Ed_Padre_* (7 categorias: no "
                     "fue a la escuela, primaria inc/comp, secundaria "
                     "inc/comp, terciario-universitario inc/comp)",
         en_eph="NIVEL_ED (1 primaria inc, 2 primaria comp, 3 secundaria inc, "
                "4 secundaria comp, 5 superior inc, 6 superior comp, 7 sin "
                "instruccion)",
         escala_comun="sin_primaria / primaria / secundaria / superior",
         estado="ARMONIZADA",
         nota="En Aprender se refiere a los padres del estudiante evaluado; en "
              "la EPH a la poblacion de 25 años o mas de la provincia. Son "
              "poblaciones distintas: la comparacion es de contexto, no de "
              "las mismas personas."),
    dict(concepto="Sexo",
         en_aprender="ap03 (Masculino / Femenino / X)",
         en_eph="CH04 (1 varon / 2 mujer)",
         escala_comun="varon / mujer / otro",
         estado="ARMONIZADA",
         nota="La EPH no tiene categoria equivalente a 'X' de Aprender."),
    dict(concepto="Territorio",
         en_aprender="jurisdiccion (24) y departamento (530)",
         en_eph="AGLOMERADO (32) y REGION (6)",
         escala_comun="provincia (24)",
         estado="ARMONIZADA",
         nota="Es el nivel de integracion del proyecto. La tabla de "
              "correspondencia esta en data/raw/documentacion/"
              "aglomerado_provincia.csv, con 2 aglomerados que cruzan "
              "provincia marcados."),
    dict(concepto="Trabajo adolescente",
         en_aprender="bloques ap21 / ap22 (horas semanales dedicadas a "
                     "actividades, 10 subpreguntas)",
         en_eph="ESTADO = 1 (ocupado) en personas de 12 a 18",
         escala_comun="pendiente",
         estado="NO ARMONIZADA",
         nota="No se puede saber cual de las 10 subpreguntas de Aprender es "
              "'trabajar fuera del hogar' sin el diccionario 2024, que no "
              "esta en el repo (el que hay es de 2022 y usa otra "
              "numeracion). Queda para el TP2."),
    dict(concepto="Asistencia escolar",
         en_aprender="no existe",
         en_eph="CH10 (1 asiste / 2 no asiste pero asistio / 3 nunca asistio)",
         escala_comun="imposible",
         estado="NO ARMONIZABLE",
         nota="ESTE ES EL HALLAZGO CENTRAL DEL ENTREGABLE. A Aprender solo va "
              "quien esta escolarizado: la base no puede contener al que "
              "abandono, por definicion. El fenomeno que el proyecto quiere "
              "predecir es invisible en su fuente principal, y solo la EPH lo "
              "ve. Por eso el target tiene que salir de la EPH (o de los "
              "Indicadores Educativos del Ministerio) y los predictores de "
              "Aprender, y por eso no se pueden unir a nivel individuo."),
]


def main():
    maestro = pd.read_csv(PROCESADO / "dataset_maestro_inicial.csv")
    eph_dicc = pd.read_csv(INTERIM / "eph_diccionario.csv")

    filas = []
    for col in maestro.columns:
        if col in ("jurisdiccion", "departamento", "sector", "ambito"):
            filas.append(dict(
                variable=col, fuente=APRENDER, variable_origen=col,
                bloque="clave territorial", dimension="territorio",
                descripcion="Clave de identificacion territorial de la fila.",
                unidad="texto", denominador="", justificacion="Define la "
                "unidad de analisis del dataset.", limitaciones=""))
        elif col == "estudiantes":
            filas.append(dict(
                variable=col, fuente=APRENDER, variable_origen="ap03 (suma)",
                bloque="volumen", dimension="territorio",
                descripcion="Estudiantes que representa la fila, ya expandidos "
                            "por el factor de ponderacion.",
                unidad="personas (ponderadas)", denominador="",
                justificacion="Es el peso de la fila: sin esto, un "
                              "departamento de 4.000 estudiantes y uno de 20 "
                              "valen igual en cualquier promedio.",
                limitaciones="Tiene decimales porque es una suma de "
                             "ponderadores, no un conteo de personas."))
        elif col == "flag_discrepancia_bases":
            filas.append(dict(
                variable=col, fuente="derivada", variable_origen="",
                bloque="calidad", dimension="calidad",
                descripcion="Marca las filas donde las bases de Lengua y "
                            "Matematica difieren mas de 10% en su total.",
                unidad="booleano", denominador="",
                justificacion="Permite repetir cualquier analisis sin esas "
                              "filas y comprobar que el resultado no cambia.",
                limitaciones="Marca 5 filas de 1.174."))
        elif col.startswith("cob__"):
            bloque = col[len("cob__"):]
            filas.append(dict(
                variable=col, fuente="derivada", variable_origen="",
                bloque=bloque, dimension="calidad",
                descripcion=f"Fraccion de los estudiantes de la fila que quedo "
                            f"representada en el bloque '{bloque}'.",
                unidad="proporcion (0 a 1)",
                denominador="estudiantes de la fila",
                justificacion="Reemplaza a una tasa de no respuesta que daba "
                              "0,00% en los 17 bloques: las columnas Blanco / "
                              "No_disponible / Multimarca del Ministerio estan "
                              "vacias en el 100% de sus celdas, asi que no "
                              "sirven para medir ausencias.",
                limitaciones="Vale 1,00 en los bloques completos."))
        elif col.startswith("eph_educ_adultos__"):
            nivel = col.split("__", 1)[1]
            filas.append(dict(
                variable=col, fuente=EPH, variable_origen="NIVEL_ED (recodificada)",
                bloque="educ_adultos_arm", dimension="contexto",
                descripcion=f"Proporcion de personas de 25 años o mas de la "
                            f"provincia cuyo maximo nivel completado es "
                            f"'{nivel.replace('_', ' ')}', en la escala comun "
                            f"de 4 niveles.",
                unidad="proporcion (0 a 1)",
                denominador="personas de 25+ de la provincia, ponderadas",
                justificacion="Contraparte de educ_madre_arm / educ_padre_arm "
                              "en la escala comun. Sirve para contrastar las "
                              "dos fuentes sobre un mismo concepto.",
                limitaciones="Mide a TODOS los adultos de la provincia, no a "
                             "los padres de los estudiantes evaluados: son "
                             "poblaciones distintas y la comparacion es de "
                             "contexto."))
        elif col.startswith("eph_"):
            fila = eph_dicc[eph_dicc["variable"] == col]
            filas.append(dict(
                variable=col, fuente=EPH, variable_origen="",
                bloque="contexto socioeconomico", dimension="contexto",
                descripcion=(fila["definicion"].item() if len(fila)
                             else "Denominador del indicador correspondiente."),
                unidad=("pesos" if "ipcf" in col else
                        "casos" if "casos" in col or "aglomerados" in col else
                        "proporcion (0 a 1)"),
                denominador="poblacion de la provincia (ver descripcion)",
                justificacion="Aporta el contexto socioeconomico que Aprender "
                              "no tiene, al unico nivel geografico donde las "
                              "dos fuentes se encuentran.",
                limitaciones="Es un valor provincial: TODOS los departamentos "
                             "de una provincia comparten el mismo numero."))
        elif "__" in col:
            bloque, categoria = col.split("__", 1)
            info = BLOQUES.get(bloque)
            if info is None:
                raise SystemExit(f"Bloque sin documentar: '{bloque}'. "
                                 "Agregarlo a BLOQUES antes de seguir.")
            filas.append(dict(
                variable=col, fuente=info["fuente"],
                variable_origen=f"{info['origen']}_{categoria}",
                bloque=bloque, dimension=info["dimension"],
                descripcion=f"{info['descripcion']} Categoria: "
                            f"{categoria.replace('_', ' ')}.",
                unidad="proporcion (0 a 1)",
                denominador=f"estudiantes con respuesta valida en el bloque "
                            f"'{bloque}' (ver cob__{bloque})",
                justificacion=info["justificacion"],
                limitaciones="Es una proporcion dentro de la fila, no un "
                             "conteo: los conteos originales no son "
                             "comparables entre bases porque cada una trae su "
                             "propio factor de expansion."))
        else:
            raise SystemExit(f"Columna sin clasificar: '{col}'")

    diccionario = pd.DataFrame(filas)
    diccionario.to_csv(PROCESADO / "diccionario_variables.csv", index=False,
                       encoding="utf-8")
    armonizacion = pd.DataFrame(ARMONIZACION)
    armonizacion.to_csv(PROCESADO / "armonizacion_fuentes.csv", index=False,
                        encoding="utf-8")

    print("=" * 74)
    print("DICCIONARIO DE VARIABLES")
    print("=" * 74)
    print(f"  variables documentadas: {len(diccionario)} de "
          f"{maestro.shape[1]} columnas del dataset")
    assert len(diccionario) == maestro.shape[1], "Quedaron columnas sin documentar"
    print()
    print(diccionario.groupby(["fuente", "dimension"]).size()
          .rename("variables").to_string())

    print()
    print("=" * 74)
    print("ARMONIZACION ENTRE FUENTES")
    print("=" * 74)
    for a in ARMONIZACION:
        print(f"  [{a['estado']:15s}] {a['concepto']}")
        print(f"      escala comun: {a['escala_comun']}")
    print()
    print(f"  archivos: data/processed/diccionario_variables.csv")
    print(f"            data/processed/armonizacion_fuentes.csv")


if __name__ == "__main__":
    main()
