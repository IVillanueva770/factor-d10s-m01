"""Paso 9: las visualizaciones del entregable.

Tres graficos, cada uno con una pregunta atras. Ninguno es decorativo.

  A. ¿El contexto socioeconomico se relaciona con el rendimiento?
     Es el unico que usa las dos fuentes a la vez, o sea que muestra para que
     sirvio integrarlas.
  B. ¿Donde estan las brechas dentro del sistema educativo?
  C. ¿Cuanto podemos confiar en lo que construimos?

Criterios aplicados: marcas finas, grilla recesiva, etiquetas directas en vez
de leyenda cuando hay una sola serie, texto siempre en tinta y nunca del color
de la serie, y una paleta categorica validada (separacion para daltonismo
ΔE 9,1 protan y 22,9 en vision normal).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESADO = BASE_DIR / "data" / "processed"
FIGURAS = BASE_DIR / "figuras"

# Paleta categorica validada. Orden fijo: nunca se cicla ni se reasigna.
AZUL, NARANJA, VERDE, AMARILLO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
TINTA = "#0b0b0b"
TINTA_SUAVE = "#52514e"
GRIS_GRILLA = "#e3e3e0"

plt.rcParams.update({
    "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb",
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


def promedio_ponderado(grupo, columnas):
    """Promedio de columnas de proporcion, pesado por estudiantes de la fila."""
    peso = grupo["estudiantes"]
    return (grupo[columnas].sum(axis=1) * peso).sum() / peso.sum()


def grafico_a(maestro):
    """Dos paneles: el cruce que funciona y el que no.

    Se probaron los cuatro indicadores de la EPH contra el desempeño. El
    ingreso mediano da r = -0,82; el proxy de abandono da r = +0,16. Mostrar
    solo el primero seria elegir el resultado lindo, asi que van los dos.
    """
    prov = maestro.groupby("jurisdiccion").apply(
        lambda g: pd.Series({
            "ipcf": g["eph_ipcf_mediano"].iloc[0] / 1000,
            "no_asiste": g["eph_no_asiste_12_18"].iloc[0],
            "bajo_matematica": promedio_ponderado(
                g, ["desemp_matematica__por_debajo_del_nivel_basico"]),
            "estudiantes": g["estudiantes"].sum(),
        }), include_groups=False)

    paneles = [
        ("ipcf", "Ingreso per cápita familiar mediano (miles de $, EPH)",
         AZUL, lambda x, _: f"${x:.0f}k"),
        ("no_asiste", "No asiste a la escuela, 12 a 18 años (EPH)",
         NARANJA, lambda x, _: f"{x:.0%}"),
    ]

    fig, ejes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
    correlaciones = {}
    for ax, (variable, etiqueta, color, formato) in zip(ejes, paneles):
        r = prov[variable].corr(prov["bajo_matematica"])
        correlaciones[variable] = r
        ax.grid(zorder=0)
        ax.set_axisbelow(True)
        ax.scatter(prov[variable], prov["bajo_matematica"],
                   s=prov["estudiantes"] / 150, color=color, alpha=0.75,
                   edgecolor="#fcfcfb", linewidth=2, zorder=3)

        # Etiquetas: los extremos de los dos ejes y las dos provincias mas
        # grandes. Nunca las 24, que taparia el grafico.
        destacar = (prov.nlargest(2, "bajo_matematica").index.tolist()
                    + prov.nsmallest(2, "bajo_matematica").index.tolist()
                    + prov.nlargest(1, variable).index.tolist()
                    + prov.nlargest(2, "estudiantes").index.tolist())
        for nombre in dict.fromkeys(destacar):
            fila = prov.loc[nombre]
            ax.annotate(nombre.split(",")[0], (fila[variable],
                                               fila["bajo_matematica"]),
                        xytext=(8, 5), textcoords="offset points",
                        fontsize=9, color=TINTA_SUAVE)

        ax.set_xlabel(etiqueta)
        ax.xaxis.set_major_formatter(formato)
        ax.set_title(f"r = {r:+.2f}", loc="left", pad=8, color=TINTA)

    ejes[0].set_ylabel("Desempeño por debajo del nivel básico en Matemática\n"
                       "(Aprender 2024)")
    ejes[0].yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
    fig.suptitle("Qué del contexto socioeconómico explica el rendimiento\n"
                 "cada punto es una provincia; el tamaño es la cantidad de "
                 "estudiantes evaluados", x=0.012, ha="left", y=0.99,
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(FIGURAS / "a_contexto_vs_rendimiento.png", dpi=150)
    plt.close(fig)
    return correlaciones


def grafico_b(maestro):
    """Sobreedad y repitencia segun sector de gestion y ambito."""
    sobreedad = [c for c in maestro.columns
                 if c.startswith("sobreedad__") and "sobreedad_" in c[11:]]
    repitencia = ["repitencia__repitio_1_vez",
                  "repitencia__repitio_2_veces_o_mas"]

    grupos = maestro.groupby(["sector", "ambito"]).apply(
        lambda g: pd.Series({
            "Sobreedad (1 año o más)": promedio_ponderado(g, sobreedad),
            "Repitió alguna vez": promedio_ponderado(g, repitencia),
            "estudiantes": g["estudiantes"].sum(),
        }), include_groups=False)
    grupos.index = [f"{s}\n{a.lower()}" for s, a in grupos.index]
    grupos = grupos.sort_values("Sobreedad (1 año o más)", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.grid(axis="y", zorder=0)
    ax.set_axisbelow(True)
    x = np.arange(len(grupos))
    ancho = 0.36

    for desplazamiento, (etiqueta, color) in zip(
            (-ancho / 2 - 0.01, ancho / 2 + 0.01),
            [("Sobreedad (1 año o más)", AZUL), ("Repitió alguna vez", NARANJA)]):
        barras = ax.bar(x + desplazamiento, grupos[etiqueta], ancho,
                        label=etiqueta, color=color, zorder=3)
        ax.bar_label(barras, fmt="%.0f%%",
                     labels=[f"{v:.0%}" for v in grupos[etiqueta]],
                     padding=3, fontsize=9, color=TINTA_SUAVE)

    ax.set_xticks(x, grupos.index)
    ax.set_ylabel("% de estudiantes")
    ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
    ax.set_ylim(0, max(grupos["Sobreedad (1 año o más)"].max(),
                       grupos["Repitió alguna vez"].max()) * 1.22)
    ax.legend(frameon=False, loc="upper right", ncols=2)
    ax.set_title("Las cuatro realidades del secundario argentino\n"
                 "atraso escolar según gestión y ámbito, Aprender 2024",
                 loc="left", pad=14)
    fig.tight_layout()
    fig.savefig(FIGURAS / "b_brechas_sector_ambito.png", dpi=150)
    plt.close(fig)
    return grupos


def grafico_c(maestro):
    """Cuantos estudiantes de Aprender dependen de cuantos encuestados EPH."""
    prov = maestro.groupby("jurisdiccion").agg(
        estudiantes=("estudiantes", "sum"),
        encuestados=("eph_casos_12_18", "first"),
    )
    prov["ratio"] = prov["estudiantes"] / prov["encuestados"]
    prov = prov.sort_values("ratio")
    mediana = prov["ratio"].median()

    fig, ax = plt.subplots(figsize=(9, 8))
    ax.grid(axis="x", zorder=0)
    ax.set_axisbelow(True)
    etiquetas = [n.split(",")[0] for n in prov.index]
    barras = ax.barh(etiquetas, prov["ratio"], color=AZUL, height=0.68, zorder=3)
    ax.bar_label(barras, labels=[f"{v:,.0f}" for v in prov["ratio"]],
                 padding=6, fontsize=9, color=TINTA_SUAVE, zorder=5)

    ax.axvline(mediana, color=NARANJA, linewidth=2, zorder=2)
    ax.annotate(f"mediana: {mediana:,.0f}", (mediana, len(prov) - 0.2),
                xytext=(8, 0), textcoords="offset points",
                color=NARANJA, fontsize=9, va="center")

    ax.set_xlabel("Estudiantes de Aprender por cada adolescente encuestado "
                  "en la EPH")
    ax.set_xlim(0, prov["ratio"].max() * 1.16)
    ax.set_title("Sobre cuántos casos se apoya el contexto de cada provincia\n"
                 "cuanto más largo, más fino el hilo del que cuelga el dato "
                 "socioeconómico", loc="left", pad=14)
    fig.tight_layout()
    fig.savefig(FIGURAS / "c_solidez_del_cruce.png", dpi=150)
    plt.close(fig)
    return prov


def main():
    FIGURAS.mkdir(exist_ok=True)
    maestro = pd.read_csv(PROCESADO / "dataset_maestro_inicial.csv")

    correlaciones = grafico_a(maestro)
    grupos = grafico_b(maestro)
    prov = grafico_c(maestro)

    print("=" * 74)
    print("GRAFICOS GENERADOS")
    print("=" * 74)
    print("  A. contexto vs rendimiento:")
    for k, v in correlaciones.items():
        print(f"       {k:12s} vs bajo desempeño en Matematica: r = {v:+.3f}")
    print(f"  B. brechas sector x ambito:")
    print(grupos[["Sobreedad (1 año o más)", "Repitió alguna vez",
                  "estudiantes"]].to_string(float_format=lambda x: f"{x:,.3f}"))
    print(f"  C. solidez del cruce -> mediana "
          f"{prov['ratio'].median():,.0f} estudiantes por encuestado, "
          f"maximo {prov['ratio'].max():,.0f}")
    print()
    for archivo in sorted(FIGURAS.glob("*.png")):
        print(f"  {archivo.relative_to(BASE_DIR)} "
              f"({archivo.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
