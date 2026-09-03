"""Las etapas del pipeline, en orden, con lo que consume y lo que produce cada una.

Este archivo es el mapa del proyecto. Si alguien lee una sola cosa antes de
tocar nada, que sea esto: dice que se hace, en que orden, y de que depende cada
paso. El detalle del como esta en el docstring de cada script.

Regla que ordena todo (ver `contrato.py`): una etapa NUNCA escribe sobre su
propia entrada. Por eso la integracion produce `dataset_maestro_base.csv` y la
armonizacion lo lee para producir `dataset_maestro_inicial.csv`, en vez de las
dos escribir sobre el mismo archivo.
"""

from contrato import Etapa

RAW = "data/raw"
DOCS = "data/raw/documentacion"
INTERIM = "data/interim"
PROC = "data/processed"

ETAPAS = [
    Etapa(
        numero=1,
        nombre="aprender",
        archivo="01_aprender.py",
        que_hace=(
            "Convierte las bases censales de Aprender 2024 en proporciones por "
            "fila, con la cobertura de cada bloque al lado como indicador de "
            "calidad del dato."
        ),
        entradas=(
            f"{RAW}/ap2024_Desempenos_de_Lengua.csv",
            f"{RAW}/ap2024_Desempenos_de_Matematica.csv",
        ),
        salidas=(f"{INTERIM}/aprender_2024_proporciones.csv",),
    ),
    Etapa(
        numero=2,
        nombre="eph_unir",
        archivo="02_eph_unir.py",
        que_hace=(
            "Une las bases de Hogar e Individual de la EPH 3T-2025 por "
            "CODUSU + NRO_HOGAR. CODUSU solo no alcanza: hay viviendas con mas "
            "de un hogar."
        ),
        entradas=(f"{RAW}/eph3t.zip",),
        salidas=(f"{INTERIM}/eph_3t2025_unida.parquet",),
    ),
    Etapa(
        numero=3,
        nombre="eph_indicadores",
        archivo="03_eph_indicadores.py",
        que_hace=(
            "Calcula los indicadores socioeconomicos por provincia, todos "
            "ponderados. El ingreso va con PONDIH y no con PONDERA."
        ),
        entradas=(
            f"{INTERIM}/eph_3t2025_unida.parquet",
            f"{DOCS}/aglomerado_provincia.csv",
        ),
        salidas=(
            f"{INTERIM}/eph_indicadores_provincia.csv",
            f"{INTERIM}/eph_diccionario.csv",
        ),
    ),
    Etapa(
        numero=4,
        nombre="integrar",
        archivo="04_integrar.py",
        que_hace=(
            "Cruza Aprender con el contexto de la EPH. Es un join de muchos a "
            "uno: cada departamento hereda los indicadores de su provincia, y "
            "esa es la principal limitacion del dataset."
        ),
        entradas=(
            f"{INTERIM}/aprender_2024_proporciones.csv",
            f"{INTERIM}/eph_indicadores_provincia.csv",
        ),
        salidas=(f"{PROC}/dataset_maestro_base.csv",),
    ),
    Etapa(
        numero=5,
        nombre="armonizar",
        archivo="05_armonizar.py",
        que_hace=(
            "Lleva a una escala comparable las variables que las dos fuentes "
            "miden distinto, y deja el dataset maestro final."
        ),
        entradas=(
            f"{PROC}/dataset_maestro_base.csv",
            f"{INTERIM}/eph_3t2025_unida.parquet",
            f"{DOCS}/aglomerado_provincia.csv",
        ),
        salidas=(f"{PROC}/dataset_maestro_inicial.csv",),
    ),
    Etapa(
        numero=6,
        nombre="diccionario",
        archivo="06_diccionario.py",
        que_hace=(
            "Genera una fila por columna del dataset, con su definicion y su "
            "fuente, mas la tabla de correspondencia entre Aprender y la EPH."
        ),
        entradas=(
            f"{PROC}/dataset_maestro_inicial.csv",
            f"{INTERIM}/eph_diccionario.csv",
        ),
        salidas=(
            f"{PROC}/diccionario_variables.csv",
            f"{PROC}/armonizacion_fuentes.csv",
        ),
    ),
]


def por_nombre(texto: str) -> Etapa:
    """Busca una etapa por nombre o por numero. Acepta '4', '04' o 'integrar'."""
    texto = texto.strip().lstrip("0") or "0"
    for etapa in ETAPAS:
        if texto == etapa.nombre or texto == str(etapa.numero):
            return etapa
    disponibles = ", ".join(f"{e.numero}={e.nombre}" for e in ETAPAS)
    raise SystemExit(f"No existe la etapa '{texto}'. Hay: {disponibles}")
