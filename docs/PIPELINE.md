# El pipeline del proyecto

Cómo está organizado el trabajo de datos, por qué así, y cómo tocarlo sin romperlo.

## La idea en una frase

Cada etapa es un contrato: declara qué archivos necesita y qué archivos produce, y el runner lo hace cumplir. Nadie tiene que acordarse del orden ni de qué depende de qué, porque está escrito en `pipeline/etapas.py` y se verifica al correr.

## El orden

```
data/raw/                        los crudos, no se tocan nunca
   │
   ├─ 01 aprender          ap2024_*.csv ──────────→ aprender_2024_proporciones.csv
   │
   ├─ 02 eph_unir          eph3t.zip ─────────────→ eph_3t2025_unida.parquet
   │      └─ 03 eph_indicadores ─────────────────→ eph_indicadores_provincia.csv
   │                                               eph_diccionario.csv
   │
   ├─ 04 integrar          (01 + 03) ─────────────→ dataset_maestro_base.csv
   │
   ├─ 05 armonizar         (04 + 02) ─────────────→ dataset_maestro_inicial.csv
   │                                                  ↑ el entregable del TP1
   ├─ 07 perfilado         (05) ──────────────────→ perfil_columnas.csv
   │                                                 docs/07_perfil_calidad.md
   ├─ 08 curar             (05) ──────────────────→ dataset_maestro_curado.csv
   │                                                 docs/08_decisiones_curacion.md
   ├─ 09 diccionario       (08) ──────────────────→ diccionario_variables.csv
   │                                                 armonizacion_fuentes.csv
   ├─ 10 relaciones        (08) ──────────────────→ docs/10_relaciones.md
   │
   └─ 11 figuras           (08) ──────────────────→ figuras/tp2_*.png
```

**Falta el 06 a propósito.** Era el diccionario, que pasó a ser el 09 cuando se
movió al final del pipeline para que documentara el dataset curado. Los números
son identidad estable y no posición: renumerar invalidaría cada referencia a
"la etapa 08" en commits, documentos y conversaciones, igual que renumerar
commits de git.

Para ver esto mismo con las rutas completas y qué hace cada etapa:

```bash
python pipeline/correr.py --listar
```

## Cómo se corre

```bash
python pipeline/correr.py                 # todas las etapas, en orden
python pipeline/correr.py 4               # solo la etapa 4 (o 'integrar')
python pipeline/correr.py --desde 4       # de la 4 en adelante
python pipeline/correr.py --verificar     # corre dos veces y compara hashes
python tests/test_invariantes.py          # las propiedades que tienen que valer
```

Correr una sola etapa muestra su diagnóstico completo. Correrlas todas muestra un resumen de una línea por etapa.

## Las tres reglas, y por qué

### 1. Ninguna etapa escribe sobre su propia entrada

Se verifica antes de ejecutar nada. Si una etapa declara el mismo archivo como entrada y como salida, el runner corta con `CONTRATO ROTO` y explica por qué.

**De dónde salió esta regla.** El 2026-09-03, midiendo si el pipeline era reproducible, apareció que la etapa de armonización leía `dataset_maestro_inicial.csv` y escribía encima del mismo archivo. Correrla dos veces seguidas sin rehacer la etapa anterior llevaba el dataset de **131 a 155 columnas**, apilando columnas armonizadas sobre las que ya estaban. No fallaba, no avisaba, y el resultado dependía de cuántas veces habías corrido el script. Por eso ahora la etapa 04 produce `dataset_maestro_base.csv` y la 05 lo lee para producir el maestro final.

Es el mismo tipo de problema que el pipeline ya tenía resuelto en otro lado: una regla escrita dos veces (la normalización de provincias) fallaba en silencio, y por eso existe `pipeline/comun.py`.

### 2. Misma entrada, misma salida, siempre

```bash
python pipeline/correr.py --verificar
```

Corre el pipeline entero dos veces y compara los SHA-256 de todas las salidas. Si alguna difiere, hay una fecha, un orden no determinista o un random sin semilla adentro, y **ningún número que salga de ahí es confiable** hasta arreglarlo.

Estado al 2026-09-07: **18 de 18 salidas idénticas byte a byte** y **55 de 55 invariantes** en verde. Las 5 salidas que ya existían al cerrar el TP1 siguen coincidiendo con las entregadas y aprobadas.

> Estos dos números crecen con el proyecto, así que **se leen corriendo el pipeline, no de acá**. Este párrafo quedó desactualizado una vez (decía 8 y 41 cuando ya eran 18 y 55) y de ahí lo copió el informe del TP2.

### 3. Lo que se afirma, se mide

`pipeline/MANIFIESTO.json` guarda, por etapa, el hash y la forma (`1.174 x 131`) de cada salida. Al correr el pipeline completo, el runner compara contra el manifiesto y avisa qué cambió:

```
CAMBIOS respecto del manifiesto:
  - 05_armonizar: data/processed/dataset_maestro_inicial.csv cambio (1.174 x 131 -> 1.174 x 138)
```

Sirve para lo que más cuesta cuando un proyecto crece: tocar una etapa de arriba y saber exactamente qué se movió abajo. El manifiesto no lleva timestamp a propósito, porque si lo llevara dos corridas idénticas darían archivos distintos y dejaría de servir para comparar.

## Qué hay en cada carpeta

| Carpeta | Qué es |
|---|---|
| `pipeline/` | Las etapas que construyen el dataset. Es lo que hay que correr. |
| `exploracion/` | Los scripts que **justifican** las decisiones del pipeline: por qué se eligieron esos bloques de Aprender, por qué el ingreso se pondera con PONDIH, por qué el cruce es a nivel provincia. No hace falta correrlos, pero son la evidencia detrás de cada elección. |
| `tests/` | `test_invariantes.py`: las propiedades que tienen que valer sobre los datos. Es la red: si tocás una etapa y rompés algo que antes valía, falla acá en vez de producir un dataset malo en silencio. |
| `data/raw/` | Los crudos. No se modifican nunca. |
| `data/interim/` | Resultados intermedios. Se regeneran corriendo el pipeline. |
| `data/processed/` | El dataset maestro, el diccionario y la armonización. |
| `notebooks/` | Los entregables de la mentoría. |
| `docs/` | Este archivo y lo que documente decisiones. |

## Cómo agregar una etapa

1. Escribí el script en `pipeline/`, numerado, con un `main()` y un docstring que explique **por qué** hace lo que hace (no qué).
2. Declaralo en `pipeline/etapas.py` con sus entradas y salidas.
3. Corré `python pipeline/correr.py --listar`. Si la declaración está mal, te lo dice ahí.
4. Corré `python pipeline/correr.py --verificar` y `python tests/test_invariantes.py`.

Si la etapa establece una propiedad nueva que tiene que valer siempre, agregá el invariante en `tests/test_invariantes.py`. Un hallazgo sin invariante se vuelve a perder.

## Lo que este pipeline tiene y conviene no perder

Dos piezas que no son estándar y que valen:

- **`tests/test_invariantes.py`**: convierte en verificación automática cada afirmación que el análisis hace sobre los datos. La mayoría de los proyectos de datos no tiene esto, y es lo que separa "el número me dio" de "el número no puede estar mal".
- **Las columnas `cob__`**: cada bloque de variables lleva al lado qué fracción de la fila quedó representada. Es el indicador de calidad viajando pegado al dato, en vez de en un comentario aparte.
