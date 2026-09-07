# Handoff: subir el TP2 de la mentoría M01

Escrito el 2026-09-07 al cerrar la sesión que construyó el entregable. Es para
la sesión que ayude a Ignacio a **terminar de subirlo**, no a rehacerlo.

Repo público: **https://github.com/IVillanueva770/factor-d10s-m01**
Proyecto local: `C:\Users\Ignacio Villanueva\Desktop\Karpathy\personal-infra\Diplomatura en Ciencia de Datos\05 Mentoria M01 - El Factor D10S`

---

## Lo que hay que hacer (esto es todo)

El trabajo está terminado y verificado. **Lo que falta son tres acciones de
Ignacio, ninguna de código.**

1. **Subir el notebook a Google Colab** y compartirlo **con permiso de
   comentarios**. La consigna lo pide explícitamente para la devolución de la
   mentoría. Alternativa que la consigna también acepta: pasar el link del
   repo, que ya existe.
2. **Chequear si abrieron el buzón de entrega** en el aula virtual. Al 2026-09-02
   el curso 764 (`famaf.aulavirtual.unc.edu.ar/mod/assign/index.php?id=764`)
   tenía un solo assign, el Práctico 1. Si sigue cerrado, avisarle a Noelia por
   el Slack del grupo.
3. **Confirmar la fecha.** Noelia dijo el 04/09 en `#todo-el-factor-d10s` que
   estaban evaluando pasar la entrega al lunes siguiente, pero que no lo veía
   reflejado en el aula. Nunca llegó la confirmación.

Los tres archivos a entregar:

| Producto que pide la consigna | Archivo |
|---|---|
| Notebook de EDA | `notebooks/TP2_EDA_y_curacion_El_Factor_D10S.ipynb` |
| Resumen de hallazgos en PDF | `entrega/TP2_Resumen_de_hallazgos_El_Factor_D10S.pdf` |
| Dataset curado | lo genera el propio notebook al correr |

---

## Estado verificado al cerrar

No son promesas: cada uno se midió corriendo algo.

- **Pipeline reproducible**: 18 de 18 salidas idénticas byte a byte en dos
  corridas seguidas (`python pipeline/correr.py --verificar`).
- **55 de 55 invariantes** en verde (`python tests/test_invariantes.py`).
- **Notebook**: ejecutado entero con `nbclient` en un entorno limpio, 25 de 25
  celdas sin error, 4 de 4 figuras generadas desde el código, 12 tablas.
- **Test ciego en entorno tipo Colab** (Python 3.12, pandas 2.2.2, numpy 2.0.2,
  matplotlib 3.10): 24 de 24 celdas, cero warnings propios, verificación de
  SHA-256 probada también por el camino negativo (corrompiendo un archivo a
  propósito y confirmando que corta).
- **PDF**: 4 páginas, auditado visualmente página por página, cero guiones
  largos, sin nombres propios.
- Todo commiteado y pusheado. Último commit: `2ceb33d`.

**Veredicto sobre Colab**: arrastrarlo y darle "Ejecutar todas las celdas"
funciona. El notebook no necesita ningún `pip install` porque pandas, numpy,
matplotlib y scipy vienen preinstalados. Igual conviene que Ignacio lo abra una
vez: Colab cambia versiones sin avisar y ningún entorno simulado es el real.

---

## Cómo está organizado el proyecto

Leer `docs/PIPELINE.md` antes de tocar nada. En corto: **cada etapa es un
contrato** que declara qué archivos necesita y qué produce, y el runner lo hace
cumplir.

```bash
python pipeline/correr.py --listar     # qué hace cada etapa y de qué depende
python pipeline/correr.py 8            # una sola, con su diagnóstico completo
python pipeline/correr.py --verificar  # corre dos veces y compara hashes
python tests/test_invariantes.py       # las propiedades que tienen que valer
```

Once etapas: 01-05 construyen el dataset (eso era el TP1), 07-11 son el TP2
(perfilado, curación, diccionario, relaciones, figuras), 12-13 arman los
entregables. **El 06 falta a propósito**: era el diccionario y pasó a ser el 09
cuando se movió al final. Los números son identidad estable, no posición.

Piezas que conviene no romper:

- `pipeline/decisiones.py` es la **fuente única** de las cuatro decisiones de
  curación. De ahí salen el código que las aplica, las filas del diccionario y
  el informe que las justifica. Cambiar una decisión se hace ahí y solo ahí.
- `pipeline/06_entrega/contenido_tp2.py` tiene el texto y el código del
  notebook. **El notebook se genera, no se edita a mano.** Si alguien lo edita
  directo, el próximo `python pipeline/06_entrega/12_notebook.py` lo pisa.
- `tests/test_invariantes.py` es la red. Un hallazgo sin invariante se vuelve a
  perder.

---

## Decisiones cerradas, para no re-discutirlas

- **Las cuatro decisiones de curación no borran filas ni modifican valores.**
  Hacen visible el problema en vez de taparlo. El motivo: los tres problemas
  encontrados golpean a los grupos chicos y rurales, que son la población de
  mayor riesgo de abandono, así que limpiar por el camino fácil habría sesgado
  el dataset contra su propio objeto de estudio.
- **El titular del informe es la comparación urbana** (estatal 0,62 contra
  privada 0,38, que cubre el 93,5% de los estudiantes), no la de privada rural,
  que ilustra mejor pero descansa en el 0,7%.
- **La hipótesis sobre inasistencias va marcada como NO verificada.** Decisión
  explícita de Ignacio: reportarla como pregunta abierta, no como conclusión.
- **El Censo 2022 queda como propuesta para el TP3**, no para ahora.
- **No hacer hincapié en los errores del diccionario de la mentora.** Ignacio ya
  lo habló con Noelia y ella dijo que es común en proyectos reales de datos.
- **El informe no lleva autor individual.** Es del grupo M01. Pedido explícito
  de Ignacio: no quiere mandar al frente a los compañeros que no participaron.

---

## Contexto humano que importa

- **Los compañeros del grupo 1 no responden.** Ignacio hizo el TP2 solo. La
  intención es trabajar en grupo, así que conviene compartir el repo con ellos.
- **Noelia recomendó jupytext** el 04/09 para versionar notebooks. Acá el
  notebook se genera desde código, que da la misma propiedad por otro camino.
  **La condición concreta para adoptar jupytext**: que alguien empiece a editar
  el notebook a mano. Ahí el modelo del generador se rompe y jupytext pasa a ser
  la respuesta correcta.
- El TP3 (aprendizaje supervisado y no supervisado) **vence el 02/10**, y ese
  mismo día hay clase de la optativa Programación Distribuida de 18 a 22.

---

## El hallazgo que ordena lo que viene

**El proyecto no tiene una variable de abandono.** El proxy construido en el TP1
desde la EPH correlaciona +0,16 con el desempeño, o sea que no mide lo que dice
medir. Todo el TP2 describe desempeño y sobreedad, que son antecedentes
plausibles del abandono, no el abandono.

Sin resolver eso, el TP3 no tiene qué predecir. Es lo primero que hay que
plantear en la próxima reunión con Noelia, por encima de cualquier hallazgo.

Hay un camino medido: el repo de referencia que la mentora recomendó
(`github.com/agus476/radar-trayectorias-educativas-argentinas`) trae los flujos
oficiales por grado, incluida la columna de **salidos sin pase**, que es el
target real. Se midió el cruce contra el dataset del proyecto y **pega 1.174 de
1.174 claves, el 100%**, normalizando solo dos nombres de jurisdicción. El
script que lo mide está en `exploracion/20_cruce_con_repo_referencia.py`.

---

## Lo que quedó sin verificar

Honesto, para que nadie lo dé por hecho:

- **Nadie corrió el notebook en Google Colab de verdad.** Se simuló con las
  versiones que Colab trae hoy.
- **No se validó la corrección estadística** de los análisis, solo que corren y
  producen las salidas que declaran.
- **La hipótesis sobre inasistencias sigue sin verificar** y así está escrita en
  los tres artefactos. Cerrarla requiere datos de asistencia administrativa que
  este dataset no tiene.
- **Que el Censo 2022 sirva como reemplazo de la EPH es una propuesta**, no un
  hecho: no se descargó ni se cruzó contra nada.
