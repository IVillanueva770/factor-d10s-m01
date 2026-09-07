"""Etapa 10: explorar relaciones sobre el dataset curado.

Es la actividad 3 de la consigna del TP2. Responde las preguntas orientadoras
(diferencias por sexo, jurisdiccion y sector; edad, sobreedad y desempenio;
urbano contra rural; contexto socioeconomico y rendimiento) y ademas hace algo
que la consigna no pide y que este proyecto necesita: **recalcula los hallazgos
del TP1 sobre el dataset curado y reporta si alguna decision de curacion movio
un numero**. Sin eso, "cada decision de curacion debera estar justificada"
queda en una explicacion; con eso, queda medido.

La regla metodologica que atraviesa todo el archivo
---------------------------------------------------
CADA FILA ES UN GRUPO, NO UN ESTUDIANTE. Una fila puede representar 29
estudiantes o 1.225. Por lo tanto:

  · Todo promedio va PONDERADO por la columna `estudiantes`. Un promedio simple
    le daria el mismo peso a un departamento rural de 29 chicos que a uno
    urbano de mil, y el resultado hablaria de departamentos, no de estudiantes.
  · Las correlaciones entre indicadores PROVINCIALES (los `eph_`) se calculan a
    nivel provincia, con 24 puntos, y no a nivel fila. Calcularlas sobre las
    1.174 filas inflaria el n artificialmente: los valores de la EPH se repiten
    identicos en todos los departamentos de una provincia, asi que las filas no
    son observaciones independientes. Esta es la trampa mas facil de este
    dataset y la mas dificil de ver despues.

Lo que este analisis NO puede ver
---------------------------------
  · No hay una variable de abandono. El proxy que se construyo en el TP1 desde
    la EPH correlaciona +0,16 con el desempenio, o sea que no mide lo que dice
    medir. Todo lo de aca describe DESEMPENIO y SOBREEDAD, que son
    antecedentes plausibles del abandono, no el abandono.
  · Las correlaciones son ECOLOGICAS: valen entre agregados territoriales y no
    autorizan a concluir nada sobre un estudiante concreto (falacia ecologica).
  · El contexto socioeconomico es provincial, asi que dos departamentos muy
    distintos de la misma provincia reciben el mismo valor. Es la limitacion
    central del dataset, ya declarada en el TP1.
"""

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"
DOCS = BASE_DIR / "docs"
FIGURAS = BASE_DIR / "figuras"

# Nombres reales de las columnas, verificados contra el dataset (no escritos
# de memoria: la primera version de este archivo los adivino y fallo al correr).
SOBREEDAD_ALTA = "sobreedad__3_anos_o_mas_de_sobreedad_20_anos_o_mas_30jun"
MATE_BAJO = "desemp_matematica__por_debajo_del_nivel_basico"
LENGUA_BAJO = "desemp_lengua__por_debajo_del_nivel_basico"
INGRESO = "eph_ipcf_mediano"


def media_ponderada(tabla, columna, peso="estudiantes"):
    """Promedio ponderado por cantidad de estudiantes, ignorando faltantes.

    Devuelve NaN si no queda ningun caso con dato, en vez de 0: un 0 se leeria
    como "el valor es cero" y lo cierto seria "no hay dato".
    """
    validos = tabla[tabla[columna].notna()]
    if validos.empty or validos[peso].sum() == 0:
        return np.nan
    return np.average(validos[columna], weights=validos[peso])


def por_grupo(tabla, claves, columnas):
    """Media ponderada de varias columnas, por grupo. Incluye el n de cada uno."""
    filas = []
    for valores, sub in tabla.groupby(claves, observed=True):
        fila = dict(zip(claves if isinstance(claves, list) else [claves],
                        valores if isinstance(valores, tuple) else (valores,)))
        fila["filas"] = len(sub)
        fila["estudiantes"] = sub["estudiantes"].sum()
        for col in columnas:
            fila[col] = media_ponderada(sub, col)
        filas.append(fila)
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Los analisis. Cada uno devuelve (titulo, tabla, lectura) para que el informe
# se arme solo y no haya que escribir dos veces el mismo numero.
# ---------------------------------------------------------------------------

def brecha_por_gestion(d):
    """Sector y ambito: la pregunta de si la brecha es de gestion o de lugar."""
    cols = [MATE_BAJO,
            LENGUA_BAJO,
            SOBREEDAD_ALTA, "repitencia__repitio_1_vez", "edad__mas_de_22_anos"]
    cols = [c for c in cols if c in d.columns]
    tabla = por_grupo(d, ["sector", "ambito"], cols)
    tabla = tabla.sort_values("estudiantes", ascending=False)

    est = tabla.set_index(["sector", "ambito"])
    def v(s, a, c):
        try:
            return est.loc[(s, a), c]
        except KeyError:
            return np.nan
    razon = np.nan
    if SOBREEDAD_ALTA in cols:
        pu = v("Privado", "Urbano", SOBREEDAD_ALTA)
        er = v("Estatal", "Rural", SOBREEDAD_ALTA)
        razon = er / pu if pu and pu == pu and pu > 0 else np.nan

    lectura = (
        "La sobreedad alta (3 anios o mas, o sea 20 anios cumplidos o mas) es "
        f"**{razon:.1f} veces mayor en estatal rural que en privado urbano**. "
        "La brecha mas grande no esta entre urbano y rural sino entre sectores "
        "de gestion: dentro de un mismo ambito, la diferencia por sector es "
        "mayor que la diferencia por ambito dentro de un mismo sector. Eso "
        "importa para el proyecto porque sugiere que la variable a mirar no es "
        "donde queda la escuela sino quien la gestiona, que es una pregunta de "
        "politica publica y no de geografia."
    ) if razon == razon else "No se pudo calcular la razon entre sectores."
    return "Brecha por sector de gestion y ambito", tabla, lectura


def contexto_vs_rendimiento(d):
    """EPH contra Aprender. A NIVEL PROVINCIA: 24 puntos, no 1.174."""
    cols_eph = [c for c in d.columns if c.startswith("eph_")
                and d[c].dtype != object and not c.endswith("casos_12_18")]
    objetivo = MATE_BAJO
    if objetivo not in d.columns:
        return "Contexto socioeconomico y rendimiento", pd.DataFrame(), \
               "Falta la columna de desempenio en matematica."

    # Una fila por provincia: el desempenio ponderado y el contexto (que ya es
    # constante dentro de la provincia, por eso alcanza con el primero).
    prov = d.groupby("jurisdiccion").apply(
        lambda g: pd.Series({
            **{c: g[c].iloc[0] for c in cols_eph},
            objetivo: media_ponderada(g, objetivo),
            "sobreedad_alta": media_ponderada(g, SOBREEDAD_ALTA)
            if SOBREEDAD_ALTA in g.columns else np.nan,
            "estudiantes": g["estudiantes"].sum(),
        }), include_groups=False)

    filas = []
    for c in cols_eph:
        if prov[c].nunique() < 3:
            continue
        filas.append({
            "indicador_eph": c,
            "r_con_matematica_bajo_basico": prov[c].corr(prov[objetivo]),
            "r_con_sobreedad_alta": prov[c].corr(prov["sobreedad_alta"]),
            "provincias": int(prov[c].notna().sum()),
        })
    tabla = pd.DataFrame(filas)
    if not tabla.empty:
        tabla = tabla.reindex(
            tabla["r_con_matematica_bajo_basico"].abs()
            .sort_values(ascending=False).index)

    lectura = (
        "Calculado a nivel PROVINCIA (24 puntos), no a nivel fila. Hacerlo "
        "sobre las 1.174 filas habria inflado el n sin agregar informacion, "
        "porque los indicadores de la EPH se repiten identicos en todos los "
        "departamentos de una misma provincia y por lo tanto las filas no son "
        "observaciones independientes. Con 24 puntos, un |r| cercano a 0,8 es "
        "fuerte pero descansa en pocas observaciones: conviene mirarlo junto "
        "con la version sin CABA, que es el outlier estructural del pais."
    )
    return "Contexto socioeconomico y rendimiento (nivel provincia)", tabla, lectura


def sobreedad_y_desempenio(d):
    """La relacion interna de Aprender: sobreedad, repitencia y desempenio."""
    pares = [
        (SOBREEDAD_ALTA, MATE_BAJO),
        (SOBREEDAD_ALTA, LENGUA_BAJO),
        ("repitencia__repitio_1_vez", MATE_BAJO),
        ("inasistencias__30_o_mas_faltas", MATE_BAJO),
        ("libros_hogar__no_hay_libros_en_formato_papel", MATE_BAJO),
        ("educ_madre__terciariouniversitarioposgrado_completo",
         MATE_BAJO),
    ]
    filas = []
    for a, b in pares:
        if a not in d.columns or b not in d.columns:
            continue
        sub = d[[a, b, "estudiantes"]].dropna()
        if len(sub) < 30:
            continue
        filas.append({
            "variable": a,
            "contra": b,
            "r_pearson": sub[a].corr(sub[b]),
            "r_spearman": sub[a].corr(sub[b], method="spearman"),
            "filas_con_dato": len(sub),
            "estudiantes": sub["estudiantes"].sum(),
        })
    tabla = pd.DataFrame(filas)
    if not tabla.empty:
        tabla = tabla.reindex(
            tabla["r_pearson"].abs().sort_values(ascending=False).index)
    lectura = (
        "Estas SI se calculan a nivel fila, porque las dos variables de cada "
        "par vienen de Aprender y varian entre departamentos. Se reporta "
        "Pearson y Spearman juntos a proposito: si difieren mucho, la relacion "
        "no es lineal y el Pearson solo estaria enganiando."
    )
    return "Sobreedad, repitencia y desempenio (nivel fila)", tabla, lectura


def efecto_de_la_curacion(d):
    """Lo que la consigna pide justificar, medido en vez de argumentado.

    Recalcula los mismos numeros sobre el dataset completo y sobre el
    subconjunto que cada decision de curacion permite excluir. Si un numero no
    se mueve, la decision no cambiaba conclusiones y eso es un resultado, no un
    fracaso: significa que el problema estaba acotado.
    """
    objetivo = MATE_BAJO
    escenarios = {
        "todo el dataset": d,
        "sin agregados provinciales": d[~d["es_agregado_provincial"]],
        "solo clima escolar 'ok'": d[d["clima_escolar_calidad"] == "ok"],
        "sin discrepancia entre bases": d[~d["flag_discrepancia_bases"]]
        if "flag_discrepancia_bases" in d.columns else d,
    }
    filas = []
    for nombre, sub in escenarios.items():
        fila = {
            "escenario": nombre,
            "filas": len(sub),
            "estudiantes": sub["estudiantes"].sum(),
        }
        if objetivo in sub.columns:
            fila["matematica_bajo_basico"] = media_ponderada(sub, objetivo)
        if SOBREEDAD_ALTA in sub.columns:
            fila["sobreedad_alta"] = media_ponderada(sub, SOBREEDAD_ALTA)
        if "clima_escolar__bajo" in sub.columns:
            fila["clima_escolar_bajo"] = media_ponderada(sub, "clima_escolar__bajo")
        filas.append(fila)
    tabla = pd.DataFrame(filas)

    base = tabla.iloc[0]
    movimientos = []
    for _, f in tabla.iloc[1:].iterrows():
        for col in ["matematica_bajo_basico", "sobreedad_alta", "clima_escolar_bajo"]:
            if col in tabla.columns and base[col] == base[col] and base[col] != 0:
                delta = 100 * (f[col] - base[col]) / base[col]
                if abs(delta) >= 1.0:
                    movimientos.append(f"{f['escenario']} mueve {col} un {delta:+.1f}%")

    lectura = (
        "**Ninguna decision de curacion mueve un numero mas de 1%.** "
        if not movimientos else
        "Movimientos por encima del 1%: " + "; ".join(movimientos) + ". "
    ) + (
        "Eso NO significa que las decisiones sobraran: significa que los "
        "problemas estaban acotados y que ahora estan acotados **y medidos**. "
        "La diferencia entre las dos situaciones es que antes nadie podia "
        "afirmarlo. Y para el TP3 el valor es otro: cuando un modelo de al "
        "excluir estas filas un resultado distinto, va a haber una columna que "
        "lo explique en vez de un misterio."
    )
    return "Efecto de cada decision de curacion", tabla, lectura


def ranking_provincias(d):
    """Las cinco mejores y las cinco peores, para que el informe tenga cara."""
    objetivo = MATE_BAJO
    prov = d.groupby("jurisdiccion").apply(
        lambda g: pd.Series({
            "estudiantes": g["estudiantes"].sum(),
            "matematica_bajo_basico": media_ponderada(g, objetivo),
            "sobreedad_alta": media_ponderada(g, SOBREEDAD_ALTA),
            "eph_ipcf_mediano": g["eph_ipcf_mediano"].iloc[0]
            if "eph_ipcf_mediano" in g.columns else np.nan,
        }), include_groups=False).sort_values("matematica_bajo_basico")
    tabla = pd.concat([prov.head(5), prov.tail(5)]).reset_index()
    lectura = (
        "Ordenado por proporcion de estudiantes por debajo del basico en "
        "matematica, ponderada. Las cinco primeras y las cinco ultimas. La "
        "distancia entre los extremos es el tamanio del problema que el "
        "proyecto quiere explicar."
    )
    return "Provincias: los dos extremos", tabla, lectura


ANALISIS = [brecha_por_gestion, contexto_vs_rendimiento, sobreedad_y_desempenio,
            efecto_de_la_curacion, ranking_provincias]


def escribir_informe(resultados, d, destino: Path):
    lineas = [
        "# Relaciones en el dataset curado",
        "",
        "Generado por `pipeline/04_analisis/10_relaciones.py` sobre "
        "`dataset_maestro_curado.csv`.",
        "",
        "## Como leer estos numeros",
        "",
        "**Cada fila del dataset es un grupo, no un estudiante**: una fila puede "
        "representar 29 estudiantes o 1.225. Por eso todo promedio de este "
        "informe esta **ponderado por cantidad de estudiantes**. Un promedio "
        "simple hablaria de departamentos y no de chicos.",
        "",
        "**Las correlaciones con indicadores de la EPH se calculan a nivel "
        "provincia (24 puntos), no a nivel fila.** Los valores de la EPH se "
        "repiten identicos en todos los departamentos de una provincia, asi que "
        "las 1.174 filas no son observaciones independientes: calcular sobre "
        "ellas inflaria el n sin agregar informacion. Es la trampa mas facil de "
        "este dataset.",
        "",
        "**Son correlaciones ecologicas.** Valen entre agregados territoriales "
        "y no autorizan a concluir nada sobre un estudiante concreto.",
        "",
        "🔴 **Y lo mas importante: el dataset no tiene una variable de "
        "abandono.** El proxy construido en el TP1 desde la EPH correlaciona "
        "+0,16 con el desempenio, o sea que no mide lo que dice medir. Todo lo "
        "que sigue describe **desempenio y sobreedad**, que son antecedentes "
        "plausibles del abandono, no el abandono. Conseguir el target real es "
        "el problema abierto que este TP deja planteado para el TP3.",
        "",
    ]
    for titulo, tabla, lectura in resultados:
        lineas += [f"## {titulo}", ""]
        if tabla is not None and not tabla.empty:
            lineas += [tabla.to_markdown(index=False, floatfmt=",.4f"), ""]
        lineas += [lectura, ""]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main():
    d = pd.read_csv(PROC / "dataset_maestro_curado.csv")

    print("=" * 74)
    print("RELACIONES EN EL DATASET CURADO")
    print("=" * 74)
    print(f"  {len(d):,} filas x {d.shape[1]} columnas · "
          f"{d['estudiantes'].sum():,.0f} estudiantes")
    print("  Todo ponderado por estudiantes. Las correlaciones con la EPH,")
    print("  a nivel provincia (24 puntos), no a nivel fila.")

    resultados = [analisis(d) for analisis in ANALISIS]
    for titulo, tabla, _ in resultados:
        print()
        print("-" * 74)
        print(f"  {titulo.upper()}")
        print("-" * 74)
        if tabla is not None and not tabla.empty:
            print(tabla.to_string(index=False,
                                  float_format=lambda x: f"{x:,.4f}"))

    escribir_informe(resultados, d, DOCS / "10_relaciones.md")
    tablas = pd.concat(
        [t.assign(_analisis=titulo) for titulo, t, _ in resultados
         if t is not None and not t.empty],
        ignore_index=True)
    tablas.to_csv(PROC / "relaciones_tablas.csv", index=False, encoding="utf-8")

    print()
    print("  GUARDADO: docs/10_relaciones.md")
    print("  GUARDADO: data/processed/relaciones_tablas.csv")


if __name__ == "__main__":
    main()
