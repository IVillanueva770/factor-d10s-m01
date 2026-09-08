"""Etapa 12: genera el notebook de Colab del TP2.

El notebook se GENERA desde este script en vez de editarse a mano, igual que en
el TP1. La razon es la misma y vale repetirla: un notebook editado a mano se
desincroniza del pipeline el primer dia que alguien cambia una decision en
`pipeline/` y se olvida de reflejarla. Aca la fuente de verdad es el codigo, y
el .ipynb es una salida.

Eso ademas resuelve por otro camino el problema que Noelia planteo con
jupytext: un .ipynb versiona pesimo porque guarda outputs y metadata como JSON,
asi que dos personas que corren la misma celda generan un diff enorme. Como
este notebook se genera, lo que se versiona y se revisa es este .py, que diffea
limpio. **Si en algun momento el equipo empieza a editar el notebook a mano,
este modelo se rompe y ahi jupytext pasa a ser la respuesta correcta.**

De donde saca los datos
-----------------------
El notebook baja `dataset_maestro_inicial.csv` (la salida del TP1, ya entregada
y aprobada) desde el repo del proyecto, FIJADO A UN COMMIT EXACTO y verificando
el SHA-256. No se embebe el dataset adentro del .ipynb: son 2,3 MB que dejarian
el archivo ilegible en GitHub, que es justo lo que se quiere evitar.

El TP2 arranca de ahi y agrega lo suyo: perfilado, curacion y analisis de
relaciones. Reconstruir el maestro adentro seria duplicar 600 lineas del TP1.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contenido_tp2 import secciones_2_a_7  # noqa: E402

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"
NOTEBOOKS = BASE_DIR / "notebooks"
DESTINO = NOTEBOOKS / "TP2_EDA_y_curacion_El_Factor_D10S.ipynb"

MAESTRO = "data/processed/dataset_maestro_inicial.csv"
DICCIONARIO = "data/processed/diccionario_variables.csv"


def git(*args):
    return subprocess.run(["git", "-C", str(BASE_DIR), *args],
                          capture_output=True, text=True).stdout.strip()


def origen_del_repo():
    """URL cruda del repo y commit actual, para fijar la descarga.

    Falla ruidosamente si no hay remoto configurado, en vez de generar un
    notebook que apunte a ningun lado y descubrirlo cuando la mentora lo abra.
    """
    remoto = git("remote", "get-url", "origin")
    if not remoto:
        raise SystemExit(
            "No hay remoto 'origin' configurado.\n"
            "El notebook necesita una URL publica de donde bajar el dataset.\n"
            "Crear el repo con:\n"
            "  gh repo create factor-d10s-m01 --public --source=. "
            "--remote=origin\n"
            "  git push -u origin master")
    slug = (remoto.replace("https://github.com/", "")
                  .replace("git@github.com:", "").replace(".git", ""))
    commit = git("rev-parse", "HEAD")
    sucio = git("status", "--porcelain")
    if sucio:
        print("  AVISO: hay cambios sin commitear. El notebook va a apuntar a")
        print("         un commit que no los incluye. Commitear antes de la entrega.")
    return f"https://raw.githubusercontent.com/{slug}/{commit}", commit, slug


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


celdas = []


def en_lineas(texto):
    """El .ipynb guarda el contenido como lista de lineas CON su salto.

    Sin los saltos el notebook abre igual pero queda todo en una linea y no
    ejecuta. Es el mismo helper del TP1.
    """
    return texto.splitlines(keepends=True)


def md(texto):
    celdas.append({"cell_type": "markdown", "metadata": {},
                   "source": en_lineas(texto.strip())})


def code(texto):
    celdas.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                   "outputs": [], "source": en_lineas(texto.strip("\n"))})


def construir(base_url: str, commit: str, slug: str):
    celdas.clear()

    # ================================================== PORTADA E INDICE
    md(f"""
# El Factor D10S · Análisis exploratorio y curación

**Entregable 2 de la mentoría** · Grupo M01 · Mentora: Noelia Ferrero
Diplomatura en Ciencia de Datos · FAMAF, UNC

Nos preguntamos si se pueden detectar señales tempranas de abandono
escolar cruzando dos fuentes públicas argentinas: las **Pruebas Aprender**
(la evaluación censal del Ministerio de Educación) y la **EPH** (la encuesta
de hogares del INDEC).

En el **entregable 1** construimos el dataset maestro. En este **entregable 2**
no agregamos fuentes: nos dedicamos a entender qué tiene esa base, qué problemas
de calidad esconde, y a dejarla curada para las etapas que siguen.

La frase que nos ordenó todo el trabajo está en la consigna: *"No queremos una
base perfectamente limpia. Queremos una base cuyas decisiones de limpieza
podamos explicar."* Por eso cada decisión de este notebook viene con lo que
medimos para tomarla y con lo que descartamos.

---

## Índice

1. **De dónde partimos**: el dataset del TP1, descargado y verificado, y cómo
   trabajamos
2. **Conocer el dataset**: qué hay adentro y cómo leerlo
3. **Explorar la calidad**: doce chequeos, cada uno con su denominador
4. **Explorar relaciones**: qué se relaciona con qué, y cuánto confiar
5. **Curar**: cuatro decisiones, con lo que medimos para tomarlas
6. **Hallazgos y preguntas nuevas**
7. **Limitaciones**: lo que esta base no puede responder
8. **Qué sigue**: las tres tareas que abrimos para el TP3, ya medidas

---

**Reproducibilidad.** Este notebook se genera desde
[`pipeline/06_entrega/12_notebook.py`](https://github.com/{slug}/blob/{commit}/pipeline/06_entrega/12_notebook.py)
y baja los datos fijados al commit `{commit[:7]}`, verificando el SHA-256 de
cada archivo. El código del proyecto está en
[github.com/{slug}](https://github.com/{slug}).
""")

    # ============================================ 1. DE DONDE PARTIMOS
    md("""
## 1. De dónde partimos

En el TP1 dejamos un dataset maestro de **1.174 filas por 131 columnas**, que
representa a **540.040 estudiantes** de 5º y 6º año de secundaria.

Lo primero y más importante para leer todo lo que sigue:

> **Cada fila es un grupo, no una persona.** Una fila es la combinación
> *jurisdicción × departamento × sector de gestión × ámbito*, y puede
> representar desde 1 estudiante hasta 13.758.

Eso tiene una consecuencia que atraviesa el notebook entero: **todo promedio
va ponderado por la cantidad de estudiantes**. Un promedio simple le daría el
mismo peso a un departamento rural de 29 chicos que a uno urbano de mil, y
entonces hablaría de departamentos en vez de hablar de chicos.

Bajamos los datos fijados a un commit exacto y verificamos el hash de cada
archivo. Si el archivo cambió, la celda falla en vez de seguir con datos
distintos de los que este análisis describe.

### Cómo trabajamos

Seguimos **CRISP-DM**, que es el estándar de la industria para proyectos de
datos. El TP1 cubrió sus dos primeras fases (*Business Understanding* y
*Data Understanding* inicial) y este TP2 completa la tercera, *Data
Preparation*: perfilar, decidir qué hacer con cada problema y consolidar el
dataset analítico. El TP3 entra en *Modeling* y *Evaluation*.

De CRISP-DM nos importa sobre todo que **es iterativo y no lineal**: el
reencuadre que trajo la devolución del TP1, pasar de un modelo individual a uno
ecológico sobre agregados territoriales, es exactamente una vuelta de
*Business Understanding* disparada por lo que aprendimos de los datos. Lo
tomamos, y por eso todo lo que sigue habla de grupos y nunca de estudiantes.

En lo operativo, el proyecto está armado como un **pipeline por etapas con
contrato explícito**: cada etapa declara qué archivos necesita y cuáles
produce, y un runner lo hace cumplir. Nada corre sin sus insumos y nada queda
escrito fuera de lo declarado. Encima corren **55 verificaciones automáticas**
sobre los datos, y dos corridas seguidas del pipeline dan **18 de 18 salidas
idénticas byte a byte**: la reproducibilidad la medimos, no la prometemos.
""")

    # Chequeo de dependencias ANTES de bajar nada. Las dos que verifica son
    # requisitos REALES del notebook que no se ven leyendolo:
    #
    #   pandas >= 2.2  por `groupby(...).apply(..., include_groups=False)`.
    #                  Con 2.1 tira "unexpected keyword argument", que no
    #                  explica nada a quien lo recibe.
    #   scipy          por `corr(method="spearman")`, que pandas delega en
    #                  scipy.stats. El notebook nunca lo importa, asi que la
    #                  dependencia es invisible hasta que revienta a mitad.
    #
    # En Colab las dos estan y esta celda no dice nada. En un entorno pelado
    # corta ACA con instrucciones, y no doce celdas mas abajo con un error
    # que no se entiende. Medido el 2026-09-07 armando un entorno limpio:
    # sin scipy fallaban 3 de 24 celdas, y con pandas 2.1.4 fallaban 2.
    md("""
Antes de bajar nada, el notebook chequea que el entorno tenga lo que necesita.
En Google Colab esta celda no dice nada porque ya está todo; en un entorno
propio, corta acá con instrucciones en vez de fallar a mitad del análisis con
un error que no se entiende.
""")

    code('''
import sys

FALTA = []

try:
    import pandas as pd
    if tuple(int(x) for x in pd.__version__.split(".")[:2]) < (2, 2):
        FALTA.append(f"pandas >= 2.2 (tenes {pd.__version__}): lo necesita "
                     "groupby(...).apply(..., include_groups=False)")
except ImportError:
    FALTA.append("pandas >= 2.2")

try:
    import scipy  # noqa: F401  (no se usa directo: lo usa pandas por dentro)
except ImportError:
    FALTA.append("scipy: lo necesita Series.corr(method='spearman'), que "
                 "pandas delega en scipy.stats")

for modulo in ("numpy", "matplotlib"):
    try:
        __import__(modulo)
    except ImportError:
        FALTA.append(modulo)

if FALTA:
    # chr(10) y no la secuencia de escape: este texto pasa por el generador
    # del notebook, donde un escape se expande a un salto REAL y parte el
    # string literal de la celda en dos. Se rompio asi una vez, con un
    # SyntaxError en la celda 3 que no decia nada del origen.
    salto = chr(10)
    raise SystemExit(
        "Faltan dependencias:" + salto + "  - " +
        (salto + "  - ").join(FALTA) + salto + salto +
        "Instalalas con:" + salto +
        "  pip install 'pandas>=2.2' numpy matplotlib scipy")

print("Entorno OK.")
print(f"  pandas {pd.__version__} . numpy {__import__('numpy').__version__} "
      f". matplotlib {__import__('matplotlib').__version__} "
      f". scipy {scipy.__version__}")
''')

    code(f'''
import hashlib
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

BASE = "{base_url}"

# El hash de cada archivo, calculado al generar este notebook. Si el archivo
# de origen cambiara, la descarga falla en vez de seguir en silencio con datos
# distintos de los que este analisis describe.
ARCHIVOS = {{
    "{MAESTRO.split('/')[-1]}": "{sha256(PROC / 'dataset_maestro_inicial.csv')}",
    "{DICCIONARIO.split('/')[-1]}": "{sha256(PROC / 'diccionario_variables.csv')}",
}}


def descargar(nombre, hash_esperado):
    """Baja el archivo y verifica su SHA-256. Sin red no hay analisis."""
    destino = Path(nombre)
    if not destino.exists():
        urllib.request.urlretrieve(f"{{BASE}}/data/processed/{{nombre}}", destino)
    real = hashlib.sha256(destino.read_bytes()).hexdigest()
    if real != hash_esperado:
        raise SystemExit(
            f"El hash de {{nombre}} no coincide.\\n"
            f"  esperado: {{hash_esperado}}\\n"
            f"  obtenido: {{real}}\\n"
            "El archivo de origen cambio: este notebook describe otra version.")
    print(f"  {{nombre}}  OK  ({{destino.stat().st_size / 1024:,.0f}} KB)")
    return destino


for nombre, h in ARCHIVOS.items():
    descargar(nombre, h)

maestro = pd.read_csv("dataset_maestro_inicial.csv")
diccionario = pd.read_csv("diccionario_variables.csv")

print()
print(f"dataset maestro: {{len(maestro):,}} filas x {{maestro.shape[1]}} columnas")
print(f"estudiantes representados: {{maestro['estudiantes'].sum():,.0f}}")
''')

    md("""
### Una función que se usa en todo el notebook

Como cada fila es un grupo de distinto tamaño, el promedio simple no sirve.
Esta función pondera por cantidad de estudiantes y devuelve `NaN` (y no cero)
cuando no hay ningún caso con dato: un cero se leería como *"el valor es
cero"*, cuando lo cierto sería *"no hay dato"*.
""")

    code('''
def media_ponderada(tabla, columna, peso="estudiantes"):
    """Promedio ponderado por cantidad de estudiantes, ignorando faltantes."""
    validos = tabla[tabla[columna].notna()]
    if validos.empty or validos[peso].sum() == 0:
        return np.nan
    return np.average(validos[columna], weights=validos[peso])


# Nombres largos que se repiten. Verificados contra el dataset, no escritos
# de memoria: una version anterior de este analisis los adivino y fallo.
MATE_BAJO = "desemp_matematica__por_debajo_del_nivel_basico"
LENGUA_BAJO = "desemp_lengua__por_debajo_del_nivel_basico"
SOBREEDAD_ALTA = "sobreedad__3_anos_o_mas_de_sobreedad_20_anos_o_mas_30jun"
INGRESO = "eph_ipcf_mediano"
CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]

print(f"{media_ponderada(maestro, MATE_BAJO):.1%} de los estudiantes esta por "
      "debajo del nivel basico en matematica")
''')

    # Las secciones 2 a 7 viven en `contenido_tp2.py`: ahi va el texto y el
    # codigo que se ve en el notebook, y aca la mecanica de armarlo. Juntos
    # darian un archivo de 900 lineas donde no se encuentra nada.
    secciones_2_a_7(md, code)

    return celdas


def main():
    base_url, commit, slug = origen_del_repo()
    construir(base_url, commit, slug)

    notebook = {
        "cells": celdas,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python"},
            "colab": {"provenance": [], "toc_visible": True},
        },
        "nbformat": 4,
        "nbformat_minor": 0,
    }
    NOTEBOOKS.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")

    print("=" * 74)
    print("NOTEBOOK DEL TP2")
    print("=" * 74)
    print(f"  repo   : {slug}")
    print(f"  commit : {commit[:7]}")
    print(f"  celdas : {len(celdas)} "
          f"({sum(1 for c in celdas if c['cell_type'] == 'markdown')} markdown, "
          f"{sum(1 for c in celdas if c['cell_type'] == 'code')} codigo)")
    print(f"  GUARDADO: notebooks/{DESTINO.name} "
          f"({DESTINO.stat().st_size / 1024:,.0f} KB)")


if __name__ == "__main__":
    main()
