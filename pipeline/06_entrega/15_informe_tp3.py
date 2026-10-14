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
from fractions import Fraction
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

LINK_COLAB = "https://colab.research.google.com/github/IVillanueva770/factor-d10s-m01/blob/master/entregas/03-machine-learning/TP3_Machine_Learning_El_Factor_D10S.ipynb"
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
# Los nombres tecnicos (curva ROC, boosting, k-means) se permiten desde el 14/10
# porque la seccion 9 los introduce explicados; lo que no entra es jerga suelta.
PROHIBIDAS = ["pipeline", "CRISP-DM", "leakage", "cross-validation", EM, EN]
MAX_PAGINAS = 7

# Integrantes del grupo: los confirma Ignacio.
INTEGRANTES = "Pablo Micheli, Jorge Luis Mira e Ignacio Villanueva"

FUENTES = [
    "Adrogué, C. y Orlicki, E. (2025). Riesgo de abandono escolar en la secundaria. "
    "Factores comunes y diferentes para varones y mujeres. Estudios Económicos 42(85), "
    "58-79. Universidad Nacional del Sur.",
    "Dirección Nacional de Información y Evaluación de la Calidad Educativa (DiNIECE), "
    "Ministerio de Educación, Ciencia y Tecnología (s/f). Definiciones básicas para la "
    "producción de estadísticas educativas.",
    "Dirección de Información y Estadística Educativa (DIEE) (s/f). Bases Usuarias "
    "Relevamiento Anual. Documento metodológico.",
    "Relevamiento Anual 2025. Educación Común. Matrícula y cargos (cuadernillo nacional, "
    "2025).",
    "Subsecretaría de Información y Evaluación Educativa, Ministerio de Capital Humano "
    "(2025). Informe de resultados 2024. Educación Secundaria (Aprender 2024).",
    "Subsecretaría de Información y Evaluación Educativa, Ministerio de Capital Humano "
    "(2024). Caminos interrumpidos: abandono escolar y sobreedad. Historias con datos.",
    "UNICEF Argentina (2022). Encuesta Nacional de Niñas, Niños y Adolescentes. MICS "
    "2019-2020. Informe temático: Adolescencias y educación.",
]
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
S["fuente"] = ParagraphStyle(
    "fuente", fontName="Helvetica", fontSize=7.8, leading=10.2,
    textColor=tp2.TINTA, leftIndent=10, firstLineIndent=-10, spaceAfter=2.2,
)
S["seccion"].spaceAfter = 8
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


def sec(numero, texto):
    """Seccion con mas aire arriba que la del TP2 (pedido de Ignacio, 14/10)."""
    return [Spacer(1, 16), tp2.regla(antes=6, despues=4), p(f"{numero}. {texto}", "seccion")]


def de_cada(x):
    """Lectura de la escala en llano: 0,75 es "3 de cada 4" (fraccion mas
    cercana con denominador chico, sacada del mismo numero que se muestra)."""
    f = Fraction(round(x, 2)).limit_denominator(5)
    return f"{f.numerator} de cada {f.denominator}"


def construir():
    c = nb.cifras()
    tasa_total = c["ssp"] / c["ini"]
    # Robustez del corte: el texto dice "en los dos casos, X contra Y"; se
    # chequea que el tercio y el quinto den lo mismo a dos decimales.
    if (num(c["auc_t_log"]), num(c["auc_t_prov"])) != (num(c["auc_q_log"]),
                                                       num(c["auc_q_prov"])):
        raise SystemExit("El tercio y el quinto ya no dan lo mismo: revisar la "
                         "seccion 5")
    if num(c["auc_eph"]) != num(c["auc_log"]):
        raise SystemExit("Sumar la EPH ya cambia la regresion logistica: revisar la "
                         "seccion 9")
    F = []

    # ------------------------------------------------------------ Pagina 1
    F.append(p("Dónde se concentra el abandono en la secundaria argentina", "titulo"))
    F.append(p(
        f"Cruzamos lo que {miles(c['estudiantes'])} estudiantes contaron en las "
        "Pruebas Aprender con los chicos que sus escuelas registraron como abandono. "
        "Entregable 3 del grupo M01, \u201cEl Factor D10S\u201d.", "subtitulo"))
    F.append(p(
        f"Integrantes: {INTEGRANTES}<br/>"
        "Mentora: Noelia Ferrero &nbsp;·&nbsp; Mentoría de la Diplomatura en Ciencia "
        "de Datos, FAMAF (UNC), 2026", "meta"))
    F.append(Spacer(1, 6))

    F += sec(1, "El problema y los datos")
    F.append(p(
        "Queremos saber <b>en qué grupos de escuelas secundarias se concentra el "
        "abandono</b>, para que quien tenga que decidir dónde intervenir sepa por "
        "dónde empezar. Usamos dos fuentes públicas del Ministerio de Educación que "
        "miran cosas distintas. Las <b>Pruebas Aprender</b> son la evaluación nacional "
        "que rinden los estudiantes del último año: además de la prueba, responden un "
        "cuestionario sobre su hogar, su trayectoria y su escuela. El <b>Relevamiento "
        "Anual</b> es el formulario que cada escuela completa todos los años: cuenta "
        "cuántos chicos se inscribieron, cuántos pasaron de año y cuántos se fueron. "
        "Aprender no puede ver el abandono, porque el que ya dejó no va a rendir; el "
        "Relevamiento sí, pero no sabe nada de los hogares. La <b>Encuesta "
        "Permanente de Hogares</b> (EPH, la encuesta oficial del INDEC sobre empleo "
        "e ingresos de los hogares) tampoco sirve para medir el abandono acá: no se "
        "puede unir a estos grupos, porque solo llega a provincia, y su dato es de "
        "2025."))
    F.append(p(
        "La pregunta de partida era qué estudiante abandona, pero "
        "Aprender no se publica estudiante por estudiante sino por <b>grupo de "
        "escuelas</b>: un departamento de una provincia, separando escuelas estatales "
        f"y privadas, urbanas y rurales. Son {miles(c['n'])} grupos con "
        f"{miles(c['estudiantes'])} estudiantes, y todo lo que sigue habla de esos "
        "grupos, nunca de un chico en particular. Llamamos <b>perfil</b> de un grupo "
        "a lo que cuentan sus estudiantes en Aprender sobre su hogar, su trayectoria "
        "y su escuela. Como abandono usamos "
        "las <b>salidas sin pase</b>: estudiantes que dejaron la escuela sin "
        "inscribirse en otra. En los dos últimos años de la secundaria fueron "
        f"{miles(c['ssp'])} sobre {miles(c['ini'])} inscriptos, el "
        f"<b>{pct(tasa_total)}</b>: poco en el total y muy desparejo entre lugares. "
        "Decimos que un grupo tiene <b>abandono alto</b> si está en el cuarto de "
        f"grupos con la tasa más alta del país ({pct(c['corte'])} o más)."))

    F += sec(2, "Lo que encontramos, en cinco líneas")
    F.append(p(
        "Probamos dos modelos que miran solo el perfil (una regresión logística y "
        "otro de árboles combinados) y un tercero que además conoce la provincia. "
        "Cuando decimos <b>el modelo</b> hablamos de la regresión logística con el "
        "perfil solo. Para medirlos usamos una escala de qué tan bien ordenan los "
        "grupos de más a menos riesgo: <b>0,5 es lo que lograría un sorteo y 1 es "
        f"ordenarlos perfecto</b>. {num(c['auc_log'])} quiere decir que si tomamos un "
        "grupo con abandono alto y uno sin, el modelo pone primero al de abandono "
        f"alto {de_cada(c['auc_log'])} veces (y {num(c['auc_pyp_log'])}, "
        f"{de_cada(c['auc_pyp_log'])}). Además, el modelo <b>marca</b> como de riesgo "
        f"al cuarto de grupos que pone más arriba: de los {c['altos_tot']} grupos con "
        f"abandono alto encuentra {c['det_tot']} ({pct(c['recall_tot'], 0)}), y de "
        f"sus {c['marcas_tot']} marcas aciertan {c['det_tot']} "
        f"({pct(c['prec_tot'], 0)}).", "cuerpo"))
    F.append(p(
        "<b>1. Con el perfil de los estudiantes se puede ordenar qué grupos tienen "
        f"más riesgo de abandono:</b> el modelo llega a <b>{num(c['auc_log'])}</b>.",
        "cuerpo_ap"))
    F.append(p(
        "<b>2. La provincia y el perfil aportan información distinta.</b> Con solo "
        f"saber en qué provincia está el grupo se llega a {num(c['auc_prov'])}, lo "
        "mismo que con el perfil. Juntos llegan a "
        f"<b>{num(c['auc_pyp_log'])}</b>: lo que sabe uno no lo sabe el otro.",
        "cuerpo_ap"))
    F.append(p(
        "<b>3. Sin conocer la provincia, el perfil dice poco más que la regla "
        "simple.</b> Probado en provincias que nunca vio, el modelo llega a "
        f"{num(c['auc_log_pp'])}, contra {num(c['auc_sa_pp'])} de mirar solo si la "
        "escuela es estatal o privada, urbana o rural. La diferencia "
        f"({num(c['auc_log_pp'] - c['auc_sa_pp'])}) es menor que lo que varía el "
        f"resultado de una prueba a otra ({num(c['auc_log_pp_desv'])}).",
        "cuerpo_ap"))
    F.append(p(
        "<b>4. El abandono registrado cambia mucho de una provincia a otra:</b> de "
        f"{pct(c['prov_min'])} en {c['prov_min_n']} a {pct(c['prov_max'])} en "
        f"{c['prov_max_n']}, unas {c['prov_veces']:.0f} veces más. Creemos que una "
        "parte es la forma de completar el registro y no abandono real, pero es una "
        "hipótesis nuestra: el área de estadística del Ministerio de Educación "
        "sostiene que el dato es comparable entre provincias.", "cuerpo_ap"))
    F.append(p(
        "<b>5. Lo que más acompaña al abandono coincide en buena parte con lo que ya "
        "documenta la investigación en Argentina:</b> hogares de nivel "
        "socioeconómico bajo, madres que no terminaron la primaria, haber repetido, "
        "tener más edad de la que corresponde al año, haber empezado el jardín "
        "recién en sala de 5 y la escuela estatal (sección 6). Es una asociación "
        "entre grupos, no una causa.", "cuerpo_ap"))

    F += sec(3, "Qué significa para quien decide")
    F.append(p(
        "Que lo que los estudiantes cuentan de sus hogares sirve para ordenar dónde "
        "mirar, también dentro de una misma provincia, aunque no explique por qué "
        "pasa. Sumarle la provincia ordena mejor, pero no sabemos cuánto de lo que "
        "aporta la provincia es abandono y cuánto es la forma de registrarlo: antes "
        "de usarla para comparar provincias entre sí, conviene saber cómo registra "
        "el abandono cada una."))

    F += sec(4, "Qué haríamos con esto")
    F.append(v(
        "<b>Mientras no se revise cómo registra cada provincia, usar el perfil para "
        "ordenar dentro de cada provincia</b>, y tomar la provincia como un dato a "
        "revisar. Es una señal modesta, pero es la única que no depende de cómo "
        "registra cada provincia: si el abandono alto se define dentro de cada provincia (el cuarto "
        "de sus grupos con la tasa más alta), el perfil ordena en "
        f"{num(c['auc_cp_log'])}, contra {num(c['auc_cp_sa'])} de la regla "
        "estatal/privado y urbano/rural."))
    F.append(v(
        "<b>Antes de comparar provincias, revisar con ellas cómo registran las "
        "salidas sin pase</b>, empezando por las que más se apartan de lo que predice "
        "el modelo (Buenos Aires y Santa Fe)."))
    F.append(v(
        "<b>Dar una segunda mirada a los grupos que el modelo no marca:</b> entre "
        f"ellos quedan {c['no_det']} de los {c['altos_tot']} con abandono alto, "
        f"{c['perf_top_nv']} en escuelas estatales urbanas y {c['perf_rural_nv']} "
        "en estatales rurales (sección 8)."))

    # ------------------------------------------------------------ Detalle
    F.append(KeepTogether(sec(5, "El modelo contra las reglas simples") + [
        p(
            "Un modelo solo vale si le gana a una regla que cualquiera podría aplicar "
            "sin él. Por eso comparamos los modelos contra tres reglas: darle a todos "
            "el mismo riesgo (un sorteo), darle a cada grupo el riesgo promedio de los "
            "grupos de su mismo tipo (estatal o privado, urbano o rural), y darle el "
            "riesgo promedio de su provincia. Con todas las provincias a la vista, el "
            f"modelo llega a {num(c['auc_log'])} y la regla de la provincia a "
            f"{num(c['auc_prov'])}: empatan. El de árboles combinados, más complejo, "
            f"no mejora ({num(c['auc_boost'])}), señal de que el patrón es simple. "
            "Pero empatar no es saber lo mismo: el modelo que conoce la provincia y el "
            f"perfil a la vez llega a <b>{num(c['auc_pyp_log'])}</b> (la barra de "
            "arriba de la figura 1). Si la provincia solo resumiera el perfil de sus "
            "estudiantes, sumarla no agregaría nada."),
        p(
            "Sin la provincia, el perfil dice poco: si probamos el modelo en "
            "provincias que no usó para aprender, la regla de la provincia queda sin "
            f"nada que decir y el modelo llega a {num(c['auc_log_pp'])}, apenas por "
            "encima de la regla estatal/privado y urbano/rural "
            f"({num(c['auc_sa_pp'])}). Elegir el cuarto de "
            "grupos con más abandono como \u201calto\u201d fue decisión nuestra, así que lo "
            "movimos al tercio y al quinto: el perfil solo y la provincia sola siguen "
            f"parejos (en los dos casos, {num(c['auc_t_log'])} contra "
            f"{num(c['auc_t_prov'])})."),
        *fig(
            "tp3_a_modelo_vs_reglas.png", 178,
            "Figura 1. Qué tan bien ordena el riesgo cada modelo y cada regla (0,5 es "
            "un sorteo, 1 es perfecto). Azul, los modelos; naranja, las reglas "
            "simples. Izquierda: el modelo aprende y se prueba con todas las "
            "provincias. Derecha: se prueba en provincias que no vio. La línea fina en "
            "la punta de cada barra muestra cuánto varía el resultado de una prueba a "
            "otra."),
    ]))

    F += sec(6, "Qué acompaña al abandono, y qué ya se sabía")
    F.append(p(
        "En nuestros datos hay más abandono donde hay más hogares de nivel "
        "socioeconómico bajo, más madres que no terminaron la primaria, más "
        "estudiantes que repitieron o que tienen más edad de la que corresponde al "
        "año, más que empezaron el jardín recién en sala de 5, y en las escuelas "
        "estatales. No lo dimos por sentado: buscamos qué dice la investigación "
        "previa."))
    F.append(v(
        "<b>Nivel socioeconómico y escuela estatal: documentado.</b> Un estudio de "
        "Adrogué y Orlicki (2025), que siguió veinte años de la Encuesta Permanente "
        "de Hogares del INDEC, encuentra más riesgo de abandono en los hogares más "
        "pobres y en las escuelas de gestión estatal."))
    F.append(v(
        "<b>Educación de la madre: documentado.</b> La encuesta de UNICEF Argentina "
        "sobre adolescencias (2022) lo muestra como \u201cclima educativo del hogar\u201d. "
        "Ojo: en Aprender 2024 el índice de nivel socioeconómico ya incluye la "
        "educación de la madre, así que en nuestros datos no son dos señales "
        "independientes."))
    F.append(v(
        "<b>Repitencia y sobreedad: documentado con dato oficial.</b> El área de "
        "estadística del Ministerio de Educación mostró en 2024 un abandono del 27% "
        "entre quienes tienen sobreedad contra 4,5% entre quienes no (con otra forma "
        "de medir el abandono, que sigue a cada estudiante a lo largo de los años, "
        "en 11 provincias)."))
    F.append(v(
        "<b>Jardín desde sala de 3: documentado en parte.</b> El informe nacional de "
        "Aprender 2024 lo asocia a mejores aprendizajes, pero no encontramos una "
        "fuente argentina que lo mida contra el abandono."))
    F.append(p(
        "Ningún tema por separado es imprescindible para el modelo: al sacar uno, los "
        "otros lo cubren, porque todos cuentan la misma desigualdad. Y que algo "
        "acompañe al abandono no lo vuelve causa: sirve para saber dónde mirar; qué "
        "cambiar es otra pregunta."))

    F.append(KeepTogether(sec(7, "Abandono o forma de registrar") + [
        p(
            "Los errores del modelo no se reparten parejo entre provincias. En Buenos "
            f"Aires hay {c['ba_altos']} grupos con abandono alto y el modelo detecta "
            f"{c['ba_det']}, pero marca otros {c['ba_fa']} que el registro da como "
            "bajos: por el perfil de sus estudiantes, esos grupos \u201cdeberían\u201d tener más "
            f"abandono del que figura. En Santa Fe pasa al revés: {c['sf_altos']} "
            f"grupos con abandono alto y el modelo detecta {c['sf_det']}. O cada "
            "provincia registra distinto, o hay algo propio de cada una que Aprender "
            "no ve; con estos datos no lo podemos distinguir."),
        p(
            "<b>Que el registro cambie entre provincias es una hipótesis nuestra.</b> "
            "El área de estadística del Ministerio de Educación, que administra el "
            "Relevamiento, sostiene lo contrario: que su sistema "
            "\u201cgarantiza la homogeneidad y comparabilidad de los datos en todo el "
            "ámbito nacional\u201d. No encontramos ningún documento oficial que advierta "
            "diferencias. Nos apoyamos en la distancia entre provincias y en la caída "
            f"de Buenos Aires, que con la secundaria entera pasa de "
            f"{pct(c['ba_tasa_ini'])} en {c['ba_anio_ini']} a {pct(c['ba_tasa_fin'])} "
            f"en {c['ba_anio_fin']}. Por eso proponemos revisarlo con las provincias "
            "antes de compararlas."),
        *fig(
            "tp3_b_tasa_por_provincia.png", 135,
            "Figura 2. Abandono registrado en los dos últimos años de la secundaria, "
            "por provincia. Naranja, por encima de la media nacional; azul, por "
            "debajo."),
    ]))

    F.append(KeepTogether(sec(8, "Los grupos que el modelo no marca") + [
        p(
            "La mentora propuso una segunda mirada: dentro de los grupos que el modelo "
            "no marca como abandono alto, ¿hay perfiles distintos? Los agrupamos por "
            "seis rasgos (nivel socioeconómico, educación de la madre, repitencia, "
            "desempeño en matemática, sector y ámbito), sin usar el abandono para "
            f"armarlos, y aparecen {c['perf_k']} perfiles. El privado urbano casi no "
            "tiene abandono. Los otros tres (estatal urbano, rural estatal y rural más "
            "vulnerable) tienen tasas parecidas entre sí. Entre todos los no marcados "
            f"quedan {c['no_det']} de los {c['altos_tot']} grupos con abandono alto: "
            f"{c['perf_top_nv']} ({pct(c['perf_top_nv_pct'], 0)}) en el estatal "
            f"urbano y {c['perf_rural_nv']} entre los dos rurales."),
        *fig(
            "tp3_c_perfiles.png", 178,
            "Figura 3. Los cuatro perfiles de grupos que el modelo no marca. Cada "
            "celda es el porcentaje del perfil que tiene ese rasgo; a la derecha, "
            "cuánto abandono registran."),
        p(
            "<b>Para quien decide:</b> el estatal urbano junta más casos por su tamaño "
            f"(reúne el {pct(c['perf_top_est'], 0)} de los estudiantes de estos "
            "grupos); el rural más vulnerable tiene la tasa más alta."),
    ]))

    F += sec(9, "Cómo lo analizamos")
    F.append(p(
        "<b>Qué predecimos.</b> Si un grupo tiene abandono alto, con la regla de la "
        "sección 1. Para la definición de salida sin pase usamos la oficial del área "
        "de estadística del Ministerio de Educación: "
        "\u201cel que se va de la "
        "escuela a la que asistía, sin inscripción (o pase) en otra escuela\u201d. Tomamos "
        "los dos últimos años porque son los que evalúa Aprender."))
    F.append(p(
        "<b>Con qué modelos.</b> Una regresión logística, que estima la probabilidad "
        "de abandono alto sumando el peso de cada variable y se puede leer, y un "
        "modelo de árboles combinados (boosting), que capta relaciones no lineales. "
        "La escala de 0,5 a 1 con la que los comparamos es el área bajo la curva ROC. "
        "Los perfiles de la sección 8 salen de un agrupamiento k-means."))
    F.append(p(
        "<b>Qué acompaña al abandono.</b> La lista de las secciones 2 y 6 no sale de "
        "los pesos de la regresión: miramos la correlación de cada respuesta con la "
        "tasa de abandono, para ver hacia dónde empuja, y cuánto empeora el modelo al "
        "sacar cada tema, para ver cuánto aporta."))
    F.append(p(
        "<b>Sin mirar la respuesta.</b> Cada grupo lo evaluó un modelo que no lo había "
        "visto: partimos los datos en cinco y cada parte se predijo con lo aprendido "
        "de las otras cuatro. No usamos nada que se conozca después del abandono (los "
        "que no pasaron de año, los pases ni los egresados del mismo año)."))
    F.append(p(
        "<b>La encuesta de hogares.</b> Como pidió la mentora, probamos sumar dos "
        "indicadores de la EPH por provincia: el ingreso per cápita mediano del hogar "
        "y la proporción de adultos sin secundaria completa. Con la regresión "
        f"logística no cambia ({num(c['auc_eph'])}), pero con árboles combinados "
        f"sube de {num(c['auc_boost'])} a {num(c['auc_eph_b'])}: dos datos por "
        "provincia alcanzan para que el modelo reconozca la provincia, que es la "
        "información que el perfil no tiene."))

    cierre = []
    cierre += sec(10, "Limitaciones")
    cierre.append(v("<b>Grupos, no personas.</b> Nada de esto permite decir algo de un "
                    "estudiante concreto."))
    cierre.append(v("<b>El abandono registrado no es el abandono real.</b> Un cero no se "
                    "distingue de \u201cno se registró\u201d, y hay muchos: "
                    f"{miles(c['ceros'])} de los {miles(c['n'])} grupos "
                    f"({pct(c['ceros_pct'], 0)}) no tienen ninguna salida registrada. "
                    "Que la diferencia entre provincias sea por cómo registra cada una "
                    "es una hipótesis nuestra (sección 7)."))
    cierre.append(v("<b>Lo que el registro no cuenta y lo que cuenta de más.</b> Quien se "
                    "va entre diciembre y marzo, después del último día de clase, no "
                    "figura como salida sin pase, según el formulario 2025 del "
                    "Relevamiento; y la categoría incluye a quienes siguen en otra escuela "
                    "sin haber hecho el trámite del pase."))
    cierre.append(v("<b>Un año de diferencia.</b> El Relevamiento de cada año informa las "
                    "salidas del ciclo anterior: el de 2024 trae las de 2023, y Aprender "
                    "es de octubre de 2024. Es decir, el perfil se midió después del "
                    "abandono con el que lo comparamos: esto ordena, no anticipa. "
                    "Anticipar es el próximo paso."))
    cierre.append(v("<b>Lo que medimos es inestable.</b> De los grupos con abandono alto "
                    f"en el Relevamiento 2024, solo el {pct(c['est_rep2'], 0)} lo tenía "
                    f"en el anterior (por azar sería el {pct(c['prev'], 0)}): en grupos "
                    "chicos, una sola salida mueve la tasa."))
    cierre.append(v("<b>El modelo detecta peor a los grupos más grandes.</b> En el quinto "
                    "de grupos más grandes encuentra el "
                    f"{pct(c['rec_grandes'], 0)} de los que tienen abandono alto, contra "
                    f"el {pct(c['rec_chicos'], 0)} en el quinto más chico: ahí las tasas "
                    "son más bajas y parejas, y lo poco que pasa queda diluido."))
    cierre.append(v("<b>Aprender solo ve a quien fue a rendir</b>, y eso subestima justo a "
                    "los grupos con más abandono."))

    cierre += sec(11, "Próximos pasos")
    cierre.append(v("Sumar el Relevamiento 2025, que trae el abandono del ciclo 2024, el "
                    "mismo año de Aprender."))
    cierre.append(v("Incorporar el abandono interanual oficial (quiénes no se reinscriben "
                    "al año siguiente), que capta lo que las salidas sin pase no ven."))
    cierre.append(v("Revisar con las provincias cómo registran las salidas sin pase, "
                    "empezando por Buenos Aires y Santa Fe."))
    cierre.append(v("Predecir el año siguiente con los datos del anterior, que es lo que "
                    "haría un sistema de alerta temprana."))
    cierre.append(tp2.regla(antes=8, despues=4))
    cierre.append(p(
        "El notebook que reproduce todo, el código y la lista completa de fuentes con "
        "sus citas textuales y enlaces están en el repositorio del proyecto: "
        f"<a href='{LINK_REPO}' color='#2a78d6'>github.com/IVillanueva770/factor-d10s-m01</a>. "
        f"El notebook se puede <a href='{LINK_COLAB}' color='#2a78d6'>abrir y correr en "
        "Colab</a> sin instalar nada.", "enlace"))
    F.append(KeepTogether(cierre))

    F += sec(12, "Fuentes")
    for ref in FUENTES:
        F.append(p(ref, "fuente"))
    return F


def verificar():
    from pypdf import PdfReader

    lector = PdfReader(str(SALIDA))
    n = len(lector.pages)
    texto = " ".join(pg.extract_text() or "" for pg in lector.pages)
    plano = re.sub(r"\s+", " ", texto)
    corte = plano.find("12. Fuentes")
    cuerpo, nota = (plano[:corte], plano[corte:]) if corte >= 0 else (plano, "")
    print(f"  paginas: {n} (maximo {MAX_PAGINAS})")
    if INTEGRANTES == "PENDIENTE":
        print("  AVISO: faltan los nombres de los integrantes (INTEGRANTES)")
    print("  palabra              cuerpo  fuentes")
    for w in PROHIBIDAS:
        patron = re.compile(re.escape(w), re.IGNORECASE)
        etiqueta = {EM: "em-dash", EN: "en-dash"}.get(w, w)
        print(f"  {etiqueta:<20} {len(patron.findall(cuerpo)):>6} "
              f"{len(patron.findall(nota)):>5}")
    sucios = [w for w in PROHIBIDAS
              if re.search(re.escape(w), cuerpo, re.IGNORECASE)]
    raya_nota = [w for w in (EM, EN) if w in nota]
    assert n <= MAX_PAGINAS, f"el PDF tiene {n} paginas"
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
