"""Definiciones del TP3 (modelado). FUENTE UNICA.

De aca salen el target, los bloques de variables y la lista de experimentos.
Las etapas 12 a 17 lo importan; ninguna redefine nada de esto por su cuenta.

Para probar otra combinacion no se toca ninguna etapa: se agrega o se cambia
una entrada de EXPERIMENTOS y se corre

    python pipeline/correr.py --desde 15

Las decisiones que estan detras de cada valor viven en
entregas/03-machine-learning/DECISIONES-TP3.md (seccion "Vigente al 2026-10-09").
"""

# ---------------------------------------------------------------------------
# La fuente del target: Relevamiento Anual, consolidado por el repo de
# referencia (agus476/radar-trayectorias-educativas-argentinas), fijado a un
# commit y verificado por hash. Los datos no se versionan: se bajan solos.
# ---------------------------------------------------------------------------

REPO_REFERENCIA = "agus476/radar-trayectorias-educativas-argentinas"
COMMIT_REFERENCIA = "1bbaa58a3e5b0ed7efef9e4c752a1bf373825823"
ARCHIVOS_RELEVAMIENTO = {
    "Trayectoria_Sexo_Final.csv": (
        "02_data_formatting/Trayectoria_Sexo_Final.csv",
        "4de444e641932eca98f1bd24bab4fb7108bbe1af726a6f59558c7dc2d1694d14",
    ),
    "Establecimiento_Caracteristicas_Final.csv": (
        "02_data_formatting/Establecimiento_Caracteristicas_Final.csv",
        "fbe9921bbfad6c7236483289f6005d6cfd668b9e9562734a4a9f5b5227b32c4f",
    ),
}

# El archivo "2024" del Relevamiento parece traer el ciclo lectivo 2023
# (INFERIDO de los datos, no documentado: la matricula inicial de ultimo anio
# del archivo 2024 coincide con la matricula 2023). Se usa igual y la etapa 13
# mide cuan estable es la tasa de cada grupo entre dos archivos seguidos.
ANIO_RELEVAMIENTO = 2024
ANIO_ESTABILIDAD = 2023

# ---------------------------------------------------------------------------
# Los anios de estudio. El Relevamiento numera de corrido del 1 al 12 (mas
# "1314", el anio extra de las tecnicas) sin decir donde empieza la
# secundaria. En 12 jurisdicciones la escuela es 7 + 5 y en las otras 12 es
# 6 + 6 (MEDIDO el 09/10 comparando promocion y salidas de los indices 6, 7 y
# 8). Lo comun a todo el pais: 11 y 12 son los dos ultimos anios de la
# secundaria, que es la poblacion que evalua Aprender.
# ---------------------------------------------------------------------------

PROVINCIAS_7_5 = {
    "chaco", "ciudad autonoma de buenos aires", "jujuy", "la rioja",
    "mendoza", "misiones", "neuquen", "rio negro", "salta", "santa cruz",
    "santa fe", "santiago del estero",
}

ANIOS_TARGET = {
    # principal: la misma poblacion que Aprender
    "ultimos2": lambda es_7_5: ["11", "12"],
    # control: la secundaria entera de cada provincia
    "secundaria": lambda es_7_5: (
        ["8", "9", "10", "11", "12", "1314"] if es_7_5
        else ["7", "8", "9", "10", "11", "12", "1314"]
    ),
}

# "Abandono alto" = el cuarto de grupos con la tasa mas alta. El corte se
# calcula sobre los grupos con matricula en esos anios.
CUANTIL_ALTO = 0.75

# ---------------------------------------------------------------------------
# Los bloques de variables. Un bloque es un conjunto de columnas que entra o
# sale entero de un experimento.
# ---------------------------------------------------------------------------

# Aprender: las proporciones dentro de la fila (columnas con "__"), sin la
# cobertura ni los indicadores de la EPH. Es el diferencial del proyecto.
PREFIJOS_EXCLUIDOS_APRENDER = ("cob__", "eph_")

# Contexto del grupo que no es una respuesta de los estudiantes.
CONTEXTO = ["sector_estatal", "ambito_rural", "log_estudiantes"]

# El edificio (Relevamiento, todos los niveles de la localizacion, no solo
# secundaria): proporcion de localizaciones con cada atributo.
EDIFICIO = {
    "edif_electricidad": "electricidadsi",
    "edif_sala_informatica": "disponedesalaolaboratoriodeinformáticasi",
    "edif_biblioteca": "bibliotecadisponedealmenosunasi",
    "edif_internet_pago": "internettipodeserviciopago",
}

# EPH "acotada" (Noelia, 23/09): dos indicadores provinciales.
EPH = ["eph_ipcf_mediano", "eph_adultos_sin_secundaria"]

# Lo que NUNCA entra como predictor: describe el mismo cierre de ciclo que el
# abandono (no promovidos, pases, egresados) o es el propio target. Lo chequea
# tests/test_invariantes.py.
PROHIBIDOS = ("ssp", "scp", "nopromo", "promovidos", "egresados", "ultimo_",
              "entrados", "tasa_", "alto_")

# ---------------------------------------------------------------------------
# Los experimentos. Cada uno es una combinacion. El primero es el principal.
# ---------------------------------------------------------------------------

# La provincia como variable (una columna 0/1 por provincia, "provincia_<nombre>").
# Responde a la pregunta de Ignacio del 09/10 sobre modelos por provincia: con
# ~49 grupos y ~12 positivos por provincia no se puede entrenar uno por cada
# una, pero un modelo unico que sabe la provincia Y el perfil si se puede.
PREFIJO_PROVINCIA = "provincia_"

EXPERIMENTOS = [
    {"id": "principal", "anios": "ultimos2", "corte": "nacional",
     "bloques": ["aprender", "contexto"]},
    {"id": "con_edificio", "anios": "ultimos2", "corte": "nacional",
     "bloques": ["aprender", "contexto", "edificio"]},
    {"id": "con_eph", "anios": "ultimos2", "corte": "nacional",
     "bloques": ["aprender", "contexto", "eph"]},
    {"id": "secundaria_entera", "anios": "secundaria", "corte": "nacional",
     "bloques": ["aprender", "contexto"]},
    {"id": "corte_por_provincia", "anios": "ultimos2", "corte": "provincial",
     "bloques": ["aprender", "contexto"]},
    # 13/10: lo que quedo abierto el 09/10
    {"id": "provincia_y_perfil", "anios": "ultimos2", "corte": "nacional",
     "bloques": ["aprender", "contexto", "provincia"]},
    {"id": "corte_tercio", "anios": "ultimos2", "corte": "nacional",
     "cuantil": 2 / 3, "bloques": ["aprender", "contexto"]},
    {"id": "corte_quinto", "anios": "ultimos2", "corte": "nacional",
     "cuantil": 0.80, "bloques": ["aprender", "contexto"]},
]


def cuantil_de(exp):
    """El corte de "abandono alto" de un experimento (por defecto, el cuarto)."""
    return exp.get("cuantil", CUANTIL_ALTO)


def columna_target(anios, corte, cuantil=CUANTIL_ALTO):
    """Nombre de la columna del target. UNA regla para las etapas 14, 15 y 16."""
    sufijo = "" if abs(cuantil - CUANTIL_ALTO) < 1e-9 else f"_q{round(cuantil * 100)}"
    return f"alto_{anios}_{corte}{sufijo}"


def target_de(exp):
    return columna_target(exp["anios"], exp["corte"], cuantil_de(exp))

SEMILLA = 2026
FOLDS = 5
