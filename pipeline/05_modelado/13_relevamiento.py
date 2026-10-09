"""Etapa 13: el target y el edificio, por grupo territorial.

Que hace:
  1. Lee la trayectoria del Relevamiento (archivo 2024) y calcula, por grupo
     jurisdiccion x departamento x sector x ambito, la tasa de salidas sin pase
     sobre la matricula inicial, para dos definiciones de anios
     (modelado.ANIOS_TARGET): los dos ultimos anios de la secundaria
     (principal) y la secundaria entera (control).
  2. Mide la estabilidad: la misma tasa con el archivo del anio anterior, y la
     correlacion entre los dos. Si los grupos que abandonan mucho un anio son
     los mismos al siguiente, el desfase de un anio entre el Relevamiento y
     Aprender no cambia las conclusiones.
  3. Calcula las variables del edificio como proporcion de localizaciones.

Lo que NO ve: un cero de salidas sin pase no se distingue de "no reporto". El
vacio en el CSV solo aparece cuando tampoco hay matricula (sin oferta de esos
anios), asi que un grupo con matricula y cero salidas queda como cero real.
Lo declara como limitacion el notebook.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from comun import clave_provincia  # noqa: E402
from modelado import (  # noqa: E402
    ANIO_ESTABILIDAD, ANIO_RELEVAMIENTO, ANIOS_TARGET, EDIFICIO,
    PROVINCIAS_7_5,
)

BASE_DIR = Path(__file__).resolve().parents[2]
RAW = BASE_DIR / "data" / "raw" / "relevamiento"
INTERIM = BASE_DIR / "data" / "interim"

CLAVES_RA = ["provincia", "departamento", "sector", "ambito"]


def normalizar_provincia(texto):
    """Las dos fuentes nombran distinto a CABA y a Tierra del Fuego; el resto
    coincide sacando tildes y mayusculas (medido: 1.174 de 1.174 en 2024)."""
    p = clave_provincia(texto)
    if "buenos aires" in p and ("ciudad" in p or "aut" in p):
        return "ciudad autonoma de buenos aires"
    if p.startswith("tierra del fuego"):
        return "tierra del fuego"
    return p


def normalizar_texto(texto):
    return clave_provincia(texto)


def agregar_claves(tabla, col_provincia):
    tabla = tabla.copy()
    tabla["k_prov"] = tabla[col_provincia].map(normalizar_provincia)
    tabla["k_depto"] = tabla["departamento"].map(normalizar_texto)
    tabla["k_sector"] = tabla["sector"].map(normalizar_texto)
    tabla["k_ambito"] = tabla["ambito"].map(normalizar_texto)
    return tabla


K = ["k_prov", "k_depto", "k_sector", "k_ambito"]


def tasas(trayectoria, anio):
    filas = trayectoria[trayectoria["anio"] == anio].copy()
    if filas[K].duplicated().any():
        raise SystemExit(f"Claves duplicadas en la trayectoria {anio}")
    salida = filas[K].copy()
    es_7_5 = filas["k_prov"].isin(PROVINCIAS_7_5)
    for nombre, anios_de in ANIOS_TARGET.items():
        ssp = np.zeros(len(filas))
        ini = np.zeros(len(filas))
        for flag in (True, False):
            mascara = (es_7_5 == flag).to_numpy()
            for a in anios_de(flag):
                ssp[mascara] += pd.to_numeric(
                    filas[f"ssp_{a}"], errors="coerce").fillna(0).to_numpy()[mascara]
                ini[mascara] += pd.to_numeric(
                    filas[f"inicial_{a}"], errors="coerce").fillna(0).to_numpy()[mascara]
        salida[f"ssp_{nombre}"] = ssp
        salida[f"inicial_{nombre}"] = ini
        with np.errstate(divide="ignore", invalid="ignore"):
            salida[f"tasa_{nombre}"] = np.where(ini > 0, ssp / ini, np.nan)
    return salida


def main():
    tray = pd.read_csv(RAW / "Trayectoria_Sexo_Final.csv", low_memory=False)
    tray = agregar_claves(tray, "provincia")

    actual = tasas(tray, ANIO_RELEVAMIENTO)
    previo = tasas(tray, ANIO_ESTABILIDAD)

    print("=" * 74)
    print(f"1. TARGET, archivo {ANIO_RELEVAMIENTO} del Relevamiento")
    print("=" * 74)
    for nombre in ANIOS_TARGET:
        t = actual[f"tasa_{nombre}"]
        ssp = actual[f"ssp_{nombre}"].sum()
        ini = actual[f"inicial_{nombre}"].sum()
        validas = t.notna().sum()
        print(f"  {nombre:<11} tasa media ponderada {100 * ssp / ini:5.2f}% "
              f"({ssp:,.0f} / {ini:,.0f})  |  grupos con matricula: "
              f"{validas} de {len(t)}  |  en cero: {(t == 0).sum()} de {validas}")

    print()
    print("=" * 74)
    print(f"2. ESTABILIDAD: archivo {ANIO_ESTABILIDAD} contra {ANIO_RELEVAMIENTO}")
    print("=" * 74)
    par = actual.merge(previo, on=K, suffixes=("", "_prev"))
    estabilidad = {}
    for nombre in ANIOS_TARGET:
        a, b = par[f"tasa_{nombre}"], par[f"tasa_{nombre}_prev"]
        ok = a.notna() & b.notna()
        rho = a[ok].corr(b[ok], method="spearman")
        alto_a = a[ok] >= a[ok].quantile(0.75)
        alto_b = b[ok] >= b[ok].quantile(0.75)
        repite = (alto_a & alto_b).sum() / alto_a.sum()
        estabilidad[nombre] = (rho, repite, ok.sum())
        print(f"  {nombre:<11} Spearman {rho:.2f} sobre {ok.sum()} grupos  |  "
              f"de los 'alto' de {ANIO_RELEVAMIENTO}, {100 * repite:.0f}% ya lo "
              f"era en {ANIO_ESTABILIDAD}")
    actual = actual.merge(
        previo[K + [f"tasa_{n}" for n in ANIOS_TARGET]].rename(
            columns={f"tasa_{n}": f"tasa_{n}_prev" for n in ANIOS_TARGET}),
        on=K, how="left")

    print()
    print("=" * 74)
    print("3. EDIFICIO (todas las localizaciones del grupo, no solo secundaria)")
    print("=" * 74)
    est = pd.read_csv(RAW / "Establecimiento_Caracteristicas_Final.csv",
                      low_memory=False)
    est = agregar_claves(est, "provincia")
    est = est[est["anio"] == ANIO_RELEVAMIENTO]
    loc = pd.to_numeric(est["localizacion"], errors="coerce")
    edif = est[K].copy()
    for nuevo, original in EDIFICIO.items():
        valor = pd.to_numeric(est[original], errors="coerce")
        excede = (valor > loc).sum()
        if excede:
            raise SystemExit(f"{original}: {excede} grupos con mas localizaciones "
                             f"con el atributo que localizaciones. Dato roto.")
        edif[nuevo] = np.where(loc > 0, valor.fillna(0) / loc, np.nan)
        print(f"  {nuevo:<24} mediana {np.nanmedian(edif[nuevo]):.2f}")
    if edif[K].duplicated().any():
        raise SystemExit("Claves duplicadas en Establecimiento")

    salida = actual.merge(edif, on=K, how="left", validate="one_to_one")
    INTERIM.mkdir(parents=True, exist_ok=True)
    salida.sort_values(K).to_csv(INTERIM / "relevamiento_target.csv",
                                 index=False, float_format="%.10g")
    pd.DataFrame(
        [{"anios": n, "spearman": r, "repite_alto": p, "grupos": g}
         for n, (r, p, g) in estabilidad.items()]
    ).to_csv(INTERIM / "relevamiento_estabilidad.csv", index=False,
             float_format="%.6g")
    print()
    print(f"  -> relevamiento_target.csv: {len(salida):,} grupos")


if __name__ == "__main__":
    main()
