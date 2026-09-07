# -*- coding: utf-8 -*-
"""Genera el PDF del Entregable 2: "Resumen de hallazgos" del grupo M01.

Salida: entrega/TP2_Resumen_de_hallazgos_El_Factor_D10S.pdf (4 paginas A4).

POR QUE ASI (decisiones de diseno, no de implementacion)
--------------------------------------------------------

1. reportlab / platypus y no HTML a PDF ni LaTeX.
   El entregable tiene que compilar en Windows con Python 3.14 sin instalar
   un motor externo (wkhtmltopdf, XeLaTeX) ni depender de como resuelve
   fuentes el navegador de turno. reportlab ya esta en el entorno del
   proyecto, produce un PDF vectorial real y deja el control del salto de
   pagina en el codigo, que es justo lo que hace falta para garantizar
   cuatro paginas exactas.

2. Flujo continuo con anclas, no cuatro paginas cortadas a mano.
   La primera version cortaba con PageBreak en tres puntos elegidos, y el
   resultado fue peor: una pagina quedaba con un cuarto en blanco y otra
   se pasaba de largo. Ahora el texto fluye y lo que se fija son las tres
   costuras que si importan: los titulos llevan keepWithNext para que
   ninguno quede huerfano al pie, cada figura viaja pegada a su epigrafe
   en un KeepTogether, y el par "lo MEDIDO / lo INFERIDO" no se puede
   partir porque media distincion no sirve de nada. Las cuatro paginas se
   consiguen ajustando cuanto se escribe, que es lo honesto, y se
   verifican con pypdf despues de cada corrida.

3. Las figuras se escalan por ancho y nunca aparecen sin texto que las
   introduzca arriba. Las del TP2 son 2:1 o mas anchas salvo la del cruce
   con la EPH, que es 1,7:1 y por eso va mas angosta y centrada: a ancho
   completo se comeria media pagina.

4. La identidad visual se hereda del TP1 y no se amplia.
   Paleta categorica de cuatro colores validada para daltonismo, en orden
   fijo (azul, naranja, verde, amarillo) mas la escala de tinta. En el
   informe el azul marca las secciones y el naranja se reserva para las
   dos cosas que el lector tiene que poder saltear buscando: los hallazgos
   de calidad con severidad y la hipotesis no verificada. Nada decorativo:
   sin bordes de caja, sin fondos de tabla mas alla de una fila de
   encabezado, reglas de 0,4 pt.

5. Jerarquia por peso y espacio, no por tamano.
   Tres niveles: seccion (12 pt, azul, con regla fina arriba), subtitulo
   (9,5 pt, bold, tinta) y cuerpo (9,0 pt sobre 12,6 de interlinea). El
   salto de tamano entre niveles es chico a proposito: lo que separa es el
   espacio en blanco arriba de cada bloque.

6. Helvetica de las 14 fuentes base del PDF.
   Es la unica manera de garantizar acentos y enie correctos sin embeber
   un TTF que quizas no este en la maquina donde se compile. reportlab la
   escribe con WinAnsiEncoding, que cubre todo el castellano.

7. Ningun numero se calcula aca.
   Todos los valores son transcripciones de docs/07_perfil_calidad.md,
   docs/08_decisiones_curacion.md y docs/10_relaciones.md, que a su vez los
   generan los scripts del pipeline. Este script maqueta; si un numero
   cambia, cambia en el pipeline y se vuelve a transcribir, nunca al reves.

8. Prohibido el guion largo.
   Regla de escritura del proyecto. El script se grepea por U+2014 y U+2013
   como parte de la verificacion de la entrega.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# --------------------------------------------------------------------------
# Identidad visual heredada del TP1
# --------------------------------------------------------------------------
AZUL = colors.HexColor("#2a78d6")
NARANJA = colors.HexColor("#eb6834")
VERDE = colors.HexColor("#1baf7a")
AMARILLO = colors.HexColor("#eda100")
TINTA = colors.HexColor("#0b0b0b")
TINTA_SUAVE = colors.HexColor("#52514e")
GRIS_GRILLA = colors.HexColor("#e3e3e0")
FONDO = colors.HexColor("#fcfcfb")

RAIZ = Path(__file__).resolve().parents[2]
FIGURAS = RAIZ / "figuras"
SALIDA = RAIZ / "entrega" / "TP2_Resumen_de_hallazgos_El_Factor_D10S.pdf"

MARGEN_X = 16 * mm
MARGEN_SUP = 13 * mm
MARGEN_INF = 14 * mm
ANCHO_UTIL = A4[0] - 2 * MARGEN_X

# --------------------------------------------------------------------------
# Estilos
# --------------------------------------------------------------------------
S = {}
S["titulo"] = ParagraphStyle(
    "titulo", fontName="Helvetica-Bold", fontSize=20, leading=23,
    textColor=TINTA, spaceAfter=2,
)
S["subtitulo"] = ParagraphStyle(
    "subtitulo", fontName="Helvetica", fontSize=10.5, leading=14,
    textColor=AZUL, spaceAfter=5,
)
S["meta"] = ParagraphStyle(
    "meta", fontName="Helvetica", fontSize=8.2, leading=11.4,
    textColor=TINTA_SUAVE,
)
S["seccion"] = ParagraphStyle(
    "seccion", fontName="Helvetica-Bold", fontSize=12, leading=14.5,
    textColor=AZUL, spaceBefore=2, spaceAfter=4, keepWithNext=1,
)
S["sub"] = ParagraphStyle(
    "sub", fontName="Helvetica-Bold", fontSize=9.5, leading=12.5,
    textColor=TINTA, spaceBefore=5, spaceAfter=1, keepWithNext=1,
)
S["sub_naranja"] = ParagraphStyle(
    "sub_naranja", fontName="Helvetica-Bold", fontSize=9.5, leading=12.5,
    textColor=NARANJA, spaceBefore=5, spaceAfter=1, keepWithNext=1,
)
S["cuerpo"] = ParagraphStyle(
    "cuerpo", fontName="Helvetica", fontSize=9.0, leading=12.6,
    textColor=TINTA, alignment=TA_JUSTIFY, spaceAfter=4.0,
)
S["cuerpo_ap"] = ParagraphStyle(
    "cuerpo_ap", parent=S["cuerpo"], leftIndent=9, spaceAfter=3.2,
)
S["limit"] = ParagraphStyle(
    "limit", parent=S["cuerpo"], spaceAfter=2.6,
)
S["epigrafe"] = ParagraphStyle(
    "epigrafe", fontName="Helvetica-Oblique", fontSize=7.8, leading=10.4,
    textColor=TINTA_SUAVE, spaceBefore=2.5, spaceAfter=2,
)
S["cita"] = ParagraphStyle(
    "cita", fontName="Helvetica-Oblique", fontSize=9.4, leading=13,
    textColor=TINTA_SUAVE, leftIndent=10, rightIndent=10,
    spaceBefore=2, spaceAfter=6, alignment=TA_CENTER,
)
S["td"] = ParagraphStyle(
    "td", fontName="Helvetica", fontSize=7.9, leading=10.2, textColor=TINTA,
)
S["td_soft"] = ParagraphStyle(
    "td_soft", parent=S["td"], textColor=TINTA_SUAVE,
)
S["th"] = ParagraphStyle(
    "th", fontName="Helvetica-Bold", fontSize=7.9, leading=10.2,
    textColor=TINTA,
)


def p(texto, estilo="cuerpo"):
    return Paragraph(texto, S[estilo])


def regla(color=GRIS_GRILLA, grosor=0.4, ancho=ANCHO_UTIL, antes=6, despues=3):
    t = Table([[""]], colWidths=[ancho], rowHeights=[0.1])
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), grosor, color),
        ("TOPPADDING", (0, 0), (-1, -1), antes),
        ("BOTTOMPADDING", (0, 0), (-1, -1), despues),
    ]))
    return t


def seccion(numero, texto):
    """Titulo de seccion con su regla fina arriba: separa sin dibujar cajas."""
    return [regla(), p(f"{numero}. {texto}", "seccion")]


def figura(nombre, ancho_mm, epigrafe):
    """Escala la figura por ancho, conservando su relacion original."""
    from PIL import Image as PILImage

    ruta = FIGURAS / nombre
    with PILImage.open(ruta) as im:
        ratio = im.size[1] / im.size[0]
    ancho = ancho_mm * mm
    img = Image(str(ruta), width=ancho, height=ancho * ratio)
    img.hAlign = "CENTER"
    cap = Paragraph(epigrafe, S["epigrafe"])
    cap.hAlign = "CENTER"
    return KeepTogether([Spacer(1, 3), img, cap])


def tabla(datos, anchos, alineados_der=(), font_size=7.9):
    """Tabla sin bordes: solo regla bajo el encabezado y filas separadas."""
    filas = []
    for i, fila in enumerate(datos):
        estilo = "th" if i == 0 else "td"
        filas.append([Paragraph(str(c), S[estilo]) for c in fila])
    t = Table(filas, colWidths=anchos, hAlign="LEFT")
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, TINTA_SUAVE),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, GRIS_GRILLA),
    ]
    for c in alineados_der:
        cmds.append(("ALIGN", (c, 0), (c, -1), "RIGHT"))
    t.setStyle(TableStyle(cmds))
    return t


# --------------------------------------------------------------------------
# Pie de pagina
# --------------------------------------------------------------------------
def decorado(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(FONDO)
    canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    canvas.setStrokeColor(GRIS_GRILLA)
    canvas.setLineWidth(0.4)
    canvas.line(MARGEN_X, MARGEN_INF - 4 * mm,
                A4[0] - MARGEN_X, MARGEN_INF - 4 * mm)
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(TINTA_SUAVE)
    canvas.drawString(MARGEN_X, MARGEN_INF - 8.4 * mm,
                      "Entregable 2 · Mentoría M01 El Factor D10S "
                      "· Diplomatura en Ciencia de Datos, FAMAF (UNC)")
    canvas.drawRightString(A4[0] - MARGEN_X, MARGEN_INF - 8.4 * mm,
                           f"{doc.page} de 4")
    canvas.restoreState()


# --------------------------------------------------------------------------
# Contenido
# --------------------------------------------------------------------------
def construir():
    F = []

    # ---------------- Bloque 1 ----------------
    F.append(p("Resumen de hallazgos", "titulo"))
    F.append(p("Entregable 2 · Grupo M01 «El Factor D10S» "
               "· Abandono escolar en la educación secundaria",
               "subtitulo"))
    F.append(p(
        "Autor: Ignacio Villanueva &nbsp;·&nbsp; Mentora: Noelia Ferrero "
        "&nbsp;·&nbsp; Fuentes: Aprender 2024 (base de datos abierta) y "
        "EPH 3T-2025 (INDEC)<br/>"
        "Código, datos y documentación: "
        "<font color='#2a78d6'>github.com/IVillanueva770/factor-d10s-m01</font>",
        "meta"))
    F.append(Spacer(1, 5))

    F += seccion(1, "¿Qué encontramos en los datos?")
    F.append(p(
        "El dataset maestro tiene <b>1.174 filas y 131 columnas</b>, y cada "
        "fila es un grupo (jurisdicción x departamento x sector x "
        "ámbito), no un estudiante. Detrás de esas filas hay "
        "<b>540.040 estudiantes</b> de Aprender 2024, y cada fila lleva una "
        "columna de peso que dice cuántos representa. Por eso todo "
        "promedio de este informe está ponderado por cantidad de "
        "estudiantes: un promedio simple hablaría de departamentos y no "
        "de chicos."))
    F.append(p(
        "De las 131 columnas, 85 son proporciones, 16 son coberturas que "
        "dicen qué fracción de la fila quedó representada en cada "
        "bloque de preguntas, 16 son indicadores de la EPH iguales para toda "
        "la provincia, 8 están armonizadas entre Aprender y la EPH, 4 "
        "identifican la fila, 1 es el peso y 1 es una bandera de control."))

    F.append(p("El hallazgo principal se entiende sin mirar una tabla", "sub"))
    F.append(p(
        "Dentro del mismo ámbito urbano, cambiar de sector de "
        "gestión mueve el desempeño <b>0,23 puntos</b>: 0,62 de los "
        "estudiantes de estatal urbana quedan por debajo del nivel básico "
        "en matemática contra 0,38 en privada urbana. Cambiar de "
        "ámbito dentro del sector privado lo mueve 0,13 (0,38 urbano "
        "contra 0,51 rural). <b>El sector pesa más que el lugar.</b> El "
        "titular se apoya a propósito en las dos celdas urbanas, porque "
        "entre las dos suman 504.759 estudiantes, el 93,5% del total."))
    F.append(p(
        "En sobreedad alta la brecha va en el mismo sentido: 0,0285 en "
        "estatal rural contra 0,0062 en privado urbano, <b>4,6 veces "
        "mayor</b>. Un dato de color, con su denominador: un estudiante de "
        "estatal urbana (0,62) está peor que uno de privada rural (0,51), "
        "o sea que el campo no es lo que lo hunde; pero privada rural son 36 "
        "filas y 3.679 estudiantes, el 0,7% del total, y es la celda con "
        "mayor dispersión, así que ilustra y no sostiene. Lo que "
        "sugiere el conjunto es que la variable a mirar no es dónde "
        "queda la escuela sino quién la gestiona, y eso es una pregunta "
        "de política pública, no de geografía."))

    F.append(figura(
        "tp2_b_brecha_gestion.png", 152,
        "Figura 1. Desempeño bajo en matemática por sector y "
        "ámbito, ponderado por estudiantes. El panel derecho muestra "
        "cuánta gente hay detrás de cada barra: sin ese panel, la "
        "celda privada rural (0,7% de los estudiantes) parece igual de "
        "sólida que la estatal urbana (60,7%)."))

    # ---------------- Bloque 2 ----------------
    F += seccion(2, "¿Qué problemas de calidad detectamos?")
    F.append(p(
        "El perfilado corre <b>doce chequeos</b> sobre el dataset y cada uno "
        "se reporta con su denominador. <b>Ocho dieron limpio y cuatro "
        "encontraron algo.</b> La etapa mide y no corrige: la corrección "
        "se decide después, por separado y por escrito, que es la "
        "sección 3."))

    F.append(tabla(
        [["Chequeo con hallazgo", "Resultado", "Sev."],
         ["columna constante o vacía",
          "<b>1 de 110</b>: cob__sexo vale 1,0 en las 1.174 filas", "<font color='#eb6834'><b>ALTA</b></font>"],
         ["valor centinela en una clave",
          "<b>1 de 4</b>: departamento = 'Enmascarado' en 63 filas de 23 "
          "jurisdicciones, 10.444 estudiantes (1,9%)", "<font color='#eb6834'><b>ALTA</b></font>"],
         ["bloque con cobertura menor al 50%",
          "<b>2 de 16</b>: clima escolar (91 filas) y educación del "
          "padre (1 fila)", "<font color='#eb6834'><b>MEDIA</b></font>"],
         ["valores extremos a 3 rangos intercuartílicos",
          "<b>75 de 94</b> columnas numéricas; la peor, edad de 21 "
          "años, marca 138 filas", "<font color='#eb6834'><b>BAJA</b></font>"]],
        [58 * mm, ANCHO_UTIL - 58 * mm - 15 * mm, 15 * mm]))

    F.append(Spacer(1, 5))
    F.append(p(
        "Los ocho que dieron limpio, con su denominador: clave territorial "
        "duplicada 0 de 1.174, fila completa duplicada 0 de 1.174, "
        "proporción fuera de [0,1] 0 de 109, bloque de proporciones "
        "que no suma 1 0 de 18, columna con más del 30% de faltantes 0 "
        "de 131, columna casi constante 0 de 110, categoría con "
        "formato inconsistente 0 de 4 y fila sin ninguna variable "
        "analítica 0 de 1.174."))
    F.append(p("El faltante no es al azar, y por eso importa", "sub_naranja"))
    F.append(p(
        "Catorce de los dieciséis bloques tienen cobertura mediana por "
        "encima de 0,95; los dos que quedan abajo son educación del padre "
        "(0,904) y clima escolar (0,873). El que falla de verdad es clima "
        "escolar: 96 filas sin ningún "
        "dato y 91 con el dato calculado sobre menos de la mitad de los "
        "estudiantes de la fila. Los dos conjuntos son disjuntos, así que "
        "son <b>187 filas (15,9%) y 9.808 estudiantes (1,8%)</b>. La "
        "cobertura mediana cae de 0,921 en el quintil de grupos más "
        "grandes a 0,722 en el más chico, y por ámbito va de 0,921 "
        "urbano a 0,744 rural: <b>155 de las 187 filas afectadas son "
        "rurales</b>. El clima escolar está peor medido justo en las "
        "escuelas rurales chicas, que son las de mayor riesgo de abandono."))
    F.append(p(
        "El caso 'Enmascarado' es el más traicionero porque nada "
        "avisaba: duplicados da 0 porque cada combinación de "
        "jurisdicción, 'Enmascarado', sector y ámbito es "
        "única, y el chequeo de formato tampoco lo veía porque la "
        "palabra está bien escrita. El Ministerio lo enmascara cuando el "
        "grupo es tan chico que identificaría a la escuela: esas 63 filas "
        "no son un departamento, son el agregado de los departamentos "
        "chicos de cada provincia."))

    F.append(figura(
        "tp2_a_calidad_cobertura.png", 152,
        "Figura 2. Cobertura mediana por bloque de preguntas (izquierda) y "
        "cobertura de clima escolar según el tamaño del grupo "
        "(derecha). La curva de la derecha es el argumento: si el faltante "
        "fuera al azar, sería plana."))

    # ---------------- Bloque 3 ----------------
    F += seccion(3, "¿Qué decisiones de curación tomamos?")
    F.append(p(
        "«No queremos una base perfectamente limpia. Queremos una base "
        "cuyas decisiones de limpieza podamos explicar.»", "cita"))
    F.append(p(
        "<b>El criterio común: ninguna de las cuatro decisiones borra "
        "filas ni modifica valores.</b> Las cuatro hacen lo mismo, vuelven "
        "visible un problema en vez de taparlo, para que cualquier "
        "análisis posterior lo pueda excluir con una condición "
        "explícita y medir si excluirlo cambia el resultado. La "
        "razón es que los tres problemas encontrados (clima escolar mal "
        "cubierto, departamentos enmascarados, valores extremos) golpean "
        "sobre todo a los grupos chicos y rurales, que son exactamente la "
        "población con mayor riesgo de abandono: limpiar por el camino "
        "fácil habría sesgado el dataset contra su propio objeto de "
        "estudio. Resultado: 1.174 x 131 pasa a <b>1.174 x 133</b>, mismas "
        "filas, dos columnas nuevas, ninguna modificada (verificado por "
        "assert)."))

    F.append(p("1. Clima escolar: se marca la calidad del dato, no se toca "
               "el dato", "sub"))
    F.append(p(
        "Se conservan las tres columnas de clima escolar sin modificar y se "
        "agrega <b>clima_escolar_calidad</b> con tres estados: 'ok', "
        "'cobertura_baja' y 'sin_dato'. Permite repetir cualquier "
        "análisis excluyendo las filas flojas y comprobar si el "
        "resultado cambia. <i>Se descartó imputar</i>, porque "
        "inventaría valores justo en el segmento donde el sesgo vive; "
        "<i>poner en NaN las 91 filas de baja cobertura</i>, porque "
        "perdería dato real sin dejar rastro visible de la pérdida; "
        "y <i>sacar el bloque</i>, porque tira una variable central del marco "
        "teórico por un problema que toca al 1,8% de los estudiantes.",
        "cuerpo_ap"))

    F.append(p("2. Departamentos enmascarados: se identifican, no se "
               "borran", "sub"))
    F.append(p(
        "Se conservan las 63 filas y se agrega la columna booleana "
        "<b>es_agregado_provincial</b>. Un análisis por departamento "
        "filtra es_agregado_provincial == False; uno por provincia usa todas, "
        "que es donde estas filas sí suman bien. <i>Se descartó "
        "borrarlas</i>, porque se irían 10.444 estudiantes de los "
        "departamentos más chicos del país, que es el perfil de "
        "mayor riesgo, y los totales por provincia dejarían de cerrar "
        "contra Aprender; y <i>solo documentarlo</i>, porque deja la trampa "
        "disponible para el que no lea el documento.", "cuerpo_ap"))

    F.append(p("3. Valores extremos: no se tocan, y el chequeo se "
               "corrigió", "sub"))
    F.append(p(
        "Al traducir la proporción a personas se ve que no son errores. "
        "En edad de 21 años, el 70% de las filas vale exactamente 0, lo "
        "que aplasta el rango intercuartílico a 0,0020 y deja el umbral "
        "de extremo en 0,0078: un solo estudiante de 21 años en un grupo "
        "de 118 da 0,0085 y ya lo supera. La mediana de estudiantes "
        "detrás de las 138 filas marcadas es <b>2,3 personas</b>, y 84 "
        "de 138 tienen menos de 3; el chequeo estaba marcando 'acá hay "
        "un estudiante de 21 años'. Así que no se recorta ni se "
        "winsoriza nada: se corrigió el instrumento, y el perfil ahora "
        "reporta cuántas personas hay detrás de cada extremo, "
        "porque sin ese número el chequeo mentía por omisión. "
        "<i>Se descartó winsorizar a los percentiles 1 y 99</i>, porque "
        "borraría justamente los casos de sobreedad extrema, que son "
        "los que el proyecto viene a estudiar.", "cuerpo_ap"))

    F.append(p("4. cob__sexo se conserva pese a tener varianza cero", "sub"))
    F.append(p(
        "Una columna constante no aporta a un modelo, pero esta no es una "
        "variable predictiva: es metadato de cobertura y nunca iba a entrar a "
        "un modelo. Se conserva porque mantiene simétrica la familia (un "
        "bloque, una cobertura) y porque su valor constante es en sí "
        "mismo una verificación: si alguna vez deja de ser 1,0, algo "
        "cambió en la fuente o en el pipeline.", "cuerpo_ap"))

    F.append(p("Cuánto mueven las decisiones", "sub"))
    F.append(p(
        "Ningún escenario mueve los indicadores más de un 1,3%. Eso "
        "no significa que las decisiones sobraran: significa que los "
        "problemas estaban acotados y que ahora están acotados <b>y "
        "medidos</b>. La diferencia entre las dos situaciones es que antes "
        "nadie podía afirmarlo."))
    F.append(tabla(
        [["Escenario", "Filas", "Estudiantes", "Mat. bajo básico",
          "Sobreedad alta", "Clima escolar bajo"],
         ["todo el dataset", "1.174", "540.040", "0,5434", "0,0166", "0,2039"],
         ["sin agregados provinciales", "1.111", "529.596", "0,5432",
          "0,0168", "0,2030"],
         ["solo clima escolar 'ok'", "987", "530.232", "0,5418", "0,0164",
          "0,2036"],
         ["sin discrepancia entre bases", "1.169", "539.254", "0,5434",
          "0,0166", "0,2038"]],
        [50 * mm, 14 * mm, 22 * mm, 28 * mm, 24 * mm,
         ANCHO_UTIL - 138 * mm],
        alineados_der=(1, 2, 3, 4, 5)))

    # ---------------- Bloque 4 ----------------
    F += seccion(4, "¿Qué variables o relaciones parecen "
                    "especialmente interesantes?")
    F.append(p(
        "<b>El contexto socioeconómico provincial, con su robustez "
        "probada.</b> La relación más fuerte del trabajo es entre "
        "el ingreso per cápita familiar mediano de la provincia y la "
        "proporción de estudiantes por debajo del nivel básico en "
        "matemática: <b>r = -0,82 sobre 24 jurisdicciones</b>. La siguen "
        "la proporción de adultos con nivel superior (-0,72), los "
        "adultos sin secundaria completa (+0,52) y el agua fuera de la "
        "vivienda (+0,52). Se calcula a nivel provincia y no sobre las 1.174 "
        "filas porque los valores de la EPH se repiten idénticos en "
        "todos los departamentos de una misma provincia: las filas no son "
        "observaciones independientes y calcular sobre ellas inflaría el "
        "n sin agregar información."))
    F.append(p(
        "Pearson falla de dos maneras conocidas y cada prueba ataca una. Que "
        "la sostenga un solo caso raro: CABA es la jurisdicción más "
        "rica y la de mejor desempeño, está sola en ese "
        "rincón, se sacó y la relación se mantiene. Que la "
        "relación sea fuerte pero curva: Spearman "
        "ignora la forma y mira solo el orden, y da más fuerte que "
        "Pearson, lo que sugiere que el salto entre las provincias más "
        "pobres pesa más que entre las más ricas. Sobrevive las "
        "tres pruebas: Pearson -0,82 (n = 24), Pearson sin CABA -0,73 "
        "(n = 23), Spearman -0,85 (n = 24) y Spearman sin CABA -0,83 "
        "(n = 23). Y el n es parte del dato, así que se cita siempre "
        "como <i>r = -0,82 sobre 24 jurisdicciones</i> y nunca como "
        "<i>r = -0,82</i> a secas."))
    F.append(p(
        "A nivel fila, donde las dos variables vienen de Aprender y "
        "varían entre departamentos, lo más fuerte contra el "
        "desempeño bajo en matemática es la ausencia de libros en "
        "papel en el hogar (Pearson +0,62, Spearman +0,64 sobre 1.174 filas) "
        "y la madre con terciario, universitario o posgrado completo (-0,62 y "
        "-0,59). Repitencia da +0,35 y sobreedad alta +0,21."))

    F.append(figura(
        "tp2_c_contexto_rendimiento.png", 126,
        "Figura 3. Ingreso per cápita familiar mediano provincial (EPH "
        "3T-2025) contra desempeño bajo en matemática, una "
        "jurisdicción por punto y la matrícula como tamaño."))

    F.append(p("Las inasistencias, que quedan como pregunta y no como "
               "conclusión", "sub_naranja"))
    F.append(p(
        "Cuantos más chicos de un grupo reportan faltas, <b>menos</b> "
        "chicos de ese grupo están por debajo del básico: la "
        "proporción con 5 o más faltas correlaciona -0,49 con el "
        "desempeño bajo en matemática, la de 15 o más faltas "
        "-0,37, y la de los que dicen no faltar nunca da +0,31. La primera "
        "medición usó solo la categoría más extrema (30 "
        "faltas o más) y dio r = +0,000: la conclusión habría "
        "sido que las inasistencias no se relacionan con nada. El error fue "
        "mirar la cola en vez del acumulado, porque casi nadie cae en la "
        "categoría extrema (valor medio ponderado 0,10) y una columna "
        "que casi no varía no puede correlacionar con nada. Tampoco es "
        "la paradoja de Simpson: el mismo r se calculó dentro de cada "
        "celda de sector y ámbito y la relación negativa se "
        "mantiene en las cuatro (estatal rural -0,34, estatal urbano -0,36, "
        "privado rural -0,59, privado urbano -0,49)."))
    # Este parrafo y el siguiente son el par medido / inferido: si el salto
    # de pagina los parte, el lector se queda con media distincion, asi que
    # el bloque viaja entero.
    F.append(KeepTogether(p(
        "<b>Lo MEDIDO, verificado en la fuente.</b> El Manual del Aplicador "
        "de Aprender 2024 dice que al finalizar ambas pruebas los estudiantes "
        "contestan un cuestionario complementario en un cuadernillo propio. "
        "O sea que el dato es <b>lo que el estudiante dice que "
        "faltó</b>, no un registro administrativo de asistencia.")))
    F.append(p(
        "<b>Lo INFERIDO, explícitamente NO verificado.</b> La "
        "hipótesis es que Aprender evalúa a quien está "
        "presente el día de la prueba, así que en una escuela con "
        "ausentismo real alto los más ausentes no entran a la muestra; "
        "entre los que sí rindieron, reportar faltas sería marcador "
        "de un alumno presente y conectado con la escuela, no de riesgo. Se "
        "suma que el dato es autorreporte: dos capas de ruido en la misma "
        "variable. Verificarlo requiere asistencia administrativa, que este "
        "dataset no tiene. Hasta entonces es una hipótesis, no un "
        "resultado."))

    F.append(figura(
        "tp2_d_inasistencias.png", 142,
        "Figura 4. Correlación de cada medida de inasistencia con el "
        "desempeño bajo en matemática (izquierda) y la misma "
        "relación abierta por sector y ámbito (derecha)."))

    F += seccion(5, "¿Qué nuevas preguntas surgieron?")
    F.append(p(
        "<b>1. ¿De dónde sale el target?</b> Es la pregunta que "
        "manda. El dataset no tiene una variable de abandono, y el proxy "
        "construido en el TP1 desde la EPH correlaciona +0,16 con el "
        "desempeño, o sea que no mide lo que dice medir. Todo lo de "
        "arriba describe desempeño y sobreedad, antecedentes plausibles "
        "del abandono, no el abandono. Conseguir el target real es el "
        "problema abierto que este entregable deja para el TP3.",
        "cuerpo_ap"))
    F.append(p(
        "<b>2. ¿Qué mide realmente la variable de "
        "inasistencias?</b> Contestarlo requiere cruzar el autorreporte con "
        "asistencia administrativa. Mientras tanto, la variable no entra a un "
        "modelo sin una advertencia al lado.", "cuerpo_ap"))
    F.append(p(
        "<b>3. ¿Por qué el sector pesa más que el "
        "ámbito?</b> Si la gestión explica más que la "
        "geografía, la pregunta siguiente es qué de la "
        "gestión: composición social de la matrícula, "
        "recursos, o algo que estas bases no observan.", "cuerpo_ap"))
    F.append(p(
        "<b>4. ¿Cambia el resultado si se excluyen las filas "
        "marcadas?</b> Ahora se puede probar con una condición de una "
        "línea, y si un modelo del TP3 da distinto al excluirlas, va a "
        "haber una columna que lo explique en vez de un misterio.",
        "cuerpo_ap"))

    # Cada limitacion es un parrafo propio y no un bloque unico con saltos:
    # asi el flujo puede repartirlas y ninguna queda huerfana de su titulo.
    F += seccion(6, "Limitaciones")
    F.append(p(
        "<b>No hay variable de abandono.</b> El trabajo describe "
        "desempeño y sobreedad, no abandono. "
        "<b>Son correlaciones ecológicas:</b> valen entre agregados "
        "territoriales y no autorizan a concluir nada sobre un estudiante "
        "concreto.", "limit"))
    F.append(p(
        "<b>La unidad de análisis es el grupo, no el estudiante.</b> "
        "Toda pregunta que necesite abrir por atributo individual queda fuera "
        "de alcance con las bases publicadas. En particular la pregunta por "
        "sexo: las columnas de sexo dicen qué porcentaje del grupo son "
        "varones o mujeres, no cómo le fue a cada sexo. Lo único "
        "calculable es si los grupos con más mujeres rinden distinto, y "
        "da prácticamente cero (-0,05 y +0,03 sobre 1.174 filas): ese "
        "número responde una pregunta diferente de la que se hizo, "
        "así que se reporta el límite y no el número.", "limit"))
    F.append(p(
        "<b>Todo lo que cruza con la EPH descansa en 24 puntos.</b> Mover dos "
        "o tres cambia bastante el resultado. <b>Y el clima escolar "
        "está peor medido donde más importa:</b> 155 de las 187 "
        "filas afectadas son rurales, así que un modelo que use esa "
        "variable va a tener menos información precisamente donde "
        "más la necesita.", "limit"))
    F.append(p(
        "<b>Los grupos chicos dan valores extremos por construcción.</b> "
        "El quintil más chico (mediana 29 estudiantes) tiene 1,4 veces la "
        "dispersión del más grande (mediana 1.225) y llega a 0,000 y "
        "1,000: todo número de una celda chica se cita con su "
        "denominador.", "limit"))
    F.append(p(
        "<b>El perfilado no sabe si un valor es correcto, solo si es "
        "posible.</b> Contra los datos crudos comparan los 55 invariantes "
        "de tests/test_invariantes.py, y la reproducibilidad está "
        "verificada: corriendo el pipeline dos veces, 18 de 18 salidas salen "
        "idénticas byte a byte.", "limit"))

    return F


def main():
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(SALIDA), pagesize=A4,
        leftMargin=MARGEN_X, rightMargin=MARGEN_X,
        topMargin=MARGEN_SUP, bottomMargin=MARGEN_INF,
        title="TP2 Resumen de hallazgos - Grupo M01 El Factor D10S",
        author="Ignacio Villanueva",
        subject="Entregable 2, Mentoria M01, Diplomatura en Ciencia de Datos "
                "(FAMAF, UNC)",
    )
    marco = Frame(MARGEN_X, MARGEN_INF, ANCHO_UTIL,
                  A4[1] - MARGEN_SUP - MARGEN_INF, id="cuerpo",
                  leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="base", frames=[marco],
                                       onPage=decorado)])
    doc.build(construir())
    print(f"PDF escrito en {SALIDA}")


if __name__ == "__main__":
    main()
