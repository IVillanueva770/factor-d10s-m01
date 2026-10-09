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
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"
INTERIM = BASE_DIR / "data" / "interim"
DESTINO = (BASE_DIR / "entregas" / "03-machine-learning"
           / "TP3_Machine_Learning_El_Factor_D10S.ipynb")


def git(*args):
    return subprocess.run(["git", "-C", str(BASE_DIR), *args],
                          capture_output=True, text=True).stdout.strip()


def pct(x, d=2):
    return f"{100 * x:.{d}f}%".replace(".", ",")


def num(x, d=3):
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
        "ba_altos": int(prov.loc["Buenos Aires", "altos_reales"]),
        "ba_det": int(prov.loc["Buenos Aires", "detectados"]),
        "ba_fa": int(prov.loc["Buenos Aires", "falsas_alarmas"]),
        "sf_altos": int(prov.loc["Santa Fe", "altos_reales"]),
        "sf_det": int(prov.loc["Santa Fe", "detectados"]),
        "perf_k": len(perf),
        "perf_no_vistos": int(perf["altos_no_vistos"].sum()),
    }
    por_prov = d.groupby("jurisdiccion")[["ssp_ultimos2", "inicial_ultimos2"]].sum()
    tasa_prov = por_prov["ssp_ultimos2"] / por_prov["inicial_ultimos2"]
    c["prov_min"], c["prov_min_n"] = tasa_prov.min(), tasa_prov.idxmin()
    c["prov_max"], c["prov_max_n"] = tasa_prov.max(), tasa_prov.idxmax()
    return c


def construir(slug, commit):
    c = cifras()
    celdas.clear()

    md(f"""
# El Factor D10S · Machine Learning

**Entregable 3 de la mentoría** · Grupo M01 · Mentora: Noelia Ferrero
Diplomatura en Ciencia de Datos · FAMAF, UNC

## Lo que encontramos, en cinco líneas

1. **Se puede ordenar qué grupos de escuelas tienen más riesgo de abandono** con lo que
   Aprender cuenta de los chicos y de sus hogares: el modelo acierta el orden en
   {pct(c['auc_log'], 0)} de los pares (un sorteo acertaría el 50%).
2. **Pero casi todo lo que el modelo sabe también lo sabe la provincia.** Con solo
   mirar en qué provincia está el grupo se llega a {pct(c['auc_prov'], 0)}. El modelo
   le gana por muy poco.
3. **Sin conocer la provincia, el perfil de los chicos sigue diciendo algo**:
   probado en provincias que nunca vio, el modelo llega a {pct(c['auc_log_pp'], 0)},
   contra {pct(c['auc_sa_pp'], 0)} de la regla "estatal o privado, urbano o rural".
4. **Las provincias registran el abandono de forma muy distinta**: la tasa va de
   {pct(c['prov_min'], 1)} en {c['prov_min_n']} a {pct(c['prov_max'], 1)} en {c['prov_max_n']}.
   No podemos separar cuánto de eso es abandono real y cuánto es cómo se carga el
   formulario, y lo decimos.
5. **Lo que más acompaña al abandono** es lo de siempre: hogares de menor nivel
   socioeconómico, madres que no terminaron la primaria, haber repetido y la gestión
   estatal. Es asociación entre grupos, no causa.

## Qué haríamos con esto

- Usarlo para **ordenar dónde mirar primero** dentro de cada provincia, no para comparar
  provincias entre sí.
- Antes de cualquier uso, **revisar con cada provincia cómo registra las salidas sin
  pase**: es la pregunta que este trabajo no puede cerrar y la que más cambia el
  resultado.
- Sumar el Relevamiento 2025 cuando se publique, para que el abandono y Aprender
  hablen del mismo ciclo.

---

Lo que sigue explica cómo llegamos a esto: el problema (1), qué predecimos (2),
con qué datos (3), las reglas simples contra las que nos medimos (4), los modelos (5),
dónde se equivocan (6), qué aprendimos (7), los perfiles que el modelo no marca (8),
las limitaciones (9) y qué sigue (10). El código vive en el repo del proyecto,
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
  pase** del Relevamiento Anual, que completa cada escuela para el Ministerio. Es el
  indicador estándar de abandono (el estudiante se va y no se anota en otra escuela).
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
Relevamiento publicado de 2025, así que todo es 2024. La encuesta de hogares (EPH), que es
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
- **El archivo "2024" del Relevamiento parece traer el ciclo 2023**: su matrícula de último
  año coincide con la de 2023 y no con la de 2024. No está documentado; lo inferimos de los
  datos. Si es así, el abandono que medimos es del año anterior a Aprender. Lo usamos igual
  porque los grupos se parecen bastante de un año al siguiente, y lo dejamos declarado.
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

Probamos dos modelos: una **regresión logística**, porque es simple y se puede leer, y un
**boosting de árboles**, por si el patrón no es lineal. Todos, reglas y modelos, se evalúan
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
           "boosting": "Boosting de árboles"}
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
  sector y ámbito a **{num(c['auc_sa'])}**. El modelo le gana a la provincia por muy poco.
  El boosting ({num(c['auc_boost'])}) no mejora a la regresión: el patrón es casi lineal.
- Probando en provincias que el modelo nunca vio, la regla de la provincia no tiene nada que
  decir y cae al azar, y el modelo llega a **{num(c['auc_log_pp'])}** contra
  **{num(c['auc_sa_pp'])}** de sector y ámbito. **Lo que sabemos de los chicos sirve aun sin
  saber dónde están.**

**Las combinaciones que probamos además** (todas en la tabla de abajo):

- **Sumar el edificio** lleva la regresión a {num(c['auc_edif'])}: casi nada.
- **Sumar la EPH** la deja en {num(c['auc_eph'])} (el boosting llega a {num(c['auc_eph_b'])}).
  Como pidió la mentora, la probamos acotada, y no aporta: lo que dice de la provincia ya lo
  dice Aprender.
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
    md("""
- **Ningún tema por separado es imprescindible.** Sacar cualquier bloque mueve el resultado
  apenas un punto: el nivel socioeconómico, la educación de los padres, los libros en la
  casa y el desempeño cuentan, en el fondo, la misma historia de desigualdad. Por eso al
  sacar uno los otros lo cubren.
- **El sentido es el esperable**: más abandono donde hay más hogares del nivel
  socioeconómico más bajo, más madres que no terminaron la primaria, más repitencia, más
  chicos que llegaron al jardín recién en sala de 5, y en la gestión estatal. Menos abandono
  donde los chicos tienen la edad que corresponde, nunca repitieron y fueron al jardín
  desde sala de 3.
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
parecidas entre sí y entre ellos quedan **{c['perf_no_vistos']} grupos con abandono alto que el
modelo no vio**, la mayoría en el estatal urbano, que es además donde están la mayoría de los
estudiantes. Para un uso real, ahí es donde conviene una segunda mirada.
""")

    md("""
## 9. Limitaciones

- **Grupos, no personas.** Todo lo que decimos es sobre grupos de escuelas. Nada de esto
  permite decir nada de un estudiante.
- **El abandono registrado no es el abandono real.** Un cero en salidas sin pase no se
  distingue de "no se registró", y las provincias registran muy distinto.
- **El target es inestable** en grupos chicos y de un año al otro.
- **Probable desfase de un año** entre el Relevamiento y Aprender (sección 2).
- **Aprender solo ve a quien fue a rendir**: el que ya abandonó no está, y eso sesga hacia
  abajo justo a los grupos con más abandono.
- **La EPH es de 2025 y por provincia**: por eso quedó afuera del modelo principal.
- **El edificio** del Relevamiento cuenta todas las escuelas del grupo, no solo las
  secundarias.

## 10. Qué sigue

- **El Relevamiento 2025**, para que el abandono y Aprender hablen del mismo ciclo.
- **El abandono interanual oficial** del Ministerio (quién no se reinscribe al año
  siguiente), que capta lo que las salidas sin pase no ven.
- **Revisar con las provincias cómo registran las salidas sin pase**, empezando por las que
  más se apartan del modelo (Buenos Aires y Santa Fe).
- **Predecir el año siguiente con datos del anterior**, que es lo que haría un sistema de
  alerta temprana de verdad.

---

*Cómo se hizo.* Cada número de este notebook lo produce el pipeline del proyecto
(`pipeline/05_modelado/`), con las decisiones en un solo archivo (`pipeline/modelado.py`) y
verificaciones automáticas en `tests/test_invariantes.py`. Para probar otra combinación
alcanza con editar la lista de experimentos y volver a correr desde la etapa 15. Las
decisiones y sus motivos están en `entregas/03-machine-learning/DECISIONES-TP3.md`.
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
