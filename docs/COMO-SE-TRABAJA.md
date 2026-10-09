# Cómo se trabaja El Factor D10S

El proceso lo lleva `/desarrollar` (skills globales en `~/.claude/skills/`). Acá va solo lo que este proyecto instancia distinto.

## El stack

Python (probado con 3.14 local y 3.12 en Colab) con pandas, numpy, scipy y scikit-learn. No hay base: todo son archivos CSV y parquet en `data/`. El producto que se entrega es un notebook de Google Colab autocontenido (baja los datos solo, fijados a un commit y con hash) más, cuando la consigna lo pide, un informe en PDF.

## Dónde vive cada cosa

| Qué | Dónde |
|---|---|
| El pipeline (la única forma de producir datos) | `pipeline/`, una carpeta por fase; el mapa de etapas es `pipeline/etapas.py` y el runner `pipeline/correr.py` |
| Decisiones de curación (fuente única: código, diccionario e informe salen de ahí) | `pipeline/decisiones.py` |
| Decisiones de diseño de cada entrega | `entregas/<NN-tema>/DECISIONES-*.md` (una entrada por tema; cuando cambia se reescribe con su fecha y quién decidió, y lo viejo queda como línea de historia) |
| Specs y tickets | `docs/tickets/<tema>/` (al cerrar, `docs/tickets/hecho/`) |
| Lo que viene de la mentora (consignas, devoluciones) | `mentoria/`, sin editar |
| Lo entregado de cada TP | `entregas/<NN-tema>/` |
| Narrativa de sesiones | `DEVLOG.md` |
| Glosario | no hay todavía; los términos del dominio están definidos en `PARA-EL-EQUIPO.md` y en `docs/` |

## El gate

```
python tests/test_invariantes.py
python pipeline/correr.py --verificar
```

El primero convierte en chequeo cada afirmación que el análisis hace sobre los datos (55 de 55 al 2026-10-09). El segundo corre el pipeline entero dos veces y compara el SHA-256 de cada salida: si cambia algo con la misma entrada, el pipeline no es reproducible y ningún número de abajo vale. Mientras el gate no cubra la etapa de modelado, todo merge pasa por Ignacio.

## Los tests

`tests/test_invariantes.py` es un script plano (sin pytest): `python tests/test_invariantes.py`. Cada chequeo imprime `[OK  ]` o `[FALLA]` con lo que afirma, y el total al final. Para una sola etapa: `python pipeline/correr.py <número o nombre>` corre solo esa y muestra su diagnóstico; `--desde N` corre de la N en adelante.

Ejemplo del dominio: "la curación conserva los 540.040 estudiantes".

## La receta para probar como usuario

El usuario es quien abre el notebook: la mentora, que lo corrige, y el grupo. La prueba es correr el notebook entero en una carpeta vacía (o en Colab) y que todas las celdas tengan salida sin error, con las figuras y los números iguales a los del pipeline. El TP2 se verificó así (25 de 25 celdas, 4 de 4 figuras, más un test ciego con Python 3.12 y pandas 2.2.2).

## Lo específico de este proyecto

- **Una fila no es un estudiante**: es jurisdicción, departamento, sector y ámbito. Todo resultado es ecológico (de grupos), nunca de personas.
- **Las reglas del contrato del pipeline son duras** (`pipeline/contrato.py`): ninguna etapa escribe sobre su propia entrada, misma entrada da misma salida, y lo que se afirma se mide.
- **Un vacío casi nunca es un cero.** Es el error más repetido del proyecto (`PARA-EL-EQUIPO.md`).
- **Todo cruce por nombre de departamento imprime su denominador** (DECISIONES-TP3, D3): filas y estudiantes que matchearon, y la lista de los que no.
- Puertas de un solo sentido: publicar en el repo público (`IVillanueva770/factor-d10s-m01`) y subir una entrega al aula. Las dos son de Ignacio.
