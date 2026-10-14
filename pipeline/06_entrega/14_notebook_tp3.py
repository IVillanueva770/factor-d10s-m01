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

El PDF (15_informe_tp3.py) es la fuente de verdad de lo que el trabajo afirma
(14/10): el notebook puede ser mas largo y tecnico, pero sus conclusiones,
recomendaciones, definiciones y numeros son los del PDF. Los integrantes, la
lista de fuentes y la lectura "3 de cada 4" se toman del 15, no se copian.
"""

import importlib.util
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

# Las fuentes citadas son SOLO las siete de la lista del PDF (FUENTES en
# 15_informe_tp3.py). Los enlaces salen de
# entregas/03-machine-learning/FUENTES-TP3.md; el texto de cada referencia no se
# copia aca, se toma del 15 (ver fuentes_con_enlace).
_ADROGUE = ("https://ri.conicet.gov.ar/bitstream/handle/11336/267725/"
            "CONICET_Digital_Nro.edd2aab9-34e4-449f-a0c2-93e0f205899b_B.pdf?sequence=2")
_ZIP_METODOLOGICOS = ("https://www.argentina.gob.ar/sites/default/files/2018/04/"
                      "documentos_metodologicos_3.10.zip")
_DIEE = "https://www.argentina.gob.ar/sites/default/files/documento_metodologico.pdf"
_CUADERNILLO_RA = "https://cge.entrerios.gov.ar/wp-content/uploads/cei/2025-COMUN-TP.pdf"
_APRENDER_2024 = ("https://www.argentina.gob.ar/sites/default/files/"
                  "informe_nacional_aprender_2024.pdf")
_SOBREEDAD = ("https://www.argentina.gob.ar/sites/default/files/"
              "historias_con_datos_sobredad_final.pdf")
_UNICEF = ("https://www.unicef.org/argentina/media/18746/file/"
           "Serie%20MICS:%20Adolescencias%20y%20Educaci%C3%B3n.pdf")
# Una marca por referencia del PDF: cada referencia tiene que contener
# exactamente una, asi el enlace no se le pega a la cita equivocada.
ENLACES = [
    ("Orlicki", _ADROGUE),
    ("Definiciones básicas", _ZIP_METODOLOGICOS),
    ("Bases Usuarias", _DIEE),
    ("Relevamiento Anual 2025", _CUADERNILLO_RA),
    ("Aprender 2024", _APRENDER_2024),
    ("Caminos interrumpidos", _SOBREEDAD),
    ("UNICEF", _UNICEF),
]
CITA = {
    "adrogue": f"[Adrogué y Orlicki, 2025]({_ADROGUE})",
    "definiciones": f"[DiNIECE, s/f, p. 7]({_ZIP_METODOLOGICOS})",
    "diee": f"[DIEE, s/f]({_DIEE})",
    "cuadernillo": f"[Relevamiento Anual 2025, cuadernillo nacional, sección 3.12]({_CUADERNILLO_RA})",
    "aprender": f"[Aprender 2024]({_APRENDER_2024})",
    "sobreedad": f"[Caminos interrumpidos, 2024]({_SOBREEDAD})",
    "unicef": f"[UNICEF Argentina, 2022]({_UNICEF})",
}


def informe():
    """El generador del PDF, cargado a pedido. De ahi salen INTEGRANTES, FUENTES
    y de_cada: una sola fuente para los dos entregables. No se carga al importar
    este modulo porque el 15 importa a este al cargarse."""
    spec = importlib.util.spec_from_file_location(
        "informe_tp3", Path(__file__).resolve().parent / "15_informe_tp3.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fuentes_con_enlace(fuentes):
    """Las referencias del PDF, tal cual, cada una con su enlace."""
    filas = []
    for ref in fuentes:
        urls = [url for marca, url in ENLACES if marca in ref]
        if len(urls) != 1:
            raise SystemExit(f"La referencia no tiene un enlace unico: {ref[:60]}")
        filas.append(f"- {ref} [Enlace]({urls[0]})")
    if len(filas) != len(ENLACES):
        raise SystemExit("La lista de fuentes del PDF y la de enlaces ya no coinciden")
    return "\n".join(filas)
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
    # 14/10: los no detectados de los perfiles rurales estatales, sumados (el
    # texto los compara con los del estatal urbano).
    rural_est = perf[(perf["estatal"] > 0.5) & (perf["rural"] > 0.5)]
    c["perf_rural_nv"] = int(rural_est["altos_no_vistos"].sum())
    c["perf_top_nv_pct"] = c["perf_top_nv"] / c["perf_no_vistos"]
    # El perfil con la tasa mas alta: el texto dice que es el rural mas
    # vulnerable (rural y el de mas NSE bajo); se chequea, no se supone.
    alta = perf.loc[perf["tasa_real_ponderada"].idxmax()]
    if not (alta["rural"] > 0.5 and alta["nse_bajo"] == perf["nse_bajo"].max()):
        raise SystemExit("El perfil con la tasa mas alta ya no es el rural mas "
                         "vulnerable: revisar el cierre de la seccion 8")

    # 14/10: que es "marcar". El modelo marca como de riesgo al cuarto de grupos
    # que pone mas arriba; las cuentas salen de errores_principal (corte por
    # tamanio, que reparte a todos los grupos), las mismas de los no detectados.
    tam = err[err["corte"] == "tamanio"]
    c["altos_tot"] = int(tam["altos_reales"].sum())
    c["det_tot"] = int(tam["detectados"].sum())
    c["fa_tot"] = int(tam["falsas_alarmas"].sum())
    c["marcas_tot"] = c["det_tot"] + c["fa_tot"]
    c["no_det"] = c["altos_tot"] - c["det_tot"]
    c["recall_tot"] = c["det_tot"] / c["altos_tot"]
    c["prec_tot"] = c["det_tot"] / c["marcas_tot"]
    if c["no_det"] != c["perf_no_vistos"]:
        raise SystemExit("Los no detectados de errores_principal y de los perfiles "
                         "ya no coinciden: revisar las secciones 4 y 8")
    chicos, grandes = tam.iloc[0], tam.iloc[-1]
    c["rec_chicos"] = chicos["detectados"] / chicos["altos_reales"]
    c["rec_grandes"] = grandes["detectados"] / grandes["altos_reales"]
    # Por azar, la proporcion de grupos con abandono alto (referencia de la
    # estabilidad entre anios).
    c["prev"] = c["positivos"] / c["n"]
    c["ceros_pct"] = c["ceros"] / c["n"]
    c["auc_log_pp_desv"] = float(r[(r.experimento == "principal")
                                   & (r.separacion == "por_provincia")
                                   & (r.modelo == "logistica")]["roc_auc_desvio"].iloc[0])
    por_prov = d.groupby("jurisdiccion")[["ssp_ultimos2", "inicial_ultimos2"]].sum()
    tasa_prov = por_prov["ssp_ultimos2"] / por_prov["inicial_ultimos2"]
    c["prov_min"], c["prov_min_n"] = tasa_prov.min(), tasa_prov.idxmin()
    c["prov_max"], c["prov_max_n"] = tasa_prov.max(), tasa_prov.idxmax()
    # Las veces, con los dos porcentajes redondeados como los muestra la
    # figura 2 (dos decimales), para que la cuenta cierre a la vista.
    c["prov_veces"] = round(100 * c["prov_max"], 2) / round(100 * c["prov_min"], 2)
    # Por que no un modelo por provincia: cuantos grupos y positivos tiene cada una.
    n_prov = d["jurisdiccion"].nunique()
    c["grupos_x_prov"] = len(d) / n_prov
    c["pos_x_prov"] = c["positivos"] / n_prov
    # 14/10: los numeros que el texto del notebook todavia escribia a mano.
    c["n_prov"] = n_prov
    c["prov_7_5"] = len(PROVINCIAS_7_5)
    c["clima_na"] = int(d["clima_escolar__bajo"].isna().sum())
    aporte = pd.read_csv(PROC / "aporte_bloques.csv")
    c["aporte_max"] = aporte["caida"].abs().max()

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
    inf = informe()
    de_cada = inf.de_cada
    C = CITA
    celdas.clear()
    tasa_total = c["ssp"] / c["ini"]

    # Lo que el texto afirma con palabras se chequea, igual que en el PDF.
    if (num(c["auc_t_log"]), num(c["auc_t_prov"])) != (num(c["auc_q_log"]),
                                                       num(c["auc_q_prov"])):
        raise SystemExit("El tercio y el quinto ya no dan lo mismo: revisar la "
                         "seccion 5")
    if num(c["auc_eph"]) != num(c["auc_log"]):
        raise SystemExit("Sumar la EPH ya cambia la regresion logistica: revisar la "
                         "seccion 5")
    if c["auc_log_pp"] - c["auc_sa_pp"] >= c["auc_log_pp_desv"]:
        raise SystemExit("En provincias no vistas el perfil ya le gana a la regla "
                         "simple por mas que la variacion: revisar la conclusion 3")
    if c["marcas_tot"] != c["altos_tot"]:
        raise SystemExit("El modelo ya no marca tantos grupos como hay con abandono "
                         "alto: revisar la seccion 5")

    md(f"""
# Dónde se concentra el abandono en la secundaria argentina

**Entregable 3 de la mentoría (Machine Learning)** · Grupo M01, “El Factor D10S” ·
Diplomatura en Ciencia de Datos, FAMAF (UNC), 2026

**Integrantes:** {inf.INTEGRANTES}

**Mentora:** Noelia Ferrero

Cruzamos lo que {miles(c['estudiantes'])} estudiantes contaron en las Pruebas Aprender con
los chicos que sus escuelas registraron como abandono.

## El problema y los datos

Queremos saber **en qué grupos de escuelas secundarias se concentra el abandono**, para que
quien tenga que decidir dónde intervenir sepa por dónde empezar. Usamos dos fuentes públicas
del Ministerio de Educación que miran cosas distintas. Las **Pruebas Aprender** son la
evaluación nacional que rinden los estudiantes del último año: además de la prueba,
responden un cuestionario sobre su hogar, su trayectoria y su escuela. El **Relevamiento
Anual** es el formulario que cada escuela completa todos los años: cuenta cuántos chicos se
inscribieron, cuántos pasaron de año y cuántos se fueron. Aprender no puede ver el abandono,
porque el que ya dejó no va a rendir; el Relevamiento sí, pero no sabe nada de los hogares.
La **Encuesta Permanente de Hogares** (EPH, la encuesta oficial del INDEC sobre empleo e
ingresos de los hogares) tampoco sirve para medir el abandono acá: no se puede unir a estos
grupos, porque solo llega a provincia, y su dato es de 2025.

La pregunta de partida era qué estudiante abandona, pero Aprender no se publica estudiante
por estudiante sino por **grupo de escuelas**: un departamento de una provincia, separando
escuelas estatales y privadas, urbanas y rurales. Son {miles(c['n'])} grupos con
{miles(c['estudiantes'])} estudiantes, y todo lo que sigue habla de esos grupos, nunca de un
chico en particular. Llamamos **perfil** de un grupo a lo que cuentan sus estudiantes en
Aprender sobre su hogar, su trayectoria y su escuela. Como abandono usamos las **salidas sin
pase**: estudiantes que dejaron la escuela sin inscribirse en otra. En los dos últimos años
de la secundaria fueron {miles(c['ssp'])} sobre {miles(c['ini'])} inscriptos, el
**{pct(tasa_total)}**: poco en el total y muy desparejo entre lugares. Decimos que un grupo
tiene **abandono alto** si está en el cuarto de grupos con la tasa más alta del país
({pct(c['corte'])} o más).

## Lo que encontramos, en cinco líneas

Probamos dos modelos que miran solo el perfil (una regresión logística y otro de árboles
combinados) y un tercero que además conoce la provincia. Cuando decimos **el modelo**
hablamos de la regresión logística con el perfil solo. Para medirlos usamos una escala de qué
tan bien ordenan los grupos de más a menos riesgo: **0,5 es lo que lograría un sorteo y 1 es
ordenarlos perfecto**. {num(c['auc_log'])} quiere decir que si tomamos un grupo con abandono
alto y uno sin, el modelo pone primero al de abandono alto {de_cada(c['auc_log'])} veces (y
{num(c['auc_pyp_log'])}, {de_cada(c['auc_pyp_log'])}). Además, el modelo **marca** como de
riesgo al cuarto de grupos que pone más arriba: de los {c['altos_tot']} grupos con abandono
alto encuentra {c['det_tot']} ({pct(c['recall_tot'], 0)}), y de sus {c['marcas_tot']} marcas
aciertan {c['det_tot']} ({pct(c['prec_tot'], 0)}).

1. **Con el perfil de los estudiantes se puede ordenar qué grupos tienen más riesgo de
   abandono:** el modelo llega a **{num(c['auc_log'])}**.
2. **La provincia y el perfil aportan información distinta.** Con solo saber en qué
   provincia está el grupo se llega a {num(c['auc_prov'])}, lo mismo que con el perfil.
   Juntos llegan a **{num(c['auc_pyp_log'])}**: lo que sabe uno no lo sabe el otro.
3. **Sin conocer la provincia, el perfil dice poco más que la regla simple.** Probado en
   provincias que nunca vio, el modelo llega a {num(c['auc_log_pp'])}, contra
   {num(c['auc_sa_pp'])} de mirar solo si la escuela es estatal o privada, urbana o rural. La
   diferencia ({num(c['auc_log_pp'] - c['auc_sa_pp'])}) es menor que lo que varía el
   resultado de una prueba a otra ({num(c['auc_log_pp_desv'])}). Detalle en la sección 5.
4. **El abandono registrado cambia mucho de una provincia a otra:** de {pct(c['prov_min'])}
   en {c['prov_min_n']} a {pct(c['prov_max'])} en {c['prov_max_n']}, unas
   {c['prov_veces']:.0f} veces más. Creemos que una parte es la forma de completar el
   registro y no abandono real, pero es una hipótesis nuestra: el área de estadística del
   Ministerio de Educación sostiene que el dato es comparable entre provincias (sección 6).
5. **Lo que más acompaña al abandono coincide en buena parte con lo que ya documenta la
   investigación en Argentina:** hogares de nivel socioeconómico bajo, madres que no
   terminaron la primaria, haber repetido, tener más edad de la que corresponde al año,
   haber empezado el jardín recién en sala de 5 y la escuela estatal (sección 7, con las
   fuentes). Es una asociación entre grupos, no una causa.

## Qué significa para quien decide

Que lo que los estudiantes cuentan de sus hogares sirve para ordenar dónde mirar, también
dentro de una misma provincia, aunque no explique por qué pasa. Sumarle la provincia ordena
mejor, pero no sabemos cuánto de lo que aporta la provincia es abandono y cuánto es la forma
de registrarlo: antes de usarla para comparar provincias entre sí, conviene saber cómo
registra el abandono cada una.

## Qué haríamos con esto

- **Mientras no se revise cómo registra cada provincia, usar el perfil para ordenar dentro de
  cada provincia**, y tomar la provincia como un dato a revisar. Es una señal modesta, pero
  es la única que no depende de cómo registra cada provincia: si el abandono alto se define
  dentro de cada provincia (el cuarto de sus grupos con la tasa más alta), el perfil ordena
  en {num(c['auc_cp_log'])}, contra {num(c['auc_cp_sa'])} de la regla estatal/privado y
  urbano/rural.
- **Antes de comparar provincias, revisar con ellas cómo registran las salidas sin pase**,
  empezando por las que más se apartan de lo que predice el modelo (Buenos Aires y Santa Fe).
- **Dar una segunda mirada a los grupos que el modelo no marca:** entre ellos quedan
  {c['no_det']} de los {c['altos_tot']} con abandono alto, {c['perf_top_nv']} en escuelas
  estatales urbanas y {c['perf_rural_nv']} en estatales rurales (sección 8).

---

Lo que sigue explica cómo llegamos a esto: el problema (1), qué predecimos (2), con qué datos
(3), las reglas simples contra las que nos medimos (4), los modelos (5), dónde se equivocan
(6), qué acompaña al abandono y qué ya se sabía (7), los grupos que el modelo no marca (8),
las limitaciones (9), qué sigue (10), qué es hallazgo nuestro (11) y las fuentes (12). Al
final, cómo reproducirlo. El código vive en el repo del proyecto,
[github.com/{slug}](https://github.com/{slug}), y este notebook lo corre fijado al commit
`{commit[:7]}`.
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

Queremos saber **en qué grupos de escuelas secundarias se concentra el abandono**. La
consigna nos pide primero contestar cinco preguntas, y las contestamos antes de tocar un
modelo:

- **¿Qué representa una fila?** Un grupo de escuelas: un departamento de una provincia,
  separando estatales y privadas, urbanas y rurales. Son {miles(c['n'])} grupos que juntan a
  {miles(c['estudiantes'])} estudiantes que rindieron Aprender. **No es un estudiante**:
  Aprender no se publica estudiante por estudiante.
- **¿Qué queremos predecir?** Si un grupo tiene **abandono alto**: si la proporción de
  estudiantes de los dos últimos años que dejaron la escuela sin inscribirse en otra está en
  el cuarto de grupos con la tasa más alta del país.
- **¿Existe una variable que lo observe?** Sí, y no la inventamos: las **salidas sin pase**
  del Relevamiento Anual, que completa cada escuela. Usamos la definición oficial del área de
  estadística del Ministerio de Educación: salido sin pase es “el que se va de la escuela a la
  que asistía, sin inscripción (o pase) en otra escuela” ({C['definiciones']}). No es el
  abandono interanual oficial, que además cuenta a quienes no se vuelven a inscribir al año
  siguiente; lo retomamos en la sección 10.
- **¿Qué información está disponible antes del resultado?** El perfil de los estudiantes que
  cuenta Aprender, el sector, el ámbito y el tamaño del grupo. **No usamos** nada que se
  conozca después del abandono (los que no pasaron de año, los pases ni los egresados del
  mismo año): salen del mismo cierre de ciclo, y usarlos sería mirar la respuesta.
- **¿Qué podemos afirmar?** Cosas sobre grupos, nunca sobre una persona; asociaciones, nunca
  causas.

**Por qué dos fuentes y no una.** Aprender lo responde el estudiante el día de la prueba:
dice cómo le va y cómo vive, pero **no puede ver el abandono**, porque el que ya dejó no va a
rendir. El Relevamiento lo completa la escuela: cuenta quién se fue, pero no sabe nada de los
hogares. Juntas permiten preguntar qué perfiles acompañan a las tasas de abandono que
registra el sistema.

**Un solo año, 2024.** La mentora nos pidió trabajar con una sola época. El resumen de esa
reunión dice “2025”, pero no hay Aprender de secundaria 2025 (se toma en 2022 y 2024) ni
Relevamiento publicado de 2025, así que todo sale de los archivos 2024 (el del Relevamiento
trae las salidas del ciclo 2023: sección 2). La EPH no sirve para medir el abandono acá: no
se puede unir a los grupos, porque solo llega a provincia, y su dato es de 2025. Queda afuera
del modelo principal y, como pidió la mentora, la probamos aparte (sección 5).
""")

    md(f"""
## 2. Qué predecimos, y cómo lo construimos

**La regla, igual para todos los grupos:**

> tasa de abandono = salidas sin pase de los dos últimos años ÷ matrícula inicial de esos
> mismos años. **Abandono alto** = el grupo está en el cuarto de grupos con la tasa más alta
> del país (en estos datos, {pct(c['corte'])} o más).

- **Por qué los dos últimos años.** Son los que evalúa Aprender. La secundaria no dura lo
  mismo en todo el país (en {c['prov_7_5']} provincias es 7 de primaria y 5 de secundaria, en
  las otras {c['n_prov'] - c['prov_7_5']} es 6 y 6), pero los dos últimos años caen en el
  mismo lugar en todas.
- **Por qué clases y no el número.** La mentora propuso un enfoque en dos etapas (primero
  separar grupos con y sin abandono alto, después mirar por dentro a los que quedan sin
  marcar), y eso pide clases. Además la tasa tiene muchos ceros: {miles(c['ceros'])} de los
  {miles(c['n'])} grupos ({pct(c['ceros_pct'], 0)}) no tienen ninguna salida registrada.
- **Lo que mide en total:** {miles(c['ssp'])} salidas sin pase sobre {miles(c['ini'])}
  inscriptos, el **{pct(tasa_total)}**. Poco en el total y muy desparejo entre lugares.
""")
    code("""
!python pipeline/05_modelado/12_bajar_relevamiento.py
!python pipeline/05_modelado/13_relevamiento.py
""")
    md(f"""
**Dos cosas que medimos y que limitan lo que se puede decir:**

- **Lo que medimos es inestable de un año a otro.** De los grupos con abandono alto en el
  Relevamiento 2024, solo el {pct(c['est_rep2'], 0)} lo tenía en el anterior (por azar sería
  el {pct(c['prev'], 0)}; con la secundaria entera sube a {pct(c['est_repS'], 0)}). En grupos
  chicos, una sola salida mueve la tasa.
- **El Relevamiento de cada año informa las salidas del ciclo anterior.** Primero lo
  inferimos de los datos (la matrícula de último año del archivo 2024 coincide con la de 2023
  y no con la de 2024) y después lo encontramos documentado: el formulario 2025 pregunta por
  la “Trayectoria de matrícula durante el ciclo lectivo 2024”, con las salidas producidas
  “entre el 30 de abril de 2024 y el último día de clase del período escolar del año 2024”
  ({C['cuadernillo']}). Entonces el Relevamiento 2024 trae las salidas de 2023, y Aprender es
  de octubre de 2024: el perfil se midió después del abandono con el que lo comparamos. Esto
  ordena, no anticipa. Lo usamos igual, porque es el último archivo publicado, y lo dejamos
  declarado (sección 9).
""")

    md("""
## 3. Los datos y cómo los preparamos

Partimos del dataset curado del TP2 y le sumamos el Relevamiento por la misma clave. El cruce
imprime cuántos estudiantes encuentran su par, y la etapa se corta si se pierden demasiados.
""")
    code("""
!python pipeline/05_modelado/14_dataset_modelado.py
""")
    md(f"""
**Qué entra al modelo, en bloques que se pueden prender y apagar:**

| Bloque | Qué es |
|---|---|
| Aprender (el perfil) | las proporciones de cada respuesta en el grupo: hogar, educación de la madre y el padre, nivel socioeconómico, repitencia, sobreedad, inasistencias, desempeño en lengua y matemática |
| Contexto | estatal o privado, urbano o rural, tamaño del grupo |
| Edificio (prueba) | proporción de escuelas con electricidad, sala de informática, biblioteca, internet |
| EPH (prueba) | dos indicadores de la provincia: el ingreso per cápita mediano del hogar y la proporción de adultos sin secundaria completa |

Los faltantes (por ejemplo, el clima escolar, que no tiene dato en {c['clima_na']} grupos) se
completan con la mediana **dentro de cada partición de entrenamiento**, nunca mirando los datos
con los que se evalúa.
""")

    md(f"""
## 4. Las reglas simples contra las que nos medimos

Un modelo solo vale si le gana a una regla que cualquiera podría aplicar sin él. Por eso
comparamos los modelos contra tres reglas:

- **Un sorteo**: a todos el mismo riesgo.
- **Sector y ámbito**: a cada grupo, el riesgo promedio de los grupos de su mismo tipo
  (estatal urbano, estatal rural, privado urbano, privado rural).
- **La provincia**: a cada grupo, el riesgo promedio de su provincia.

## 5. Los modelos, y cómo los comparamos

Probamos una **regresión logística**, que estima la probabilidad de abandono alto sumando el
peso de cada variable y se puede leer, y un modelo de **árboles combinados** (boosting), que
capta relaciones no lineales. Cuando decimos **el modelo** hablamos de la regresión logística
con el perfil solo. Todos, reglas y modelos, se evalúan igual: partimos los datos en cinco y
cada parte se predijo con lo aprendido de las otras cuatro, así que cada grupo lo evaluó un
modelo que no lo había visto (con semilla fija).

Medimos con el **área bajo la curva ROC**, la escala de qué tan bien ordenan los grupos de más
a menos riesgo (0,5 es un sorteo, 1 es ordenarlos perfecto). Y miramos qué pasa cuando el
modelo **marca** como de riesgo al cuarto de grupos que pone más arriba: de los
{c['altos_tot']} grupos con abandono alto encuentra {c['det_tot']} ({pct(c['recall_tot'], 0)},
la cobertura), y de sus {c['marcas_tot']} marcas aciertan {c['det_tot']}
({pct(c['prec_tot'], 0)}, la precisión). Como marca tantos grupos como hay con abandono alto,
las dos dan lo mismo. No usamos solo el acierto: con un cuarto de grupos con abandono alto,
decir “nadie tiene abandono alto” ya acierta el {pct(1 - c['prev'], 0)}.
""")
    code("""
!python pipeline/05_modelado/15_experimentos.py
""")
    code("""
import pandas as pd
r = pd.read_csv("data/processed/resultados_experimentos.csv")
nombres = {"prevalencia": "Regla: un sorteo", "sector_ambito": "Regla: sector y ámbito",
           "provincia": "Regla: la provincia", "logistica": "Regresión logística",
           "boosting": "Árboles combinados"}
t = r[r.experimento == "principal"].assign(modelo=lambda x: x.modelo.map(nombres))
t.pivot(index="modelo", columns="separacion", values="roc_auc").round(2)
""")
    code("""
from IPython.display import Image
!python pipeline/05_modelado/18_figuras.py > /dev/null
Image("figuras/tp3_a_modelo_vs_reglas.png")
""")
    md(f"""
**Lo que dice la tabla:**

- Con todas las provincias a la vista, el modelo llega a **{num(c['auc_log'])}**, la regla de
  la provincia a **{num(c['auc_prov'])}** y la de sector y ámbito a **{num(c['auc_sa'])}**.
  El perfil y la provincia empatan. El de árboles combinados, más complejo, no mejora
  ({num(c['auc_boost'])}): señal de que el patrón es simple.
- Si probamos el modelo en provincias que no usó para aprender, la regla de la provincia queda
  sin nada que decir y el modelo llega a **{num(c['auc_log_pp'])}**, apenas por encima de la
  regla de sector y ámbito (**{num(c['auc_sa_pp'])}**). La diferencia
  ({num(c['auc_log_pp'] - c['auc_sa_pp'])}) es menor que lo que varía el resultado de una
  prueba a otra ({num(c['auc_log_pp_desv'])}). **Sin la provincia, el perfil dice poco más
  que la regla simple.**

**La provincia y el perfil juntos.** Empatar no es saber lo mismo. Para verlo armamos un único
modelo que conoce las dos cosas (una columna por provincia, más el perfil): llega a
**{num(c['auc_pyp_log'])}** (con árboles combinados, {num(c['auc_pyp_boost'])}). Si la
provincia solo resumiera el perfil de sus estudiantes, sumarla no agregaría nada; agrega, así
que **cada uno aporta información que el otro no tiene**. Lo probamos así y no con un modelo
por provincia porque cada provincia tiene unos {c['grupos_x_prov']:.0f} grupos y unos
{c['pos_x_prov']:.0f} con abandono alto: no alcanza para entrenar ni para evaluar un modelo
propio.

**Las combinaciones que probamos además** (todas en la tabla de abajo):

- **Mover el corte de abandono alto.** Elegir el cuarto de grupos con más abandono como
  “alto” fue decisión nuestra, así que lo movimos al tercio y al quinto: el perfil solo y la
  provincia sola siguen parejos (en los dos casos, {num(c['auc_t_log'])} contra
  {num(c['auc_t_prov'])}).
- **Sumar el edificio** lleva la regresión a {num(c['auc_edif'])}: casi nada.
- **Sumar la EPH.** Como pidió la mentora, probamos sumar sus dos indicadores por provincia.
  Con la regresión logística no cambia ({num(c['auc_eph'])}), pero con árboles combinados sube
  de {num(c['auc_boost'])} a {num(c['auc_eph_b'])}: dos datos por provincia alcanzan para que
  el modelo reconozca la provincia, que es la información que el perfil no tiene. Lo que la
  provincia agrega por encima del perfil, estos datos no lo nombran: puede ser algo propio de
  cada provincia o su forma de registrar (sección 6).
- **Con la secundaria entera** como target, la regla de la provincia sube a
  {num(c['auc_sec_prov'])} y el modelo queda en {num(c['auc_sec_log'])}: ahí la provincia
  pesa todavía más.
- **Con el corte dentro de cada provincia** (el cuarto de sus grupos con la tasa más alta), el
  perfil ordena en {num(c['auc_cp_log'])} contra {num(c['auc_cp_sa'])} de sector y ámbito. Es
  la señal que no depende de cómo registra cada provincia, y por eso es la que recomendamos
  usar mientras eso no se revise.
""")
    code("""
t = r[r.separacion == "estratificada"].assign(modelo=lambda x: x.modelo.map(nombres))
t.pivot(index="experimento", columns="modelo", values="roc_auc").round(2)
""")

    md("""
## 6. Dónde se equivoca: abandono o forma de registrar

Miramos los errores del modelo por tamaño del grupo, por sector y ámbito y por provincia.
""")
    code("""
!python pipeline/05_modelado/16_errores.py
""")
    md(f"""
- **Los errores no se reparten parejo entre provincias, y eso es lo más importante.** En
  Buenos Aires hay {c['ba_altos']} grupos con abandono alto y el modelo detecta {c['ba_det']},
  pero marca otros {c['ba_fa']} que el registro da como bajos: **por el perfil de sus
  estudiantes, esos grupos “deberían” tener más abandono del que figura.** En Santa Fe pasa
  al revés: {c['sf_altos']} grupos con abandono alto y el modelo detecta {c['sf_det']}. O cada
  provincia registra distinto, o hay algo propio de cada una que Aprender no ve; con estos
  datos no lo podemos distinguir.
- **Que el registro cambie entre provincias es una hipótesis nuestra.** El área de estadística
  del Ministerio de Educación, que administra el Relevamiento, sostiene lo contrario: que su
  sistema “garantiza la homogeneidad y comparabilidad de los datos en todo el ámbito
  nacional” ({C['diee']}). No encontramos ningún documento oficial que advierta diferencias.
  Nos apoyamos en la distancia entre provincias (de {pct(c['prov_min'])} en
  {c['prov_min_n']} a {pct(c['prov_max'])} en {c['prov_max_n']}) y en la caída de Buenos
  Aires, que con la secundaria entera pasa de {pct(c['ba_tasa_ini'])} en {c['ba_anio_ini']} a
  {pct(c['ba_tasa_fin'])} en {c['ba_anio_fin']}. Por eso proponemos revisarlo con las
  provincias antes de compararlas.
- **El privado urbano casi no tiene abandono alto**, y el modelo lo sabe: ahí casi no se
  equivoca.
- **El modelo detecta peor a los grupos más grandes.** En el quinto de grupos más grandes
  encuentra el {pct(c['rec_grandes'], 0)} de los que tienen abandono alto, contra el
  {pct(c['rec_chicos'], 0)} en el quinto más chico: ahí las tasas son más bajas y parejas, y
  lo poco que pasa queda diluido.
""")
    code("""
Image("figuras/tp3_b_tasa_por_provincia.png")
""")

    md("""
## 7. Qué acompaña al abandono, y qué ya se sabía

La lista de qué acompaña al abandono no sale de los pesos de la regresión. Para ver hacia
dónde empuja cada respuesta, miramos su correlación con la tasa de abandono; para ver cuánto
aporta cada tema, sacamos un bloque entero de variables, volvemos a evaluar y miramos cuánto
empeora el modelo (la caída va en centésimas de la escala de 0,5 a 1).
""")
    code("""
a = pd.read_csv("data/processed/aporte_bloques.csv")
a.assign(caida_en_centesimas=100 * a.caida)[
    ["bloque", "auc_sin_el_bloque", "caida_en_centesimas"]].round(2)
""")
    code("""
s = pd.read_csv("data/processed/sentido_variables.csv")
pd.concat([s.head(6), s.tail(6)]).round(2)
""")
    md(f"""
- **El sentido.** En nuestros datos hay más abandono donde hay más hogares de nivel
  socioeconómico bajo, más madres que no terminaron la primaria, más estudiantes que
  repitieron o que tienen más edad de la que corresponde al año, más que empezaron el jardín
  recién en sala de 5, y en las escuelas estatales. Menos abandono donde los estudiantes tienen
  la edad que corresponde, nunca repitieron y fueron al jardín desde sala de 3.
- **Ningún tema por separado es imprescindible para el modelo.** Sacar cualquier bloque mueve
  el resultado {num(100 * c['aporte_max'])} centésimas como mucho: al sacar uno, los otros lo
  cubren, porque todos cuentan la misma desigualdad.
- **Qué de esto ya estaba documentado.** No lo dimos por sentado: buscamos qué dice la
  investigación previa.
  - *Nivel socioeconómico y escuela estatal: documentado.* Un estudio que siguió veinte años
    de la EPH encuentra más riesgo de abandono en los hogares más pobres (“los estudiantes de
    los quintiles más pobres tienen más probabilidad de entrar en ese grupo”) y en las
    escuelas de gestión estatal ({C['adrogue']}).
  - *Educación de la madre: documentado.* La encuesta de UNICEF Argentina sobre
    adolescencias lo muestra como “clima educativo del hogar” ({C['unicef']}, p. 22). Ojo: en
    Aprender 2024 el índice de nivel socioeconómico ya incluye la educación de la madre (se
    construye “considerando diversas variables como el nivel educativo de la madre, el
    hacinamiento”, {C['aprender']}, p. 30), así que en nuestros datos no son dos señales
    independientes.
  - *Repitencia y sobreedad: documentado con dato oficial.* El área de estadística del
    Ministerio de Educación mostró en 2024 un abandono del 27% entre quienes tienen sobreedad
    contra 4,5% entre quienes no, con otra forma de medir el abandono, que sigue a cada
    estudiante a lo largo de los años, en 11 provincias ({C['sobreedad']}, p. 5). Y el informe
    de Aprender dice que repetir “en muchos casos, se asocia con un mayor riesgo de abandono
    escolar” ({C['aprender']}, p. 46).
  - *Jardín desde sala de 3: documentado en parte.* El informe nacional de Aprender 2024 lo
    asocia a mejores aprendizajes ({C['aprender']}, p. 45), pero no encontramos una fuente
    argentina que lo mida contra el abandono.
- **Un resultado raro que ya conocíamos**: los grupos donde la mayoría falta poco tienen
  *más* abandono, no menos. Es el sesgo de selección del TP2: Aprender solo ve a quien fue a
  rendir, y el que más faltaba probablemente ya se fue.
- **Que algo acompañe al abandono no lo vuelve causa.** Sirve para saber dónde mirar; qué
  cambiar es otra pregunta.
""")

    md(f"""
## 8. Los grupos que el modelo no marca

La mentora propuso una segunda mirada: dentro de los grupos que el modelo no marca como
abandono alto, ¿hay perfiles distintos? Los agrupamos por seis rasgos (nivel socioeconómico,
educación de la madre, repitencia, desempeño en matemática, sector y ámbito), sin usar el
abandono para armarlos, con un agrupamiento k-means, y aparecen {c['perf_k']} perfiles.
""")
    code("""
!python pipeline/05_modelado/17_perfiles.py
Image("figuras/tp3_c_perfiles.png")
""")
    md(f"""
Lo que el modelo no marca no es todo igual. El **privado urbano** casi no tiene abandono. Los
otros tres (**estatal urbano**, **rural estatal** y **rural más vulnerable**) tienen tasas
parecidas entre sí. Entre todos los no marcados quedan {c['no_det']} de los
{c['altos_tot']} grupos con abandono alto: {c['perf_top_nv']}
({pct(c['perf_top_nv_pct'], 0)}) en el estatal urbano y {c['perf_rural_nv']} entre los dos
rurales.

**Para quien decide:** el estatal urbano junta más casos por su tamaño (reúne el
{pct(c['perf_top_est'], 0)} de los estudiantes de estos grupos); el rural más vulnerable tiene
la tasa más alta.
""")

    md(f"""
## 9. Limitaciones

- **Grupos, no personas.** Nada de esto permite decir algo de un estudiante concreto.
- **El abandono registrado no es el abandono real.** Un cero no se distingue de “no se
  registró”, y hay muchos: {miles(c['ceros'])} de los {miles(c['n'])} grupos
  ({pct(c['ceros_pct'], 0)}) no tienen ninguna salida registrada. Que la diferencia entre
  provincias sea por cómo registra cada una es una hipótesis nuestra (sección 6).
- **Lo que el registro no cuenta y lo que cuenta de más.** Quien se va entre diciembre y
  marzo, después del último día de clase, no figura como salida sin pase, según el formulario
  2025 del Relevamiento ({C['cuadernillo']}); y la categoría incluye a quienes siguen en otra
  escuela sin haber hecho el trámite del pase.
- **Un año de diferencia.** El Relevamiento de cada año informa las salidas del ciclo
  anterior: el de 2024 trae las de 2023, y Aprender es de octubre de 2024. Es decir, el perfil
  se midió después del abandono con el que lo comparamos: esto ordena, no anticipa. Anticipar
  es el próximo paso.
- **Lo que medimos es inestable.** De los grupos con abandono alto en el Relevamiento 2024,
  solo el {pct(c['est_rep2'], 0)} lo tenía en el anterior (por azar sería el
  {pct(c['prev'], 0)}): en grupos chicos, una sola salida mueve la tasa.
- **El modelo detecta peor a los grupos más grandes.** En el quinto de grupos más grandes
  encuentra el {pct(c['rec_grandes'], 0)} de los que tienen abandono alto, contra el
  {pct(c['rec_chicos'], 0)} en el quinto más chico: ahí las tasas son más bajas y parejas, y
  lo poco que pasa queda diluido.
- **Aprender solo ve a quien fue a rendir**, y eso subestima justo a los grupos con más
  abandono.
- **El corte del cuarto superior es una decisión nuestra.** Lo probamos con el tercio y el
  quinto y aguanta: el perfil solo y la provincia sola siguen parejos (sección 5).
- **El edificio** del Relevamiento cuenta todas las escuelas del grupo, no solo las
  secundarias.

## 10. Qué sigue

- **Sumar el Relevamiento 2025**, que trae el abandono del ciclo 2024, el mismo año de
  Aprender.
- **Incorporar el abandono interanual oficial** (quiénes no se reinscriben al año siguiente),
  que capta lo que las salidas sin pase no ven.
- **Revisar con las provincias cómo registran las salidas sin pase**, empezando por Buenos
  Aires y Santa Fe.
- **Predecir el año siguiente con los datos del anterior**, que es lo que haría un sistema de
  alerta temprana.

## 11. Qué es hallazgo nuestro y qué ya se sabía

- **Ya se sabía**: que el nivel socioeconómico bajo, la escuela estatal, el clima educativo del
  hogar, la repitencia y la sobreedad acompañan al abandono; qué es una salida sin pase, y que
  el Relevamiento la informa para el ciclo anterior.
- **Se sabía en parte**: lo del jardín (documentado para los aprendizajes, no contra el
  abandono).
- **Es hallazgo nuestro** (no lo encontramos dicho en las fuentes):
  - que, con datos agregados por grupo, la provincia sola ordene el riesgo igual que el perfil
    de los estudiantes ({num(c['auc_prov'])} y {num(c['auc_log'])}), y que juntos lleguen a
    {num(c['auc_pyp_log'])};
  - que sin conocer la provincia el perfil diga poco más que la regla estatal/privado y
    urbano/rural ({num(c['auc_log_pp'])} contra {num(c['auc_sa_pp'])}, una diferencia menor
    que la variación entre pruebas);
  - que dos indicadores de la EPH por provincia no le agreguen nada a la regresión logística
    pero le alcancen al modelo de árboles combinados para reconocer la provincia;
  - la asociación invertida de las inasistencias, que leemos como sesgo de selección de
    Aprender (TP2);
  - la hipótesis de que las provincias registran distinto las salidas sin pase, que el área de
    estadística del Ministerio de Educación no comparte.

## 12. Fuentes

{fuentes_con_enlace(inf.FUENTES)}

---

## Cómo reproducirlo

Cada número de este notebook lo produce el pipeline del proyecto (`pipeline/05_modelado/`),
con las decisiones en un solo archivo (`pipeline/modelado.py`) y verificaciones automáticas en
`tests/test_invariantes.py`. Para probar otra combinación alcanza con editar la lista de
experimentos y volver a correr desde la etapa 15. Las decisiones y sus motivos están en
`entregas/03-machine-learning/DECISIONES-TP3.md`, y cada afirmación que no sale de nuestros
datos tiene su cita textual y su enlace en `entregas/03-machine-learning/FUENTES-TP3.md`.
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
