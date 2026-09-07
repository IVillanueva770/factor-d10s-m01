"""Etapa 11: las figuras del TP2.

Cuatro graficos, uno por hallazgo. Ninguno es decorativo: cada uno responde una
pregunta que el informe hace, y si el grafico no se entiende sin leer el texto,
esta mal hecho.

  A. ¿Que tan sano esta el dataset, y donde no?
     La cobertura por bloque, que es el unico indicador de calidad que viaja
     pegado al dato. Muestra que 15 de 16 bloques estan sanos y que clima
     escolar es la excepcion, y que su problema NO es aleatorio.
  B. ¿La brecha es de gestion o de geografia?
     Las cuatro celdas de sector x ambito, con el tamanio de cada una a la
     vista para que nadie cite la mas chica sin saberlo.
  C. ¿El contexto socioeconomico se relaciona con el rendimiento?
     24 provincias, una por punto. Es el unico que usa las dos fuentes a la
     vez, o sea el que muestra para que sirvio integrarlas.
  D. ¿Que pasa con las inasistencias?
     El hallazgo contraintuitivo, con la comparacion entre medir la cola y
     medir el acumulado, que es lo que lo hizo aparecer.

Estilo heredado del TP1 (`exploracion/16_graficos.py`), sin cambios: paleta
categorica validada para daltonismo (ΔE 9,1 protan), orden fijo que no se
cicla, marcas finas, grilla recesiva, etiquetas directas en vez de leyenda
cuando hay una sola serie, y texto siempre en tinta y nunca del color de la
serie. No se agregan colores nuevos: si hace falta una quinta categoria, se
repiensa el grafico antes que la paleta.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

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

MATE_BAJO = "desemp_matematica__por_debajo_del_nivel_basico"
SOBREEDAD_ALTA = "sobreedad__3_anos_o_mas_de_sobreedad_20_anos_o_mas_30jun"
INGRESO = "eph_ipcf_mediano"


def media_ponderada(t, c, peso="estudiantes"):
    v = t[t[c].notna()]
    return np.average(v[c], weights=v[peso]) if len(v) else np.nan


def titulo(ax, texto, bajada=None):
    """Titulo a la izquierda con bajada opcional. La bajada dice la conclusion.

    Un titulo que nombra la variable ("cobertura por bloque") obliga a leer el
    grafico para saber que pasa. Uno que dice la conclusion ahorra ese paso.

    Los dos van como anotaciones sobre el eje y NO con set_title, porque
    mezclarlos hacia que se superpusieran: set_title reserva su espacio con el
    `pad` pero la anotacion se dibuja encima sin saber que el titulo estaba
    ahi. Poniendo los dos en el mismo sistema de coordenadas, las alturas se
    controlan juntas y no se pisan.
    """
    n_lineas_bajada = bajada.count("\n") + 1 if bajada else 0
    alto_bajada = 0.035 * n_lineas_bajada
    ax.annotate(texto, xy=(0, 1.035 + alto_bajada), xycoords="axes fraction",
                fontsize=12.5, color=TINTA, va="bottom", ha="left")
    if bajada:
        ax.annotate(bajada, xy=(0, 1.02), xycoords="axes fraction",
                    fontsize=9.5, color=TINTA_SUAVE, va="bottom", ha="left")


# --------------------------------------------------------------- FIGURA A
def figura_a_calidad(d):
    """Cobertura por bloque + el detalle de por que clima escolar es distinto."""
    cobs = sorted([c for c in d.columns if c.startswith("cob__")],
                  key=lambda c: d[c].median())
    medianas = [d[c].median() for c in cobs]
    etiquetas = [c.replace("cob__", "").replace("_", " ") for c in cobs]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.5, 6), gridspec_kw={"width_ratios": [1.35, 1]})

    # Izquierda: cobertura mediana por bloque. El unico flojo se pinta naranja.
    # Umbral: por debajo de 0,95 el bloque se pinta naranja. No es magico, es
    # el punto donde una de cada veinte respuestas falta y el numero empieza a
    # depender de quien contesto.
    UMBRAL_SANO = 0.95
    colores = [NARANJA if m < UMBRAL_SANO else AZUL for m in medianas]
    sanos = sum(1 for m in medianas if m >= UMBRAL_SANO)
    ax1.barh(etiquetas, medianas, color=colores, height=0.62, zorder=3)
    ax1.axvline(1.0, color=GRIS_GRILLA, lw=1, zorder=1)
    for y, (m, col) in enumerate(zip(medianas, colores)):
        ax1.annotate(f"{m:.3f}", xy=(m, y), xytext=(6, 0),
                     textcoords="offset points", va="center",
                     fontsize=9, color=TINTA)
    ax1.set_xlim(0, 1.09)
    ax1.set_xlabel("cobertura mediana del bloque")
    ax1.grid(axis="x", zorder=0)
    ax1.set_axisbelow(True)
    # El titulo sale del dato, no escrito a mano: una version anterior decia
    # "15 de 16" mientras la figura mostraba dos barras naranjas.
    titulo(ax1, f"{sanos} de {len(medianas)} bloques por encima de "
                f"{UMBRAL_SANO:.2f}".replace(".", ","),
           "cobertura = que fraccion de los estudiantes de la fila\n"
           "quedo representada en ese bloque de preguntas")

    # Derecha: la cobertura de clima escolar cae con el tamanio del grupo.
    dd = d.copy()
    dd["_q"] = pd.qcut(dd["estudiantes"], 5, labels=False)
    res = dd.groupby("_q", observed=True).agg(
        cob=("cob__clima_escolar", "median"),
        est=("estudiantes", "median")).reset_index()
    ax2.plot(res["_q"], res["cob"], color=NARANJA, lw=2.2,
             marker="o", ms=8, mfc=FONDO, mew=2.2, zorder=3)
    for _, f in res.iterrows():
        ax2.annotate(f"{f['cob']:.3f}", xy=(f["_q"], f["cob"]), xytext=(0, 11),
                     textcoords="offset points", ha="center",
                     fontsize=9, color=TINTA)
    ax2.set_xticks(res["_q"])
    ax2.set_xticklabels([f"{e:,.0f}".replace(",", ".")
                         for e in res["est"]])
    ax2.set_xlabel("estudiantes por grupo (mediana del quintil)")
    ax2.set_ylabel("cobertura de clima escolar")
    ax2.set_ylim(0.65, 1.0)
    ax2.grid(axis="y", zorder=0)
    ax2.set_axisbelow(True)
    titulo(ax2, "y el que falla, falla donde mas importa",
           "el clima escolar esta peor medido en los grupos mas chicos,\n"
           "que son mayormente rurales: no es un faltante al azar")

    fig.tight_layout()
    fig.savefig(FIGURAS / "tp2_a_calidad_cobertura.png", dpi=160,
                bbox_inches="tight")
    plt.close(fig)
    return "tp2_a_calidad_cobertura.png"


# --------------------------------------------------------------- FIGURA B
def figura_b_brecha(d):
    """Las 4 celdas, con su tamanio a la vista."""
    t = d.groupby(["sector", "ambito"]).apply(
        lambda g: pd.Series({
            "mate": media_ponderada(g, MATE_BAJO),
            "sobre": media_ponderada(g, SOBREEDAD_ALTA),
            "est": g["estudiantes"].sum(),
            "filas": len(g),
        }), include_groups=False).reset_index()
    t["etiqueta"] = t["sector"] + " · " + t["ambito"]
    t = t.sort_values("mate")

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.5, 5.6), gridspec_kw={"width_ratios": [1.5, 1]})

    colores = [AZUL if s == "Privado" else NARANJA for s in t["sector"]]
    ax1.barh(t["etiqueta"], t["mate"], color=colores, height=0.6, zorder=3)
    for y, (_, f) in enumerate(t.iterrows()):
        ax1.annotate(f"{f['mate']:.2f}", xy=(f["mate"], y), xytext=(6, 0),
                     textcoords="offset points", va="center",
                     fontsize=10, color=TINTA)
    ax1.set_xlim(0, 0.82)
    ax1.set_xlabel("proporcion por debajo del nivel basico en matematica")
    ax1.grid(axis="x", zorder=0)
    ax1.set_axisbelow(True)
    titulo(ax1, "Dentro del mismo ambito, el sector pesa mas que el lugar",
           "cambiar de privado a estatal (urbano): +0,23 · "
           "cambiar de urbano a rural (privado): +0,13")

    # El tamanio de cada celda, para que nadie cite la mas chica sin saberlo.
    ax2.barh(t["etiqueta"], t["est"], color=TINTA_SUAVE, height=0.6,
             alpha=0.28, zorder=3)
    for y, (_, f) in enumerate(t.iterrows()):
        ax2.annotate(f"{f['est']:,.0f}".replace(",", ".") +
                     f"  ({100 * f['est'] / t['est'].sum():.1f}%)",
                     xy=(f["est"], y), xytext=(6, 0),
                     textcoords="offset points", va="center",
                     fontsize=9, color=TINTA)
    ax2.set_xlim(0, t["est"].max() * 1.5)
    ax2.set_xticks([])
    ax2.set_yticklabels([])
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_visible(False)
    titulo(ax2, "cuanta gente hay atras de cada barra",
           "privado rural es el 0,7% de los estudiantes: ilustra, no sostiene")

    fig.tight_layout()
    fig.savefig(FIGURAS / "tp2_b_brecha_gestion.png", dpi=160,
                bbox_inches="tight")
    plt.close(fig)
    return "tp2_b_brecha_gestion.png"


# --------------------------------------------------------------- FIGURA C
def figura_c_contexto(d):
    """24 provincias. El tamanio del punto es la matricula."""
    prov = d.groupby("jurisdiccion").apply(
        lambda g: pd.Series({
            "ipcf": g[INGRESO].iloc[0],
            "mate": media_ponderada(g, MATE_BAJO),
            "est": g["estudiantes"].sum(),
        }), include_groups=False).reset_index()

    r = prov["ipcf"].corr(prov["mate"])
    r_sc = prov[~prov["jurisdiccion"].str.contains("Aut")]
    r_sin = r_sc["ipcf"].corr(r_sc["mate"])
    rho = prov["ipcf"].corr(prov["mate"], method="spearman")

    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.scatter(prov["ipcf"], prov["mate"], s=prov["est"] / 90,
               color=AZUL, alpha=0.7, edgecolor=FONDO, linewidth=2, zorder=3)

    # Etiquetas directas, sin leyenda: hay una sola serie. Se nombran los dos
    # extremos del eje Y y ademas las tres jurisdicciones con mas matricula,
    # porque un punto grande sin nombre es la primera pregunta que hace
    # cualquiera que mira el grafico.
    destacar = pd.concat([prov.nsmallest(3, "mate"), prov.nlargest(3, "mate"),
                          prov.nlargest(3, "est")]).drop_duplicates("jurisdiccion")
    for _, f in destacar.iterrows():
        nombre = f["jurisdiccion"].replace(
            "Ciudad Autónoma de Buenos Aires", "CABA")
        ax.annotate(nombre, xy=(f["ipcf"], f["mate"]), xytext=(0, 13),
                    textcoords="offset points", ha="center",
                    fontsize=9, color=TINTA_SUAVE)

    z = np.polyfit(prov["ipcf"], prov["mate"], 1)
    xs = np.linspace(prov["ipcf"].min(), prov["ipcf"].max(), 50)
    ax.plot(xs, np.polyval(z, xs), color=TINTA_SUAVE, lw=1.2,
            ls="--", alpha=0.6, zorder=2)

    ax.set_xlabel("ingreso per capita familiar mediano de la provincia (EPH 3T-2025)")
    ax.xaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(
            lambda v, _: "$" + f"{v:,.0f}".replace(",", ".")))
    ax.set_ylabel("por debajo del nivel basico en matematica")
    ax.grid(zorder=0)
    ax.set_axisbelow(True)
    titulo(ax, f"A mas ingreso provincial, menos estudiantes por debajo del basico",
           f"r = {r:+.2f} sobre 24 jurisdicciones · sin CABA {r_sin:+.2f} · "
           f"Spearman {rho:+.2f}   |   el tamanio del punto es la matricula")

    fig.tight_layout()
    fig.savefig(FIGURAS / "tp2_c_contexto_rendimiento.png", dpi=160,
                bbox_inches="tight")
    plt.close(fig)
    return "tp2_c_contexto_rendimiento.png"


# --------------------------------------------------------------- FIGURA D
def figura_d_inasistencias(d):
    """El hallazgo raro, y por que casi no lo vemos."""
    cols5 = ["inasistencias__de_5_a_14_faltas", "inasistencias__de_15_a_19_faltas",
             "inasistencias__de_20_a_29_faltas", "inasistencias__30_o_mas_faltas"]
    dd = d.copy()
    dd["faltas5"] = dd[cols5].sum(axis=1)

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.5, 5.8), gridspec_kw={"width_ratios": [1, 1.25]})

    # Izquierda: por que la cola no muestra nada y el acumulado si.
    medidas = [
        ("30+ faltas\n(solo la cola)", d["inasistencias__30_o_mas_faltas"]),
        ("15+ faltas", dd[cols5[1:]].sum(axis=1)),
        ("5+ faltas\n(acumulado)", dd["faltas5"]),
        ("ninguna falta", d["inasistencias__ninguna_falta"]),
    ]
    nombres = [m[0] for m in medidas]
    erres = [m[1].corr(d[MATE_BAJO]) for m in medidas]
    colores = [AMARILLO if abs(x) < 0.05 else
               (NARANJA if x > 0 else AZUL) for x in erres]
    ax1.barh(nombres, erres, color=colores, height=0.6, zorder=3)
    ax1.axvline(0, color=TINTA_SUAVE, lw=1, zorder=2)
    for y, x in enumerate(erres):
        ax1.annotate(f"{x:+.2f}", xy=(x, y),
                     xytext=(8 if x >= 0 else -8, 0),
                     textcoords="offset points", va="center",
                     ha="left" if x >= 0 else "right",
                     fontsize=10, color=TINTA)
    ax1.set_xlim(-0.62, 0.45)
    ax1.set_xlabel("correlacion con el desempenio bajo en matematica")
    ax1.grid(axis="x", zorder=0)
    ax1.set_axisbelow(True)
    titulo(ax1, "Medir la cola no muestra nada; el acumulado si",
           "la primera medicion uso solo 30+ faltas y dio 0,00")

    # Derecha: la relacion se mantiene dentro de cada celda (no es Simpson).
    # Aca SI va leyenda y no etiquetas directas: la regla del TP1 pide
    # etiquetas directas cuando hay UNA sola serie, y aca hay cuatro
    # solapadas. Etiquetarlas sobre los puntos las volvia ilegibles.
    # Doble codificacion: COLOR dice el sector y FORMA dice el ambito. Una
    # version anterior usaba transparencia para el ambito y las entradas
    # rurales quedaban casi invisibles en la leyenda: la opacidad no sirve
    # como canal categorico porque no se puede leer sin comparar contra otra.
    marcadores = {"Urbano": "o", "Rural": "^"}
    referencias = []
    for (sec, amb), g in dd.groupby(["sector", "ambito"]):
        color = AZUL if sec == "Privado" else NARANJA
        ax2.scatter(g["faltas5"], g[MATE_BAJO], s=g["estudiantes"] / 55,
                    color=color, alpha=0.6, marker=marcadores[amb],
                    edgecolor=FONDO, linewidth=0.7, zorder=3)
        referencias.append((sec, amb, color, 0.9, marcadores[amb],
                            g["faltas5"].corr(g[MATE_BAJO])))

    ax2.set_xlabel("proporcion del grupo que reporta 5 o mas faltas")
    ax2.set_ylabel("por debajo del basico en matematica")
    ax2.set_xlim(0.18, 1.03)
    ax2.set_ylim(0.05, 1.0)
    ax2.grid(zorder=0)
    ax2.set_axisbelow(True)

    # Leyenda propia en el hueco de abajo a la izquierda, con el r de cada
    # celda al lado. Se dibuja a mano y no con ax.legend() para poder poner
    # el r pegado a cada entrada, que es el dato que importa.
    referencias.sort(key=lambda x: x[5])
    for i, (sec, amb, color, alfa, marca, rg) in enumerate(referencias):
        y = 0.245 - i * 0.052
        ax2.scatter([0.235], [y], s=70, color=color, alpha=alfa,
                    marker=marca, edgecolor=FONDO, linewidth=0.7,
                    zorder=4, clip_on=False)
        ax2.annotate(f"{sec} {amb.lower()}", xy=(0.265, y),
                     va="center", fontsize=9, color=TINTA_SUAVE)
        ax2.annotate(f"r = {rg:+.2f}", xy=(0.46, y),
                     va="center", fontsize=9, color=TINTA)
    titulo(ax2, "Y no es efecto de mezclar sectores",
           "la relacion negativa se mantiene dentro de las cuatro celdas")

    fig.tight_layout()
    fig.savefig(FIGURAS / "tp2_d_inasistencias.png", dpi=160,
                bbox_inches="tight")
    plt.close(fig)
    return "tp2_d_inasistencias.png"


def main():
    d = pd.read_csv(PROC / "dataset_maestro_curado.csv")
    FIGURAS.mkdir(parents=True, exist_ok=True)

    print("=" * 74)
    print("FIGURAS DEL TP2")
    print("=" * 74)
    print("  Paleta y criterios heredados del TP1, sin colores nuevos.")
    print()
    for fn in (figura_a_calidad, figura_b_brecha,
               figura_c_contexto, figura_d_inasistencias):
        nombre = fn(d)
        peso = (FIGURAS / nombre).stat().st_size / 1024
        print(f"  GUARDADO: figuras/{nombre}  ({peso:,.0f} KB)")


if __name__ == "__main__":
    main()
