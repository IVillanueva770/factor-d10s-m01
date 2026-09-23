# TP3 (entregable 3, etapa Machine Learning): la consigna, leída el 2026-09-23

Fuente: `TP3_ML_El_Factor_D10S.pdf` en esta misma carpeta, bajado del repo de la mentora el 23/09 desde el commit `c92c3e2` de https://github.com/NoeliaFerrero/Proyecto_Mentoria_FAMAF_2026. Publicado por Noelia Ferrero en Slack el miércoles 23/09 8:40, con puesta en común el mismo día en el horario de siempre.

## Lo que hay que entender antes de leer los puntos

Noelia lo dijo en Slack y el PDF lo repite: **no es una guía paso a paso, es el brief de un proyecto.** Ella pone el problema, los datos y las cuestiones a resolver; las decisiones, las alternativas probadas y su justificación son del equipo. Lo que se evalúa es la cadena de decisiones defendibles, no el modelo.

Y la regla que ordena todo el entregable, textual: *"el modelo no empieza con RandomForestClassifier(). Empieza preguntándonos qué estamos intentando predecir y si nuestros datos realmente permiten hacerlo."*

## El nudo del TP, que es de diseño y no de modelado

La pregunta del proyecto es el abandono escolar, pero **el PDF advierte explícitamente que no se dé por supuesto que se puede predecir el abandono de un estudiante individual.** Dos razones, las dos del dataset: una fila no necesariamente representa a una persona, y Aprender y la EPH **no tienen una llave que vincule a una persona de una fuente con una de la otra**.

Por eso lo primero es **determinar qué unidad de análisis se puede sostener con evidencia** y qué tipo de predicción es razonable. Si el abandono individual no se puede observar ni construir con una regla defendible, la salida correcta no es forzar un target: es **reformular la pregunta hacia la unidad que los datos sí sostienen, o documentar por qué el problema original no se puede resolver con estas fuentes**. El PDF dice que demostrar eso también es un resultado válido.

## Los 12 puntos, resumidos

1. **El desafío**: el abandono escolar como pregunta de partida, con la advertencia de granularidad de arriba.
2. **Antes de modelar, definir el problema** (cinco preguntas a responder en el notebook, con palabras propias): qué representa una fila · qué fenómeno se predice, definido operacionalmente · si existe una variable que lo observe o si hay que construirla con una regla válida · qué información estaba disponible **antes** del resultado (nada que solo se conozca después) · qué se puede y qué no se puede afirmar.
3. **Definición del target, sin vender humo**: un target es lo que los datos permiten observar y definir de manera reproducible. Si se construye, la regla se explica y tiene que poder aplicarse igual a todas las observaciones. Trae una tabla de tres situaciones (existe la variable / se puede construir / no se puede sin asumir información que no está) con qué hacer en cada una.
4. **Preparación de los datos**: se parte del dataset que dejó el EDA, no se repite el análisis. Revisar tipos, faltantes y categorías; decidir y explicar qué se conserva, transforma o descarta; **evitar variables que filtren el target o que solo existan después del evento**; y si hay balanceo, imputación o escalado, pensar en qué momento del pipeline va para no generar leakage.
5. **Baseline obligatorio**: una referencia simple antes de cualquier modelo sofisticado, para poder contestar si el modelo aprende algo útil o si solo complica un problema que una regla simple ya resuelve.
6. **Experimentar con modelos**: no importa la cantidad de algoritmos, importa explicar por qué se probó cada uno y qué se aprendió al compararlos. Ajustar hiperparámetros si tiene sentido; **si una técnica no funciona, eso también es un resultado y se cuenta**.
7. **Evaluación, sin enamorarse del accuracy**: métrica atada al problema y nunca una sola. Para clasificación, según corresponda: matriz de confusión, precision, recall, F1, ROC-AUC y PR-AUC. Revisar el desbalance (un accuracy alto puede ser engañoso), analizar **qué tipo de observaciones clasifica mal**, y justificar la estrategia de separación entrenamiento/evaluación.
8. **Interpretación**: traducir los resultados a lenguaje de negocio o investigación. Qué variables aportan · si los patrones son razonables o raros · qué errores son relevantes · qué conclusiones se sostienen **y cuáles no**. Advertencia explícita: que una variable sirva para predecir no la vuelve causa. Predicción y causalidad son preguntas distintas.
9. **Qué se espera como entrega**: un MVP defendible, no un notebook de 80 celdas con 14 modelos. Nueve piezas visibles: problema y unidad de análisis · target (qué, cómo se definió, por qué es válido) · datos y decisiones de preparación · baseline con su resultado · al menos **una** alternativa al baseline, justificada · evaluación con métricas adecuadas, comparación y análisis de errores · interpretación de los patrones · limitaciones (datos, granularidad, representatividad, target) · próximos pasos con más datos, más tiempo u otra fuente.
10. **Libertad para experimentar**: no hay un único modelo correcto, no hay que usar todas las técnicas de clase, se puede justificar una decisión distinta a la sugerida si los datos la respaldan, y un experimento que no mejora nada igual aporta.
11. **Checklist antes de entregar** (12 ítems): sé qué representa una fila · puedo explicar la unidad de análisis · puedo explicar qué predigo · el target está observado o construido con regla explícita · no invento información que los datos no tienen · revisé leakage · separé bien entrenamiento y evaluación · tengo baseline · elegí métricas adecuadas · analicé errores y no solo métricas · puedo explicar qué aprendí del modelo · dejé claras las limitaciones.
12. **La pregunta que queda abierta al final**: qué se puede afirmar con estos datos y qué sería inventar una historia que los datos no sostienen.

## Lo que esto implica para nuestro trabajo

- El primer entregable real del TP3 **no es código**: son las cinco respuestas del punto 2 y la decisión de unidad de análisis. Todo lo demás cuelga de ahí y hacerlo al revés es el error que el PDF anticipa.
- Las limitaciones de granularidad y la ausencia de llave entre Aprender y EPH **ya están medidas** en nuestro `INVENTARIO-DATOS.md` y en `docs/10_relaciones.md`. Es material directo para los puntos 1, 3 y 8.
- El baseline (punto 5) y el análisis de errores (punto 7) son los dos lugares donde se pierde nota fácil por omisión, porque no dependen de acertar sino de haberlos hecho.
