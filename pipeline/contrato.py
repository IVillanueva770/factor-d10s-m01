"""El contrato que cumple toda etapa del pipeline.

Por que existe
--------------
Un pipeline escrito como scripts sueltos anda mientras el que lo escribio se
acuerda del orden. Meses despues nadie sabe cual va primero, que archivo espera
cada uno ni si correr uno dos veces hace dano. Este modulo convierte esa memoria
en algo declarado y verificable.

Una Etapa declara TRES cosas y el runner las hace cumplir:

  entradas  los archivos que necesita. Si falta uno, la etapa no arranca y dice
            cual falta y que etapa lo produce. No corre a medias.
  salidas   los archivos que produce. Si al terminar no aparecieron todos, es
            error aunque el script haya salido con codigo 0.
  el orden  cada etapa se numera y solo puede leer salidas de etapas anteriores.

Las tres reglas duras
---------------------
1. NINGUNA ETAPA ESCRIBE SOBRE SU PROPIA ENTRADA.
   Se verifica en `validar_declaracion()` y rompe al importar, no al correr.
   Sale de un bug medido el 2026-09-03: la etapa de armonizacion leia
   `dataset_maestro_inicial.csv` y escribia encima del mismo archivo. Correrla
   dos veces sin rehacer la etapa anterior llevaba el dataset de 131 a 155
   columnas, agregando columnas sobre columnas, sin fallar y sin avisar.

2. MISMA ENTRADA, MISMA SALIDA, SIEMPRE.
   `python pipeline/correr.py --verificar` corre el pipeline entero dos veces y
   compara los SHA-256 de cada salida. Si una etapa mete una fecha, un orden de
   diccionario o un random sin semilla, se ve ahi.

3. LO QUE SE AFIRMA SE MIDE.
   El manifiesto guarda hash, filas, columnas y tiempo de cada salida. No es
   decoracion: es contra que se compara cuando alguien toca una etapa de arriba
   y quiere saber que se movio abajo.

Como agregar una etapa
----------------------
Se escribe el script con su `main()`, se declara en `etapas.py` con sus
entradas y salidas, y listo. El runner se encarga del resto. Si la declaracion
esta mal (pisa su entrada, o pide un archivo que ninguna etapa produce y que
tampoco esta en los crudos), el runner lo dice antes de ejecutar nada.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DIR = BASE_DIR / "pipeline"
MANIFIESTO = PIPELINE_DIR / "MANIFIESTO.json"


@dataclass(frozen=True)
class Etapa:
    """Una etapa del pipeline, con su contrato declarado.

    numero    posicion en el orden. Solo puede leer salidas de numeros menores.
    nombre    identificador corto, el que se usa en la linea de comandos.
    archivo   el .py que la implementa, relativo a pipeline/.
    que_hace  una linea. Es lo que lee el que retoma en seis meses.
    entradas  rutas relativas a la raiz del proyecto.
    salidas   idem. Tienen que existir cuando la etapa termina.
    """

    numero: int
    nombre: str
    archivo: str
    que_hace: str
    entradas: tuple[str, ...] = field(default_factory=tuple)
    salidas: tuple[str, ...] = field(default_factory=tuple)

    @property
    def etiqueta(self) -> str:
        return f"{self.numero:02d}_{self.nombre}"

    @property
    def ruta(self) -> Path:
        return PIPELINE_DIR / self.archivo


class ContratoRoto(Exception):
    """Una etapa no cumplio lo que declaro. Nunca se traga: corta la corrida."""


def hash_de(ruta: Path) -> str:
    """SHA-256 del archivo, leido de a pedazos para no cargar 40 MB en memoria."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def forma_de(ruta: Path) -> str:
    """'1.174 x 131' para tablas; el tamano en KB para lo que no es tabla.

    Sirve para que el manifiesto se lea de un vistazo: un hash que cambia no
    dice que paso, 131 columnas que pasan a 155 si.
    """
    if ruta.suffix not in {".csv", ".parquet"}:
        return f"{ruta.stat().st_size / 1024:,.0f} KB"
    try:
        import pandas as pd

        tabla = (pd.read_parquet(ruta) if ruta.suffix == ".parquet"
                 else pd.read_csv(ruta, low_memory=False))
        return f"{len(tabla):,} x {tabla.shape[1]:,}"
    except Exception as e:  # el manifiesto no puede tumbar la corrida
        return f"(no se pudo leer: {type(e).__name__})"


def validar_declaracion(etapas: list[Etapa]) -> None:
    """Chequea las reglas del contrato ANTES de ejecutar nada.

    Es barato y corta temprano: si una declaracion esta mal, enterarse despues
    de veinte minutos de pipeline es el peor momento.
    """
    problemas = []

    numeros = [e.numero for e in etapas]
    if len(set(numeros)) != len(numeros):
        problemas.append("hay numeros de etapa repetidos")
    if numeros != sorted(numeros):
        problemas.append("las etapas no estan declaradas en orden")

    producido_por: dict[str, Etapa] = {}
    for etapa in etapas:
        if not etapa.ruta.exists():
            problemas.append(f"{etapa.etiqueta}: no existe {etapa.archivo}")

        # Regla 1: ninguna etapa escribe sobre su propia entrada.
        pisadas = set(etapa.entradas) & set(etapa.salidas)
        if pisadas:
            problemas.append(
                f"{etapa.etiqueta}: escribe sobre su propia entrada "
                f"({', '.join(sorted(pisadas))}). Una etapa que muta su input "
                f"no se puede correr dos veces sin cambiar de resultado: "
                f"tiene que escribir a un archivo nuevo."
            )

        for salida in etapa.salidas:
            if salida in producido_por:
                problemas.append(
                    f"{etapa.etiqueta} y {producido_por[salida].etiqueta} "
                    f"escriben las dos {salida}"
                )
            producido_por[salida] = etapa

        # Solo se puede leer lo que produjo una etapa anterior, o un crudo.
        for entrada in etapa.entradas:
            productora = producido_por.get(entrada)
            if productora is None:
                if not (BASE_DIR / entrada).exists():
                    problemas.append(
                        f"{etapa.etiqueta}: necesita {entrada}, que ninguna "
                        f"etapa anterior produce y tampoco existe como crudo"
                    )
            elif productora.numero >= etapa.numero:
                problemas.append(
                    f"{etapa.etiqueta}: lee {entrada}, que produce "
                    f"{productora.etiqueta} (posterior o igual)"
                )

    if problemas:
        raise ContratoRoto(
            "La declaracion de etapas esta mal:\n  - " + "\n  - ".join(problemas)
        )


def _importar(etapa: Etapa):
    """Importa el modulo de la etapa por ruta.

    Va por ruta y no por `import` normal porque los archivos empiezan con
    numero (`01_aprender.py`) y eso no es un identificador valido de Python.
    El numero al principio vale mas que la comodidad del import: es lo que
    hace que el orden se vea listando la carpeta.
    """
    spec = importlib.util.spec_from_file_location(
        f"etapa_{etapa.etiqueta}", etapa.ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def correr_etapa(etapa: Etapa, verboso: bool = False) -> dict:
    """Corre una etapa haciendo cumplir su contrato de las dos puntas.

    Devuelve el registro que va al manifiesto. Levanta ContratoRoto si falta
    una entrada antes o una salida despues.
    """
    faltan = [e for e in etapa.entradas if not (BASE_DIR / e).exists()]
    if faltan:
        raise ContratoRoto(
            f"{etapa.etiqueta} no puede arrancar, le faltan entradas:\n  - "
            + "\n  - ".join(faltan)
            + "\n(corre las etapas anteriores primero: "
              "python pipeline/correr.py)"
        )

    arranco = time.perf_counter()
    modulo = _importar(etapa)
    if not hasattr(modulo, "main"):
        raise ContratoRoto(f"{etapa.etiqueta}: {etapa.archivo} no define main()")

    import contextlib
    import io as _io

    if verboso:
        modulo.main()
    else:
        # Los scripts imprimen su propio diagnostico, que es util cuando se
        # corre uno solo y ruido cuando se corren los seis. Se guarda igual
        # por si la etapa falla: ahi se muestra entero.
        salida_capturada = _io.StringIO()
        try:
            with contextlib.redirect_stdout(salida_capturada):
                modulo.main()
        except Exception:
            print(salida_capturada.getvalue())
            raise
    demoro = time.perf_counter() - arranco

    no_aparecieron = [s for s in etapa.salidas if not (BASE_DIR / s).exists()]
    if no_aparecieron:
        raise ContratoRoto(
            f"{etapa.etiqueta} termino sin error pero no produjo:\n  - "
            + "\n  - ".join(no_aparecieron)
        )

    return {
        "etapa": etapa.etiqueta,
        "que_hace": etapa.que_hace,
        "segundos": round(demoro, 2),
        "salidas": {
            s: {"sha256": hash_de(BASE_DIR / s), "forma": forma_de(BASE_DIR / s)}
            for s in etapa.salidas
        },
    }


def leer_manifiesto() -> dict:
    if not MANIFIESTO.exists():
        return {}
    return json.loads(MANIFIESTO.read_text(encoding="utf-8"))


def escribir_manifiesto(registros: list[dict]) -> None:
    """Guarda el estado de la ultima corrida completa.

    Sin `generado` ni ningun otro timestamp adentro, a proposito: si el
    manifiesto llevara la hora, dos corridas identicas darian archivos
    distintos y el propio manifiesto dejaria de servir para comparar.
    """
    MANIFIESTO.write_text(
        json.dumps({"etapas": registros}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def comparar_con_manifiesto(registros: list[dict]) -> list[str]:
    """Devuelve las diferencias contra el manifiesto guardado. Vacio = igual."""
    previo = {r["etapa"]: r for r in leer_manifiesto().get("etapas", [])}
    diferencias = []
    for r in registros:
        anterior = previo.get(r["etapa"])
        if anterior is None:
            diferencias.append(f"{r['etapa']}: etapa nueva, no estaba en el manifiesto")
            continue
        for archivo, dato in r["salidas"].items():
            viejo = anterior["salidas"].get(archivo)
            if viejo is None:
                diferencias.append(f"{r['etapa']}: salida nueva {archivo}")
            elif viejo["sha256"] != dato["sha256"]:
                diferencias.append(
                    f"{r['etapa']}: {archivo} cambio "
                    f"({viejo['forma']} -> {dato['forma']})"
                )
    return diferencias
