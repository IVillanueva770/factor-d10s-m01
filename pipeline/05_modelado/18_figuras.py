"""Etapa 18: las figuras del TP3.

Tres graficos, uno por hallazgo del modelado. Igual que en el TP2, cada uno
responde una pregunta del informe y el titulo dice la respuesta.

  A. ¿El modelo sirve para algo que una regla simple no haga?
     ROC-AUC de los cinco modelos del experimento principal, en las dos
     separaciones. Le gana por poco a "saber la provincia", pero cuando la
     provincia no esta en el entrenamiento la regla de provincia cae al azar
     y el modelo sigue encontrando senial.
  B. ¿Por que la provincia pesa tanto?
     La tasa de salidas sin pase de cada jurisdiccion. La distancia entre la
     mas baja y la mas alta es enorme, y una parte puede ser como registra
     cada una, no solo cuantos chicos se van.
  C. ¿Quienes son los grupos que el modelo no marca como alto?
     Los cuatro perfiles del k-means, con sus seis rasgos y su tasa real.

Estilo heredado de `04_analisis/11_figuras.py` sin cambios: la misma paleta
validada para daltonismo, marcas finas, grilla recesiva, etiquetas directas y
texto siempre en tinta. Todo numero que aparece en un titulo sale del CSV, no
se escribe a mano.

Determinismo: los PNG se guardan sin el metadato "Software" (que lleva la
version de matplotlib) para que dos corridas den los mismos bytes.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"
FIGURAS = BASE_DIR / "figuras"

# Paleta del TP1. Orden fijo: nunca se cicla ni se reasigna.
AZUL, NARANJA, VERDE, AMARILLO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
TINTA = "#0b0b0b"
TINTA_SUAVE = "#52514e"
GRIS_GRILLA = "#e3e3e0"
FONDO = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": FONDO,
    "axes.facecolor": FONDO,
    "axes.edgecolor": GRIS_GRILLA,
    "axes.labelcolor": TINTA_SUAVE,
    "text.color": TINTA,
    "xtick.color": TINTA_SUAVE,
    "ytick.color": TINTA_SUAVE,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "grid.color": GRIS_GRILLA,
    "grid.linewidth": 0.8,
})

DPI = 200
# Sin "Software": es lo unico del PNG que cambiaria con la version instalada.
METADATA = {"Software": None}


def coma(x, decimales=2):
    """Numero con coma decimal, como se escribe en el informe."""
    return f"{x:.{decimales}f}".replace(".", ",")


def pct(x, decimales=1):
    return coma(100 * x, decimales) + "%"


def titulo(ax, texto, bajada=None):
    """Titulo y bajada como anotaciones, igual que en 11_figuras.py.

    Van en el mismo sistema de coordenadas para que las alturas se controlen
    juntas y no se pisen.
    """
    n_lineas_bajada = bajada.count("\n") + 1 if bajada else 0
    alto_bajada = 0.035 * n_lineas_bajada
    ax.annotate(texto, xy=(0, 1.035 + alto_bajada), xycoords="axes fraction",
                fontsize=12.5, color=TINTA, va="bottom", ha="left")
    if bajada:
        ax.annotate(bajada, xy=(0, 1.02), xycoords="axes fraction",
                    fontsize=9.5, color=TINTA_SUAVE, va="bottom", ha="left")


def guardar(fig, nombre):
    fig.savefig(FIGURAS / nombre, dpi=DPI, bbox_inches="tight",
                metadata=METADATA)
    plt.close(fig)
    return nombre


# --------------------------------------------------------------- FIGURA A
# Orden de abajo hacia arriba en el grafico: el azar abajo, los modelos arriba.
MODELOS = [
    ("prevalencia", "Nadie sabe nada (azar)", TINTA_SUAVE),
    ("sector_ambito", "Regla: sector y ámbito", NARANJA),
    ("provincia", "Regla: la provincia", NARANJA),
    ("logistica", "Modelo: regresión logística", AZUL),
    ("boosting", "Modelo: árboles combinados", AZUL),
    ("juntos", "Modelo: provincia y perfil juntos", AZUL),
]
SEPARACIONES = [
    ("estratificada", "Con todas las provincias en el entrenamiento",
     "separación estratificada: cada provincia aparece en el\n"
     "entrenamiento y en la prueba"),
    ("por_provincia", "Probando en provincias que nunca vio",
     "separación por provincia: la regla de la provincia\n"
     "no tiene nada que decir y cae al azar"),
]


def figura_a_modelo_vs_reglas(r):
    """ROC-AUC de modelos y reglas, en las dos separaciones.

    La ultima barra es el experimento provincia_y_perfil (logistica con la
    provincia como variable). Solo existe con la separacion estratificada: en
    provincias que el modelo nunca vio, la provincia no tiene valor que aportar.
    """
    juntos = r[(r["experimento"] == "provincia_y_perfil")
               & (r["modelo"] == "logistica")].copy()
    juntos["modelo"] = "juntos"
    r = pd.concat([r[r["experimento"] == "principal"], juntos]).set_index(
        ["separacion", "modelo"])
    est_juntos = r.loc[("estratificada", "juntos"), "roc_auc"]

    est_log = r.loc[("estratificada", "logistica"), "roc_auc"]
    est_prov = r.loc[("estratificada", "provincia"), "roc_auc"]
    pp_log = r.loc[("por_provincia", "logistica"), "roc_auc"]
    pp_sa = r.loc[("por_provincia", "sector_ambito"), "roc_auc"]

    fig, ejes = plt.subplots(1, 2, figsize=(14, 6.6), sharey=True)
    for ax, (sep, encabezado, bajada) in zip(ejes, SEPARACIONES):
        valores = [r.loc[(sep, m), "roc_auc"] if (sep, m) in r.index else 0
                   for m, _, _ in MODELOS]
        desvios = [r.loc[(sep, m), "roc_auc_desvio"] if (sep, m) in r.index else 0
                   for m, _, _ in MODELOS]
        nombres = [n for _, n, _ in MODELOS]
        colores = [c for _, _, c in MODELOS]
        y = np.arange(len(MODELOS))

        ax.barh(y, valores, color=colores, height=0.58, zorder=3)
        # El desvio entre particiones, como linea fina: dice cuanto de la
        # diferencia entre barras vecinas es ruido.
        ax.errorbar(valores, y, xerr=desvios, fmt="none", ecolor=TINTA,
                    elinewidth=1, capsize=3, capthick=1, zorder=4)
        for yi, (v, s) in enumerate(zip(valores, desvios)):
            if v == 0:
                ax.annotate("no aplica: no conoce esa provincia", xy=(0, yi),
                            xytext=(7, 0), textcoords="offset points",
                            va="center", fontsize=9.5, color=TINTA_SUAVE)
                continue
            ax.annotate(coma(v), xy=(v + s, yi), xytext=(7, 0),
                        textcoords="offset points", va="center",
                        fontsize=10, color=TINTA)

        ax.axvline(0.5, color=TINTA_SUAVE, lw=1, ls="--", zorder=5)
        ax.annotate("azar", xy=(0.5, len(MODELOS) - 0.45), xytext=(4, 0),
                    textcoords="offset points", ha="left", va="center",
                    fontsize=9, color=TINTA_SUAVE)

        ax.set_yticks(y)
        ax.set_yticklabels(nombres, fontsize=10)
        ax.set_xlim(0, 0.92)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: coma(v, 1)))
        ax.set_ylim(-0.6, len(MODELOS) - 0.25)
        ax.set_xlabel("qué tan bien ordena el riesgo (0,5 = sorteo, 1 = perfecto)")
        ax.grid(axis="x", zorder=0)
        ax.set_axisbelow(True)
        titulo(ax, encabezado, bajada)

    fig.suptitle(
        f"El perfil y la provincia, cada uno solo, ordenan casi igual ({coma(est_log)} y "
        f"{coma(est_prov)}); juntos llegan a {coma(est_juntos)}. Sin conocer la "
        f"provincia, el perfil sigue encontrando señal ({coma(pp_log)} contra {coma(pp_sa)})",
        x=0.01, ha="left", y=1.015, fontsize=13.5, color=TINTA)
    fig.text(0.01, 0.965,
             "experimento principal · la línea fina es el desvío entre "
             "particiones · naranja = regla simple, azul = modelo",
             ha="left", fontsize=9.5, color=TINTA_SUAVE)
    fig.tight_layout(w_pad=3)
    return guardar(fig, "tp3_a_modelo_vs_reglas.png")


# --------------------------------------------------------------- FIGURA B
NOMBRES_CORTOS = {
    "Ciudad Autónoma de Buenos Aires": "CABA",
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur": "Tierra del Fuego",
}


def figura_b_tasa_por_provincia(d):
    """Tasa ponderada de salidas sin pase por jurisdiccion."""
    g = (d.groupby("jurisdiccion")[["ssp_ultimos2", "inicial_ultimos2"]]
         .sum())
    g["tasa"] = g["ssp_ultimos2"] / g["inicial_ultimos2"]
    # Desempate por nombre para que el orden no dependa de la version de pandas.
    g = g.reset_index().sort_values(["tasa", "jurisdiccion"])
    nacional = d["ssp_ultimos2"].sum() / d["inicial_ultimos2"].sum()
    minimo, maximo = g.iloc[0], g.iloc[-1]
    veces = maximo["tasa"] / minimo["tasa"]

    nombres = [NOMBRES_CORTOS.get(j, j) for j in g["jurisdiccion"]]
    colores = [NARANJA if t > nacional else AZUL for t in g["tasa"]]

    fig, ax = plt.subplots(figsize=(10, 7.8))
    y = np.arange(len(g))
    ax.barh(y, g["tasa"], color=colores, height=0.68, zorder=3)
    for yi, t in enumerate(g["tasa"]):
        # Fondo del color del grafico: la linea de la media pasa por debajo
        # del numero en vez de tacharlo.
        ax.annotate(pct(t, 2), xy=(t, yi), xytext=(5, 0),
                    textcoords="offset points", va="center",
                    fontsize=10.5, color=TINTA, zorder=6,
                    bbox=dict(boxstyle="square,pad=0.1", fc=FONDO, ec="none"))
    ax.axvline(nacional, color=TINTA_SUAVE, lw=1.2, ls="--", zorder=4)
    ax.annotate(f"media nacional {pct(nacional, 2)}",
                xy=(nacional, len(g) + 0.15), xytext=(6, 0),
                textcoords="offset points", ha="left", va="center",
                fontsize=10.5, color=TINTA_SUAVE)

    ax.set_yticks(y)
    ax.set_yticklabels(nombres, fontsize=11)
    ax.set_ylim(-0.7, len(g) + 0.6)
    ax.set_xlim(0, maximo["tasa"] * 1.13)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: pct(v, 1)))
    ax.set_xlabel("estudiantes que dejaron la escuela sin pasar a otra, sobre los "
                  "inscriptos (dos últimos años de la secundaria)", fontsize=10.5)
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)
    titulo(ax,
           f"De {pct(minimo['tasa'], 1)} en "
           f"{NOMBRES_CORTOS.get(minimo['jurisdiccion'], minimo['jurisdiccion'])}"
           f" a {pct(maximo['tasa'], 1)} en "
           f"{NOMBRES_CORTOS.get(maximo['jurisdiccion'], maximo['jurisdiccion'])}"
           f": la tasa se multiplica por {veces:.0f} entre provincias",
           "parte de esa distancia puede ser cómo registra cada provincia las "
           "salidas sin pase, y no solo cuántos estudiantes se van\n"
           "azul = por debajo de la media nacional, naranja = por encima")

    fig.tight_layout()
    return guardar(fig, "tp3_b_tasa_por_provincia.png")


# --------------------------------------------------------------- FIGURA C
RASGOS = [
    ("nse_bajo", "NSE bajo"),
    ("madre_hasta_primaria", "madre hasta\nprimaria"),
    ("repitio", "repitió"),
    ("mate_debajo_basico", "matemática debajo\ndel básico"),
    ("estatal", "estatal"),
    ("rural", "rural"),
]


def nombrar_perfiles(p):
    """Nombre corto de cada perfil, derivado de sus rasgos y no escrito a mano.

    Sector y ambito salen de la mayoria (estatal y rural por encima de 0,5).
    Si dos perfiles quedan con el mismo nombre, el de mas NSE bajo se llama
    "mas vulnerable" y el otro conserva el nombre base.
    """
    base = {}
    for perfil, f in p.iterrows():
        sector = "Estatal" if f["estatal"] > 0.5 else "Privado"
        ambito = "rural" if f["rural"] > 0.5 else "urbano"
        base[perfil] = (f"Rural {sector.lower()}" if ambito == "rural"
                        else f"{sector} {ambito}")
    nombres = dict(base)
    for nombre in set(base.values()):
        iguales = [k for k, v in base.items() if v == nombre]
        if len(iguales) > 1:
            mas_bajo = max(iguales, key=lambda k: p.loc[k, "nse_bajo"])
            ambito = "Rural" if p.loc[mas_bajo, "rural"] > 0.5 else "Urbano"
            nombres[mas_bajo] = f"{ambito} más vulnerable"
    return nombres


def figura_c_perfiles(p):
    """Heatmap de los seis rasgos + la tasa real de cada perfil al costado."""
    p = p.set_index("perfil")
    nombres = nombrar_perfiles(p)
    # Orden por tasa real, la mas alta arriba.
    p = p.sort_values("tasa_real_ponderada", ascending=True)
    etiquetas = [f"{nombres[k]}\n{int(f['grupos'])} grupos · "
                 f"{f['estudiantes']:,.0f} est.".replace(",", ".")
                 for k, f in p.iterrows()]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14, 6.4), gridspec_kw={"width_ratios": [2.3, 1]},
        sharey=True)

    # Escala de un solo tono, del fondo al azul de la paleta. Llega al azul
    # pleno y no mas oscuro, asi el numero en tinta se lee en todas las celdas.
    escala = LinearSegmentedColormap.from_list("fondo_azul", [FONDO, AZUL])
    matriz = p[[c for c, _ in RASGOS]].to_numpy()
    ax1.imshow(matriz, cmap=escala, vmin=0, vmax=1, aspect="auto",
               origin="lower")
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            ax1.annotate(coma(matriz[i, j], 2), xy=(j, i), ha="center",
                         va="center", fontsize=10.5, color=TINTA)
    ax1.set_xticks(range(len(RASGOS)))
    ax1.set_xticklabels([n for _, n in RASGOS], fontsize=9.5)
    ax1.xaxis.tick_top()
    ax1.tick_params(axis="x", length=0, pad=6)
    ax1.set_yticks(range(len(p)))
    ax1.set_yticklabels(etiquetas, fontsize=9.5)
    ax1.tick_params(axis="y", length=0)
    for lado in ax1.spines.values():
        lado.set_visible(False)
    # Lineas blancas entre celdas: separan sin agregar tinta.
    ax1.set_xticks(np.arange(-0.5, len(RASGOS)), minor=True)
    ax1.set_yticks(np.arange(-0.5, len(p)), minor=True)
    ax1.grid(which="minor", color=FONDO, linewidth=3)
    ax1.tick_params(which="minor", length=0)

    ax2.barh(range(len(p)), p["tasa_real_ponderada"], color=NARANJA,
             height=0.55, zorder=3)
    for yi, t in enumerate(p["tasa_real_ponderada"]):
        ax2.annotate(pct(t, 2), xy=(t, yi), xytext=(6, 0),
                     textcoords="offset points", va="center",
                     fontsize=10, color=TINTA)
    ax2.set_xlim(0, p["tasa_real_ponderada"].max() * 1.35)
    ax2.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.005))
    ax2.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
        lambda v, _: pct(v, 1)))
    ax2.set_xlabel("tasa real de salidas sin pase (ponderada)")
    ax2.grid(axis="x", zorder=0)
    ax2.set_axisbelow(True)
    ax2.tick_params(axis="y", length=0)
    ax2.spines["left"].set_visible(False)
    titulo(ax2, "y cuánto abandono tienen de verdad")

    privado = p[p["estatal"] < 0.5]
    resto = p[p["estatal"] >= 0.5]
    fig.suptitle(
        "Lo que el modelo no marca no es todo igual: el "
        f"{nombres[privado.index[0]].lower()} casi no tiene abandono"
        f" ({pct(privado['tasa_real_ponderada'].iloc[0], 2)}"
        f"), los otros tres perfiles están entre "
        f"{pct(resto['tasa_real_ponderada'].min(), 1)} y "
        f"{pct(resto['tasa_real_ponderada'].max(), 1)}",
        x=0.01, ha="left", y=1.03, fontsize=13.5, color=TINTA)
    fig.text(0.01, 0.98,
             "cuatro perfiles (grupos con rasgos parecidos) de los grupos que el modelo no marca "
             "como abandono alto · cada celda es la proporción del rasgo "
             "en el perfil, de 0 a 1",
             ha="left", fontsize=9.5, color=TINTA_SUAVE)
    fig.tight_layout(w_pad=2)
    return guardar(fig, "tp3_c_perfiles.png")


def main():
    resultados = pd.read_csv(PROC / "resultados_experimentos.csv")
    modelado = pd.read_csv(
        PROC / "dataset_modelado.csv",
        usecols=["jurisdiccion", "inicial_ultimos2", "ssp_ultimos2"])
    perfiles = pd.read_csv(PROC / "perfiles_no_alto.csv")
    FIGURAS.mkdir(parents=True, exist_ok=True)

    print("=" * 74)
    print("FIGURAS DEL TP3")
    print("=" * 74)
    print("  Paleta y criterios heredados del TP2, sin colores nuevos.")
    print()
    for fn, datos in ((figura_a_modelo_vs_reglas, resultados),
                      (figura_b_tasa_por_provincia, modelado),
                      (figura_c_perfiles, perfiles)):
        nombre = fn(datos)
        peso = (FIGURAS / nombre).stat().st_size / 1024
        print(f"  GUARDADO: figuras/{nombre}  ({peso:,.0f} KB)")


if __name__ == "__main__":
    main()
