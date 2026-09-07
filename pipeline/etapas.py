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
        archivo="01_fuentes/01_aprender.py",
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
        archivo="01_fuentes/02_eph_unir.py",
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
        archivo="01_fuentes/03_eph_indicadores.py",
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
        archivo="02_integracion/04_integrar.py",
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
        archivo="02_integracion/05_armonizar.py",
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
        numero=7,
        nombre="perfilado",
        archivo="03_curacion/07_perfilado.py",
        que_hace=(
            "Mide el dataset maestro columna por columna: tipos, faltantes, "
            "rangos, duplicados, variabilidad y valores imposibles. No corrige "
            "nada: produce la evidencia con la que se deciden las curaciones."
        ),
        entradas=(f"{PROC}/dataset_maestro_inicial.csv",),
        salidas=(
            f"{INTERIM}/perfil_columnas.csv",
            "docs/07_perfil_calidad.md",
        ),
    ),
    Etapa(
        numero=8,
        nombre="curar",
        archivo="03_curacion/08_curar.py",
        que_hace=(
            "Aplica las decisiones de curacion que salieron del perfil. No "
            "borra filas ni modifica valores: agrega columnas que hacen visible "
            "cada problema, para poder excluirlo con una condicion explicita."
        ),
        entradas=(f"{PROC}/dataset_maestro_inicial.csv",),
        salidas=(
            f"{PROC}/dataset_maestro_curado.csv",
            "docs/08_decisiones_curacion.md",
        ),
    ),
    Etapa(
        numero=9,
        nombre="diccionario",
        archivo="03_curacion/09_diccionario.py",
        que_hace=(
            "Genera UNA fila por cada columna del dataset curado, con su "
            "definicion, su fuente y su denominador, mas la tabla de "
            "correspondencia entre Aprender y la EPH. Va al final del pipeline "
            "para que documente lo que el proyecto entrega y para que haya un "
            "solo diccionario, no uno por version del dataset."
        ),
        entradas=(
            f"{PROC}/dataset_maestro_curado.csv",
            f"{INTERIM}/eph_diccionario.csv",
        ),
        salidas=(
            f"{PROC}/diccionario_variables.csv",
            f"{PROC}/armonizacion_fuentes.csv",
        ),
    ),
    Etapa(
        numero=10,
        nombre="relaciones",
        archivo="04_analisis/10_relaciones.py",
        que_hace=(
            "Explora las relaciones del dataset curado (actividad 3 de la "
            "consigna) y ademas mide si alguna decision de curacion movio algun "
            "numero. Todo ponderado por estudiantes; las correlaciones con la "
            "EPH, a nivel provincia."
        ),
        entradas=(f"{PROC}/dataset_maestro_curado.csv",),
        salidas=(
            f"{PROC}/relaciones_tablas.csv",
            "docs/10_relaciones.md",
        ),
    ),
    Etapa(
        numero=11,
        nombre="figuras",
        archivo="04_analisis/11_figuras.py",
        que_hace=(
            "Las cuatro figuras del TP2, una por hallazgo. Heredan la paleta y "
            "los criterios del TP1 sin agregar colores: paleta validada para "
            "daltonismo, marcas finas, grilla recesiva y etiquetas directas."
        ),
        entradas=(f"{PROC}/dataset_maestro_curado.csv",),
        salidas=(
            "figuras/tp2_a_calidad_cobertura.png",
            "figuras/tp2_b_brecha_gestion.png",
            "figuras/tp2_c_contexto_rendimiento.png",
            "figuras/tp2_d_inasistencias.png",
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
