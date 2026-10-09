"""Etapa 14: el dataset de modelado.

Une el dataset curado del TP2 (Aprender 2024 + EPH, 1 fila = grupo
territorial) con el target y el edificio del Relevamiento. Es un join uno a
uno por la clave territorial, e imprime su denominador (DECISIONES-TP3, D3):
filas y estudiantes que encontraron par, y la lista de los que no.

Agrega las variables de contexto (sector, ambito, tamanio) y los targets
binarios de "abandono alto" para cada definicion de anios y cada tipo de corte.
No borra filas: las que no tienen target (sin matricula en esos anios) quedan
con el target vacio y cada experimento las excluye diciendo cuantas son.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modelado import ANIOS_TARGET, CUANTIL_ALTO  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
_rel = __import__("importlib").import_module  # noqa: E731

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM = BASE_DIR / "data" / "interim"
PROC = BASE_DIR / "data" / "processed"

K = ["k_prov", "k_depto", "k_sector", "k_ambito"]


def _normalizar():
    """Reusa la normalizacion de la etapa 13 (una sola regla para la clave)."""
    import importlib.util
    ruta = Path(__file__).resolve().parent / "13_relevamiento.py"
    spec = importlib.util.spec_from_file_location("rel13", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.agregar_claves


def main():
    agregar_claves = _normalizar()
    curado = pd.read_csv(PROC / "dataset_maestro_curado.csv")
    rel = pd.read_csv(INTERIM / "relevamiento_target.csv")
    curado = agregar_claves(curado, "jurisdiccion")

    if curado[K].duplicated().any():
        raise SystemExit("La clave normalizada no es unica en el dataset curado")

    datos = curado.merge(rel, on=K, how="left", validate="one_to_one",
                         indicator=True)
    pegaron = datos["_merge"] == "both"
    est = datos["estudiantes"]
    print("=" * 74)
    print("1. CRUCE CON EL RELEVAMIENTO (denominador, D3)")
    print("=" * 74)
    print(f"  filas que encontraron par: {pegaron.sum()} de {len(datos)} "
          f"({100 * pegaron.mean():.1f}%)")
    print(f"  estudiantes representados: {est[pegaron].sum():,.1f} de "
          f"{est.sum():,.1f} ({100 * est[pegaron].sum() / est.sum():.1f}%)")
    if (~pegaron).any():
        print("  sin par:")
        for _, f in datos[~pegaron].iterrows():
            print(f"    {f['jurisdiccion']} | {f['departamento']} | "
                  f"{f['sector']} | {f['ambito']} | {f['estudiantes']:.0f}")
    if est[pegaron].sum() / est.sum() < 0.95:
        raise SystemExit("El cruce no llega al 95% de los estudiantes (D3)")
    datos = datos.drop(columns=["_merge"])

    # Contexto del grupo
    datos["sector_estatal"] = (datos["k_sector"] == "estatal").astype(int)
    datos["ambito_rural"] = (datos["k_ambito"] == "rural").astype(int)
    datos["log_estudiantes"] = np.log10(datos["estudiantes"])
    print()
    print(f"  sector: {datos['k_sector'].value_counts().to_dict()}")
    print(f"  ambito: {datos['k_ambito'].value_counts().to_dict()}")

    # Targets binarios: "abandono alto" = cuarto superior de la tasa
    print()
    print("=" * 74)
    print("2. TARGETS: 'abandono alto' = tasa en el cuarto superior")
    print("=" * 74)
    for nombre in ANIOS_TARGET:
        tasa = datos[f"tasa_{nombre}"]
        corte = tasa.quantile(CUANTIL_ALTO)
        datos[f"alto_{nombre}_nacional"] = np.where(
            tasa.notna(), (tasa >= corte).astype(float), np.nan)
        cortes_prov = datos.groupby("k_prov")[f"tasa_{nombre}"].transform(
            lambda s: s.quantile(CUANTIL_ALTO))
        datos[f"alto_{nombre}_provincial"] = np.where(
            tasa.notna() & (cortes_prov > 0),
            (tasa >= cortes_prov).astype(float), np.nan)
        for tipo in ("nacional", "provincial"):
            y = datos[f"alto_{nombre}_{tipo}"]
            print(f"  {nombre:<11} {tipo:<11} positivos {int(y.sum())} de "
                  f"{int(y.notna().sum())} con target "
                  f"(sin target: {int(y.isna().sum())})"
                  + (f"  | corte nacional = tasa >= {100 * corte:.2f}%"
                     if tipo == "nacional" else ""))

    PROC.mkdir(parents=True, exist_ok=True)
    datos.to_csv(PROC / "dataset_modelado.csv", index=False,
                 float_format="%.10g")
    print()
    print(f"  -> dataset_modelado.csv: {len(datos):,} x {datos.shape[1]}")


if __name__ == "__main__":
    main()
