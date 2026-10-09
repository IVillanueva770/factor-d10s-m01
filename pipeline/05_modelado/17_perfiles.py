"""Etapa 17: perfiles de los grupos que el modelo da como "no alto".

Es la segunda etapa que propuso la mentora (23/09): despues del supervisado,
un analisis no supervisado sobre el grupo que el modelo clasifica como "no
abandona", como valor agregado. La pregunta que contesta: entre los grupos
que el modelo no marca, ¿hay perfiles distintos, y alguno esconde abandono
que el modelo no ve?

Se agrupa con k-means sobre pocas variables legibles (estandarizadas), con la
cantidad de grupos elegida por silueta entre 3 y 5, y semilla fija. Cada
perfil se describe con sus medias y con su tasa real de abandono, que no se
uso para agrupar.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modelado import CUANTIL_ALTO, SEMILLA  # noqa: E402

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"

VARIABLES = {
    "nse_bajo": "nse__q1",
    "madre_hasta_primaria": ["educ_madre__primaria_incompleto",
                             "educ_madre__primaria_completo"],
    "repitio": ["repitencia__repitio_1_vez", "repitencia__repitio_2_veces_o_mas"],
    "mate_debajo_basico": "desemp_matematica__por_debajo_del_nivel_basico",
    "estatal": "sector_estatal",
    "rural": "ambito_rural",
}


def main():
    datos = pd.read_csv(PROC / "dataset_modelado.csv", low_memory=False)
    pred = pd.read_csv(PROC / "predicciones_principal.csv")
    K = ["k_prov", "k_depto", "k_sector", "k_ambito"]
    tabla = datos.merge(pred[K + ["p_logistica"]], on=K, validate="one_to_one")
    corte = tabla["p_logistica"].quantile(CUANTIL_ALTO)
    no_alto = tabla[tabla["p_logistica"] < corte].reset_index(drop=True).copy()

    X = pd.DataFrame(index=no_alto.index)
    for nombre, col in VARIABLES.items():
        faltan = [c for c in ([col] if isinstance(col, str) else col)
                  if c not in no_alto.columns]
        if faltan:
            raise SystemExit(f"{nombre}: faltan columnas {faltan}")
        X[nombre] = (no_alto[col] if isinstance(col, str)
                     else no_alto[col].sum(axis=1))
    X = X.fillna(X.median())
    Z = StandardScaler().fit_transform(X)

    print("=" * 74)
    print(f"PERFILES entre los {len(no_alto)} grupos que el modelo no marca "
          f"como alto (de {len(tabla)})")
    print("=" * 74)
    siluetas = {}
    for k in (3, 4, 5):
        etiquetas = KMeans(k, n_init=20, random_state=SEMILLA).fit_predict(Z)
        siluetas[k] = silhouette_score(Z, etiquetas)
        print(f"  k={k}: silueta {siluetas[k]:.3f}")
    k = max(siluetas, key=siluetas.get)
    no_alto["perfil"] = KMeans(k, n_init=20, random_state=SEMILLA).fit_predict(Z)

    resumen = X.assign(perfil=no_alto["perfil"]).groupby("perfil").mean()
    resumen["grupos"] = no_alto.groupby("perfil").size()
    resumen["estudiantes"] = no_alto.groupby("perfil")["estudiantes"].sum()
    resumen["tasa_real_ponderada"] = no_alto.groupby("perfil").apply(
        lambda d: d["ssp_ultimos2"].sum() / d["inicial_ultimos2"].sum(),
        include_groups=False)
    resumen["altos_no_vistos"] = no_alto.groupby("perfil")[
        "alto_ultimos2_nacional"].sum().astype(int)
    print(f"\n  elegido k={k} (mayor silueta)\n")
    print(resumen.round(3).to_string())
    resumen.to_csv(PROC / "perfiles_no_alto.csv", float_format="%.6g")
    pd.DataFrame([{"k": kk, "silueta": s} for kk, s in siluetas.items()]).to_csv(
        PROC / "perfiles_silueta.csv", index=False, float_format="%.6g")


if __name__ == "__main__":
    main()
