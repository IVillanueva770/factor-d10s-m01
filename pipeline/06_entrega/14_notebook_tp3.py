"""Genera el notebook de Colab del TP3 (Machine Learning).

Igual que en el TP1 y el TP2, el .ipynb es una SALIDA: se genera desde aca y
no se edita a mano. Los numeros que aparecen en el texto se leen de las
salidas del pipeline al generar, nunca se escriben a mano, asi que el texto y
las tablas no pueden decir cosas distintas.

Orden del notebook: lo de alto impacto primero (devolucion del TP2 y reunion
del 09/09: "la ultima seccion deberia ir al comienzo", "pensar que se lo
planteamos a un stakeholder"), y el como despues. Sin jerga en el texto: lo
tecnico vive en las celdas de codigo y en el pipeline.

En Colab el notebook clona el repo del proyecto fijado al commit del codigo,
reconstruye el dataset curado desde el maestro versionado y corre las etapas
12 a 18. No embebe resultados: los produce.
"""

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"
INTERIM = BASE_DIR / "data" / "interim"
RAW_RA = BASE_DIR / "data" / "raw" / "relevamiento"

sys.path.insert(0, str(BASE_DIR / "pipeline"))
from modelado import ANIO_RELEVAMIENTO, ANIOS_TARGET, PROVINCIAS_7_5  # noqa: E402

# Las fuentes citadas, como enlaces de markdown. TODAS salen de
# entregas/03-machine-learning/FUENTES-TP3.md, que es la fuente unica de citas:
# no se agrega una cita que no este ahi.
_ZIP_METODOLOGICOS = ("https://www.argentina.gob.ar/sites/default/files/2018/04/"
                      "documentos_metodologicos_3.10.zip")
_APRENDER_2024 = ("https://www.argentina.gob.ar/sites/default/files/"
                  "informe_nacional_aprender_2024.pdf")
_ADROGUE = ("https://ri.conicet.gov.ar/bitstream/handle/11336/267725/"
            "CONICET_Digital_Nro.edd2aab9-34e4-449f-a0c2-93e0f205899b_B.pdf?sequence=2")
_UNICEF = ("https://www.unicef.org/argentina/media/18746/file/"
           "Serie%20MICS:%20Adolescencias%20y%20Educaci%C3%B3n.pdf")
_ARGXEDU_2023 = ("https://argentinosporlaeducacion.org/wp-content/uploads/2023/09/"
                 "Trayectorias-escolares-Cuantos-estudiantes-abandonan-la-secundaria-"
                 "en-Argentina-1.pdf")
_CUADERNILLO_RA = "https://cge.entrerios.gov.ar/wp-content/uploads/cei/2025-COMUN-TP.pdf"
_DGCYE = ("https://abc.gob.ar/secretarias/sites/default/files/2022-11/"
          "MANUAL%20METODOL%C3%93GICO%20DE%20INDICADORES%20EDUCATIVOS%202022.pdf")
CITA = {
    "adrogue": f"[Adrogué y Orlicki, 2025]({_ADROGUE})",
    "unicef": f"[UNICEF Argentina, 2022]({_UNICEF})",
    "boniolo": "[Boniolo y Najmias, 2018](https://ri.conicet.gov.ar/handle/11336/99328)",
    "argxedu": f"[Argentinos por la Educación, 2023]({_ARGXEDU_2023})",
    "sobreedad": ("[Subsecretaría de Información y Evaluación Educativa, 2024]"
                  "(https://www.argentina.gob.ar/sites/default/files/"
                  "historias_con_datos_sobredad_final.pdf)"),
    "aprender": f"[Aprender 2024]({_APRENDER_2024})",
    "berlinski": ("[Berlinski, Cruces, Galiani, Gertler y Gonzalez, 2025]"
                  "(https://ideas.repec.org/p/nbr/nberwo/34552.html)"),
    "berlinski08": ("[Berlinski, Galiani y Manacorda, 2008]"
                    "(https://econ.umd.edu/publication/"
                    "giving-children-better-start-preschool-attendance-and-school-age-profiles)"),
    "albornoz": ("[Albornoz, Furman, Podestá, Razquin y Warnes, 2016]"
                 "(https://ri.conicet.gov.ar/bitstream/handle/11336/47190/"
                 "CONICET_Digital_Nro.1b4e72c0-8b30-4864-9922-fb8e27908f0a_A.pdf"
                 "?sequence=2&isAllowed=y)"),
    "definiciones": f"[DiNIECE y RedFIE, c. 2003, p. 7]({_ZIP_METODOLOGICOS})",
    "manual_ind": f"[DiNIECE, c. 2005, indicador 40]({_ZIP_METODOLOGICOS})",
    "cuadernillo": f"[cuadernillo nacional del Relevamiento Anual 2025, sección 3.12]({_CUADERNILLO_RA})",
    "cuadernillo_c": f"[cuadernillo del Relevamiento Anual 2025]({_CUADERNILLO_RA})",
    "caba": ("[glosario de la Ciudad de Buenos Aires]"
             "(https://buenosaires.gob.ar/equidadycalidadeducativa/glosario/"
             "indicadores-de-eficiencia-interna)"),
    "dgcye": f"[DGCyE, 2022, p. 29]({_DGCYE})",
    "diee": ("[DIEE, Documento metodológico de las Bases Usuarias del Relevamiento Anual]"
             "(https://www.argentina.gob.ar/sites/default/files/documento_metodologico.pdf)"),
}
DESTINO = (BASE_DIR / "entregas" / "03-machine-learning"
           / "TP3_Machine_Learning_El_Factor_D10S.ipynb")


def git(*args):
    return subprocess.run(["git", "-C", str(BASE_DIR), *args],
                          capture_output=True, text=True).stdout.strip()


def pct(x, d=2):
    return f"{100 * x:.{d}f}%".replace(".", ",")


def num(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


def miles(x):
    return f"{x:,.0f}".replace(",", ".")


celdas = []


def md(texto):
    celdas.append({"cell_type": "markdown", "metadata": {},
                   "source": texto.strip().splitlines(keepends=True)})


def code(texto):
    celdas.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                   "outputs": [], "source": texto.strip("\n").splitlines(keepends=True)})


def cifras():
    """Todo numero que cita el texto sale de aca."""
    d = pd.read_csv(PROC / "dataset_modelado.csv", low_memory=False)
    r = pd.read_csv(PROC / "resultados_experimentos.csv")
    est = pd.read_csv(INTERIM / "relevamiento_estabilidad.csv").set_index("anios")
    err = pd.read_csv(PROC / "errores_principal.csv")
    perf = pd.read_csv(PROC / "perfiles_no_alto.csv")

    def auc(exp, sep, mod):
        fila = r[(r.experimento == exp) & (r.separacion == sep) & (r.modelo == mod)]
        return float(fila["roc_auc"].iloc[0])

    prov = err[err["corte"] == "provincia"].set_index("valor")
    c = {
        "n": len(d),
        "estudiantes": d["estudiantes"].sum(),
        "ssp": d["ssp_ultimos2"].sum(),
        "ini": d["inicial_ultimos2"].sum(),
        "ceros": int((d["tasa_ultimos2"] == 0).sum()),
        "corte": d.loc[d["alto_ultimos2_nacional"] == 1, "tasa_ultimos2"].min(),
        "positivos": int(d["alto_ultimos2_nacional"].sum()),
        "est_rho2": est.loc["ultimos2", "spearman"],
        "est_rep2": est.loc["ultimos2", "repite_alto"],
        "est_rhoS": est.loc["secundaria", "spearman"],
        "est_repS": est.loc["secundaria", "repite_alto"],
        "auc_log": auc("principal", "estratificada", "logistica"),
        "auc_boost": auc("principal", "estratificada", "boosting"),
        "auc_prov": auc("principal", "estratificada", "provincia"),
        "auc_sa": auc("principal", "estratificada", "sector_ambito"),
        "auc_log_pp": auc("principal", "por_provincia", "logistica"),
        "auc_sa_pp": auc("principal", "por_provincia", "sector_ambito"),
        "auc_edif": auc("con_edificio", "estratificada", "logistica"),
        "auc_eph": auc("con_eph", "estratificada", "logistica"),
        "auc_eph_b": auc("con_eph", "estratificada", "boosting"),
        "auc_sec_log": auc("secundaria_entera", "estratificada", "logistica"),
        "auc_sec_prov": auc("secundaria_entera", "estratificada", "provincia"),
        "auc_cp_log": auc("corte_por_provincia", "estratificada", "logistica"),
        "auc_cp_sa": auc("corte_por_provincia", "estratificada", "sector_ambito"),
        # 13/10: la provincia y el perfil juntos, y el corte movido al tercio y
        # al quinto superior (pyp = provincia y perfil; no confundir con _pp,
        # que es la separacion por provincia).
        "auc_pyp_log": auc("provincia_y_perfil", "estratificada", "logistica"),
        "auc_pyp_boost": auc("provincia_y_perfil", "estratificada", "boosting"),
        "auc_t_log": auc("corte_tercio", "estratificada", "logistica"),
        "auc_t_prov": auc("corte_tercio", "estratificada", "provincia"),
        "auc_q_log": auc("corte_quinto", "estratificada", "logistica"),
        "auc_q_prov": auc("corte_quinto", "estratificada", "provincia"),
        "ba_altos": int(prov.loc["Buenos Aires", "altos_reales"]),
        "ba_det": int(prov.loc["Buenos Aires", "detectados"]),
        "ba_fa": int(prov.loc["Buenos Aires", "falsas_alarmas"]),
        "sf_altos": int(prov.loc["Santa Fe", "altos_reales"]),
        "sf_det": int(prov.loc["Santa Fe", "detectados"]),
        "perf_k": len(perf),
        "perf_no_vistos": int(perf["altos_no_vistos"].sum()),
    }
    # El perfil que concentra mas altos no vistos: se nombra por sus rasgos y
    # se chequea que sea el que el texto dice (estatal urbano), no se supone.
    top = perf.loc[perf["altos_no_vistos"].idxmax()]
    if not (top["estatal"] > 0.5 and top["rural"] < 0.5):
        raise SystemExit("El perfil con mas altos no vistos ya no es el estatal urbano: "
                         "revisar el texto de la seccion 8")
    c["perf_top_nv"] = int(top["altos_no_vistos"])
    c["perf_top_est"] = top["estudiantes"] / perf["estudiantes"].sum()
    por_prov = d.groupby("jurisdiccion")[["ssp_ultimos2", "inicial_ultimos2"]].sum()
    tasa_prov = por_prov["ssp_ultimos2"] / por_prov["inicial_ultimos2"]
    c["prov_min"], c["prov_min_n"] = tasa_prov.min(), tasa_prov.idxmin()
    c["prov_max"], c["prov_max_n"] = tasa_prov.max(), tasa_prov.idxmax()
    # Por que no un modelo por provincia: cuantos grupos y positivos tiene cada una.
    n_prov = d["jurisdiccion"].nunique()
    c["grupos_x_prov"] = len(d) / n_prov
    c["pos_x_prov"] = c["positivos"] / n_prov

    # El texto dice "cada uno solo ordena parecido, juntos mejor" y "con el
    # tercio y el quinto quedan parejos": se chequea, no se supone.
    parejo = 0.02
    if abs(c["auc_log"] - c["auc_prov"]) > parejo:
        raise SystemExit("El perfil solo y la provincia sola ya no ordenan parecido: "
                         "revisar la conclusion 2")
    if c["auc_pyp_log"] <= max(c["auc_log"], c["auc_prov"]):
        raise SystemExit("Provincia y perfil juntos ya no mejoran a cada uno solo: "
                         "revisar la conclusion 2")
    if (abs(c["auc_t_log"] - c["auc_t_prov"]) > parejo
            or abs(c["auc_q_log"] - c["auc_q_prov"]) > parejo):
        raise SystemExit("Con el tercio o el quinto el perfil y la provincia ya no "
                         "quedan parejos: revisar la robustez del corte")

    # Buenos Aires a lo largo de la serie del Relevamiento (secundaria entera,
    # con la regla de anios de modelado.py): apoyo de la hipotesis del registro.
    es_7_5 = "buenos aires" in PROVINCIAS_7_5
    indices = ANIOS_TARGET["secundaria"](es_7_5)
    cols = [f"{pre}_{i}" for pre in ("ssp", "inicial") for i in indices]
    tray = pd.read_csv(RAW_RA / "Trayectoria_Sexo_Final.csv",
                       usecols=["anio", "provincia", *cols], low_memory=False)
    tray = tray[tray["provincia"].str.strip().str.lower() == "buenos aires"]
    for col in cols:
        tray[col] = pd.to_numeric(tray[col], errors="coerce").fillna(0)
    serie = tray.groupby("anio")[cols].sum()
    tasa_ba = (serie[[f"ssp_{i}" for i in indices]].sum(axis=1)
               / serie[[f"inicial_{i}" for i in indices]].sum(axis=1))
    c["ba_anio_ini"] = int(tasa_ba.index.min())
    c["ba_anio_fin"] = ANIO_RELEVAMIENTO
    c["ba_tasa_ini"] = tasa_ba.loc[c["ba_anio_ini"]]
    c["ba_tasa_fin"] = tasa_ba.loc[ANIO_RELEVAMIENTO]
    return c


def construir(slug, commit):
    c = cifras()
    C = CITA
    celdas.clear()

    md(f"""
# El Factor D10S · Machine Learning

**Entregable 3 de la mentoría** · Grupo M01 · Mentora: Noelia Ferrero
Diplomatura en Ciencia de Datos · FAMAF, UNC

## Lo que encontramos, en cinco líneas

1. **Se puede ordenar qué grupos de escuelas tienen más riesgo de abandono** con lo que
   Aprender cuenta de los chicos y de sus hogares: el modelo acierta el orden en
   {pct(c['auc_log'], 0)} de los pares (un sorteo acertaría el 50%).
2. **La provincia y el perfil de los estudiantes aportan información distinta.** Cada
   uno solo ordena el riesgo parecido: la provincia sola acierta en
   {pct(c['auc_prov'], 0)} de los pares, casi lo mismo que el perfil. Juntos, en un mismo
   modelo, llegan a **{pct(c['auc_pyp_log'], 0)}**: lo que sabe uno no lo sabe el otro.
3. **Sin conocer la provincia, el perfil de los chicos sigue diciendo algo**:
   probado en provincias que nunca vio, el modelo llega a {pct(c['auc_log_pp'], 0)},
   contra {pct(c['auc_sa_pp'], 0)} de la regla "estatal o privado, urbano o rural".
4. **La tasa registrada cambia mucho de una provincia a otra**: va de
   {pct(c['prov_min'], 1)} en {c['prov_min_n']} a {pct(c['prov_max'], 1)} en {c['prov_max_n']}.
   Pensamos que una parte es la forma de registrar y no abandono real, pero es una
   hipótesis nuestra: el documento oficial del Relevamiento sostiene que los datos son
   comparables entre provincias, y no encontramos ninguno que advierta lo contrario
   (sección 6).
5. **Lo que más acompaña al abandono coincide con lo que ya documenta la investigación
   argentina**: hogares de menor nivel socioeconómico, madres con menos educación, haber
   repetido y tener más edad de la que corresponde. Lo del jardín y lo de la gestión
   estatal está documentado solo en parte. Es asociación entre grupos, no causa
   (sección 7, con las fuentes).

## Qué haríamos con esto

- **Usar la provincia y el perfil juntos para ordenar dónde mirar primero**: juntos
  ordenan mejor que cada uno por separado.
- **Antes de comparar provincias entre sí, revisar con ellas cómo registran las salidas
  sin pase**: es la pregunta que este trabajo no puede cerrar y la que más cambia el
  resultado.
- **Sumar el Relevamiento 2025** cuando se publique: trae las salidas del ciclo 2024, el
  mismo en el que se tomó Aprender.

---

Lo que sigue explica cómo llegamos a esto: el problema (1), qué predecimos (2),
con qué datos (3), las reglas simples contra las que nos medimos (4), los modelos (5),
dónde se equivocan (6), qué aprendimos (7), los perfiles que el modelo no marca (8),
las limitaciones (9), qué sigue (10) y qué es hallazgo nuestro y qué ya se sabía (11).
El código vive en el repo del proyecto,
[github.com/{slug}](https://github.com/{slug}), y este notebook lo corre fijado al
commit `{commit[:7]}`.
""")

    code(f"""
# Prepara el entorno: baja el proyecto fijado a un commit y corre el pipeline del TP3.
# Tarda alrededor de un minuto. Cada etapa imprime lo que mide.
import os, subprocess, sys
if not os.path.exists("factor-d10s-m01"):
    subprocess.run(["git", "clone", "-q", "https://github.com/{slug}.git", "factor-d10s-m01"], check=True)
os.chdir("factor-d10s-m01")
subprocess.run(["git", "checkout", "-q", "{commit}"], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], check=True)
print("Proyecto en el commit", subprocess.run(["git", "rev-parse", "--short", "HEAD"],
      capture_output=True, text=True).stdout.strip())
""")

    code("""
# El dataset curado del TP2 se reconstruye desde el maestro del TP1, que está versionado.
!python pipeline/03_curacion/08_curar.py > /dev/null && echo "dataset curado listo"
""")

    md(f"""
## 1. El problema y qué representa cada fila

Queremos saber **dónde se concentra el abandono escolar en el secundario**. La
consigna nos pide primero contestar cinco preguntas, y las contestamos antes de
tocar un modelo:

- **¿Qué representa una fila?** Un grupo de escuelas: una provincia, un departamento,
  estatal o privado, urbano o rural. Son {miles(c['n'])} grupos que juntan a
  {miles(c['estudiantes'])} estudiantes que rindieron Aprender. **No es un estudiante**:
  Aprender solo se publica agregado.
- **¿Qué queremos predecir?** Si un grupo tiene **abandono alto**: si la proporción de
  estudiantes de los dos últimos años que dejaron la escuela sin pasar a otra está
  entre el cuarto más alto del país.
- **¿Existe una variable que lo observe?** Sí, y no la inventamos: las **salidas sin
  pase** del Relevamiento Anual, que completa cada escuela para el Ministerio. La
  definición oficial: salido sin pase es "el que se va de la escuela a la que asistía,
  sin inscripción (o pase) en otra escuela" ({C['definiciones']}). No es el abandono
  interanual oficial, que además cuenta a quienes no se vuelven a inscribir al año
  siguiente ({C['manual_ind']}); lo retomamos en la sección 10.
- **¿Qué información está disponible antes del resultado?** Lo que Aprender cuenta de
  los chicos y sus hogares, el sector, el ámbito y el tamaño del grupo. **No usamos** los
  no promovidos, los pases ni los egresados del mismo año: salen del mismo cierre de
  ciclo que el abandono, y usarlos sería mirar la respuesta.
- **¿Qué podemos afirmar?** Cosas sobre grupos, nunca sobre una persona; asociaciones,
  nunca causas.

**Por qué dos fuentes y no una.** Aprender lo responde el estudiante el día de la prueba:
dice cómo le va y cómo vive, pero **no puede ver el abandono**, porque el que ya se fue no
rinde. El Relevamiento lo completa la escuela: cuenta quién se fue, pero no sabe nada del
hogar de los chicos. Juntas permiten preguntar qué características de los chicos
acompañan a las tasas de abandono que registra el sistema.

**Un solo año, 2024.** La mentora nos pidió trabajar con una sola época. El resumen de esa
reunión dice "2025", pero no hay Aprender de secundaria 2025 (se toma 2022 y 2024) ni
Relevamiento publicado de 2025, así que todo sale de los archivos 2024 (el del Relevamiento
trae las salidas del ciclo 2023: sección 2). La encuesta de hogares (EPH), que es
de 2025 y solo existe por provincia, queda afuera del modelo principal y se prueba aparte
(sección 5).
""")

    md(f"""
## 2. Qué predecimos, y cómo lo construimos

**La regla, igual para todos los grupos:**

> tasa de abandono = salidas sin pase de los dos últimos años ÷ matrícula inicial de esos
> mismos años. **Abandono alto** = tasa en el cuarto superior del país
> (en estos datos, {pct(c['corte'])} o más).

- **Por qué los dos últimos años.** Es la misma población que evalúa Aprender. La secundaria
  no dura lo mismo en todo el país (en 12 provincias es 7 de primaria y 5 de secundaria, en
  las otras 12 es 6 y 6), pero los dos últimos años caen en el mismo lugar en todas.
- **Por qué clases y no el número.** La mentora propuso un enfoque en dos etapas (primero
  separar grupos con y sin abandono alto, después mirar por dentro a los que quedan sin
  marcar), y eso pide clases. Además la tasa tiene muchos ceros: {miles(c['ceros'])} de
  {miles(c['n'])} grupos no registran ninguna salida.
- **Lo que mide en total:** {miles(c['ssp'])} salidas sin pase sobre {miles(c['ini'])}
  estudiantes, **{pct(c['ssp'] / c['ini'])}**. Es un fenómeno chico y desparejo.
""")
    code("""
!python pipeline/05_modelado/12_bajar_relevamiento.py
!python pipeline/05_modelado/13_relevamiento.py
""")
    md(f"""
**Dos cosas que medimos y que limitan lo que se puede decir:**

- **El target es inestable de un año a otro.** De los grupos con abandono alto en el
  archivo 2024, solo el {pct(c['est_rep2'], 0)} ya lo tenía en el archivo anterior (con la
  secundaria entera sube a {pct(c['est_repS'], 0)}). En grupos chicos, una sola salida
  mueve la tasa entera.
- **El archivo "2024" del Relevamiento trae las salidas del ciclo 2023.** Primero lo
  inferimos de los datos (su matrícula de último año coincide con la de 2023 y no con la de
  2024) y después lo encontramos documentado: el Relevamiento informa la trayectoria del
  ciclo lectivo anterior. El de 2025 pregunta por la "Trayectoria de matrícula durante el
  ciclo lectivo 2024", con las salidas producidas "entre el 30 de abril de 2024 y el último
  día de clase del período escolar del año 2024" ({C['cuadernillo']}; lo confirma el
  {C['caba']}). El abandono que medimos es entonces del ciclo anterior a Aprender, que se
  tomó en octubre de 2024. Lo usamos igual, porque es el último archivo publicado, y lo
  dejamos declarado.
""")

    md("""
## 3. Los datos y cómo los preparamos

Partimos del dataset curado del TP2 y le sumamos el Relevamiento por la misma clave. El cruce
imprime su denominador: si no encontrara su par al menos el 95% de los estudiantes, la etapa
se corta.
""")
    code("""
!python pipeline/05_modelado/14_dataset_modelado.py
""")
    md("""
**Qué entra al modelo, en bloques que se pueden prender y apagar:**

| Bloque | Qué es |
|---|---|
| Aprender | las proporciones de cada respuesta en el grupo: hogar, educación de la madre y el padre, nivel socioeconómico, repitencia, sobreedad, inasistencias, desempeño en lengua y matemática |
| Contexto | estatal o privado, urbano o rural, tamaño del grupo |
| Edificio (prueba) | proporción de escuelas con electricidad, sala de informática, biblioteca, internet |
| EPH (prueba) | dos indicadores de la provincia: ingreso mediano y adultos sin secundaria |

Los faltantes (por ejemplo, el clima escolar, que no tiene dato en 96 grupos) se completan
con la mediana **dentro de cada partición de entrenamiento**, nunca mirando los datos con
los que se evalúa.
""")

    md(f"""
## 4. Las reglas simples contra las que nos medimos

Un modelo solo vale si le gana a una regla que cualquiera podría aplicar sin modelo:

- **Nadie sabe nada**: a todos el mismo riesgo. Ordena como un sorteo.
- **Sector y ámbito**: el riesgo de un grupo es el de su celda (estatal urbano, estatal
  rural, privado urbano, privado rural).
- **La provincia**: el riesgo de un grupo es el de su provincia.

## 5. Los modelos, y cómo los comparamos

Probamos dos modelos: una **regresión logística**, porque es simple y se puede leer, y uno de
**árboles combinados** (boosting), por si el patrón no es lineal. Todos, reglas y modelos, se evalúan
igual: cinco particiones, cada grupo predicho por un modelo que no lo vio, con semilla fija.

Medimos con el **área bajo la curva ROC** (qué tan bien ordena: 0,5 es azar, 1 es perfecto)
y la **precisión y la cobertura** al marcar como alto al cuarto de grupos con más riesgo. No
usamos solo el acierto: con un cuarto de positivos, decir "nadie tiene abandono alto" ya
acierta el 75%.
""")
    code("""
!python pipeline/05_modelado/15_experimentos.py
""")
    code("""
import pandas as pd
r = pd.read_csv("data/processed/resultados_experimentos.csv")
nombres = {"prevalencia": "Nadie sabe nada", "sector_ambito": "Regla: sector y ámbito",
           "provincia": "Regla: la provincia", "logistica": "Regresión logística",
           "boosting": "Árboles combinados"}
t = r[r.experimento == "principal"].assign(modelo=lambda x: x.modelo.map(nombres))
t.pivot(index="modelo", columns="separacion", values="roc_auc").round(3)
""")
    code("""
from IPython.display import Image
!python pipeline/05_modelado/18_figuras.py > /dev/null
Image("figuras/tp3_a_modelo_vs_reglas.png")
""")
    md(f"""
**Lo que dice la tabla:**

- Con todas las provincias en el entrenamiento, la regresión logística llega a
  **{num(c['auc_log'])}**, la regla de la provincia a **{num(c['auc_prov'])}** y la de
  sector y ámbito a **{num(c['auc_sa'])}**. Solos, el perfil de los chicos y la provincia
  ordenan casi igual. El de árboles ({num(c['auc_boost'])}) no mejora a la regresión: el
  patrón es casi lineal.
- Probando en provincias que el modelo nunca vio, la regla de la provincia no tiene nada que
  decir y cae al azar, y el modelo llega a **{num(c['auc_log_pp'])}** contra
  **{num(c['auc_sa_pp'])}** de sector y ámbito. **Lo que sabemos de los chicos sirve aun sin
  saber dónde están.**

**La provincia y el perfil juntos.** Que ordenen casi igual no quiere decir que sepan lo
mismo. Para verlo, armamos un único modelo que conoce las dos cosas (una columna por
provincia, más el perfil): llega a **{num(c['auc_pyp_log'])}** (con árboles,
{num(c['auc_pyp_boost'])}). Si la provincia solo resumiera el perfil de sus chicos, sumarla no
agregaría nada; agrega, así que **cada uno aporta información que el otro no tiene**. Lo
probamos así y no con un modelo por provincia porque cada provincia tiene unos
{c['grupos_x_prov']:.0f} grupos y unos {c['pos_x_prov']:.0f} con abandono alto: no alcanza para
entrenar ni para evaluar un modelo propio.

**Las combinaciones que probamos además** (todas en la tabla de abajo):

- **Mover el corte de "abandono alto"** del cuarto superior al tercio o al quinto superior no
  cambia la conclusión: el perfil solo y la provincia sola quedan parejos
  ({num(c['auc_t_log'])} contra {num(c['auc_t_prov'])} con el tercio; {num(c['auc_q_log'])}
  contra {num(c['auc_q_prov'])} con el quinto). El cuarto superior es una decisión nuestra, y
  la probamos: aguanta.
- **Sumar el edificio** lleva la regresión a {num(c['auc_edif'])}: casi nada.
- **Sumar la EPH** la deja en {num(c['auc_eph'])} (el de árboles llega a {num(c['auc_eph_b'])}).
  Como pidió la mentora, la probamos acotada, y no aporta: lo que la EPH mide de cada
  provincia (ingreso, educación de los adultos) ya lo dice Aprender. Lo que la provincia
  agrega por encima del perfil es otra cosa, que estos datos no nombran: puede ser algo
  propio de cada provincia o su forma de registrar (sección 6).
- **Con la secundaria entera** como target, la regla de la provincia sube a
  {num(c['auc_sec_prov'])} y el modelo queda en {num(c['auc_sec_log'])}: ahí la provincia
  explica todavía más.
- **Con el corte dentro de cada provincia** (abandono alto respecto de su provincia), el
  modelo llega a {num(c['auc_cp_log'])} contra {num(c['auc_cp_sa'])} de sector y ámbito.
""")
    code("""
t = r[r.separacion == "estratificada"].assign(modelo=lambda x: x.modelo.map(nombres))
t.pivot(index="experimento", columns="modelo", values="roc_auc").round(3)
""")

    md(f"""
## 6. Dónde se equivoca

Miramos los errores del modelo principal por tamaño del grupo, por sector y ámbito y por
provincia.
""")
    code("""
!python pipeline/05_modelado/16_errores.py
""")
    md(f"""
- **Los errores no son parejos entre provincias, y eso es lo más importante.** En Buenos
  Aires hay {c['ba_altos']} grupos con abandono alto y el modelo detecta {c['ba_det']}, pero
  marca otros {c['ba_fa']} que el registro da como bajos: **por el perfil de sus chicos, esos
  grupos "deberían" tener más abandono del que figura.** En Santa Fe pasa al revés:
  {c['sf_altos']} grupos con abandono alto y el modelo detecta {c['sf_det']}. O el registro
  de cada provincia mide distinto, o hay algo de cada provincia que Aprender no ve. Con estos
  datos no lo podemos distinguir.
- **Que el registro cambie entre provincias es una hipótesis nuestra, no un dato oficial.**
  El documento oficial del Relevamiento sostiene lo contrario: el sistema "garantiza la
  homogeneidad y comparabilidad de los datos en todo el ámbito nacional" ({C['diee']}). No
  encontramos ningún documento oficial que advierta diferencias entre provincias en cómo se
  registra el salido sin pase. Nuestra hipótesis se apoya en los datos: la dispersión entre
  provincias (de {pct(c['prov_min'], 1)} a {pct(c['prov_max'], 1)}) y la caída de Buenos
  Aires, que con la secundaria entera pasa de {pct(c['ba_tasa_ini'])} en el archivo
  {c['ba_anio_ini']} a {pct(c['ba_tasa_fin'])} en el de {c['ba_anio_fin']}. Y en que la
  categoría incluye a "los que continúan en otra escuela sin haber realizado el trámite de
  pase" ({C['dgcye']}), algo que depende del seguimiento que haga cada provincia.
- **El privado urbano casi no tiene abandono alto**, y el modelo lo sabe: ahí casi no se
  equivoca.
- **En los grupos más grandes el modelo detecta menos**: tienen tasas más bajas y más
  parejas, y lo poco que pasa queda diluido.
""")
    code("""
Image("figuras/tp3_b_tasa_por_provincia.png")
""")

    md("""
## 7. Qué aprendimos del modelo

Para ver qué aporta cada tema, sacamos un bloque entero de variables, volvemos a evaluar y
miramos cuánto empeora. Y para ver hacia dónde empuja cada respuesta, miramos cómo se
mueve junto con la tasa de abandono.
""")
    code("""
pd.read_csv("data/processed/aporte_bloques.csv").round(4)
""")
    code("""
s = pd.read_csv("data/processed/sentido_variables.csv")
pd.concat([s.head(6), s.tail(6)]).round(3)
""")
    md(f"""
- **Ningún tema por separado es imprescindible.** Sacar cualquier bloque mueve el resultado
  apenas un punto: el nivel socioeconómico, la educación de los padres, los libros en la
  casa y el desempeño cuentan, en el fondo, la misma historia de desigualdad. Por eso al
  sacar uno los otros lo cubren.
- **El sentido**: más abandono donde hay más hogares del nivel socioeconómico más bajo, más
  madres que no terminaron la primaria, más repitencia, más chicos que llegaron al jardín
  recién en sala de 5, y en la gestión estatal. Menos abandono donde los chicos tienen la
  edad que corresponde, nunca repitieron y fueron al jardín desde sala de 3.
- **Qué de esto ya estaba documentado.** No lo damos por sentado: lo buscamos, y no todo
  tiene el mismo respaldo.
  - *Nivel socioeconómico*: documentado. Sobre el riesgo de abandono, "los estudiantes de
    los quintiles más pobres tienen más probabilidad de entrar en ese grupo"
    ({C['adrogue']}; también {C['unicef']}).
  - *Educación de la madre*: documentado como "clima educativo del hogar": "hogares de
    menores ingresos y con madres/padres de menor nivel educativo protagonizan el
    abandono" ({C['argxedu']}, p. 3; también {C['unicef']}, p. 22, y {C['boniolo']}).
  - *Repitencia y sobreedad*: documentado, con dato oficial. "Los datos confirman que la
    sobreedad es un factor crítico asociado al abandono escolar" ({C['sobreedad']}, p. 5), y
    repetir "en muchos casos, se asocia con un mayor riesgo de abandono escolar"
    ({C['aprender']}, p. 46).
  - *Jardín desde sala de 3*: documentado solo en parte. Hay evidencia para los aprendizajes
    ({C['aprender']}, p. 45) y para terminar la secundaria ({C['berlinski']}, documento de
    trabajo; en Uruguay, {C['berlinski08']}), pero no encontramos una fuente argentina que lo
    mida contra el abandono.
  - *Gestión estatal*: documentado solo en parte. La brecha está documentada: el abandono
    "se concentra en escuelas estatales" ({C['argxedu']}, p. 3; también {C['adrogue']}). Que
    se explique por la composición social del alumnado está mostrado para los aprendizajes
    ({C['albornoz']}), no para el abandono.
- **Una advertencia para leer estas variables.** En Aprender 2024 el índice de nivel
  socioeconómico ya incluye la educación de la madre: se construye "considerando diversas
  variables como el nivel educativo de la madre, el hacinamiento" ({C['aprender']}, p. 30).
  En nuestros datos no son dos señales independientes, y eso explica en parte que al sacar
  una la otra la cubra.
- **Un resultado raro que ya conocíamos**: los grupos donde la mayoría falta poco tienen
  *más* abandono, no menos. Es el sesgo de selección del TP2: Aprender solo ve a quien fue a
  rendir, y el que más faltaba probablemente ya se fue.
- **Que algo prediga no lo vuelve causa.** Que la educación de la madre acompañe al abandono
  no dice que cambiarla lo reduzca: dice dónde mirar.
""")

    md(f"""
## 8. Los grupos que el modelo no marca

La mentora propuso una segunda etapa: mirar por dentro a los grupos que el modelo no marca
como abandono alto. Los agrupamos por seis rasgos legibles (sin usar el abandono para
agruparlos) y aparecen {c['perf_k']} perfiles.
""")
    code("""
!python pipeline/05_modelado/17_perfiles.py
Image("figuras/tp3_c_perfiles.png")
""")
    md(f"""
Lo que el modelo no marca no es todo igual. El **privado urbano** casi no tiene abandono. Los
otros tres (**estatal urbano**, **rural estatal** y **rural más vulnerable**) tienen tasas
parecidas entre sí. Entre todos los grupos que el modelo no marca quedan **{c['perf_no_vistos']}
con abandono alto que no vio**; el perfil que más concentra es el **estatal urbano**
({c['perf_top_nv']} de {c['perf_no_vistos']}), que además reúne al {pct(c['perf_top_est'], 0)} de
los estudiantes de estos grupos. Para un uso real, ahí es donde conviene una segunda mirada.
""")

    md(f"""
## 9. Limitaciones

- **Grupos, no personas.** Todo lo que decimos es sobre grupos de escuelas. Nada de esto
  permite decir nada de un estudiante.
- **El abandono registrado no es el abandono real.** Un cero en salidas sin pase no se
  distingue de "no se registró", y la tasa cambia mucho entre provincias.
- **Lo que el registro no cuenta y lo que cuenta de más.** Quien se va después del último
  día de clase (entre diciembre y marzo) no figura como salida sin pase sino como no
  promovido ({C['cuadernillo_c']}): esas salidas no están en nuestro target. Y la categoría
  incluye pases no tramitados: chicos que siguen en otra escuela sin haber hecho el trámite
  ({C['dgcye']}).
- **Que el registro cambie entre provincias es una hipótesis nuestra** (sección 6): el
  documento oficial del Relevamiento sostiene que los datos son comparables.
- **El target es inestable** en grupos chicos y de un año al otro.
- **Desfase de un año, documentado**: el abandono es del ciclo 2023 y Aprender de 2024
  (sección 2).
- **El corte del cuarto superior es una decisión nuestra.** Lo probamos con el tercio y el
  quinto superior y aguanta: el perfil solo y la provincia sola quedan parejos en los dos
  (sección 5).
- **Aprender solo ve a quien fue a rendir**: el que ya abandonó no está, y eso sesga hacia
  abajo justo a los grupos con más abandono.
- **La EPH es de 2025 y por provincia**: por eso quedó afuera del modelo principal.
- **El edificio** del Relevamiento cuenta todas las escuelas del grupo, no solo las
  secundarias.

## 10. Qué sigue

- **El Relevamiento 2025**, que trae las salidas del ciclo 2024: el mismo en el que se tomó
  Aprender.
- **El abandono interanual oficial** del Ministerio (quién no se reinscribe al año
  siguiente, {C['manual_ind']}), que capta lo que las salidas sin pase no ven.
- **Revisar con las provincias cómo registran las salidas sin pase**, empezando por las que
  más se apartan del modelo (Buenos Aires y Santa Fe), antes de comparar provincias entre sí.
- **Predecir el año siguiente con datos del anterior**, que es lo que haría un sistema de
  alerta temprana de verdad.

## 11. Qué es hallazgo nuestro y qué ya se sabía

Cada afirmación que no sale de nuestros datos tiene su fuente, con la cita textual y el
enlace, en `entregas/03-machine-learning/FUENTES-TP3.md`.

- **Ya se sabía**: que el nivel socioeconómico bajo, el clima educativo del hogar, la
  repitencia y la sobreedad acompañan al abandono; qué es una salida sin pase, y que el
  Relevamiento la informa para el ciclo anterior.
- **Se sabía en parte**: lo del jardín (documentado para aprendizajes y para terminar la
  secundaria, no contra el abandono) y lo de la gestión estatal (la brecha sí; que se
  explique por quiénes asisten, solo para aprendizajes).
- **Es hallazgo nuestro** (no lo encontramos dicho en esas fuentes):
  - que, con datos agregados por grupo, la provincia sola ordene el riesgo casi tan bien
    como el perfil de los estudiantes ({num(c['auc_prov'])} contra {num(c['auc_log'])}), y
    que juntos lleguen a {num(c['auc_pyp_log'])};
  - que el perfil siga ordenando en provincias que el modelo no vio
    ({num(c['auc_log_pp'])} contra {num(c['auc_sa_pp'])});
  - que la EPH provincial no agregue información por encima de Aprender;
  - la asociación invertida de las inasistencias, que leemos como sesgo de selección de
    Aprender (TP2);
  - la hipótesis de que las provincias registran distinto las salidas sin pase, que la
    posición oficial no comparte.

---

*Cómo se hizo.* Cada número de este notebook lo produce el pipeline del proyecto
(`pipeline/05_modelado/`), con las decisiones en un solo archivo (`pipeline/modelado.py`) y
verificaciones automáticas en `tests/test_invariantes.py`. Para probar otra combinación
alcanza con editar la lista de experimentos y volver a correr desde la etapa 15. Las
decisiones y sus motivos están en `entregas/03-machine-learning/DECISIONES-TP3.md`, y las
fuentes citadas en `entregas/03-machine-learning/FUENTES-TP3.md`.
""")


def main():
    remoto = git("remote", "get-url", "origin")
    slug = remoto.replace("https://github.com/", "").replace(".git", "")
    commit = git("rev-parse", "HEAD")
    if git("status", "--porcelain", "--", "pipeline", "requirements.txt", "tests"):
        print("  AVISO: hay cambios sin commitear en el pipeline. El notebook apunta")
        print(f"         a {commit[:7]}, que no los incluye. Commitear y regenerar.")
    construir(slug, commit)
    nb = {"cells": celdas,
          "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                      "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    DESTINO.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  notebook: {DESTINO.relative_to(BASE_DIR)} ({len(celdas)} celdas, commit {commit[:7]})")


if __name__ == "__main__":
    main()
