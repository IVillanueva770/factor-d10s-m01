# -*- coding: utf-8 -*-
"""Genera el PDF corto del Entregable 3 (Machine Learning) del grupo M01.

Salida: entregas/03-machine-learning/TP3_Resumen_El_Factor_D10S.pdf (A4, 4 paginas
como maximo, verificado con pypdf al final de cada corrida).

POR QUE ASI
-----------

1. Mismo relato que el notebook, mas corto y para quien decide.
   El texto es una version resumida del markdown de 14_notebook_tp3.py. La
   devolucion del TP2 pidio lo de alto impacto en la primera hoja: la pagina 1
   es el problema, las cinco conclusiones y que hariamos; el como va despues.

2. Ningun numero se escribe a mano.
   Todos salen de cifras() de 14_notebook_tp3.py, que los lee de los CSV del
   proyecto, y se formatean con sus mismos helpers (pct, num, miles). Si un
   numero cambia, cambia ahi y este PDF se regenera.

3. Estilo heredado del TP2, importado y no copiado.
   Paleta, Helvetica, margenes, estilos y los helpers p, regla, seccion,
   figura y tabla se importan de 13_informe_pdf.py (importarlo no construye
   nada: su build vive en main()). Lo unico propio es el pie de pagina, porque
   el del TP2 dice "Entregable 2", y tres estilos nuevos (vinetas, nota y
   enlaces).

4. Sin jerga en el cuerpo.
   Los nombres tecnicos aparecen una sola vez, en la nota chica del final. La
   verificacion busca las palabras prohibidas en el texto extraido del PDF y
   cuenta por separado cuerpo y nota.

5. Prohibido el guion largo y el corto de rango (U+2014, U+2013), tambien
   verificado sobre el PDF.
"""

import importlib.util
import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Spacer,
)

LINK_COLAB = "PENDIENTE"
LINK_REPO = "https://github.com/IVillanueva770/factor-d10s-m01"

AQUI = Path(__file__).resolve().parent


def _cargar(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, AQUI / archivo)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tp2 = _cargar("informe_tp2", "13_informe_pdf.py")
nb = _cargar("notebook_tp3", "14_notebook_tp3.py")

S, p, seccion, figura = tp2.S, tp2.p, tp2.seccion, tp2.figura
pct, num, miles = nb.pct, nb.num, nb.miles

RAIZ = tp2.RAIZ
SALIDA = RAIZ / "entregas" / "03-machine-learning" / "TP3_Resumen_El_Factor_D10S.pdf"
ANCHO_UTIL = tp2.ANCHO_UTIL

EM, EN = chr(0x2014), chr(0x2013)  # guion largo y de rango, escritos por codigo
PROHIBIDAS = ["ROC-AUC", "AUC", "boosting", "k-means", "pipeline", "CRISP-DM",
              "leakage", "cross-validation", EM, EN]
MARCA_NOTA = "Nota para lectores técnicos"

# Estilos propios (se agregan al diccionario del TP2, no lo reemplazan).
S["vineta"] = ParagraphStyle(
    "vineta", parent=S["cuerpo"], leftIndent=11, bulletIndent=2,
    spaceAfter=2.6,
)
S["nota"] = ParagraphStyle(
    "nota", fontName="Helvetica", fontSize=7.2, leading=9.6,
    textColor=tp2.TINTA_SUAVE, spaceBefore=2,
)
S["enlace"] = ParagraphStyle(
    "enlace", parent=S["cuerpo"], spaceAfter=1.5,
)


def v(texto):
    """Vineta con punto: la jerarquia la da la sangria, no un numero."""
    return tp2.Paragraph(texto, S["vineta"], bulletText="•")


def fig(nombre, ancho_mm, epigrafe):
    """La figura del TP2 sin su KeepTogether propio, para meterla en el de la
    seccion: anidados, reportlab sobrestima el alto y manda la seccion entera a
    la pagina siguiente aunque entre."""
    return figura(nombre, ancho_mm, epigrafe)._content


def decorado(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(tp2.FONDO)
    canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    canvas.setStrokeColor(tp2.GRIS_GRILLA)
    canvas.setLineWidth(0.4)
    y = tp2.MARGEN_INF - 4 * mm
    canvas.line(tp2.MARGEN_X, y, A4[0] - tp2.MARGEN_X, y)
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(tp2.TINTA_SUAVE)
    canvas.drawString(tp2.MARGEN_X, tp2.MARGEN_INF - 8.4 * mm,
                      "Entregable 3 · Mentoría M01 El Factor D10S "
                      "· Diplomatura en Ciencia de Datos, FAMAF (UNC)")
    total = getattr(doc, "total_paginas", None)
    marca = f"{doc.page} de {total}" if total else f"{doc.page}"
    canvas.drawRightString(A4[0] - tp2.MARGEN_X, tp2.MARGEN_INF - 8.4 * mm, marca)
    canvas.restoreState()


def construir():
    c = nb.cifras()
    tasa_total = c["ssp"] / c["ini"]
    veces = c["prov_max"] / c["prov_min"]
    F = []

    # ------------------------------------------------------------ Pagina 1
    F.append(p("Dónde se concentra el abandono en la secundaria", "titulo"))
    F.append(p("Entregable 3 · Grupo M01 «El Factor D10S» · Lo que aprendimos "
               "al predecir el abandono escolar", "subtitulo"))
    F.append(p(
        "Mentora: Noelia Ferrero &nbsp;·&nbsp; Diplomatura en Ciencia de Datos, "
        "FAMAF (UNC)<br/>"
        "Fuentes: Aprender 2024 y Relevamiento Anual 2024 de escuelas<br/>"
        f"Código, datos y documentación: <font color='#2a78d6'>{LINK_REPO}</font>",
        "meta"))
    F.append(Spacer(1, 8))

    F += seccion(1, "El problema")
    F.append(p(
        "Queremos saber <b>en qué grupos de escuelas secundarias se concentra el "
        "abandono</b>, para que quien tenga que decidir dónde intervenir sepa por "
        f"dónde empezar. Trabajamos con {miles(c['n'])} grupos de escuelas (una "
        "provincia, un departamento, estatal o privado, urbano o rural) que juntan "
        f"a {miles(c['estudiantes'])} estudiantes. En los dos últimos años de la "
        f"secundaria se registraron {miles(c['ssp'])} estudiantes que dejaron la "
        f"escuela sin pasar a otra, sobre {miles(c['ini'])} inscriptos: "
        f"<b>{pct(tasa_total)}</b>. Es un fenómeno chico en el total y muy "
        "desparejo entre lugares. Todo lo que sigue habla de grupos de escuelas, "
        "nunca de un estudiante en particular."))

    F += seccion(2, "Lo que encontramos, en cinco líneas")
    F.append(p(
        "<b>1. Se puede ordenar qué grupos tienen más riesgo de abandono</b> con lo "
        "que los estudiantes cuentan de sí mismos y de sus hogares en Aprender. "
        "Medimos qué tan bien ordena el riesgo en una escala donde 0,5 es un sorteo "
        f"y 1 es perfecto: llegamos a <b>{num(c['auc_log'])}</b>.", "cuerpo_ap"))
    F.append(p(
        "<b>2. Pero casi todo eso ya lo dice la provincia.</b> Con solo saber en qué "
        f"provincia está el grupo se llega a {num(c['auc_prov'])}. El modelo le gana "
        "por muy poco.", "cuerpo_ap"))
    F.append(p(
        "<b>3. Sin conocer la provincia, el perfil de los estudiantes sigue diciendo "
        "algo.</b> Probado en provincias que nunca vio, el modelo llega a "
        f"{num(c['auc_log_pp'])}, contra {num(c['auc_sa_pp'])} de la regla "
        "«estatal o privado, urbano o rural».", "cuerpo_ap"))
    F.append(p(
        "<b>4. Las provincias registran el abandono de forma muy distinta.</b> La "
        f"tasa va de {pct(c['prov_min'], 1)} en {c['prov_min_n']} a "
        f"{pct(c['prov_max'], 1)} en {c['prov_max_n']}, unas {veces:.0f} veces más. "
        "No podemos separar cuánto de eso es abandono real y cuánto es la forma de "
        "completar el registro.", "cuerpo_ap"))
    F.append(p(
        "<b>5. Lo que más acompaña al abandono es lo conocido:</b> hogares de menor "
        "nivel socioeconómico, madres que no terminaron la primaria, haber repetido "
        "y la gestión estatal. Es una asociación entre grupos, no una causa.",
        "cuerpo_ap"))

    F += seccion(3, "Qué significa para quien decide")
    F.append(p(
        "Que lo que los estudiantes cuentan de sus hogares alcanza para señalar "
        "dónde mirar, aunque no explique por qué. Que ese señalamiento sirve "
        "dentro de una provincia y no entre provincias, porque los registros de "
        "abandono de cada una todavía no son comparables. Y que una parte del "
        "problema está en el dato: antes de afinar el modelo, conviene saber cómo "
        "se registra el abandono en cada lugar."))

    F += seccion(4, "Qué haríamos con esto")
    F.append(v(
        "<b>Usarlo para ordenar dónde mirar primero dentro de cada provincia</b>, "
        "no para comparar provincias entre sí: entre provincias, el registro pesa "
        "tanto como el abandono."))
    F.append(v(
        "<b>Antes de cualquier uso, revisar con cada provincia cómo registra las "
        "salidas sin pase</b>, empezando por las que más se apartan de lo esperable "
        "(Buenos Aires y Santa Fe). Es la pregunta que este trabajo no puede cerrar "
        "y la que más cambia el resultado."))
    F.append(v(
        "<b>Dar una segunda mirada a los grupos que el modelo no marca.</b> Entre "
        f"ellos quedan {c['perf_no_vistos']} con abandono alto. El perfil que más "
        "concentra es el de las escuelas estatales urbanas, que es además donde "
        "está la mayor parte de los estudiantes."))
    F.append(v(
        "<b>Sumar el Relevamiento 2025 cuando se publique</b>, para que el abandono "
        "y lo que cuentan los estudiantes hablen del mismo ciclo lectivo."))

    # ------------------------------------------------------------ Detalle
    # Cada seccion con figura viaja entera (titulo, texto que la introduce,
    # figura y epigrafe): con keepWithNext solo, el titulo quedaba huerfano al
    # pie porque el bloque siguiente no entraba y reportlab no los une.
    F.append(KeepTogether(seccion(5, "El modelo contra las reglas simples") + [
        p(
            "Un modelo solo vale si le gana a una regla que cualquiera podría aplicar "
            "sin él. Comparamos dos modelos contra tres reglas: a todos el mismo riesgo "
            "(un sorteo), el riesgo de su combinación de sector y ámbito, y el riesgo "
            "de su provincia. Con todas las provincias a la vista, el mejor modelo "
            f"llega a {num(c['auc_log'])} y la regla de la provincia a "
            f"{num(c['auc_prov'])}: prácticamente empatan. El segundo modelo, más "
            f"complejo, no mejora ({num(c['auc_boost'])}), señal de que el patrón es "
            "simple. La diferencia aparece cuando probamos en provincias que el "
            "modelo nunca vio: ahí la regla de la provincia no tiene nada que decir y "
            f"el modelo conserva {num(c['auc_log_pp'])}."),
        *fig(
            "tp3_a_modelo_vs_reglas.png", 178,
            "Figura 1. Qué tan bien ordena el riesgo cada modelo y cada regla (0,5 es "
            "un sorteo, 1 es perfecto). Azul, los modelos; naranja, las reglas "
            "simples. Izquierda: todas las provincias a la vista. Derecha: probando "
            "en provincias que el modelo no vio."),
    ]))

    F.append(KeepTogether(seccion(6, "Las provincias registran distinto") + [
        p(
            "Los errores del modelo no se reparten parejo entre provincias, y es lo "
            f"más importante que aprendimos. En Buenos Aires hay {c['ba_altos']} "
            f"grupos con abandono alto y el modelo detecta {c['ba_det']}, pero marca "
            f"otros {c['ba_fa']} que el registro da como bajos: por el perfil de sus "
            "estudiantes, esos grupos «deberían» tener más abandono del que figura. "
            f"En Santa Fe pasa al revés: {c['sf_altos']} grupos con abandono alto y "
            f"el modelo detecta {c['sf_det']}. O cada provincia registra distinto, o "
            "hay algo propio de cada una que Aprender no ve. Con estos datos no lo "
            "podemos distinguir, y por eso proponemos revisarlo con ellas antes de "
            "usar el modelo."),
        *fig(
            "tp3_b_tasa_por_provincia.png", 145,
            "Figura 2. Tasa de abandono registrada en los dos últimos años de la "
            "secundaria, por provincia. Naranja, por encima de la media nacional; "
            "azul, por debajo."),
    ]))

    F.append(KeepTogether(seccion(7, "Los grupos que el modelo no marca") + [
        p(
            "La mentora propuso una segunda mirada sobre los grupos que el modelo no "
            "marca como abandono alto. Los agrupamos por seis rasgos parecidos (sin "
            f"usar el abandono para armarlos) y aparecen {c['perf_k']} perfiles. El "
            "privado urbano casi no tiene abandono. Los otros tres (estatal urbano, "
            "rural estatal y rural más vulnerable) tienen tasas parecidas entre sí, "
            f"y entre todos los no marcados quedan {c['perf_no_vistos']} grupos con "
            "abandono alto que el modelo no vio. El perfil que más concentra es el "
        "estatal urbano."),
        *fig(
            "tp3_c_perfiles.png", 178,
            "Figura 3. Los cuatro perfiles de grupos que el modelo no marca. Cada "
            "celda es la proporción del rasgo en el perfil (de 0 a 1); a la derecha, "
            "cuánto abandono registran de verdad."),
    ]))
    F.append(p(
        "<b>Qué acompaña al abandono.</b> Más abandono donde hay más hogares de nivel "
        "socioeconómico bajo, más madres que no terminaron la primaria, más "
        "repitencia, más estudiantes que empezaron el jardín recién en sala de 5, y "
        "en la gestión estatal. Ningún tema por separado es imprescindible: al sacar "
        "uno, los otros lo cubren, porque cuentan la misma historia de desigualdad. "
        "Que algo acompañe al abandono no lo vuelve causa: sirve para saber dónde "
        "mirar, y qué cambiar es otra pregunta."))

    F += seccion(8, "Cómo lo analizamos")
    F.append(p(
        "<b>Dos fuentes que miran cosas distintas.</b> Aprender lo responde el "
        "estudiante el día de la prueba: cuenta cómo le va y cómo vive, pero no puede "
        "ver el abandono, porque el que ya se fue no rinde. El Relevamiento Anual lo "
        "completa cada escuela: cuenta quién se fue, pero no sabe nada de los hogares. "
        "Las unimos por grupo de escuelas, todo en 2024. <b>Qué predecimos:</b> la "
        "tasa de abandono es la cantidad de salidas sin pase de los dos últimos años "
        "dividida por los inscriptos de esos años (la misma población que evalúa "
        "Aprender), y un grupo tiene abandono alto si su tasa está en el cuarto más "
        f"alto del país ({pct(c['corte'])} o más; son {c['positivos']} grupos). "
        "<b>Contra qué nos medimos:</b> las tres reglas simples de la sección 5. "
        "<b>Sin mirar la respuesta:</b> no usamos nada que se conozca después del "
        "resultado (los no promovidos, los pases ni los egresados del mismo año), y "
        "cada grupo lo evaluó un modelo que no lo había visto. <b>Lo que no aportó:</b> "
        "sumar dos indicadores de la Encuesta Permanente de Hogares por provincia, "
        f"como pidió la mentora, deja el resultado en {num(c['auc_eph'])}: lo que dice "
        "de la provincia ya lo dice Aprender."))

    # El cierre viaja entero a la ultima pagina: partido, la nota y los
    # enlaces quedaban solos en una hoja casi vacia.
    cierre = []
    cierre += seccion(9, "Limitaciones")
    cierre.append(v("<b>Grupos, no personas.</b> Nada de esto permite decir algo de un "
               "estudiante concreto."))
    cierre.append(v("<b>El abandono registrado no es el abandono real.</b> Un cero no se "
               "distingue de «no se registró», y las provincias registran muy "
               "distinto."))
    cierre.append(v("<b>Lo que medimos es inestable.</b> De los grupos con abandono alto "
               f"en 2024, solo el {pct(c['est_rep2'], 0)} ya lo tenía el año "
               "anterior: en grupos chicos, una sola salida mueve la tasa entera."))
    cierre.append(v("<b>Probable desfase de un año.</b> El archivo 2024 del Relevamiento "
               "parece traer el ciclo 2023; lo inferimos de los datos y lo dejamos "
               "declarado."))
    cierre.append(v("<b>Aprender solo ve a quien fue a rendir</b>, y eso subestima justo a "
               "los grupos con más abandono."))

    cierre += seccion(10, "Qué sigue")
    cierre.append(v("Sumar el Relevamiento 2025 para que todo hable del mismo ciclo."))
    cierre.append(v("Incorporar el abandono interanual oficial (quién no se reinscribe al "
               "año siguiente), que capta lo que las salidas sin pase no ven."))
    cierre.append(v("Revisar con las provincias cómo registran las salidas sin pase, "
               "empezando por Buenos Aires y Santa Fe."))
    cierre.append(v("Predecir el año siguiente con los datos del anterior, que es lo que "
               "haría un sistema de alerta temprana de verdad."))

    cierre.append(tp2.regla(antes=8, despues=4))
    cierre.append(p(f"Código, datos y documentación: <font color='#2a78d6'>{LINK_REPO}</font>",
               "enlace"))
    cierre.append(p(f"Notebook en Colab: <font color='#2a78d6'>{LINK_COLAB}</font>",
               "enlace"))
    cierre.append(p(
        f"{MARCA_NOTA}: la escala de 0,5 a 1 es el área bajo la curva ROC (ROC-AUC); "
        "los dos modelos son una regresión logística y un boosting de árboles; los "
        "perfiles salen de k-means sobre seis rasgos; la evaluación es una "
        "cross-validation de cinco particiones, estratificada y también agrupada "
        "por provincia, sin leakage de variables posteriores al resultado.", "nota"))
    F.append(KeepTogether(cierre))
    return F


def verificar():
    from pypdf import PdfReader

    lector = PdfReader(str(SALIDA))
    n = len(lector.pages)
    texto = " ".join(pg.extract_text() or "" for pg in lector.pages)
    plano = re.sub(r"\s+", " ", texto)
    corte = plano.find(MARCA_NOTA)
    cuerpo, nota = (plano[:corte], plano[corte:]) if corte >= 0 else (plano, "")
    print(f"  paginas: {n} (maximo 4)")
    print("  palabra              cuerpo  nota")
    for w in PROHIBIDAS:
        patron = re.compile(re.escape(w), re.IGNORECASE)
        etiqueta = {EM: "em-dash", EN: "en-dash"}.get(w, w)
        print(f"  {etiqueta:<20} {len(patron.findall(cuerpo)):>6} "
              f"{len(patron.findall(nota)):>5}")
    sucios = [w for w in PROHIBIDAS
              if re.search(re.escape(w), cuerpo, re.IGNORECASE)]
    raya_nota = [w for w in (EM, EN) if w in nota]
    assert n <= 4, f"el PDF tiene {n} paginas"
    assert not sucios and not raya_nota, f"palabras prohibidas en el cuerpo: {sucios}"


def main():
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(SALIDA), pagesize=A4,
        leftMargin=tp2.MARGEN_X, rightMargin=tp2.MARGEN_X,
        topMargin=tp2.MARGEN_SUP, bottomMargin=tp2.MARGEN_INF,
        title="TP3 Resumen - Grupo M01 El Factor D10S",
        author="Grupo M01 - El Factor D10S",
        subject="Entregable 3, Mentoria M01, Diplomatura en Ciencia de Datos "
                "(FAMAF, UNC)",
    )
    marco = Frame(tp2.MARGEN_X, tp2.MARGEN_INF, ANCHO_UTIL,
                  A4[1] - tp2.MARGEN_SUP - tp2.MARGEN_INF, id="cuerpo",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="base", frames=[marco], onPage=decorado)])
    doc.build(construir())
    doc.total_paginas = doc.page
    doc.build(construir())
    print(f"PDF escrito en {SALIDA} ({doc.total_paginas} paginas)")
    verificar()


if __name__ == "__main__":
    main()
