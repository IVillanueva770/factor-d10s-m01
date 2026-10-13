# DEVLOG - El Factor D10S (mentoría M01, Diplodatos 2026)

## Estado Actual

Repo único para las tres entregas de la mentoría (abandono escolar, mentora Noelia Ferrero). TP1 (dataset maestro) aprobado, TP2 (EDA y curación) aprobado. TP3 (Machine Learning) construido el 09/10, día de la entrega: el modelado vive en `pipeline/05_modelado/` como etapas 12 a 18, con las variantes en `pipeline/modelado.py`; el notebook se genera con `pipeline/06_entrega/14_notebook_tp3.py` y el PDF corto con `15_informe_tp3.py`. Gate: `python tests/test_invariantes.py` y `python pipeline/correr.py --verificar`. Cómo se trabaja: `docs/COMO-SE-TRABAJA.md`. Decisiones del TP3: `entregas/03-machine-learning/DECISIONES-TP3.md` (sección "Vigente al 2026-10-09"). Lo que sigue: el video final del 07/11 (pitch sin código, el PDF es su base).

## Tareas Activas

- [ ] TP3: subir al aula (Ignacio) el PDF y, en el texto, el link de Colab y el del repo (todo publicado el 13/10, commit `5c65aae`)
- [ ] Correr `--verificar` completo y actualizar `pipeline/MANIFIESTO.json` (se cortó el 09/10 por falta de RAM)
- [ ] Relevamiento 2025 (ciclo 2024) cuando se publique, para sacar el desfase de un año
- [ ] Video final, vence el 07/11

## Decisiones de Arquitectura

- El pipeline es la única forma de producir datos: cada etapa declara entradas y salidas (`pipeline/contrato.py`) y `--verificar` compara hashes de dos corridas.
- Los notebooks y PDF se generan desde código; los números del texto se leen de las salidas, nunca se escriben a mano.
- TP3: cada variante de modelado es una entrada de `EXPERIMENTOS` en `pipeline/modelado.py`, evaluada con la misma partición y las mismas métricas; no hay un script por variante.

## Sesiones

### [2026-10-13] - Sesión 2 (TP3, cierre y fuentes; se entrega tarde con OK de Ignacio)
**Objetivo:** cerrar lo que el 09/10 quedó frágil y dejarlo trackeable.
**Hecho:**
- `FUENTES-TP3.md`: cada asociación con cita textual y link verificado; separa documentado, parcial y hallazgo propio. El desfase de un año del Relevamiento pasó de inferido a documentado (el cuadernillo pide la trayectoria del ciclo anterior).
- Experimentos nuevos: `provincia_y_perfil` (0,797 contra 0,746 provincia sola y 0,752 perfil solo) y cortes en el tercio y el quinto (la conclusión aguanta). La regla del nombre del target pasó a un solo lugar (`modelado.target_de`).
- Notebook y PDF reescritos con el relato nuevo por un delegado; figura 1 con el modelo combinado; 80 de 80 tests; publicado en GitHub (`5c65aae`) con el link de Colab en el PDF.
**Decisiones:** la conclusión central cambia de "casi todo lo sabe la provincia" a "provincia y perfil aportan información distinta" (Ignacio, 13/10). El registro distinto por provincia queda como hipótesis propia: la fuente oficial sostiene la comparabilidad.
**Problemas encontrados:** el texto del 09/10 daba asociaciones por "esperables" sin fuente (lo marcó Ignacio). El guardián de RAM pausó los tests 47 minutos. Git trataba los PDF como texto (arreglado con `*.pdf binary`; el PDF del TP2 en el repo puede estar alterado).
**Fricción del flujo:** el delegado de texto rindió bien con el encargo cerrado (decisiones y fuentes en archivos); la auditoría página por página la hizo el orquestador.


### [2026-10-09] - Sesión 1 (TP3, día de la entrega)
**Objetivo:** cerrar la parte de Ignacio del TP3 (nadie del grupo tenía tareas asignadas).
**Hecho:**
- Medido el Relevamiento Anual del repo de referencia (commit `1bbaa58`): cruce 1.174 de 1.174 grupos; 12 jurisdicciones son 7 + 5 y 12 son 6 + 6, por eso el target usa los índices 11 y 12 (los dos últimos años en todas).
- Etapas 12 a 18: bajar el Relevamiento con hash, target y estabilidad, dataset de modelado, experimentos (5 combinaciones, 3 reglas simples y 2 modelos, validación estratificada y por provincia), errores e interpretación por bloques, perfiles k-means de los "no alto", figuras.
- Resultado: la logística ordena 0,752 contra 0,746 de la regla "la provincia"; probando en provincias no vistas, 0,683 contra 0,651 de sector y ámbito. EPH y edificio casi no aportan.
**Decisiones:** ver DECISIONES-TP3, sección del 09/10 (año 2024, EPH en variante, sin flujos del mismo ciclo, clasificación de "abandono alto" en el cuarto superior, perfiles como segunda etapa).
**Problemas encontrados:**
- El archivo "2024" del Relevamiento parece traer el ciclo 2023 (inferido de la matrícula, no documentado).
- El target de dos años es inestable (53% de los "alto" repite de un archivo al siguiente; 70% con la secundaria entera).
- Las métricas por partición tienen que calcularse dentro de cada parte: juntando las predicciones, una regla constante dejaba de dar 0,5.
- `--verificar` y los tests quedaron pausados por el guardián de RAM (otra sesión corría whisper).
**Fricción del flujo:** con 4 horas de plazo, grill, spec y tickets se comprimieron en las cajitas y en DECISIONES-TP3; los agentes en paralelo rindieron para figuras y PDF, no para variantes (son configuración).
**Próximos pasos:** subir la entrega; `--verificar` completo; video del 07/11.
