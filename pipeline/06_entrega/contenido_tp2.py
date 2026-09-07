"""El contenido del notebook del TP2: las celdas, en orden.

Vive aparte de `12_notebook.py` por una razon practica: ese archivo se ocupa de
la mecanica (resolver el repo, calcular hashes, armar el JSON del .ipynb) y
este del texto y el codigo que va adentro. Mezclarlos daria un archivo de 900
lineas donde no se encuentra nada.

Recibe `md` y `code` como parametros en vez de importarlos, asi este modulo no
sabe nada de como se construye el notebook y se puede probar solo.

Sobre las figuras: el codigo de los cuatro graficos esta ACA y no se baja como
PNG. Un analisis exploratorio donde los graficos no salen del mismo codigo que
produce los numeros no es reproducible, y la consigna pide justamente que el
notebook permita reproducir el proceso.
"""

# ---------------------------------------------------------------------------
# Codigo de las figuras. Se define como texto porque son celdas del notebook,
# no codigo de este modulo.
# ---------------------------------------------------------------------------

FIGURAS_SETUP = r"""
import matplotlib.pyplot as plt
import matplotlib.ticker

# Paleta heredada del TP1. Es categorica y esta validada para daltonismo
# (separacion DeltaE 9,1 protan). Orden fijo: nunca se cicla ni se reasigna, y
# no se agregan colores nuevos. Si hiciera falta una quinta categoria, se
# repiensa el grafico antes que la paleta.
AZUL, NARANJA, VERDE, AMARILLO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
TINTA, TINTA_SUAVE = "#0b0b0b", "#52514e"
GRIS_GRILLA, FONDO = "#e3e3e0", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": FONDO, "axes.facecolor": FONDO,
    "axes.edgecolor": GRIS_GRILLA, "axes.labelcolor": TINTA_SUAVE,
    "text.color": TINTA, "xtick.color": TINTA_SUAVE, "ytick.color": TINTA_SUAVE,
    "font.size": 10, "axes.titlesize": 12,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRIS_GRILLA, "grid.linewidth": 0.8,
})


def titulo(ax, texto, bajada=None):
    # La bajada dice la CONCLUSION, no la variable. Un titulo que nombra la
    # variable obliga a leer el grafico para saber que pasa.
    #
    # Los dos van como anotaciones y no con set_title porque mezclarlos hace
    # que se superpongan: set_title reserva su espacio con `pad`, pero la
    # anotacion se dibuja encima sin saber que el titulo estaba ahi.
    alto = 0.035 * ((bajada.count(chr(10)) + 1) if bajada else 0)
    ax.annotate(texto, xy=(0, 1.035 + alto), xycoords="axes fraction",
                fontsize=12.5, color=TINTA, va="bottom", ha="left")
    if bajada:
        ax.annotate(bajada, xy=(0, 1.02), xycoords="axes fraction",
                    fontsize=9.5, color=TINTA_SUAVE, va="bottom", ha="left")

print("Estilo cargado: paleta del TP1, sin colores nuevos.")
"""

FIGURA_A = r"""
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6),
                               gridspec_kw={"width_ratios": [1.35, 1]})

orden = sorted(cobs, key=lambda c: maestro[c].median())
medianas = [maestro[c].median() for c in orden]
UMBRAL = 0.95
colores = [NARANJA if m < UMBRAL else AZUL for m in medianas]
sanos = sum(1 for m in medianas if m >= UMBRAL)

ax1.barh([c.replace("cob__", "").replace("_", " ") for c in orden],
         medianas, color=colores, height=0.62, zorder=3)
for y, m in enumerate(medianas):
    ax1.annotate(f"{m:.3f}", xy=(m, y), xytext=(6, 0),
                 textcoords="offset points", va="center",
                 fontsize=9, color=TINTA)
ax1.set_xlim(0, 1.09)
ax1.set_xlabel("cobertura mediana del bloque")
ax1.grid(axis="x", zorder=0)
ax1.set_axisbelow(True)
titulo(ax1, f"{sanos} de {len(medianas)} bloques por encima de 0,95",
       "cobertura = que fraccion de los estudiantes de la fila" + chr(10) +
       "quedo representada en ese bloque de preguntas")

res = tmp.groupby("quintil").agg(
    cob=("cob__clima_escolar", "median"), est=("estudiantes", "median"))
ax2.plot(range(len(res)), res["cob"], color=NARANJA, lw=2.2, marker="o",
         ms=8, mfc=FONDO, mew=2.2, zorder=3)
for i, (_, f) in enumerate(res.iterrows()):
    ax2.annotate(f"{f['cob']:.3f}", xy=(i, f["cob"]), xytext=(0, 11),
                 textcoords="offset points", ha="center",
                 fontsize=9, color=TINTA)
ax2.set_xticks(range(len(res)))
ax2.set_xticklabels([f"{e:,.0f}".replace(",", ".") for e in res["est"]])
ax2.set_xlabel("estudiantes por grupo (mediana del quintil)")
ax2.set_ylabel("cobertura de clima escolar")
ax2.set_ylim(0.65, 1.0)
ax2.grid(axis="y", zorder=0)
ax2.set_axisbelow(True)
titulo(ax2, "y el que falla, falla donde mas importa",
       "el clima escolar esta peor medido en los grupos mas chicos," + chr(10) +
       "que son mayormente rurales: no es un faltante al azar")

fig.tight_layout()
plt.show()
"""

FIGURA_B = r"""
b = brecha.reset_index()
b["etiqueta"] = b["sector"] + " . " + b["ambito"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.6),
                               gridspec_kw={"width_ratios": [1.5, 1]})

colores = [AZUL if s == "Privado" else NARANJA for s in b["sector"]]
ax1.barh(b["etiqueta"], b["matematica_bajo_basico"], color=colores,
         height=0.6, zorder=3)
for y, v in enumerate(b["matematica_bajo_basico"]):
    ax1.annotate(f"{v:.2f}", xy=(v, y), xytext=(6, 0),
                 textcoords="offset points", va="center",
                 fontsize=10, color=TINTA)
ax1.set_xlim(0, 0.82)
ax1.set_xlabel("proporcion por debajo del nivel basico en matematica")
ax1.grid(axis="x", zorder=0)
ax1.set_axisbelow(True)
titulo(ax1, "Dentro del mismo ambito, el sector pesa mas que el lugar",
       "cambiar de privado a estatal (urbano): +0,23  .  "
       "cambiar de urbano a rural (privado): +0,13")

ax2.barh(b["etiqueta"], b["estudiantes"], color=TINTA_SUAVE, height=0.6,
         alpha=0.28, zorder=3)
for y, (_, f) in enumerate(b.iterrows()):
    ax2.annotate(f"{f['estudiantes']:,.0f}".replace(",", ".") +
                 f"   ({f['% de estudiantes']:.1f}%)",
                 xy=(f["estudiantes"], y), xytext=(6, 0),
                 textcoords="offset points", va="center",
                 fontsize=9, color=TINTA)
ax2.set_xlim(0, b["estudiantes"].max() * 1.5)
ax2.set_xticks([])
ax2.set_yticklabels([])
ax2.spines["left"].set_visible(False)
ax2.spines["bottom"].set_visible(False)
titulo(ax2, "cuanta gente hay atras de cada barra",
       "privado rural es el 0,7% de los estudiantes: ilustra, no sostiene")

fig.tight_layout()
plt.show()
"""

FIGURA_C = r"""
p = provincias.reset_index()
fig, ax = plt.subplots(figsize=(11, 6.4))
ax.scatter(p["ipcf_mediano"], p["matematica_bajo"], s=p["estudiantes"] / 90,
           color=AZUL, alpha=0.7, edgecolor=FONDO, linewidth=2, zorder=3)

# Etiquetas directas y no leyenda: hay una sola serie. Se nombran los dos
# extremos y las tres jurisdicciones con mas matricula, porque un punto grande
# sin nombre es la primera pregunta de cualquiera que mire el grafico.
destacar = pd.concat([p.nsmallest(3, "matematica_bajo"),
                      p.nlargest(3, "matematica_bajo"),
                      p.nlargest(3, "estudiantes")]).drop_duplicates("jurisdiccion")
for _, f in destacar.iterrows():
    nombre = f["jurisdiccion"].replace("Ciudad Autónoma de Buenos Aires", "CABA")
    ax.annotate(nombre, xy=(f["ipcf_mediano"], f["matematica_bajo"]),
                xytext=(0, 13), textcoords="offset points", ha="center",
                fontsize=9, color=TINTA_SUAVE)

z = np.polyfit(p["ipcf_mediano"], p["matematica_bajo"], 1)
xs = np.linspace(p["ipcf_mediano"].min(), p["ipcf_mediano"].max(), 50)
ax.plot(xs, np.polyval(z, xs), color=TINTA_SUAVE, lw=1.2, ls="--",
        alpha=0.6, zorder=2)

ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
    lambda v, _: "$" + f"{v:,.0f}".replace(",", ".")))
ax.set_xlabel("ingreso per capita familiar mediano de la provincia (EPH 3T-2025)")
ax.set_ylabel("por debajo del nivel basico en matematica")
ax.grid(zorder=0)
ax.set_axisbelow(True)
titulo(ax, "A mas ingreso provincial, menos estudiantes por debajo del basico",
       f"r = {pruebas['r'][0]:+.2f} sobre 24 jurisdicciones  .  "
       f"sin CABA {pruebas['r'][1]:+.2f}  .  "
       f"Spearman {pruebas['r'][2]:+.2f}"
       "     |     el tamanio del punto es la matricula")

fig.tight_layout()
plt.show()
"""

FIGURA_D = r"""
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.8),
                               gridspec_kw={"width_ratios": [1, 1.25]})

nombres = ["30+ faltas" + chr(10) + "(solo la cola)", "15+ faltas",
           "5+ faltas" + chr(10) + "(acumulado)", "ninguna falta"]
claves = ["30 o mas faltas (solo la cola)", "15 o mas faltas",
          "5 o mas faltas", "ninguna falta"]
erres = [maestro[acumulados[k]].sum(axis=1).corr(maestro[MATE_BAJO])
         for k in claves]
colores = [AMARILLO if abs(x) < 0.05 else (NARANJA if x > 0 else AZUL)
           for x in erres]

ax1.barh(nombres, erres, color=colores, height=0.6, zorder=3)
ax1.axvline(0, color=TINTA_SUAVE, lw=1, zorder=2)
for y, x in enumerate(erres):
    ax1.annotate(f"{x:+.2f}", xy=(x, y), xytext=(8 if x >= 0 else -8, 0),
                 textcoords="offset points", va="center",
                 ha="left" if x >= 0 else "right", fontsize=10, color=TINTA)
ax1.set_xlim(-0.62, 0.45)
ax1.set_xlabel("correlacion con el desempenio bajo en matematica")
ax1.grid(axis="x", zorder=0)
ax1.set_axisbelow(True)
titulo(ax1, "Medir la cola no muestra nada; el acumulado si",
       "la primera medicion uso solo 30+ faltas y dio 0,00")

# Doble codificacion: COLOR dice el sector y FORMA dice el ambito. Aca SI va
# leyenda y no etiquetas directas, porque hay cuatro series solapadas y
# etiquetarlas sobre los puntos las vuelve ilegibles. Una version anterior
# codificaba el ambito con transparencia y las entradas rurales quedaban
# invisibles: la opacidad no sirve como canal categorico.
marcadores = {"Urbano": "o", "Rural": "^"}
referencias = []
for (sec, amb), g in tmp.groupby(["sector", "ambito"]):
    color = AZUL if sec == "Privado" else NARANJA
    ax2.scatter(g["faltas_5mas"], g[MATE_BAJO], s=g["estudiantes"] / 55,
                color=color, alpha=0.6, marker=marcadores[amb],
                edgecolor=FONDO, linewidth=0.7, zorder=3)
    referencias.append((sec, amb, color, marcadores[amb],
                        g["faltas_5mas"].corr(g[MATE_BAJO])))

ax2.set_xlabel("proporcion del grupo que reporta 5 o mas faltas")
ax2.set_ylabel("por debajo del basico en matematica")
ax2.set_xlim(0.18, 1.03)
ax2.set_ylim(0.05, 1.0)
ax2.grid(zorder=0)
ax2.set_axisbelow(True)

referencias.sort(key=lambda x: x[4])
for i, (sec, amb, color, marca, rg) in enumerate(referencias):
    y = 0.245 - i * 0.052
    ax2.scatter([0.235], [y], s=70, color=color, alpha=0.9, marker=marca,
                edgecolor=FONDO, linewidth=0.7, zorder=4, clip_on=False)
    ax2.annotate(f"{sec} {amb.lower()}", xy=(0.265, y), va="center",
                 fontsize=9, color=TINTA_SUAVE)
    ax2.annotate(f"r = {rg:+.2f}", xy=(0.46, y), va="center",
                 fontsize=9, color=TINTA)

titulo(ax2, "Y no es efecto de mezclar sectores",
       "la relacion negativa se mantiene dentro de las cuatro celdas")

fig.tight_layout()
plt.show()
"""


def secciones_2_a_7(md, code):
    """Agrega las secciones 2 a 7 del notebook. La 1 la arma `12_notebook.py`."""

    # ==================================================== 2. CONOCER
    md("""
## 2. Conocer el dataset

Antes de buscar problemas hay que saber qué hay. Esta sección responde la
primera actividad de la consigna: cuántos registros y variables, de qué tipo,
cuáles son categóricas y cuáles numéricas, y qué valores faltan.

Pero un listado de 131 columnas no se entiende. Lo que sí se entiende es
**agruparlas por el rol que cumplen**, porque cada familia se lee distinto y,
sobre todo, se juzga distinto. Un chequeo genérico de calidad aplicado a ciegas
produce falsos positivos: marcaría como sospechosas las columnas de contexto
socioeconómico por tener poca variación, cuando esa poca variación es
exactamente cómo fueron construidas.
""")

    code('''
def familia_de(columna):
    """Clasifica cada columna por el rol que cumple en el dataset."""
    if columna in CLAVES:
        return "clave"
    if columna == "estudiantes":
        return "peso"
    if columna.startswith("flag_"):
        return "control"
    if columna.startswith("cob__"):
        return "cobertura"
    if columna.startswith("eph_"):
        return "contexto_provincial"
    if "_arm__" in columna:
        return "armonizada"
    if "__" in columna:
        return "proporcion"
    return "otra"


GLOSARIO = {
    "clave": "identifican la fila (jurisdiccion, departamento, sector, ambito)",
    "peso": "cuantos estudiantes representa la fila",
    "proporcion": "reparto dentro de la fila (cada bloque suma 1)",
    "cobertura": "que fraccion de la fila quedo representada en ese bloque",
    "contexto_provincial": "indicador de la EPH, IGUAL para toda la provincia",
    "armonizada": "llevada a escala comparable entre Aprender y la EPH",
    "control": "bandera derivada para analisis de sensibilidad",
}

perfil = pd.DataFrame({
    "columna": maestro.columns,
    "familia": [familia_de(c) for c in maestro.columns],
    "tipo": [str(maestro[c].dtype) for c in maestro.columns],
    "faltantes": [int(maestro[c].isna().sum()) for c in maestro.columns],
    "unicos": [int(maestro[c].nunique(dropna=True)) for c in maestro.columns],
})

resumen = (perfil.groupby("familia")
           .agg(columnas=("columna", "size"), faltantes=("faltantes", "sum"))
           .sort_values("columnas", ascending=False))
resumen["que_son"] = [GLOSARIO.get(f, "") for f in resumen.index]
resumen
''')

    md("""
### Cómo leer las columnas

Tres convenciones del dataset que conviene tener a mano:

- Las columnas con `__` son **proporciones dentro de la fila**. `sexo__femenino`
  es qué fracción de ese grupo son mujeres, no una cantidad. Cada bloque suma 1.
- Las que empiezan con `cob__` dicen **sobre qué fracción de la fila se calculó
  ese bloque**. Es el indicador de calidad viajando pegado al dato en vez de en
  un comentario aparte, y va a ser central en la sección 3.
- Las que empiezan con `eph_` son indicadores socioeconómicos **de la
  provincia**, iguales para todos sus departamentos. Es la limitación central
  del dataset, declarada desde el TP1.

Y el dato que define casi todo lo que sigue: el tamaño de los grupos es muy
desparejo.
""")

    code('''
print("TAMANIO DE LOS GRUPOS (columna 'estudiantes')")
print(f"  minimo  : {maestro['estudiantes'].min():>10,.0f}")
print(f"  mediana : {maestro['estudiantes'].median():>10,.0f}")
print(f"  maximo  : {maestro['estudiantes'].max():>10,.0f}")
print()
print("Repartidos en las cuatro combinaciones de sector y ambito:")
reparto = maestro.groupby(["sector", "ambito"]).agg(
    filas=("estudiantes", "size"), estudiantes=("estudiantes", "sum"))
reparto["% filas"] = (100 * reparto["filas"] / reparto["filas"].sum()).round(1)
reparto["% estudiantes"] = (
    100 * reparto["estudiantes"] / reparto["estudiantes"].sum()).round(1)
reparto.sort_values("estudiantes", ascending=False)
''')

    md("""
Ahí está el motivo de ponderar, con número: **el ámbito rural es el 39% de las
filas y el 6,6% de los estudiantes.** Un promedio simple le daría a lo rural
casi seis veces el peso que tiene en la población real.
""")

    # ==================================================== 3. CALIDAD
    md("""
## 3. Explorar la calidad

La segunda actividad pide buscar los problemas que puedan afectar el análisis
posterior: faltantes, categorías inconsistentes, valores imposibles,
duplicados, extremos y variables sin variabilidad.

Se corren doce chequeos, los mismos que el pipeline del proyecto. Cada uno
reporta **su denominador**, porque un "0 problemas" sin decir sobre cuántos
casos se miró no significa nada.
""")

    code('''
TOLERANCIA = 1e-9
hallazgos = []


def chequeo(nombre, afectados, de, detalle):
    hallazgos.append({"chequeo": nombre, "afectados": afectados,
                      "de": de, "detalle": detalle})


chequeo("clave territorial duplicada",
        int(maestro.duplicated(subset=CLAVES).sum()), len(maestro),
        "cada fila tiene que ser una combinacion unica")
chequeo("fila completa duplicada",
        int(maestro.duplicated().sum()), len(maestro),
        "filas identicas en las 131 columnas")

props = perfil[perfil["familia"].isin(
    ["proporcion", "cobertura", "armonizada"])]["columna"]
fuera = [c for c in props
         if maestro[c].dropna().lt(-TOLERANCIA).any()
         or maestro[c].dropna().gt(1 + TOLERANCIA).any()]
chequeo("proporcion fuera de [0,1]", len(fuera), len(props),
        "una proporcion negativa o mayor que 1 es imposible por definicion")


def bloque_de(c):
    if "__" not in c or c.startswith(("cob__", "eph_")):
        return None
    return c.split("__")[0]


bloques = sorted({b for b in map(bloque_de, maestro.columns) if b})
rotos = []
for b in bloques:
    cols = [c for c in maestro.columns
            if bloque_de(c) == b and familia_de(c) == "proporcion"]
    if len(cols) < 2:
        continue
    suma = maestro[cols].sum(axis=1)
    if int((suma.gt(TOLERANCIA) & (suma - 1).abs().gt(1e-6)).sum()):
        rotos.append(b)
chequeo("bloque de proporciones que no suma 1", len(rotos), len(bloques),
        "cada bloque reparte el 100% de una poblacion")

altos = perfil[perfil["faltantes"] / len(maestro) > 0.30]
chequeo("columna con mas del 30% de faltantes", len(altos), len(perfil),
        "arriba de ese umbral la columna aporta poco")

candidatas = perfil[~perfil["familia"].isin(
    ["contexto_provincial", "clave", "control"])]
chequeo("columna constante o vacia",
        len(candidatas[candidatas["unicos"] <= 1]), len(candidatas),
        "un solo valor en las 1.174 filas: no aporta a ningun modelo")

inconsistentes = 0
for c in CLAVES:
    v = maestro[c].dropna().astype(str)
    limpio = v.str.strip()
    if len(v[v != limpio]) or limpio.str.upper().nunique() != limpio.nunique():
        inconsistentes += 1
chequeo("categoria con formato inconsistente", inconsistentes, len(CLAVES),
        "espacios al borde o valores que solo difieren en mayusculas")

CENTINELAS = ("ENMASCARADO", "SIN DATO", "NO APLICA", "S/D")
centinelas = []
for c in CLAVES:
    v = maestro[c].astype(str).str.strip().str.upper()
    for s in CENTINELAS:
        if int((v == s).sum()):
            centinelas.append((c, s))
chequeo("valor centinela en una clave", len(centinelas), len(CLAVES),
        "un texto que ocupa el lugar de un valor real sin serlo")

cobs = [c for c in maestro.columns if c.startswith("cob__")]
bajas = [c for c in cobs if int((maestro[c] < 0.5).sum())]
chequeo("bloque con cobertura menor al 50%", len(bajas), len(cobs),
        "el numero existe pero se calculo sobre menos de la mitad de la gente")

analiticas = perfil[perfil["familia"].isin(
    ["proporcion", "armonizada"])]["columna"]
chequeo("fila sin ninguna variable analitica",
        int(maestro[analiticas].isna().all(axis=1).sum()), len(maestro),
        "una fila sin ninguna proporcion no aporta al analisis")

# Casi constante: un mismo valor en mas del 99% de las filas. Se excluyen las
# familias cuya baja variabilidad es estructural (contexto provincial, claves
# y banderas de control), porque marcarlas seria un falso positivo.
casi = 0
for c in candidatas["columna"]:
    v = maestro[c].dropna()
    if len(v) and v.nunique() > 1 and v.value_counts(normalize=True).iloc[0] > 0.99:
        casi += 1
chequeo("columna casi constante", casi, len(candidatas),
        "un mismo valor en mas del 99% de las filas")

# Extremos por rango intercuartil. En la seccion 5 se ve por que estos NO son
# errores: al traducir la proporcion a personas, la mediana detras de cada
# valor marcado es de 2,3 estudiantes.
numericas = perfil[perfil["familia"].isin(
    ["proporcion", "armonizada"])]["columna"]
con_extremos = 0
for c in numericas:
    v = maestro[c].dropna()
    if len(v) < 20:
        continue
    q1, q3 = v.quantile(0.25), v.quantile(0.75)
    if q3 - q1 <= TOLERANCIA:
        continue
    if int(((v < q1 - 3 * (q3 - q1)) | (v > q3 + 3 * (q3 - q1))).sum()):
        con_extremos += 1
chequeo("columna con valores extremos (3x IQR)", con_extremos, len(numericas),
        "lejos del cuerpo de la distribucion, pero NO necesariamente errores")

tabla = pd.DataFrame(hallazgos)
tabla["estado"] = np.where(tabla["afectados"] > 0, "REVISAR", "ok")

# El resumen se CUENTA, no se escribe a mano. Una version anterior de este
# notebook decia "once chequeos" mientras el codigo corria diez: el mismo tipo
# de error que se corrigio en el titulo de la primera figura.
limpios = int((tabla["afectados"] == 0).sum())
print(f"{limpios} de los {len(tabla)} chequeos dan cero.")
print(f"Los {len(tabla) - limpios} restantes se detallan abajo.")
print()

tabla.sort_values("afectados", ascending=False)[
    ["estado", "chequeo", "afectados", "de", "detalle"]]
''')

    md("""
### El dataset está sano, y eso no era obvio

Ocho de los doce chequeos dan cero. No hay duplicados, ni proporciones
imposibles, ni bloques que no cierren, ni categorías mal escritas, ni filas
vacías. Tiene sentido: el TP1 se construyó con 41 verificaciones automáticas
encima, así que estos problemas se habrían detectado al armarlo.

Los dos que no dan cero son los interesantes.

### El primero: un valor centinela que casi se nos escapa

`departamento` toma el valor `"Enmascarado"` en varias filas. **No es un error
de carga**: el Ministerio reemplaza el nombre del departamento cuando el grupo
es tan chico que publicarlo permitiría identificar la escuela, y con eso a los
estudiantes. Es una protección de privacidad de la fuente.

Lo que lo vuelve una trampa es el efecto colateral.
""")

    code('''
enmascarados = maestro[
    maestro["departamento"].astype(str).str.strip().str.upper() == "ENMASCARADO"]

print(f"filas con departamento 'Enmascarado' : {len(enmascarados):>6,} "
      f"de {len(maestro):,}")
print(f"jurisdicciones que lo usan           : "
      f"{enmascarados['jurisdiccion'].nunique():>6} de 24")
print(f"estudiantes involucrados             : "
      f"{enmascarados['estudiantes'].sum():>6,.0f} "
      f"({100 * enmascarados['estudiantes'].sum() / maestro['estudiantes'].sum():.1f}%)")
print()
print("El problema: la clave territorial deja de significar lo mismo.")
print("Un group by por departamento junta escuelas de 23 provincias distintas")
print("bajo una sola etiqueta, y nada avisa, porque cada combinacion de")
print("jurisdiccion + Enmascarado + sector + ambito ES unica.")
''')

    md("""
Vale la pena decir cómo apareció, porque dice algo sobre el método: **el chequeo
automático de categorías no lo encontró.** Ese chequeo busca problemas de
formato (espacios al borde, mayúsculas inconsistentes) y `"Enmascarado"` está
perfectamente escrito. Salió mirando a mano las filas con valores extremos, y
recién después se agregó el chequeo de valores centinela que ahora sí lo caza.

### El segundo: un bloque mal cubierto, y no al azar

De los 16 bloques de preguntas, 14 tienen cobertura por encima de 0,95. Dos
quedan por debajo, y uno de ellos falla de una manera que importa.
""")

    code('''
pd.DataFrame({
    "bloque": [c.replace("cob__", "") for c in cobs],
    "cobertura_mediana": [maestro[c].median() for c in cobs],
    "sin_dato": [int(maestro[c].isna().sum()) for c in cobs],
    "filas_bajo_50pct": [int((maestro[c] < 0.5).sum()) for c in cobs],
}).sort_values("cobertura_mediana").round(3)
''')

    code('''
# La pregunta que decide si esto importa: el faltante, es al azar?
peor = "cob__clima_escolar"
tmp = maestro.copy()
tmp["quintil"] = pd.qcut(tmp["estudiantes"], 5, labels=False)

print("Cobertura de clima escolar segun el TAMANIO del grupo:")
print(tmp.groupby("quintil").agg(
    estudiantes_mediana=("estudiantes", "median"),
    cobertura_mediana=(peor, "median")).round(3).to_string())
print()
print("Y segun el AMBITO:")
print(tmp.groupby("ambito")[peor].median().round(3).to_string())
print()
afectadas = tmp[(tmp[peor] < 0.5) | (tmp[peor].isna())]
print(f"Filas con el dato ausente o flojo: {len(afectadas)} "
      f"({100 * len(afectadas) / len(tmp):.1f}%), de las cuales "
      f"{(afectadas['ambito'] == 'Rural').sum()} son rurales.")
''')

    md("""
**Este es el hallazgo de calidad más importante del trabajo.** La cobertura de
clima escolar cae de forma monótona con el tamaño del grupo, de 0,92 en el
quintil más grande a 0,72 en el más chico, y por ámbito va de 0,92 urbano a
0,74 rural.

O sea que **el clima escolar está peor medido justo en las escuelas rurales
chicas**, que son probablemente las de mayor riesgo de abandono. Un modelo que
use esa variable va a tener menos información precisamente donde más la
necesita, y eso hay que poder decirlo de antemano, no descubrirlo después.

Un faltante al azar se puede ignorar. Uno que se concentra en la población que
el proyecto quiere estudiar, no.

### Figura 1: la calidad del dataset

Las figuras de este notebook **se generan al correr**, no se muestran como
imágenes bajadas. Un análisis exploratorio donde los gráficos no salen del
mismo código que produce los números no es reproducible.
""")

    code(FIGURAS_SETUP)
    code(FIGURA_A)

    # ================================================= 4. RELACIONES
    md("""
## 4. Explorar relaciones

La tercera actividad pide analizar relaciones entre las variables relevantes.
Antes de ningún número, dos reglas metodológicas que atraviesan toda la
sección, porque sin ellas los resultados serían falsos.

**Regla 1: todo promedio va ponderado por estudiantes.** Ya vimos que una fila
puede representar 29 chicos o 1.225. Un promedio simple hablaría de
departamentos, no de estudiantes.

**Regla 2: las correlaciones con indicadores de la EPH se calculan a nivel
provincia, no a nivel fila.** Esta es la trampa más fácil del dataset y merece
explicación.

Los valores de la EPH son provinciales: los 136 departamentos de Buenos Aires
tienen todos exactamente el mismo ingreso mediano. Si calculamos una
correlación sobre las 1.174 filas, estamos contando ese único valor 136 veces y
fingiendo tener 136 mediciones independientes. El resultado se vería más
confiable sin que haya más información atrás. Por eso esas correlaciones se
calculan sobre **24 puntos, uno por jurisdicción**.
""")

    code('''
print("Cuantos valores DISTINTOS tiene realmente cada indicador de la EPH:")
for c in ["eph_ipcf_mediano", "eph_adultos_sin_secundaria", "eph_desocupacion"]:
    print(f"  {c:<32} {maestro[c].nunique():>3} valores sobre {len(maestro):,} filas")

deptos = maestro.groupby("jurisdiccion")["departamento"].nunique().sort_values(
    ascending=False)
print()
print(f"Buenos Aires tiene {deptos.iloc[0]} departamentos, todos con el MISMO "
      "valor de EPH.")
print(f"Mediana de departamentos por provincia: {int(deptos.median())}")
''')

    md("""
### 4.1 La brecha: ¿es de gestión o de geografía?
""")

    code('''
brecha = maestro.groupby(["sector", "ambito"]).apply(
    lambda g: pd.Series({
        "matematica_bajo_basico": media_ponderada(g, MATE_BAJO),
        "lengua_bajo_basico": media_ponderada(g, LENGUA_BAJO),
        "sobreedad_alta": media_ponderada(g, SOBREEDAD_ALTA),
        "filas": len(g),
        "estudiantes": g["estudiantes"].sum(),
    }), include_groups=False).sort_values("matematica_bajo_basico")

brecha["% de estudiantes"] = (
    100 * brecha["estudiantes"] / brecha["estudiantes"].sum()).round(1)
brecha.round(4)
''')

    md("""
Leído por movimientos dentro de la tabla:

- Cambiar de **privado a estatal**, quedándose en urbano: de 0,38 a 0,62, sube
  **0,23**
- Cambiar de **urbano a rural**, quedándose en privado: de 0,38 a 0,51, sube
  **0,13**

**El sector pesa casi el doble que el lugar.** Este titular se apoya en las dos
celdas urbanas a propósito, porque entre las dos suman 504.759 estudiantes, el
93,5% del total.

Hay una comparación más llamativa y hay que usarla con cuidado: un estudiante de
estatal urbana (0,62) está peor que uno de privada **rural** (0,51), o sea que
el campo no es lo que lo hunde. Ilustra muy bien, pero privada rural son 36
filas y 3.679 estudiantes, el **0,7% del total**, y es además la celda con mayor
dispersión. Sirve para ilustrar, no para sostener el argumento sola.

Eso último merece su propia verificación.
""")

    code('''
tmp2 = maestro.copy()
tmp2["quintil_tam"] = pd.qcut(
    tmp2["estudiantes"], 5,
    labels=["1 mas chico", "2", "3", "4", "5 mas grande"])
dispersion = tmp2.groupby("quintil_tam", observed=True).agg(
    filas=(MATE_BAJO, "size"),
    estudiantes_mediana=("estudiantes", "median"),
    desvio=(MATE_BAJO, "std"),
    minimo=(MATE_BAJO, "min"),
    maximo=(MATE_BAJO, "max"))

razon = dispersion["desvio"].iloc[0] / dispersion["desvio"].iloc[-1]
print(f"El quintil de grupos mas chicos tiene {razon:.1f} veces la dispersion "
      "del mas grande,")
print("y sus valores llegan a los extremos posibles (0 y 1).")
print()
dispersion.round(3)
''')

    md("""
No es que los grupos chicos sean peores ni mejores: **con pocos casos, un
estudiante más o menos mueve mucho el porcentaje.** De ahí la regla que se
aplica en todo el informe: cualquier número de una celda chica se cita con su
denominador al lado.
""")

    code(FIGURA_B)

    md("""
### 4.2 El contexto socioeconómico y el rendimiento

Es el único análisis que usa las dos fuentes a la vez, o sea el que muestra para
qué sirvió integrarlas en el TP1.
""")

    code('''
provincias = maestro.groupby("jurisdiccion").apply(
    lambda g: pd.Series({
        "ipcf_mediano": g[INGRESO].iloc[0],
        "adultos_sin_secundaria": g["eph_adultos_sin_secundaria"].iloc[0],
        "matematica_bajo": media_ponderada(g, MATE_BAJO),
        "sobreedad_alta": media_ponderada(g, SOBREEDAD_ALTA),
        "estudiantes": g["estudiantes"].sum(),
    }), include_groups=False)

correlaciones = []
for c in [c for c in maestro.columns if c.startswith("eph_")]:
    serie = maestro.groupby("jurisdiccion")[c].first()
    if serie.nunique() < 3:
        continue
    correlaciones.append({
        "indicador_eph": c,
        "r_con_matematica_bajo": serie.corr(provincias["matematica_bajo"]),
        "provincias": int(serie.notna().sum()),
    })

corr = pd.DataFrame(correlaciones)
corr.reindex(corr["r_con_matematica_bajo"].abs()
             .sort_values(ascending=False).index).head(8).round(4)
''')

    md("""
#### Antes de creerle a ese -0,82

Una correlación de Pearson falla de dos maneras conocidas, y conviene atacar las
dos antes de reportar nada.

**Miedo 1: que la sostenga un solo caso raro.** CABA es el sospechoso natural.
Es la jurisdicción más rica del país y la de mejor desempeño, y está sola en ese
rincón del gráfico. Si toda la relación fuera "CABA arriba a la izquierda y el
resto amontonado", sacarla la haría desaparecer.

**Miedo 2: que la relación sea fuerte pero curva.** Pearson solo ve líneas
rectas. Spearman ignora la forma y mira únicamente el **orden**: si la provincia
más rica es la de mejor desempeño, la segunda más rica la segunda, y así. Si
Spearman da más fuerte que Pearson, la relación existe y no es del todo lineal.

La regla que queda para todo el proyecto: **antes de creerle a una correlación,
preguntate quién la sostiene y qué forma tiene.**
""")

    code('''
sin_caba = provincias[~provincias.index.str.contains("Aut")]

pruebas = pd.DataFrame([
    {"prueba": "Pearson, las 24 jurisdicciones", "n": len(provincias),
     "r": provincias["ipcf_mediano"].corr(provincias["matematica_bajo"])},
    {"prueba": "Pearson, sin CABA", "n": len(sin_caba),
     "r": sin_caba["ipcf_mediano"].corr(sin_caba["matematica_bajo"])},
    {"prueba": "Spearman, las 24", "n": len(provincias),
     "r": provincias["ipcf_mediano"].corr(provincias["matematica_bajo"],
                                          method="spearman")},
    {"prueba": "Spearman, sin CABA", "n": len(sin_caba),
     "r": sin_caba["ipcf_mediano"].corr(sin_caba["matematica_bajo"],
                                        method="spearman")},
])
pruebas.round(4)
''')

    md("""
**La relación sobrevive las tres pruebas.** No depende de un outlier ni es un
artefacto de suponer linealidad. Que Spearman dé más fuerte que Pearson sugiere
que la relación es algo curva: el salto entre las provincias más pobres pesa más
que entre las más ricas.

**Y el n es parte del dato.** Son 24 puntos, uno por jurisdicción. Con 24
observaciones, mover dos o tres cambia bastante el resultado. Por eso el número
se cita siempre como *"r = -0,82 sobre 24 jurisdicciones"* y nunca como
*"r = -0,82"* a secas.
""")

    code(FIGURA_C)

    md("""
### 4.3 Qué predice mejor: ¿la escuela o el hogar?

Estas correlaciones sí se calculan a nivel fila, porque las dos variables de
cada par vienen de Aprender y varían entre departamentos.

Se reportan Pearson y Spearman juntos a propósito: si difieren mucho, la
relación no es lineal y el Pearson solo estaría engañando.
""")

    code('''
pares = [
    ("libros_hogar__no_hay_libros_en_formato_papel", MATE_BAJO, "hogar"),
    ("educ_madre__terciariouniversitarioposgrado_completo", MATE_BAJO, "hogar"),
    ("repitencia__repitio_1_vez", MATE_BAJO, "trayectoria"),
    (SOBREEDAD_ALTA, MATE_BAJO, "trayectoria"),
    (SOBREEDAD_ALTA, LENGUA_BAJO, "trayectoria"),
]

filas = []
for a, b, dim in pares:
    sub = maestro[[a, b]].dropna()
    filas.append({
        "variable": a, "dimension": dim,
        "r_pearson": sub[a].corr(sub[b]),
        "r_spearman": sub[a].corr(sub[b], method="spearman"),
        "filas_con_dato": len(sub),
    })

tabla_pares = pd.DataFrame(filas)
tabla_pares.reindex(tabla_pares["r_pearson"].abs()
                    .sort_values(ascending=False).index).round(4)
''')

    md("""
**Las dos variables de hogar le ganan a las dos de trayectoria escolar.** No
tener libros en casa (+0,62) y que la madre haya terminado un terciario o
universitario (-0,62) predicen el desempeño mejor que la repitencia (+0,35) o la
sobreedad (+0,21).

Pearson y Spearman dan parecido en todos los pares, así que ninguna de estas
relaciones es fuertemente no lineal.

### 4.4 Las inasistencias: el hallazgo que no esperábamos

Acá pasó algo que vale contar completo, porque el método importa tanto como el
resultado.

**La primera medición usó una sola categoría, la más extrema (30 faltas o más),
y dio r = +0,000.** La conclusión habría sido que las inasistencias no se
relacionan con el desempeño. Es falso, y el error fue mirar la cola de la
distribución en vez del acumulado: casi nadie cae en la categoría extrema, así
que esa columna casi no varía y no puede correlacionar con nada.
""")

    code('''
acumulados = {
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

pd.DataFrame([{
    "medida": nombre,
    "r_con_matematica_bajo": maestro[cols].sum(axis=1).corr(maestro[MATE_BAJO]),
    "valor_medio_ponderado": np.average(maestro[cols].sum(axis=1),
                                        weights=maestro["estudiantes"]),
} for nombre, cols in acumulados.items()]).round(4)
''')

    md("""
Con el acumulado aparece una relación clara **y contraintuitiva**: cuantos más
chicos de un grupo reportan faltar, **menos** chicos de ese grupo están por
debajo del básico. Y los grupos donde más chicos dicen no faltar nunca son los
de peor desempeño.

La primera sospecha ante algo así es que sea efecto de mezclar poblaciones
distintas (la paradoja de Simpson): si las escuelas privadas rinden mejor y
además reportan más faltas, la correlación podría aparecer sin existir dentro de
ningún grupo. Se descarta calculando la misma correlación **dentro** de cada
celda.
""")

    code('''
cols5 = acumulados["5 o mas faltas"]
tmp = maestro.copy()
tmp["faltas_5mas"] = tmp[cols5].sum(axis=1)

pd.DataFrame([{
    "sector": sec, "ambito": amb, "filas": len(g),
    "r_dentro_del_grupo": g["faltas_5mas"].corr(g[MATE_BAJO]),
    "faltas_5mas_promedio": media_ponderada(g, "faltas_5mas"),
    "matematica_bajo": media_ponderada(g, MATE_BAJO),
} for (sec, amb), g in tmp.groupby(["sector", "ambito"])]).round(4)
''')

    md("""
**No es Simpson: la relación negativa se mantiene en las cuatro celdas**, entre
-0,34 y -0,59.

#### Quién contesta esta pregunta, y por qué importa

Antes de interpretar hay que saber de dónde sale el dato. Lo verificamos en la
fuente oficial: el **Manual del Aplicador de Aprender 2024** dice que *"al
finalizar ambas pruebas, los estudiantes contestarán un cuestionario
complementario"*, y que cada alumno recibe un Cuadernillo del Estudiante con las
hojas para registrar sus respuestas. Hay un cuestionario aparte para directores,
que no es este.

O sea que el dato es **lo que el estudiante dice que faltó**, no un registro
administrativo de asistencia.

#### La hipótesis, explícitamente NO verificada

Aprender evalúa a quien está presente el día de la prueba. En una escuela con
ausentismo real alto, los más ausentes no entran a la muestra. Entre los que sí
rindieron, reportar faltas sería marcador de un alumno presente y conectado con
la escuela, no de riesgo. Se suma que el dato es autorreporte: son **dos capas
de ruido en la misma variable**.

**No lo damos por cierto.** Verificarlo requiere datos de asistencia
administrativa, que este dataset no tiene. Queda como la pregunta abierta más
interesante que deja este trabajo.
""")

    code(FIGURA_D)

    # ===================================================== 5. CURAR
    md("""
## 5. Curar los datos

La cuarta actividad pide hacer las transformaciones necesarias para obtener una
base adecuada para las etapas siguientes, **justificando cada decisión**.

Se tomaron cuatro decisiones y las cuatro son de la misma familia: **hacer
visible un problema en vez de taparlo.** Ninguna borra filas ni modifica
valores.

El criterio que las une: los tres problemas encontrados (clima escolar mal
cubierto, departamentos enmascarados, valores extremos) golpean sobre todo a los
grupos **chicos y rurales**, que son exactamente la población con mayor riesgo
de abandono. Limpiar por el camino fácil habría sesgado el dataset **contra su
propio objeto de estudio**.
""")

    code('''
curado = maestro.copy()

# Decision 1: clima escolar. Tres estados y no un booleano, porque los dos
# problemas son disjuntos y distintos: 96 filas no tienen NINGUN dato y 91 lo
# tienen calculado sobre menos de la mitad de sus estudiantes. Un booleano
# perderia la diferencia entre "no hay dato" y "el dato es flojo", que no son
# lo mismo ni para un modelo ni para una conclusion.
calidad = pd.Series("ok", index=curado.index, dtype="object")
calidad[curado["cob__clima_escolar"] < 0.50] = "cobertura_baja"
calidad[curado["cob__clima_escolar"].isna()] = "sin_dato"
curado["clima_escolar_calidad"] = calidad

# Decision 2: departamentos enmascarados. Se conservan y se identifican. Un
# analisis por departamento filtra es_agregado_provincial == False; uno por
# provincia las necesita para que los totales cierren contra la fuente.
curado["es_agregado_provincial"] = (
    curado["departamento"].astype(str).str.strip().str.upper() == "ENMASCARADO")

# Las decisiones 3 y 4 no modifican el dataset (ver el texto de abajo).

# El invariante de esta etapa: curar no puede cambiar lo que ya habia.
assert len(curado) == len(maestro), "la curacion cambio la cantidad de filas"
for col in maestro.columns:
    assert curado[col].equals(maestro[col]), f"la curacion modifico '{col}'"

print(f"entrada: {len(maestro):,} filas x {maestro.shape[1]} columnas")
print(f"salida : {len(curado):,} filas x {curado.shape[1]} columnas")
print("filas borradas: 0  .  valores modificados: 0   (verificado por assert)")
print()
for col in ["clima_escolar_calidad", "es_agregado_provincial"]:
    print(f"{col}:")
    for valor, n in curado[col].value_counts(dropna=False).items():
        est = curado.loc[curado[col] == valor, "estudiantes"].sum()
        print(f"   {str(valor):<16} {n:>5} filas   {est:>9,.0f} estudiantes "
              f"({100 * est / curado['estudiantes'].sum():>4.1f}%)")
''')

    md("""
### Las cuatro decisiones, con lo que se descartó

**1. Clima escolar: se marca la calidad del dato, no se toca el dato.** Se
agregó `clima_escolar_calidad` con tres estados. *Se descartó imputar*, porque
inventaría valores justo en el segmento donde vive el sesgo, que es el peor
lugar posible. *Se descartó poner en NaN* las 91 filas de baja cobertura, porque
perdería dato real sin dejar rastro visible de la pérdida. *Se descartó sacar el
bloque*, porque tira una variable central del marco teórico por un problema que
toca al 1,8% de los estudiantes.

**2. Departamentos enmascarados: se identifican, no se borran.** *Se descartó
borrarlos*: se irían 10.444 estudiantes de los departamentos más chicos del
país, que es el perfil de mayor riesgo, y los totales por provincia dejarían de
cerrar contra Aprender. *Se descartó solo documentarlo*, porque deja la trampa
disponible para quien no lea el documento.

**3. Valores extremos: no se tocan.** 75 de 94 columnas numéricas tienen valores
a más de 3 rangos intercuartiles del cuerpo de la distribución. Al traducir la
proporción a personas se ve que no son errores: en `edad__21_anos` el 70% de las
filas vale exactamente 0, lo que aplasta el rango intercuartil hasta que el
umbral de "extremo" queda por debajo de lo que aporta **un solo estudiante** en
un grupo de 118. La mediana de estudiantes detrás de las filas marcadas es 2,3
personas. *Se descartó winsorizar*: modificaría datos correctos y borraría
justamente los casos de sobreedad extrema, que son los que el proyecto viene a
estudiar.

**4. `cob__sexo` se conserva pese a tener varianza cero.** Vale exactamente 1,0
en las 1.174 filas: todos respondieron sexo. Una columna constante no aporta a
un modelo, pero esta no es una variable predictiva: es metadato de cobertura, de
la misma familia que las otras 15 `cob__`, y nunca iba a entrar a un modelo.
Mantiene simétrica la familia y su valor constante es en sí mismo una
verificación: si alguna vez deja de ser 1,0, algo cambió.

### ¿Alguna de estas decisiones cambia una conclusión?

La pregunta correcta para cerrar la curación, y se puede medir.
""")

    code('''
escenarios = {
    "todo el dataset": curado,
    "sin agregados provinciales": curado[~curado["es_agregado_provincial"]],
    "solo clima escolar 'ok'": curado[curado["clima_escolar_calidad"] == "ok"],
    "sin discrepancia entre bases": curado[~curado["flag_discrepancia_bases"]],
}

efecto = pd.DataFrame([{
    "escenario": nombre,
    "filas": len(sub),
    "matematica_bajo": media_ponderada(sub, MATE_BAJO),
    "sobreedad_alta": media_ponderada(sub, SOBREEDAD_ALTA),
    "clima_escolar_bajo": media_ponderada(sub, "clima_escolar__bajo"),
} for nombre, sub in escenarios.items()])

base = efecto.iloc[0]
for col in ["matematica_bajo", "sobreedad_alta", "clima_escolar_bajo"]:
    efecto[f"delta_{col}_pct"] = (
        100 * (efecto[col] - base[col]) / base[col]).round(2)

efecto[["escenario", "filas", "matematica_bajo", "delta_matematica_bajo_pct",
        "delta_sobreedad_alta_pct", "delta_clima_escolar_bajo_pct"]].round(4)
''')

    md("""
**Ninguna decisión de curación mueve ningún número más de 1%.**

Eso no significa que las decisiones sobraran: significa que los problemas
estaban acotados, y que ahora están acotados **y medidos**. La diferencia entre
las dos situaciones es que antes nadie podía afirmarlo.

Y para el TP3 el valor es otro: cuando un modelo dé un resultado distinto al
excluir estas filas, va a haber una columna que lo explique en vez de un
misterio.
""")

    code('''
curado.to_csv("dataset_maestro_curado.csv", index=False, encoding="utf-8")
print(f"dataset curado guardado: {len(curado):,} filas x {curado.shape[1]} columnas")
print("Es el segundo producto que pide la consigna.")
''')

    # ============================================ 6. HALLAZGOS
    md("""
## 6. Hallazgos y preguntas nuevas

### ¿Qué encontramos en los datos?

El contexto socioeconómico provincial se relaciona fuerte con el desempeño
(**r = -0,82 sobre 24 jurisdicciones**, robusto sin CABA y por Spearman). La
brecha más grande del sistema es **de gestión y no de geografía**: dentro del
mismo ámbito urbano, pasar de privado a estatal mueve el desempeño 0,23,
mientras que pasar de urbano a rural dentro de privado lo mueve 0,13. Y las
variables de **hogar** (libros, educación de la madre) predicen mejor que las de
trayectoria escolar (repitencia, sobreedad).

### ¿Qué problemas de calidad detectamos?

El dataset está sano: 8 de 12 chequeos dan cero, y de los cuatro restantes
dos son informativos. Los dos que no: el valor
centinela `"Enmascarado"` en `departamento`, que rompe el significado de la
clave territorial en 23 de 24 jurisdicciones; y la **cobertura sesgada del
bloque de clima escolar**, que cae de 0,92 en los grupos grandes a 0,72 en los
chicos, o sea que está peor medido justo donde el proyecto más mira.

### ¿Qué decisiones de curación tomamos?

Cuatro, todas de la misma familia: hacer visible el problema en vez de taparlo.
Dos columnas nuevas (`clima_escolar_calidad` y `es_agregado_provincial`) y dos
decisiones de no tocar nada (extremos y `cob__sexo`). **Cero filas borradas,
cero valores modificados**, verificado por assert. Y ninguna mueve un número más
de 1%.

### ¿Qué variables o relaciones parecen especialmente interesantes?

El ingreso per cápita familiar provincial, por lejos. Los libros en el hogar y
la educación de la madre, que le ganan a los marcadores escolares. Y el sector
de gestión, que es la única de las cuatro accionable desde política pública.

### ¿Qué nuevas preguntas surgieron?

**Primera y más urgente: el proyecto no tiene una variable de abandono.** El
proxy construido en el TP1 desde la EPH correlaciona +0,16 con el desempeño, o
sea que no mide lo que dice medir. Todo este trabajo describe desempeño y
sobreedad, que son antecedentes plausibles del abandono, no el abandono. Sin
resolver esto, el TP3 no tiene qué predecir.

**Segunda: ¿por qué reportar más faltas se asocia con mejor desempeño?** La
hipótesis de selección del censo es plausible y no está verificada. Requiere
datos de asistencia administrativa.

**Tercera: ¿es la EPH la fuente correcta para el contexto?** Solo releva 32
aglomerados urbanos, así que fuera de ellos no hay ni un hogar encuestado, y
todo lo rural queda representado por el promedio de su provincia. El **Censo
2022** llega a todos los departamentos e incluye educación, vivienda y
hacinamiento. Es candidato a reemplazarla, y queda como propuesta a evaluar, no
verificada contra los archivos.
""")

    # ========================================== 7. LIMITACIONES
    md("""
## 7. Limitaciones

Van juntas y explícitas, porque son el estado real del proyecto y no
advertencias de trámite.

**No hay variable de abandono.** Es la limitación principal: el objetivo del
proyecto todavía no tiene con qué medirse.

**Todas las correlaciones son ecológicas.** Valen entre agregados territoriales
y no autorizan a concluir nada sobre un estudiante concreto. Sabemos que *los
departamentos* con más hogares sin libros tienen peor desempeño; **no** sabemos
que un chico sin libros rinda peor. Podría ser que en esos departamentos el
problema sea otro y lo de los libros solo lo acompañe. Importa especialmente acá
porque el proyecto quiere identificar estudiantes en riesgo, y con datos
agregados no se llega al estudiante.

**El contexto socioeconómico es provincial.** Dos departamentos muy distintos de
la misma provincia reciben el mismo valor. Es la limitación central heredada del
TP1.

**Los períodos no coinciden.** Aprender se tomó en octubre de 2024 y la EPH que
usamos es del tercer trimestre de **2025**. La consigna del TP1 pedía 3T-2024;
se usó 2025 porque es el archivo disponible en el repositorio del proyecto. En
un país con nuestra inflación, un año de diferencia en una variable de ingresos
no es menor.

**La pregunta por diferencias según sexo no se puede responder** con esta base.
Las columnas `sexo__*` dicen qué porcentaje del grupo son varones o mujeres; no
dicen cómo le fue a cada sexo. Para eso haría falta el desempeño desagregado por
sexo, que la base agregada de Aprender no publica. Es la misma pared que el TP1
declaró: la unidad de análisis es el grupo territorial y no el estudiante.

**El bloque de clima escolar tiene cobertura sesgada**, ya descrito, y por eso
viaja con su columna de calidad al lado.

---

## Cierre

Este entregable no responde la pregunta del proyecto: la deja mejor planteada.
Sabemos qué tiene la base, dónde falla, qué decidimos sobre cada falla y por
qué, y sobre todo **qué nos falta para poder modelar**, que es una variable de
abandono real.

Todo lo de este notebook se reproduce desde el repositorio del proyecto, donde
el pipeline está organizado en etapas con contrato explícito de entradas y
salidas, y 55 verificaciones automáticas que corren sobre los datos.
""")
