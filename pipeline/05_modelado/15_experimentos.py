"""Etapa 15: corre todos los experimentos de modelado.EXPERIMENTOS.

Cada experimento es una combinacion (que anios mide el target, corte nacional
o por provincia, que bloques de variables entran). Para cada uno se evaluan,
con la MISMA particion y las mismas metricas:

  baselines (reglas simples, la referencia que pide la consigna)
    prevalencia        todos con la misma probabilidad: no sabe nada
    sector_ambito      la tasa de "alto" de su celda sector x ambito
    provincia          la tasa de "alto" de su provincia ("donde estas")
  modelos
    logistica          regresion logistica: lineal e interpretable
    boosting           gradient boosting de arboles: capta no linealidades

Separacion entrenamiento/evaluacion: validacion cruzada estratificada de 5
partes con semilla fija; cada grupo se predice con un modelo que no lo vio.
Toda transformacion (imputar, escalar) se ajusta dentro de cada parte, sobre
el entrenamiento solo, para no filtrar informacion de evaluacion.

Ademas, para el experimento principal se repite todo separando POR PROVINCIA
(ninguna provincia esta a la vez en entrenamiento y en evaluacion). Ahi la
regla "provincia" no puede funcionar, y se ve cuanto de lo que aprende el
modelo depende de conocer la provincia.

Metricas: ROC-AUC y PR-AUC (no dependen de un umbral) y, marcando como "alto"
al cuarto de grupos con mayor probabilidad, precision, recall, F1 y la matriz
de confusion. Nunca accuracy sola: con 25% de positivos, decir "nadie es alto"
ya da 75%.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, f1_score,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modelado import (  # noqa: E402
    CONTEXTO, CUANTIL_ALTO, EDIFICIO, EPH, EXPERIMENTOS, FOLDS,
    PREFIJOS_EXCLUIDOS_APRENDER, PROHIBIDOS, SEMILLA,
)

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"


def columnas_aprender(datos):
    return [c for c in datos.columns
            if "__" in c
            and not c.startswith(PREFIJOS_EXCLUIDOS_APRENDER)
            and "_arm__" not in c]  # la version armonizada duplica la original


def columnas_de(bloques, datos):
    mapa = {
        "aprender": columnas_aprender(datos),
        "contexto": CONTEXTO,
        "edificio": list(EDIFICIO),
        "eph": EPH,
    }
    cols = [c for b in bloques for c in mapa[b]]
    prohibidas = [c for c in cols if any(p in c for p in PROHIBIDOS)]
    if prohibidas:
        raise SystemExit(f"Variables prohibidas como predictor: {prohibidas}")
    return cols


def modelos():
    return {
        "logistica": make_pipeline(
            SimpleImputer(strategy="median"), StandardScaler(),
            LogisticRegression(C=0.3, max_iter=5000)),
        "boosting": HistGradientBoostingClassifier(
            max_depth=3, learning_rate=0.05, max_iter=200,
            random_state=SEMILLA),
    }


def regla(tabla_train, y_train, tabla_test, por):
    """Probabilidad = tasa de 'alto' de la celda en entrenamiento."""
    tasa = y_train.groupby(tabla_train[por].astype(str).agg("|".join, axis=1)
                           if isinstance(por, list) else tabla_train[por]).mean()
    clave_test = (tabla_test[por].astype(str).agg("|".join, axis=1)
                  if isinstance(por, list) else tabla_test[por])
    return clave_test.map(tasa).fillna(y_train.mean()).to_numpy()


def metricas(y, p):
    if len(set(p)) == 1:  # regla constante: no ordena, marca a todos igual
        pred = np.zeros(len(p), dtype=int)
    else:
        corte = np.quantile(p, CUANTIL_ALTO)
        pred = (p >= corte).astype(int)
    vp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    vn = int(((pred == 0) & (y == 0)).sum())
    return {
        "roc_auc": roc_auc_score(y, p) if len(set(p)) > 1 else 0.5,
        "pr_auc": average_precision_score(y, p),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "vp": vp, "fp": fp, "fn": fn, "vn": vn,
    }


def evaluar(datos, exp, separacion):
    y_col = f"alto_{exp['anios']}_{exp['corte']}"
    tabla = datos[datos[y_col].notna()].reset_index(drop=True)
    y = tabla[y_col].astype(int)
    X = tabla[columnas_de(exp["bloques"], tabla)]

    if separacion == "estratificada":
        partes = StratifiedKFold(FOLDS, shuffle=True, random_state=SEMILLA).split(X, y)
    else:
        partes = GroupKFold(n_splits=6).split(X, y, groups=tabla["k_prov"])

    nombres = ["prevalencia", "sector_ambito", "provincia", *modelos()]
    oof = {n: np.zeros(len(tabla)) for n in nombres}
    por_parte = {n: [] for n in nombres}
    for train, test in partes:
        tr, te = tabla.iloc[train], tabla.iloc[test]
        oof["prevalencia"][test] = y.iloc[train].mean()
        oof["sector_ambito"][test] = regla(tr, y.iloc[train], te, ["k_sector", "k_ambito"])
        oof["provincia"][test] = regla(tr, y.iloc[train], te, "k_prov")
        for nombre, modelo in modelos().items():
            modelo.fit(X.iloc[train], y.iloc[train])
            oof[nombre][test] = modelo.predict_proba(X.iloc[test])[:, 1]
        for nombre in nombres:
            por_parte[nombre].append(
                metricas(y.iloc[test].to_numpy(), oof[nombre][test]))

    # Las metricas se calculan DENTRO de cada parte y se promedian. Juntar
    # las predicciones de todas las partes y medir una sola vez inventa un
    # orden falso entre reglas constantes (cada parte tiene su propia
    # constante), y la AUC de "no sabe nada" deja de dar 0,5.
    filas = []
    for nombre in nombres:
        fila = {"experimento": exp["id"], "separacion": separacion,
                "modelo": nombre, "n": len(tabla), "positivos": int(y.sum()),
                "variables": X.shape[1]}
        partes_m = pd.DataFrame(por_parte[nombre])
        for m in ("roc_auc", "pr_auc", "precision", "recall", "f1"):
            fila[m] = partes_m[m].mean()
            fila[m + "_desvio"] = partes_m[m].std()
        for m in ("vp", "fp", "fn", "vn"):
            fila[m] = int(partes_m[m].sum())
        filas.append(fila)
    predicciones = tabla[["k_prov", "k_depto", "k_sector", "k_ambito",
                          "jurisdiccion", "departamento", "sector", "ambito",
                          "estudiantes", f"tasa_{exp['anios']}", y_col]].copy()
    for nombre in nombres:
        predicciones[f"p_{nombre}"] = oof[nombre]
    return filas, predicciones


def main():
    datos = pd.read_csv(PROC / "dataset_modelado.csv", low_memory=False)
    resultados = []
    principal = None
    for exp in EXPERIMENTOS:
        separaciones = ["estratificada"]
        if exp["id"] == "principal":
            separaciones.append("por_provincia")
        for sep in separaciones:
            filas, pred = evaluar(datos, exp, sep)
            resultados.extend(filas)
            if exp["id"] == "principal" and sep == "estratificada":
                principal = pred

    res = pd.DataFrame(resultados)
    pd.set_option("display.width", 160)
    print(res[["experimento", "separacion", "modelo", "n", "positivos",
               "variables", "roc_auc", "pr_auc", "precision", "recall"]]
          .round(3).to_string(index=False))
    res.to_csv(PROC / "resultados_experimentos.csv", index=False,
               float_format="%.6g")
    principal.to_csv(PROC / "predicciones_principal.csv", index=False,
                     float_format="%.6g")


if __name__ == "__main__":
    main()
