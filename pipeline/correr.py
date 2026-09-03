"""Corre el pipeline. Es la unica forma en que se supone que se corre.

    python pipeline/correr.py                 todas las etapas, en orden
    python pipeline/correr.py 4               solo la etapa 4 (o 'integrar')
    python pipeline/correr.py --desde 4       de la 4 en adelante
    python pipeline/correr.py --verificar     corre dos veces y compara
    python pipeline/correr.py --listar        que hace cada etapa, sin correr

`--verificar` es el que importa. Corre el pipeline entero dos veces seguidas y
compara los SHA-256 de las 8 salidas. Si dan iguales, el pipeline es
reproducible: la misma entrada da la misma salida y se puede confiar en que un
cambio en un numero viene de un cambio en el codigo o en los datos, no del azar.
Si dan distintas, alguna etapa metio una fecha, un orden no determinista o un
random sin semilla, y eso hay que arreglarlo antes de sacar conclusiones de
cualquier numero que salga de aca.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from contrato import (  # noqa: E402
    BASE_DIR,
    ContratoRoto,
    comparar_con_manifiesto,
    correr_etapa,
    escribir_manifiesto,
    validar_declaracion,
)
from etapas import ETAPAS, por_nombre  # noqa: E402


def listar():
    print()
    print("PIPELINE  ·  El Factor D10S")
    print("=" * 78)
    for etapa in ETAPAS:
        print()
        print(f"  {etapa.numero:02d}  {etapa.nombre.upper()}")
        print(f"      {etapa.que_hace}")
        for entrada in etapa.entradas:
            print(f"        <- {entrada}")
        for salida in etapa.salidas:
            print(f"        -> {salida}")
    print()


def corrida(etapas, verboso=False, titulo="CORRIENDO EL PIPELINE"):
    print()
    print(titulo)
    print("=" * 78)
    registros = []
    for etapa in etapas:
        print(f"  {etapa.numero:02d} {etapa.nombre:<18}", end="", flush=True)
        registro = correr_etapa(etapa, verboso=verboso)
        formas = " · ".join(
            f"{Path(a).name} {d['forma']}" for a, d in registro["salidas"].items())
        print(f"{registro['segundos']:>7.1f}s   {formas}")
        registros.append(registro)
    return registros


def main(argv):
    validar_declaracion(ETAPAS)

    if "--listar" in argv:
        return listar()

    if "--verificar" in argv:
        print()
        print("VERIFICACION DE REPRODUCIBILIDAD")
        print("Se corre el pipeline entero dos veces y se comparan los hashes.")
        primera = corrida(ETAPAS, titulo="PASADA 1")
        segunda = corrida(ETAPAS, titulo="PASADA 2")

        print()
        print("RESULTADO")
        print("=" * 78)
        distintos = []
        for a, b in zip(primera, segunda):
            for archivo, dato in a["salidas"].items():
                igual = b["salidas"][archivo]["sha256"] == dato["sha256"]
                marca = "identico" if igual else "DISTINTO"
                print(f"  [{marca}]  {archivo}")
                if not igual:
                    distintos.append(archivo)
        print()
        if distintos:
            print(f"  {len(distintos)} salida(s) cambiaron entre dos corridas "
                  f"con la misma entrada.")
            print("  El pipeline NO es reproducible. Revisar esas etapas antes")
            print("  de sacar conclusiones de sus numeros.")
            return 1
        total = sum(len(r["salidas"]) for r in primera)
        print(f"  Las {total} salidas son identicas byte a byte en dos corridas.")
        print("  El pipeline es reproducible.")
        escribir_manifiesto(segunda)
        return 0

    if "--desde" in argv:
        desde = por_nombre(argv[argv.index("--desde") + 1])
        elegidas = [e for e in ETAPAS if e.numero >= desde.numero]
        verboso = False
    else:
        sueltos = [a for a in argv if not a.startswith("-")]
        if sueltos:
            elegidas = [por_nombre(sueltos[0])]
            verboso = True  # una sola etapa: se quiere ver su diagnostico
        else:
            elegidas = ETAPAS
            verboso = False

    registros = corrida(elegidas, verboso=verboso)

    if len(elegidas) == len(ETAPAS):
        diferencias = comparar_con_manifiesto(registros)
        print()
        if not diferencias:
            print("  Sin cambios respecto del manifiesto.")
        else:
            print("  CAMBIOS respecto del manifiesto:")
            for d in diferencias:
                print(f"    - {d}")
            print()
            print("  Si los esperabas, actualiza el manifiesto con:")
            print("    python pipeline/correr.py --verificar")
    print()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except ContratoRoto as e:
        print()
        print("CONTRATO ROTO")
        print("=" * 78)
        print(e)
        print()
        sys.exit(2)
