"""Etapa 16: donde se equivoca el modelo principal y que lo mueve.

Sobre las predicciones fuera de muestra del experimento principal (regresion
logistica, validacion estratificada), marcando como "alto" al cuarto de grupos
con mayor probabilidad:

  1. Errores por tamanio del grupo, por sector x ambito y por provincia. Los
     grupos chicos son donde una sola salida mueve la tasa entera.
  2. Que aporta cada bloque de variables: se saca el bloque entero, se vuelve
     a evaluar con la misma particion y se mide cuanto cae la ROC-AUC. Se mide
     por bloque y no por columna porque las proporciones de un mismo bloque
     suman 1 y sus coeficientes sueltos no se pueden leer uno por uno.
  3. El sentido de cada bloque: correlacion (Spearman) entre la categoria
     "de riesgo" de cada bloque y la tasa observada. Es asociacion entre
     grupos, no causa.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modelado import CUANTIL_ALTO, EXPERIMENTOS, FOLDS, SEMILLA  # noqa: E402

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"


def _etapa15():
    import importlib.util
    ruta = Path(__file__).resolve().parent / "15_experimentos.py"
    spec = importlib.util.spec_from_file_location("exp15", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def tabla_errores(pred, por, y_col):
    g = pred.groupby(por, observed=True)
    return pd.DataFrame({
        "grupos": g.size(),
        "altos_reales": g[y_col].sum().astype(int),
        "detectados": g.apply(lambda d: int(((d["marca"] == 1) & (d[y_col] == 1)).sum()),
                              include_groups=False),
        "falsas_alarmas": g.apply(lambda d: int(((d["marca"] == 1) & (d[y_col] == 0)).sum()),
                                  include_groups=False),
        "tasa_real_media": g["tasa"].mean(),
    }).assign(recall=lambda t: t["detectados"] / t["altos_reales"].replace(0, np.nan))


def main():
    e15 = _etapa15()
    exp = next(e for e in EXPERIMENTOS if e["id"] == "principal")
    y_col = f"alto_{exp['anios']}_{exp['corte']}"
    pred = pd.read_csv(PROC / "predicciones_principal.csv")
    pred["tasa"] = pred[f"tasa_{exp['anios']}"]
    corte = pred["p_logistica"].quantile(CUANTIL_ALTO)
    pred["marca"] = (pred["p_logistica"] >= corte).astype(int)

    salidas = []
    print("=" * 74)
    print("1. ERRORES DEL MODELO PRINCIPAL")
    print("=" * 74)
    pred["tamanio"] = pd.qcut(pred["estudiantes"], 5,
                              labels=["Q1 chicos", "Q2", "Q3", "Q4", "Q5 grandes"])
    pred["celda"] = pred["sector"] + " " + pred["ambito"]
    for nombre, por in [("tamanio", "tamanio"), ("sector_ambito", "celda"),
                        ("provincia", "jurisdiccion")]:
        t = tabla_errores(pred, por, y_col)
        print(f"\n  por {nombre}:")
        print(t.round(3).to_string())
        salidas.append(t.reset_index().rename(columns={por: "valor"})
                       .assign(corte=nombre))
    pd.concat(salidas).to_csv(PROC / "errores_principal.csv", index=False,
                              float_format="%.6g")

    print()
    print("=" * 74)
    print("2. QUE APORTA CADA BLOQUE (caida de ROC-AUC al sacarlo)")
    print("=" * 74)
    datos = pd.read_csv(PROC / "dataset_modelado.csv", low_memory=False)
    tabla = datos[datos[y_col].notna()].reset_index(drop=True)
    y = tabla[y_col].astype(int)
    cols = e15.columnas_de(exp["bloques"], tabla)
    bloques = sorted({c.split("__")[0] for c in cols if "__" in c}) + ["contexto"]

    def auc_sin(excluir):
        usar = [c for c in cols
                if not (c.split("__")[0] in excluir
                        or ("contexto" in excluir and "__" not in c))]
        aucs = []
        for tr, te in StratifiedKFold(FOLDS, shuffle=True,
                                      random_state=SEMILLA).split(tabla, y):
            m = e15.modelos()["logistica"]
            m.fit(tabla.loc[tr, usar], y.iloc[tr])
            aucs.append(roc_auc_score(y.iloc[te],
                                      m.predict_proba(tabla.loc[te, usar])[:, 1]))
        return np.mean(aucs)

    base = auc_sin(set())
    filas = [{"bloque": b, "auc_sin_el_bloque": auc_sin({b})} for b in bloques]
    aporte = pd.DataFrame(filas)
    aporte["caida"] = base - aporte["auc_sin_el_bloque"]
    aporte = aporte.sort_values("caida", ascending=False)
    print(f"  AUC con todo: {base:.3f}")
    print(aporte.round(4).to_string(index=False))
    aporte.assign(auc_completo=base).to_csv(PROC / "aporte_bloques.csv",
                                            index=False, float_format="%.6g")

    print()
    print("=" * 74)
    print("3. SENTIDO: correlacion de cada categoria con la tasa (Spearman)")
    print("=" * 74)
    sentido = []
    for c in cols:
        if tabla[c].nunique() > 1:
            sentido.append({"variable": c,
                            "spearman_con_tasa": tabla[c].corr(
                                tabla[f"tasa_{exp['anios']}"], method="spearman")})
    sentido = pd.DataFrame(sentido).sort_values("spearman_con_tasa")
    print(pd.concat([sentido.head(8), sentido.tail(8)]).round(3).to_string(index=False))
    sentido.to_csv(PROC / "sentido_variables.csv", index=False,
                   float_format="%.6g")


if __name__ == "__main__":
    main()
