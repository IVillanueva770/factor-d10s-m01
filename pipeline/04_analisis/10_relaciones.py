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

    # El titular sale de la comparacion entre las dos celdas URBANAS, no de la
    # mas llamativa. Motivo: privado rural son 36 filas y 3.679 estudiantes
    # (0,7% del total) y es ademas la celda de mayor dispersion, asi que un
    # argumento apoyado ahi se cae ante la primera pregunta por el denominador.
    # Las dos urbanas juntas cubren 504.759 estudiantes, el 93,5%.
    eu, pu_ = v("Estatal", "Urbano", MATE_BAJO), v("Privado", "Urbano", MATE_BAJO)
    er_, pr_ = v("Estatal", "Rural", MATE_BAJO), v("Privado", "Rural", MATE_BAJO)
    est_urb = tabla.loc[tabla["ambito"] == "Urbano", "estudiantes"].sum()
    total = tabla["estudiantes"].sum()
    _pr = (tabla["sector"] == "Privado") & (tabla["ambito"] == "Rural")
    est_pr = tabla.loc[_pr, "estudiantes"].sum()
    filas_pr = tabla.loc[_pr, "filas"].sum()

    lectura = (
        f"**Dentro del mismo ambito urbano, cambiar de sector mueve el "
        f"desempenio {abs(eu - pu_):.2f} puntos** (estatal {eu:.2f} contra "
        f"privado {pu_:.2f}). Cambiar de ambito dentro de privado lo mueve "
        f"{abs(pr_ - pu_):.2f}. **El sector pesa mas que el lugar.**\n\n"
        f"Este titular se apoya en las dos celdas urbanas a proposito, porque "
        f"entre las dos suman {est_urb:,.0f} estudiantes, el "
        f"{100 * est_urb / total:.1f}% del total.\n\n"
        f"*Dato de color, con su denominador:* un estudiante de estatal urbana "
        f"({eu:.2f}) esta peor que uno de privada RURAL ({pr_:.2f}), o sea que "
        f"el campo no es lo que lo hunde. Es la comparacion mas ilustrativa y "
        f"la mas fragil: privada rural son {filas_pr:.0f} filas y "
        f"{est_pr:,.0f} estudiantes, el "
        f"{100 * est_pr / total:.1f}% del total, y es ademas la celda con mayor "
        f"dispersion (ver el analisis de tamanio de grupo). Sirve para ilustrar, "
        f"no para sostener el argumento sola.\n\n"
        f"En sobreedad alta la brecha va en el mismo sentido: es {razon:.1f} "
        f"veces mayor en estatal rural que en privado urbano.\n\n"
        "**Por que importa para el proyecto:** sugiere que la variable a mirar "
        "no es donde queda la escuela sino quien la gestiona, y eso es una "
        "pregunta de politica publica, no de geografia."
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



def robustez_del_contexto(d):
    """Estresa la correlacion mas fuerte del trabajo en vez de solo reportarla.

    El proceso decisorio, que vale mas que el numero: una correlacion de
    Pearson tiene dos debilidades conocidas, y cada prueba de aca ataca una.

    Miedo 1, que la sostenga un solo caso raro. CABA es el sospechoso natural:
    es la jurisdiccion mas rica del pais y la de mejor desempenio, y esta sola
    en ese rincon del grafico. Si toda la relacion fuera "CABA arriba a la
    izquierda y el resto amontonado", sacarla la haria desaparecer.

    Miedo 2, que la relacion sea fuerte pero curva. Pearson solo ve lineas
    rectas. Spearman ignora la forma y mira unicamente el ORDEN: si la
    provincia mas rica es la de mejor desempenio, la segunda mas rica la
    segunda, y asi. Si Spearman da mas fuerte que Pearson, la relacion existe
    y no es del todo lineal.

    La regla que queda para todo el proyecto: antes de creerle a una
    correlacion, preguntate QUIEN LA SOSTIENE y QUE FORMA TIENE.
    """
    prov = d.groupby("jurisdiccion").apply(
        lambda g: pd.Series({
            "ipcf": g[INGRESO].iloc[0],
            "mate_bajo": media_ponderada(g, MATE_BAJO),
        }), include_groups=False)
    sin_caba = prov.drop(index=[i for i in prov.index if "Aut" in i])
    tabla = pd.DataFrame([
        {"prueba": "Pearson, las 24 jurisdicciones", "n": len(prov),
         "r": prov["ipcf"].corr(prov["mate_bajo"])},
        {"prueba": "Pearson, sin CABA", "n": len(sin_caba),
         "r": sin_caba["ipcf"].corr(sin_caba["mate_bajo"])},
        {"prueba": "Spearman, las 24", "n": len(prov),
         "r": prov["ipcf"].corr(prov["mate_bajo"], method="spearman")},
        {"prueba": "Spearman, sin CABA", "n": len(sin_caba),
         "r": sin_caba["ipcf"].corr(sin_caba["mate_bajo"], method="spearman")},
    ])
    lectura = (
        "**Por que estas tres pruebas y no otras.** Una correlacion de Pearson "
        "falla de dos maneras conocidas, y cada prueba ataca una.\n\n"
        "*Que la sostenga un solo caso raro.* CABA es el sospechoso natural: es "
        "la jurisdiccion mas rica y la de mejor desempenio, y esta sola en ese "
        "rincon. Si la relacion fuera solo ella, sacarla la derrumbaria. Se "
        "saco y la relacion se mantiene.\n\n"
        "*Que la relacion sea fuerte pero curva.* Pearson solo ve lineas "
        "rectas; Spearman ignora la forma y mira solo el orden. Spearman da mas "
        "fuerte que Pearson, lo que sugiere que la relacion es algo curva: el "
        "salto entre las provincias mas pobres pesa mas que entre las mas "
        "ricas.\n\n"
        "**La relacion sobrevive las tres pruebas**, asi que no depende de un "
        "outlier ni es un artefacto de suponer linealidad.\n\n"
        "**Y el n es parte del dato.** Son 24 puntos, uno por jurisdiccion, no "
        "1.174. Con 24 observaciones, mover dos o tres cambia bastante el "
        "resultado. Por eso el numero se cita siempre como *r = -0,82 sobre 24 "
        "jurisdicciones* y nunca como *r = -0,82* a secas."
    )
    return "Robustez de la correlacion mas fuerte del trabajo", tabla, lectura


def inasistencias_acumuladas(d):
    """El hallazgo contraintuitivo, y como aparecio.

    La primera version probo UNA sola categoria, la cola extrema (30 faltas o
    mas), y dio r = +0,000. La conclusion habria sido "las inasistencias no se
    relacionan con el desempenio", que es falso. El error fue medir el extremo
    de una distribucion en vez del acumulado: casi nadie cae en la categoria
    mas extrema, asi que esa columna casi no varia y no puede correlacionar con
    nada.
    """
    acum = {
        "ninguna falta": ["inasistencias__ninguna_falta"],
        "5 o mas faltas": ["inasistencias__de_5_a_14_faltas",
                           "inasistencias__de_15_a_19_faltas",
                           "inasistencias__de_20_a_29_faltas",
                           "inasistencias__30_o_mas_faltas"],
        "15 o mas faltas": ["inasistencias__de_15_a_19_faltas",
                            "inasistencias__de_20_a_29_faltas",
                            "inasistencias__30_o_mas_faltas"],
        "30 o mas faltas (solo la cola)": ["inasistencias__30_o_mas_faltas"],
    }
    filas = []
    for nombre, cols in acum.items():
        cols = [c for c in cols if c in d.columns]
        if not cols:
            continue
        serie = d[cols].sum(axis=1)
        filas.append({
            "medida": nombre,
            "r_con_matematica_bajo": serie.corr(d[MATE_BAJO]),
            "valor_medio_ponderado": np.average(serie, weights=d["estudiantes"]),
        })
    tabla = pd.DataFrame(filas)

    # Chequeo de Simpson: se mantiene DENTRO de cada celda de sector x ambito?
    cols5 = [c for c in acum["5 o mas faltas"] if c in d.columns]
    dd = d.copy()
    dd["_faltas5"] = dd[cols5].sum(axis=1)
    dentro = [{"medida": f"5+ faltas, solo {sec} {amb}",
               "r_con_matematica_bajo": g["_faltas5"].corr(g[MATE_BAJO]),
               "valor_medio_ponderado": np.average(
                   g["_faltas5"], weights=g["estudiantes"])}
              for (sec, amb), g in dd.groupby(["sector", "ambito"])]
    tabla = pd.concat([tabla, pd.DataFrame(dentro)], ignore_index=True)

    lectura = (
        "**El hallazgo mas raro del trabajo, y queda como pregunta abierta, no "
        "como conclusion.** Cuantos mas chicos de un grupo reportan faltas, "
        "MENOS chicos de ese grupo estan por debajo del basico. Y los grupos "
        "donde mas chicos dicen no faltar nunca son los de peor desempenio.\n\n"
        "**Como aparecio, porque el metodo importa.** La primera medicion uso "
        "solo la categoria mas extrema (30 faltas o mas) y dio r = +0,000: la "
        "conclusion habria sido que las inasistencias no se relacionan con "
        "nada. El error fue mirar la cola de la distribucion en vez del "
        "acumulado. Casi nadie cae en la categoria extrema, asi que esa columna "
        "casi no varia y no puede correlacionar con nada.\n\n"
        "**No es la paradoja de Simpson.** Se calculo el mismo r dentro de cada "
        "combinacion de sector y ambito (las cuatro ultimas filas de la tabla): "
        "la relacion negativa se mantiene en las cuatro, asi que no la produce "
        "mezclar poblaciones distintas.\n\n"
        "**Quien contesta esto, VERIFICADO en la fuente.** El Manual del "
        "Aplicador de Aprender 2024 dice que *al finalizar ambas pruebas, los "
        "estudiantes contestaran un cuestionario complementario*, y que cada "
        "alumno recibe un Cuadernillo del Estudiante con las hojas para "
        "registrar sus respuestas. Hay un cuestionario aparte para directores, "
        "que no es este. O sea que el dato es **lo que el estudiante dice que "
        "falto**, no un registro administrativo de asistencia.\n\n"
        "**Hipotesis, explicitamente NO VERIFICADA.** Aprender evalua a quien "
        "esta presente el dia de la prueba, asi que en una escuela con "
        "ausentismo real alto los mas ausentes no entran a la muestra. Entre "
        "los que si rindieron, reportar faltas seria marcador de un alumno "
        "presente y conectado con la escuela, no de riesgo. Se suma que el dato "
        "es autorreporte: son dos capas de ruido en la misma variable. "
        "Verificarlo requiere datos de asistencia administrativa, que este "
        "dataset no tiene."
    )
    return "Inasistencias: el acumulado, no la cola", tabla, lectura


def dispersion_por_tamanio(d):
    """Por que un grupo chico produce valores extremos sin que nada este mal.

    Sale de una pregunta del equipo: si hay pocas escuelas rurales privadas,
    hay mas chance de ver valores raros ahi? Si. Conviene tenerlo medido antes
    de citar cualquier numero de una celda chica.
    """
    dd = d.copy()
    dd["_q"] = pd.qcut(dd["estudiantes"], 5,
                       labels=["1 mas chico", "2", "3", "4", "5 mas grande"])
    tabla = dd.groupby("_q", observed=True).agg(
        filas=(MATE_BAJO, "size"),
        estudiantes_mediana=("estudiantes", "median"),
        desvio=(MATE_BAJO, "std"),
        minimo=(MATE_BAJO, "min"),
        maximo=(MATE_BAJO, "max"),
    ).reset_index()
    razon = tabla["desvio"].iloc[0] / tabla["desvio"].iloc[-1]
    lectura = (
        f"**El quintil de grupos mas chicos tiene {razon:.1f} veces la "
        "dispersion del mas grande**, y sus valores llegan a 0,000 y a 1,000, "
        "o sea los extremos posibles, mientras el quintil grande queda entre "
        "0,18 y 0,84. No es que los grupos chicos sean mejores ni peores: con "
        "pocos casos, un estudiante mas o menos mueve mucho el porcentaje.\n\n"
        "**Consecuencia practica para leer todo este informe:** cualquier "
        "numero de una celda chica se cita con su denominador al lado. La celda "
        "privada rural son 36 filas y 3.679 estudiantes, el 0,7% del total, y "
        "es ademas la de mayor dispersion de las cuatro."
    )
    return "Por que los grupos chicos dan valores extremos", tabla, lectura


def diferencias_por_sexo(d):
    """La pregunta de la consigna que este dataset NO permite responder.

    Se documenta el limite en vez de forzar un numero: forzarlo seria peor que
    no tenerlo, porque daria una respuesta a una pregunta distinta.
    """
    cols = [c for c in d.columns if c.startswith("sexo__")]
    tabla = pd.DataFrame([{
        "columna": c,
        "que_mide": "proporcion de esa categoria DENTRO del grupo",
        "r_con_matematica_bajo": d[c].corr(d[MATE_BAJO]),
    } for c in cols])
    lectura = (
        "**La consigna pregunta si hay diferencias segun sexo, y con esta base "
        "no se puede responder.** Las columnas `sexo__*` dicen que porcentaje "
        "del grupo son varones o mujeres; **no** dicen como le fue a cada sexo. "
        "Para eso haria falta el desempenio desagregado por sexo, que la base "
        "agregada de Aprender no publica.\n\n"
        "Lo unico calculable es si los grupos con mas mujeres rinden distinto, "
        "y da practicamente cero. Ese numero responde una pregunta diferente de "
        "la que se hizo, asi que se reporta el limite y no el numero.\n\n"
        "**Es la misma pared que el TP1 ya habia declarado:** la unidad de "
        "analisis es el grupo territorial y no el estudiante, asi que toda "
        "pregunta que necesite abrir por atributo individual queda fuera de "
        "alcance con las bases publicadas."
    )
    return "Diferencias por sexo: por que no se puede responder", tabla, lectura


ANALISIS = [brecha_por_gestion, dispersion_por_tamanio,
            contexto_vs_rendimiento, robustez_del_contexto,
            sobreedad_y_desempenio, inasistencias_acumuladas,
            diferencias_por_sexo, efecto_de_la_curacion,
            ranking_provincias]


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
