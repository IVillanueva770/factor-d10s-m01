"""
Prueba de cruce entre el dataset maestro del TP1 (Aprender 2024 + EPH) y las bases
"BD Escuelas" del repo de referencia de Agustin Sanchez Varela
(github.com/agus476/radar-trayectorias-educativas-argentinas).

Por que existe: el TP1 dejo tres paredes abiertas, y la mas cara era que el proyecto
NO tiene una variable de abandono: el proxy que se armo desde la EPH correlaciona +0,16
con el desempenio, o sea que no mide nada. La tabla Trayectoria_Sexo_Final del repo de
referencia trae los flujos oficiales por grado (inicial, promovidos, no promovidos,
salidos con pase, salidos sin pase, egresados) en el MISMO grano geografico que Aprender.

Este script mide, sin suponer, si el cruce efectivamente pega.

Uso:  python src/07_probar_cruce_radar.py <ruta a Trayectoria_Sexo_Final.csv>
"""
import csv
import io
import sys
import collections

MAESTRO = "data/processed/dataset_maestro_inicial.csv"
SECUNDARIA = ["8", "9", "10", "11", "12"]


def normalizar_provincia(p):
    """Las dos fuentes nombran distinto a dos jurisdicciones y a nada mas.
    Aprender dice 'Ciudad Autonoma de Buenos Aires' y 'Tierra del Fuego, Antartida e
    Islas del Atlantico Sur'; el repo de referencia dice 'Ciudad de Buenos Aires' y
    'Tierra del Fuego'. Todo el resto matchea literal."""
    p = p.strip().upper()
    if "BUENOS AIRES" in p and ("CIUDAD" in p or "AUT" in p):
        return "CABA"
    if p.startswith("TIERRA DEL FUEGO"):
        return "TIERRA DEL FUEGO"
    return p


def clave(provincia, departamento, sector, ambito):
    return (
        normalizar_provincia(provincia),
        departamento.strip().upper(),
        sector.strip().upper(),
        ambito.strip().upper(),
    )


def numero(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def main(ruta_trayectoria):
    trayectoria = list(csv.DictReader(io.open(ruta_trayectoria, encoding="utf-8-sig")))
    maestro = list(csv.DictReader(io.open(MAESTRO, encoding="utf-8")))

    claves_aprender = set(
        clave(x["jurisdiccion"], x["departamento"], x["sector"], x["ambito"])
        for x in maestro
    )

    print(f"Dataset maestro TP1: {len(maestro)} filas, {len(claves_aprender)} claves unicas")
    print()

    # 1. Tasa de match por anio
    print("MATCH por anio (sobre las claves de Aprender):")
    for anio in sorted(set(x["anio"] for x in trayectoria)):
        kt = set(
            clave(x["provincia"], x["departamento"], x["sector"], x["ambito"])
            for x in trayectoria
            if x["anio"] == anio
        )
        pegan = claves_aprender & kt
        print(f"  {anio}: {len(pegan):>5} de {len(claves_aprender)}  ({100 * len(pegan) / len(claves_aprender):.1f}%)")
    print()

    # 2. Cobertura longitudinal: cuantas claves tienen la serie entera
    anios_por_clave = collections.Counter()
    for x in trayectoria:
        k = clave(x["provincia"], x["departamento"], x["sector"], x["ambito"])
        if k in claves_aprender:
            anios_por_clave[k] += 1
    total_anios = len(set(x["anio"] for x in trayectoria))
    completas = sum(1 for v in anios_por_clave.values() if v == total_anios)
    print(f"Claves con serie COMPLETA ({total_anios} anios): {completas} de {len(claves_aprender)} "
          f"({100 * completas / len(claves_aprender):.1f}%)")
    print(f"Claves de Aprender sin ninguna fila en el repo de referencia: "
          f"{len(claves_aprender - set(anios_por_clave))}")
    print()

    # 3. El target: existe y tiene datos?
    ultimo = max(x["anio"] for x in trayectoria)
    filas = [x for x in trayectoria if x["anio"] == ultimo]
    inicial = sum(numero(x["inicial_" + g]) for x in filas for g in SECUNDARIA)
    print(f"TARGET disponible, secundaria {ultimo} (anios {SECUNDARIA[0]} a {SECUNDARIA[-1]}), agregado nacional:")
    for etiqueta, col in [
        ("matricula inicial", "inicial"),
        ("promovidos", "promovidos"),
        ("no promovidos", "nopromo"),
        ("salidos SIN pase (abandono)", "ssp"),
        ("salidos con pase (traslado)", "scp"),
    ]:
        v = sum(numero(x[col + "_" + g]) for x in filas for g in SECUNDARIA)
        print(f"  {etiqueta:<30} {v:>12,.0f}   {100 * v / inicial:>6.2f}%")
    con_dato = sum(1 for x in filas if sum(numero(x["ssp_" + g]) for g in SECUNDARIA) > 0)
    print(f"  filas con salidos sin pase > 0: {con_dato} de {len(filas)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Falta la ruta a Trayectoria_Sexo_Final.csv")
    main(sys.argv[1])
