"""Genera el notebook de entrega.

El notebook se genera desde este script en vez de editarse a mano para que no
se desincronice del pipeline: si cambia una decision en src/, se cambia aca y
se regenera.

El notebook resultante es autocontenido: se baja los datos solo, fijados a un
commit exacto del repo de la mentoria, y verifica el hash de cada archivo.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DESTINO = BASE_DIR / "notebooks" / "TP1_dataset_maestro_El_Factor_D10S.ipynb"

celdas = []


def en_lineas(texto):
    """El formato .ipynb guarda el contenido como lista de lineas CON su salto.

    Sin los saltos el notebook se abre igual, pero todas las lineas quedan
    concatenadas en una sola y no ejecuta.
    """
    return texto.splitlines(keepends=True)


def md(texto):
    celdas.append({"cell_type": "markdown", "metadata": {},
                   "source": en_lineas(texto.strip())})


def code(texto):
    celdas.append({"cell_type": "code", "metadata": {}, "execution_count": None,
                   "outputs": [], "source": en_lineas(texto.strip("\n"))})


# =========================================================== 1. EL PROYECTO
md("""
# El Factor D10S: dataset maestro inicial

**Entregable 1 de la mentoría** · Grupo M01 · Mentora: Noelia Ferrero

La pregunta del proyecto es si se pueden detectar señales tempranas de abandono
escolar cruzando dos fuentes públicas argentinas: las **Pruebas Aprender** (la
evaluación censal del Ministerio de Educación) y la **EPH** (la encuesta de
hogares del INDEC).

Esta primera entrega no responde esa pregunta: construye la base sobre la que
se va a trabajar. El resultado es una tabla única que combina el desempeño y el
contexto de los estudiantes con indicadores socioeconómicos del lugar donde
viven, más su diccionario de variables y el proceso documentado para poder
rehacerla.

## Cómo leer este notebook

Cada sección tiene la misma forma: **qué queremos hacer**, el código, y **qué
encontramos**. Ese último bloque es el que importa: varias decisiones del
pipeline salieron de encontrarnos con algo inesperado en los datos, y están
contadas donde aparecieron.

El notebook se baja los datos solo. No hay que subir nada ni montar Drive:
alcanza con "Entorno de ejecución → Ejecutar todo".

## Índice

1. [Preparación y descarga de los datos](#scrollTo=prep)
2. [Las fuentes: qué hay adentro](#scrollTo=fuentes)
3. [Aprender: tres bases y una decisión](#scrollTo=aprender1)
4. [Aprender: qué variables conservamos](#scrollTo=aprender2)
5. [EPH: unir hogares con personas](#scrollTo=eph)
6. [El puente geográfico](#scrollTo=puente)
7. [Indicadores socioeconómicos de contexto](#scrollTo=indicadores)
8. [Armonizar las categorías entre fuentes](#scrollTo=armonizacion)
9. [El dataset maestro](#scrollTo=maestro)
10. [Diccionario de variables](#scrollTo=diccionario)
11. [Qué muestran los datos](#scrollTo=graficos)
12. [Dificultades encontradas](#scrollTo=dificultades)
13. [Limitaciones y qué sigue](#scrollTo=limitaciones)
""")

# ============================================================ 2. PREPARACION
md("""
<a name="prep"></a>
## 1. Preparación y descarga de los datos

Los datos se bajan del repositorio de la mentoría, **fijados a un commit
específico**. Si el repo cambia más adelante, este notebook sigue bajando
exactamente los mismos archivos y sus resultados no se mueven.

Además se verifica el hash SHA-256 de cada descarga. Si un archivo cambiara o
llegara cortado, la celda corta la ejecución en vez de seguir con datos
distintos a los que produjeron estos resultados.
""")

code('''
import hashlib
import io
import re
import unicodedata
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

# Commit exacto del repo de la mentoria. No usar "main": si el repo cambia,
# los resultados de este notebook dejarian de ser reproducibles.
COMMIT = "60db991aab25b69f34b83b521148a463689300af"
REPO = f"https://raw.githubusercontent.com/NoeliaFerrero/Proyecto_Mentoria_FAMAF_2026/{COMMIT}"

ARCHIVOS = {
    "aprender_lengua": (
        f"{REPO}/data/raw/2024%20Base%20APRENDER%20-%20Censal%20-%20Secundaria"
        f"%205-6%20a%C3%B1o%20-%20Agregada%20-%20Desempe%C3%B1os%20de%20Lengua(in).csv",
        "7d6f78503ce6f9e22203e273e2e09e219c1239426c78fdf3e12a6ea95f694b04"),
    "aprender_matematica": (
        f"{REPO}/data/raw/2024%20Base%20APRENDER%20-%20Censal%20-%20Secundaria"
        f"%205-6%20a%C3%B1o%20-%20Agregada%20-%20Desempe%C3%B1os%20de%20Matematica(in).csv",
        "264cdfbd6d9e3fae173b4e9a96e181cd5adf0e5d32da3be6ade4b449b327bd7f"),
    "eph": (
        f"{REPO}/data/raw/EPH_usu_3_Trim_2025_xls.zip",
        "685805d0a4ffdbef107c073848df025e9fb813f66475f20c18a09c5f3a1baaf9"),
}

DATOS = Path("datos")
DATOS.mkdir(exist_ok=True)


def descargar(nombre):
    """Baja el archivo si no esta, y verifica su hash siempre."""
    url, hash_esperado = ARCHIVOS[nombre]
    destino = DATOS / f"{nombre}{Path(url).suffix}"

    if not destino.exists():
        respuesta = requests.get(url, timeout=180)
        respuesta.raise_for_status()
        destino.write_bytes(respuesta.content)

    hash_real = hashlib.sha256(destino.read_bytes()).hexdigest()
    if hash_real != hash_esperado:
        raise RuntimeError(
            f"{nombre}: el archivo descargado no coincide con el esperado.\\n"
            f"  esperado: {hash_esperado}\\n  obtenido: {hash_real}")

    print(f"  {nombre:22s} {destino.stat().st_size / 1e6:6.1f} MB  hash OK")
    return destino


print("Descargando y verificando:")
rutas = {nombre: descargar(nombre) for nombre in ARCHIVOS}
''')

# ============================================================== 3. FUENTES
md("""
<a name="fuentes"></a>
## 2. Las fuentes: qué hay adentro

Antes de tocar nada conviene tener claros dos conceptos, porque explican casi
todo lo que vamos a decidir después.

### Base agregada y microdato

Un **microdato** es una tabla donde cada fila es una persona. Una **base
agregada** es una tabla donde cada fila es un grupo, y las columnas son
recuentos de ese grupo.

Las bases de Aprender que se publican son **agregadas**. Buscamos el microdato
a nivel estudiante en el portal de datos abiertos y no existe: los cinco años
publicados (2019, 2021, 2022, 2023 y 2024) traen solamente bases agregadas, y
el propio Ministerio explica por qué en su documento metodológico, donde la
agregación aparece como el método de anonimización.

Esto tiene una consecuencia grande y conviene decirla ahora: **la unidad mínima
de análisis del proyecto no es el estudiante, es el grupo
jurisdicción + departamento + sector + ámbito**.

### Factor de expansión

Cuando una encuesta no llega a todos, cada respuesta "representa" a varias
personas. Ese multiplicador es el **factor de expansión** o **ponderador**.

Si se encuesta a 1 de cada 100 personas, cada encuestado pesa 100: para saber
el total no se cuenta 1, se suman los 100. Por eso los números de estas bases
tienen decimales. Un `144,28` no son 144 personas contadas una por una, es la
suma de los pesos de un puñado de estudiantes reales.

Aprender es censal, pero igual falta gente el día de la prueba y hay escuelas
que no responden, así que el Ministerio ajusta los pesos para que el total
cierre con la matrícula real. La EPH, que sí es muestral, trae su ponderador en
la columna `PONDERA`.
""")

code('''
# Los CSV del Ministerio vienen en formato europeo: separador ';', encoding
# latin-1 y coma decimal. Sin declararlo, pandas devuelve una sola columna de
# texto y no se nota hasta tres pasos despues.
LECTURA_APRENDER = {"sep": ";", "encoding": "latin-1", "dtype": str}
CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]


def a_numero(serie):
    """Texto con coma decimal a float. Los blancos (' ') quedan en NaN."""
    return pd.to_numeric(
        serie.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce")


def cargar_aprender(ruta):
    df = pd.read_csv(ruta, **LECTURA_APRENDER)
    for columna in df.columns:
        if columna not in CLAVES:
            df[columna] = a_numero(df[columna])
    return df.sort_values(CLAVES).reset_index(drop=True)


lengua = cargar_aprender(rutas["aprender_lengua"])
matematica = cargar_aprender(rutas["aprender_matematica"])

print(f"Aprender Lengua:     {lengua.shape[0]:,} filas x {lengua.shape[1]:,} columnas")
print(f"Aprender Matematica: {matematica.shape[0]:,} filas x {matematica.shape[1]:,} columnas")
print()
print("Las cuatro primeras columnas son la clave territorial:")
print(lengua[CLAVES].head(3).to_string(index=False))
print()
print("Y las otras mil son categorias de respuesta con su conteo expandido:")
print(lengua[["ap03_Masculino", "ap03_Femenino", "NSE_nivel_Q1"]].head(3).to_string(index=False))
''')

md("""
**Qué encontramos.** 1.175 filas y unas 1.035 columnas por archivo. Las filas
son combinaciones únicas de jurisdicción, departamento, sector de gestión y
ámbito: 24 jurisdicciones y 530 departamentos, con 871 filas de gestión estatal
contra 304 privadas, y 712 urbanas contra 463 rurales.

Cada columna del cuestionario tiene la forma `pregunta_categoría`, y su valor
es la cantidad expandida de estudiantes que eligieron esa categoría. O sea que
`ap03_Femenino = 144,28` no dice "esta persona es mujer": dice "en este
departamento hay unas 144 estudiantes mujeres".
""")

# ============================================================ 4. APRENDER 1
md("""
<a name="aprender1"></a>
## 3. Aprender: tres bases y una decisión

El repositorio trae **tres** archivos de Aprender 2024: uno con el desempeño en
Lengua, otro con el de Matemática y un tercero llamado "Solo CC". Los tres
tienen las mismas 1.175 filas y casi las mismas columnas, así que lo natural
sería tomar uno y pegarle los desempeños de los otros.

Antes de hacerlo hay que responder si eso es válido.
""")

code('''
def total_del_bloque(df, prefijo):
    """Suma las categorias de una pregunta: da el total de estudiantes."""
    return df[[c for c in df.columns if c.startswith(prefijo)]].sum(axis=1)


# Cualquier pregunta sirve para contar el total: todas las categorias de una
# pregunta cubren a toda la poblacion. Lo comprobamos con cuatro distintas.
print("Total nacional segun distintas preguntas, en la base de Lengua:")
for prefijo, nombre in [("ap03_", "sexo"), ("sobreedad_", "sobreedad"),
                        ("NSE_nivel_", "nivel socioeconomico"),
                        ("repitencia_", "repitencia")]:
    print(f"  {nombre:22s} {total_del_bloque(lengua, prefijo).sum():>12,.1f}")

print()
print("El mismo total, segun cada base:")
for nombre, df in [("Lengua", lengua), ("Matematica", matematica)]:
    print(f"  {nombre:22s} {total_del_bloque(df, 'ap03_').sum():>12,.1f}")
''')

md("""
**Qué encontramos.** Dentro de una base, las cuatro preguntas dan exactamente
el mismo total: 540.040. Eso confirma que todas cuentan a la misma gente y que
los ponderadores están calibrados para cerrar en un número exacto.

Entre bases, en cambio, el total no coincide. Y comparando celda por celda,
537 de las 1.027 columnas compartidas tienen valores distintos según el
archivo. Misma provincia, mismo departamento, mismo año, distinto número.

Nuestra primera hipótesis fue que las tres bases contaban poblaciones anidadas
(los del cuestionario contendrían a los que rindieron). La descartamos
midiendo: si fuera así, "Solo CC" sería siempre la base más grande, y es la más
grande en 495 filas de 1.175, no en todas.

La respuesta estaba en el documento metodológico del Ministerio. Dice, primero,
que la información de Aprender se publica en tres bases (desempeño en Lengua,
desempeño en Matemática, y los cuestionarios complementarios), y que **según el
análisis que se quiera hacer hay que usar la base correspondiente**. Y dice,
después, que las bases están ponderadas por el factor de expansión
correspondiente a **cada uno** de esos tres cuestionarios.

O sea: tres factores de expansión distintos. Los conteos de una base y otra no
son directamente comparables, y mezclarlos significa sumar cosas calculadas
sobre denominadores diferentes.
""")

code('''
# ¿Cuanto difieren entre si las dos bases que si vamos a usar?
total_lengua = total_del_bloque(lengua, "ap03_")
total_matematica = total_del_bloque(matematica, "ap03_")
discrepancia = (total_lengua - total_matematica).abs() / total_lengua * 100

print(f"Discrepancia entre Lengua y Matematica, fila por fila:")
print(f"  mediana: {discrepancia.median():.2f}%")
print(f"  percentil 90: {discrepancia.quantile(0.90):.2f}%")
print(f"  maxima: {discrepancia.max():.2f}%")
print(f"  filas que difieren mas de 10%: {(discrepancia > 10).sum()} de {len(discrepancia):,}")
''')

md("""
**Qué encontramos.** Entre Lengua y Matemática la discrepancia mediana es
0,16%, y solo 5 filas de 1.175 superan el 10%. Tiene sentido: son los mismos
chicos rindiendo dos pruebas el mismo día. Casi toda la diferencia que veíamos
antes la aportaba la tercera base.

**Las decisiones que tomamos:**

1. La base de **Lengua** aporta el cuestionario completo y el desempeño en
   Lengua.
2. De la base de **Matemática** tomamos solamente su bloque de desempeño.
3. **"Solo CC" se descarta.** No aporta ninguna columna propia (lo verificamos:
   cero) y es la que se comporta distinto. Queda disponible como verificación
   cruzada si hiciera falta.
4. Todo se convierte a **proporciones dentro de cada base**, en vez de trabajar
   con los conteos. Así el denominador queda explícito y adentro de una misma
   base, que es la única forma de que los números de dos archivos se puedan leer
   juntos sin mentir.
5. Las 5 filas discrepantes no se eliminan: se **marcan**, para poder repetir
   cualquier análisis sin ellas y comprobar que el resultado no cambia.
""")

# ============================================================ 5. APRENDER 2
md("""
<a name="aprender2"></a>
## 4. Aprender: qué variables conservamos

El cuestionario tiene 191 preguntas. La consigna pide conservar solo las
esenciales, así que hay que elegir.

Un detalle que costó tiempo: el diccionario que viene en el repositorio es el
de **2022** y usa otra numeración, así que no sirve para 2024. Por suerte no
hace falta: los nombres de las columnas traen las opciones de respuesta, y con
eso cada bloque se identifica solo. Por ejemplo, el bloque cuyas categorías son
`Ninguna_falta / Menos_de_5_faltas / ... / 30_o_más_faltas` es, sin lugar a
dudas, el de inasistencias.

### Cobertura de un bloque

Hay un tercer concepto que necesitamos antes de seguir. Cuando pasamos un
bloque a proporciones, el denominador son los estudiantes que **respondieron
esa pregunta**, no todos los de la fila. La **cobertura** es la relación entre
esos dos números: qué fracción de la fila quedó representada en el bloque.

Vale la pena guardarla porque no es siempre 1, y sin ella no hay forma de
saber sobre cuánta gente se calculó cada proporción.
""")

code('''
# Bloque de columnas -> nombre legible. El bloque se identifica por el prefijo
# del nombre de columna y las categorias salen del sufijo.
BLOQUES = {
    "ap03_": "sexo",
    "ap12_": "tamano_hogar",
    "ap19_": "libros_hogar",
    "ap24_": "asistio_jardin",
    "ap27_": "inasistencias",
    "ap31_": "horas_estudio",
    "edadA_junio2024_": "edad",
    "sobreedad_": "sobreedad",
    "repitencia_": "repitencia",
    "migracion_": "migracion",
    "clima_": "clima_escolar",
    "NSE_nivel_": "nse",
    "Nivel_Ed_Madre_": "educ_madre",
    "Nivel_Ed_Padre_": "educ_padre",
}

# Categorias que no son respuestas reales. Ojo: en las bases 2024 vienen
# SIEMPRE vacias, asi que no sirven para medir la no respuesta. Para eso esta
# la cobertura.
NO_RESPUESTA = {"Blanco", "No_disponible", "Multimarca", "No_corresponde",
                "_Blanco", "_No_disponible"}


def normalizar_nombre(texto):
    """'De_21_a_50_libros' -> 'de_21_a_50_libros', sin tildes."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", texto)
                         if unicodedata.category(c) != "Mn")
    limpio = re.sub(r"[^0-9a-zA-Z]+", "_", sin_tildes).strip("_").lower()
    return re.sub(r"_+", "_", limpio)


def proporciones_del_bloque(df, prefijo, nombre, total_fila):
    """Conteos de un bloque a proporciones sobre quienes respondieron."""
    validas = [c for c in df.columns
               if c.startswith(prefijo) and c[len(prefijo):] not in NO_RESPUESTA]
    respondieron = df[validas].sum(axis=1, min_count=1)

    proporciones = pd.DataFrame({
        f"{nombre}__{normalizar_nombre(c[len(prefijo):])}":
            df[c].fillna(0) / respondieron
        for c in validas})
    return proporciones, (respondieron / total_fila).rename(f"cob__{nombre}")
''')

md("""
Sobre el `fillna(0)`: tratamos los valores vacíos como ceros, y eso hay que
justificarlo porque si un vacío fuera en realidad un dato oculto estaríamos
borrando justo a las categorías más chicas, que son las de los casos más
vulnerables.

Lo verificamos de dos maneras. El **valor mínimo de toda la matriz es 1,0000** y
hay 2.140 valores por debajo de 2: si el Ministerio suprimiera celdas chicas
por confidencialidad, esos valores no existirían, porque el umbral habitual de
supresión es 3 o 5. Y los bloques censales **cierran exacto** aun teniendo
celdas vacías, lo que solo puede pasar si esas celdas valen cero.
""")

code('''
# Antes de construir: hay filas que el Ministerio publica con la clave
# territorial y las 1.031 columnas vacias. Arrastrarlas ensucia los promedios.
sin_datos = lengua.drop(columns=CLAVES).isna().all(axis=1)
if sin_datos.any():
    print("Filas sin ningun dato, descartadas:")
    for _, fila in lengua.loc[sin_datos, CLAVES].iterrows():
        print(f"  {' / '.join(fila.astype(str))}")
    lengua = lengua[~sin_datos].reset_index(drop=True)
    matematica = matematica[~sin_datos.values].reset_index(drop=True)

# Las dos bases tienen que describir las mismas filas en el mismo orden antes
# de tomar columnas de una y de la otra.
assert lengua[CLAVES].equals(matematica[CLAVES])

aprender = lengua[CLAVES].copy()
aprender["estudiantes"] = total_del_bloque(lengua, "ap03_")
total_matematica = total_del_bloque(matematica, "ap03_")

coberturas = {}
for prefijo, nombre in BLOQUES.items():
    props, cobertura = proporciones_del_bloque(
        lengua, prefijo, nombre, aprender["estudiantes"])
    aprender = pd.concat([aprender, props], axis=1)
    coberturas[nombre] = cobertura

for df, prefijo, nombre, total in [
        (lengua, "ldesemp_", "desemp_lengua", aprender["estudiantes"]),
        (matematica, "mdesemp_", "desemp_matematica", total_matematica)]:
    props, cobertura = proporciones_del_bloque(df, prefijo, nombre, total)
    aprender = pd.concat([aprender, props], axis=1)
    coberturas[nombre] = cobertura

aprender = pd.concat([aprender, pd.DataFrame(coberturas).add_prefix("cob__")],
                     axis=1)
aprender["flag_discrepancia_bases"] = (
    (aprender["estudiantes"] - total_matematica).abs()
    / aprender["estudiantes"] > 0.10)

# Verificacion: cada bloque suma 1, o no tiene dato para esa fila. Cualquier
# otra cosa es un defecto de construccion y corta aca.
print(f"{'bloque':20s} {'suman 1':>9s} {'sin dato':>9s} {'raras':>7s}")
for nombre in coberturas:
    columnas = [c for c in aprender.columns if c.startswith(f"{nombre}__")]
    suma = aprender[columnas].sum(axis=1)
    sin_dato = aprender[columnas].isna().all(axis=1)
    raras = ~(suma.between(0.999, 1.001) | sin_dato)
    print(f"{nombre:20s} {suma.between(0.999, 1.001).sum():>9,} "
          f"{sin_dato.sum():>9,} {raras.sum():>7,}")
    assert raras.sum() == 0, f"{nombre}: {raras.sum()} filas mal formadas"

print()
print(f"Tabla de Aprender: {aprender.shape[0]:,} filas x {aprender.shape[1]:,} columnas")
print(f"Estudiantes representados: {aprender['estudiantes'].sum():,.0f}")
''')

code('''
print("Cobertura por bloque (que fraccion de la fila quedo representada):")
cobertura = pd.DataFrame(coberturas)
resumen_cobertura = pd.DataFrame({
    "mediana": cobertura.median(),
    "minima": cobertura.min(),
}).sort_values("mediana")
print(resumen_cobertura.to_string(float_format=lambda x: f"{x:.1%}"))
''')

md("""
**Qué encontramos.** Una fila del archivo, Chaco / General Donovan / Estatal /
Rural, viene con las 1.031 columnas vacías y cero estudiantes. No es no
respuesta: no hay nada atrás. La descartamos.

Sobre la cobertura, hay dos grupos claros. Ocho bloques dan 100% en todas las
filas: sexo, edad, sobreedad, repitencia, nivel socioeconómico, libros,
educación de la madre y los dos desempeños. Los demás bajan a una mediana de
98-99%, con mínimos cerca del 52% en algunos departamentos, y **clima escolar**
es el caso serio, con 87,3% de mediana y 96 filas sin ningún dato.

Llama la atención que los bloques completos sean justamente los **derivados**
(sobreedad, repitencia, nivel socioeconómico) más los que alimentan el índice
socioeconómico. Nuestra lectura, que no pudimos verificar, es que el Ministerio
los imputa cuando faltan. Los que quedaron crudos muestran la no respuesta real.

Dos cosas que **no** hicimos, a propósito:

- No pusimos un flag binario de "fila con poca cobertura". Probamos umbrales del
  90% al 50% y la cantidad de filas marcadas baja de forma continua (68%, 51%,
  39%, 31%, 25%, 14%, 8%) sin ningún escalón, o sea que no existe una cola
  separable de filas malas. Cualquier corte sería arbitrario y le impondría esa
  decisión, invisible, a quien use la tabla. Quedan las columnas `cob__*`
  continuas y cada análisis elige y justifica su corte.
- No incluimos la educación de la persona referente. Es una variable
  **condicional**: solo aplica cuando el referente no es la madre ni el padre, y
  cubre el 16,6% de los estudiantes. Sus proporciones no describen a la
  población sino a un subconjunto muy particular. Se puede retomar en el TP2
  leyéndola como indicador de "no convive con los padres", que es su sentido
  útil.
""")

# ================================================================== 6. EPH
md("""
<a name="eph"></a>
## 5. EPH: unir hogares con personas

La EPH publica dos tablas por trimestre: una de hogares y otra de personas. Hay
que unirlas.

La consigna dice unirlas "mediante el identificador común (CODUSU)". `CODUSU`
identifica la **vivienda**, y hay viviendas donde convive más de un hogar. Si se
une solo por ahí, esas viviendas multiplican filas y quedan personas asignadas a
hogares que no son el suyo.

La clave correcta es **`CODUSU` + `NRO_HOGAR`**, y lo comprobamos antes de unir.
""")

code('''
with zipfile.ZipFile(rutas["eph"]) as z:
    hogares = pd.read_excel(z.open("usu_hogar_T325.xlsx"))
    personas = pd.read_excel(z.open("usu_individual_T325.xlsx"))

print(f"hogares : {len(hogares):>7,} filas x {hogares.shape[1]:>3} columnas")
print(f"personas: {len(personas):>7,} filas x {personas.shape[1]:>3} columnas")
print(f"periodo : año {hogares['ANO4'].unique()} trimestre {hogares['TRIMESTRE'].unique()}")
print()

viviendas_multi_hogar = hogares.groupby("CODUSU")["NRO_HOGAR"].nunique().gt(1).sum()
print(f"CODUSU unicos: {hogares['CODUSU'].nunique():,} sobre {len(hogares):,} filas")
print(f"Viviendas con mas de un hogar: {viviendas_multi_hogar}")
print("-> unir solo por CODUSU duplicaria esas filas")
''')

code('''
# validate="many_to_one" es una guarda: si el join multiplicara filas, pandas
# tira error en vez de devolver una tabla inflada.
eph = personas.merge(hogares, on=["CODUSU", "NRO_HOGAR"], how="left",
                     suffixes=("", "_hog"), validate="many_to_one")

print(f"filas antes del join : {len(personas):,}")
print(f"filas despues        : {len(eph):,}")
print(f"personas sin hogar   : {eph['IV1'].isna().sum()}")
print()

adolescentes = eph[eph["CH06"].between(12, 18)]
print(f"Personas de 12 a 18 años: {len(adolescentes):,} de {len(eph):,}")
print(f"  representan {adolescentes['PONDERA'].sum():,.0f} adolescentes")
''')

md("""
**Qué encontramos.** Hay 77 viviendas con más de un hogar, así que la
advertencia no era teórica. Con la clave completa el join es perfecto: 44.946
filas antes y después, cero personas sin hogar y cero hogares sin personas.

La población que nos interesa son **5.025 adolescentes encuestados**, que
ponderados representan 3,5 millones de personas de 12 a 18 años.

Un detalle que casi nos hace escribir un error en el informe: al comparar las
columnas que aparecen en las dos tablas, tres pares de variables de decil
"coincidían" solo en el 48% de las filas, y estuvimos a punto de reportar que la
fuente era inconsistente. No lo es. En pandas `NaN == NaN` da `False`, y esas
columnas están vacías en las dos tablas a la vez. Contando los vacíos como
coincidencia, los tres pares dan 100%.
""")

# =============================================================== 7. PUENTE
md("""
<a name="puente"></a>
## 6. El puente geográfico

Acá está el problema central de la integración. **Las dos fuentes no comparten
ninguna clave.**

Aprender llega hasta el **departamento**: 530 departamentos en 24
jurisdicciones. La EPH llega hasta el **aglomerado**, que es una ciudad o
conjunto de ciudades relevado por la encuesta: 32 en todo el país. Un aglomerado
no es un departamento ni lo contiene: son recortes distintos del territorio.

El único nivel donde las dos se encuentran es la **provincia**.

La tabla de correspondencia de abajo se armó con los nombres oficiales de los
aglomerados, que salen del documento de diseño de registro del INDEC. Se deja
explícita, y no escondida en el código, por dos razones: es uno de los productos
que pide la consigna, y si alguien quiere cambiar un criterio edita una fila en
vez de leer el pipeline entero.
""")

code('''
# Nombres oficiales: INDEC, "EPH. Diseño de Registro y Estructura para las
# bases de microdatos", 4to trimestre 2014, Anexo de codigos de aglomerado.
# https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph/EPH_diseno_reg_t414.pdf
#
# La provincia se deduce de la localidad que da nombre al aglomerado. Los dos
# aglomerados que abarcan localidades de DOS provincias quedan marcados.
PUENTE = pd.DataFrame([
    (2,  "Gran La Plata",                    "Buenos Aires",       False),
    (3,  "Bahía Blanca - Cerri",             "Buenos Aires",       False),
    (4,  "Gran Rosario",                     "Santa Fe",           False),
    (5,  "Gran Santa Fé",                    "Santa Fe",           False),
    (6,  "Gran Paraná",                      "Entre Rios",         False),
    (7,  "Posadas",                          "Misiones",           False),
    (8,  "Gran Resistencia",                 "Chaco",              False),
    (9,  "Cdro. Rivadavia - Rada Tilly",     "Chubut",             False),
    (10, "Gran Mendoza",                     "Mendoza",            False),
    (12, "Corrientes",                       "Corrientes",         False),
    (13, "Gran Córdoba",                     "Cordoba",            False),
    (14, "Concordia",                        "Entre Rios",         False),
    (15, "Formosa",                          "Formosa",            False),
    (17, "Neuquén - Plottier",               "Neuquen",            False),
    (18, "S. del Estero - La Banda",         "Santiago del Estero", False),
    (19, "Jujuy - Palpalá",                  "Jujuy",              False),
    (20, "Río Gallegos",                     "Santa Cruz",         False),
    (22, "Gran Catamarca",                   "Catamarca",          False),
    (23, "Salta",                            "Salta",              False),
    (25, "La Rioja",                         "La Rioja",           False),
    (26, "San Luis - El Chorrillo",          "San Luis",           False),
    (27, "Gran San Juan",                    "San Juan",           False),
    (29, "Gran Tucumán - T. Viejo",          "Tucuman",            False),
    (30, "Santa Rosa - Toay",                "La Pampa",           False),
    (31, "Ushuaia - Río Grande",             "Tierra del Fuego, Antartida e Islas del Atlantico Sur", False),
    (32, "Ciudad de Buenos Aires",           "Ciudad Autonoma de Buenos Aires", False),
    (33, "Partidos del GBA",                 "Buenos Aires",       False),
    (34, "Mar del Plata - Batán",            "Buenos Aires",       False),
    (36, "Río Cuarto",                       "Cordoba",            False),
    (38, "San Nicolás - Villa Constitución", "Buenos Aires",       True),
    (91, "Rawson - Trelew",                  "Chubut",             False),
    (93, "Viedma - Carmen de Patagones",     "Rio Negro",          True),
], columns=["aglomerado", "nombre_indec", "provincia", "cruza_provincias"])

faltantes = set(eph["AGLOMERADO"]) - set(PUENTE["aglomerado"])
assert not faltantes, f"Aglomerados sin provincia: {faltantes}"

eph = eph.merge(PUENTE[["aglomerado", "provincia"]], left_on="AGLOMERADO",
                right_on="aglomerado", how="left", validate="many_to_one")

resumen = eph.groupby("provincia").agg(
    aglomerados=("AGLOMERADO", "nunique"),
    personas=("CODUSU", "size"),
    ponderadas=("PONDERA", "sum"))
resumen["casos_12_18"] = (eph[eph["CH06"].between(12, 18)]
                          .groupby("provincia").size())
print(resumen.sort_values("casos_12_18").to_string(
    float_format=lambda x: f"{x:,.0f}"))
''')

md("""
**Qué encontramos.** Las 24 jurisdicciones de Aprender tienen al menos un
aglomerado en la EPH, así que ninguna se queda sin contexto. Pero la muestra
está muy desbalanceada: **Buenos Aires concentra el 51% de la muestra ponderada
del país**, y en el otro extremo hay tres provincias con menos de 100
adolescentes encuestados (La Pampa 91, Río Negro 76, Santa Cruz 75).

Los dos aglomerados que abarcan localidades de dos provincias pesan juntos el
0,96% de la muestra ponderada. Los asignamos a la provincia de su localidad
principal. En el caso de Viedma esa decisión importa más de lo que su tamaño
sugiere, porque es el **único** aglomerado de Río Negro: excluirlo haría
desaparecer la provincia entera del dataset.
""")

# ========================================================== 8. INDICADORES
md("""
<a name="indicadores"></a>
## 7. Indicadores socioeconómicos de contexto

Con la EPH construimos siete indicadores por provincia. Todos los códigos de
variable están tomados del documento de diseño de registro del INDEC, no de
suposiciones: `CH10` es asistencia escolar y no edad, `ESTADO = 4` significa
"menor de 10 años" y no un tipo de desocupado, `II1` son las habitaciones de uso
exclusivo del hogar mientras que `II2` son solo las que se usan para dormir.

### Dos ponderadores, no uno

`PONDERA` expande personas. Para los **ingresos** hay un ponderador aparte,
`PONDIH`, porque la no respuesta de ingresos es alta y se corrige distinto.

Esto no es un detalle. En la EPH del 3er trimestre de 2025, el **27,5% de las
personas figura con ingreso per cápita familiar en 0**, y de esas, el 98,8%
tiene `PONDIH = 0`: el INDEC ya las está marcando como "no usar para ingresos".
Si se calcula la mediana con `PONDERA`, esas personas entran con peso completo
y un cero que no es un ingreso sino una ausencia de respuesta.
""")

code('''
def mediana_ponderada(valores, pesos):
    orden = np.argsort(valores)
    v, p = np.asarray(valores)[orden], np.asarray(pesos)[orden]
    acumulado = np.cumsum(p)
    return v[np.searchsorted(acumulado, acumulado[-1] / 2)] if acumulado[-1] else np.nan


def proporcion_ponderada(mascara, pesos):
    total = pesos.sum()
    return pesos[mascara].sum() / total if total else np.nan


def indicadores_de(grupo):
    peso = grupo["PONDERA"]
    ado = grupo[grupo["CH06"].between(12, 18)]
    pea = grupo[grupo["ESTADO"].isin([1, 2])]          # ocupados + desocupados
    adultos = grupo[grupo["CH06"] >= 25]
    con_ingreso = grupo[grupo["PONDIH"] > 0]
    personas_por_cuarto = grupo["IX_TOT"] / grupo["II1"].replace(0, np.nan)

    return pd.Series({
        "eph_no_asiste_12_18": proporcion_ponderada(
            ado["CH10"].isin([2, 3]), ado["PONDERA"]),
        "eph_ipcf_mediano": mediana_ponderada(
            con_ingreso["IPCF"].values, con_ingreso["PONDIH"].values),
        "eph_sin_dato_ingreso": proporcion_ponderada(grupo["PONDIH"] == 0, peso),
        "eph_hacinamiento_critico": proporcion_ponderada(
            personas_por_cuarto > 3, peso),
        "eph_agua_fuera_vivienda": proporcion_ponderada(
            grupo["IV6"].isin([2, 3]), peso),
        "eph_desocupacion": proporcion_ponderada(
            pea["ESTADO"] == 2, pea["PONDERA"]),
        "eph_adultos_sin_secundaria": proporcion_ponderada(
            adultos["NIVEL_ED"].isin([1, 2, 3, 7]), adultos["PONDERA"]),
        "eph_adolescentes_ocupados": proporcion_ponderada(
            ado["ESTADO"] == 1, ado["PONDERA"]),
        # Los denominadores van en la tabla: nadie deberia poder usar un
        # indicador sin ver sobre cuantos casos se calculo.
        "eph_casos_personas": len(grupo),
        "eph_casos_hogares": len(grupo.drop_duplicates(["CODUSU", "NRO_HOGAR"])),
        "eph_casos_12_18": len(ado),
        "eph_aglomerados": grupo["AGLOMERADO"].nunique(),
    })


indicadores = (eph.groupby("provincia")
               .apply(indicadores_de, include_groups=False).reset_index())

print(indicadores.set_index("provincia")[
    ["eph_no_asiste_12_18", "eph_ipcf_mediano", "eph_sin_dato_ingreso",
     "eph_adultos_sin_secundaria", "eph_casos_12_18"]]
      .sort_values("eph_no_asiste_12_18", ascending=False)
      .to_string(float_format=lambda x: f"{x:,.3f}"))
''')

md("""
**Qué encontramos.** La no asistencia entre los 12 y los 18 años va del 2,1% en
Santa Cruz al 10,5% en Formosa.

La columna `eph_sin_dato_ingreso` está ahí para que la mediana de ingreso no se
lea sola: en Chaco y Misiones **más de la mitad de la muestra no declara
ingresos**, así que su mediana se calcula sobre poco más del 40% de los casos.
Un número sin su denominador al lado invita a confiar de más.
""")

# ========================================================= 9. ARMONIZACION
md("""
<a name="armonizacion"></a>
## 8. Armonizar las categorías entre fuentes

La consigna pide que las variables que significan lo mismo en las dos fuentes
queden expresadas igual. El caso más claro es el nivel educativo de los adultos:
Aprender lo trae en siete categorías con nombres, la EPH en siete códigos
numéricos, y los cortes no están en los mismos lugares.

Los llevamos a una escala común de cuatro niveles de **máximo nivel completado**.
Esto no es solo cumplir un requisito: habilita comparar las dos fuentes sobre un
mismo concepto, que es la única forma que tenemos de comprobar empíricamente que
el puente geográfico no es un invento.
""")

code('''
NIVELES = ["sin_primaria", "primaria", "secundaria", "superior"]

APRENDER_A_COMUN = {
    "no_fue_a_la_escuela": "sin_primaria",
    "primaria_incompleto": "sin_primaria",
    "primaria_completo": "primaria",
    "secundaria_incompleto": "primaria",
    "secundaria_completo": "secundaria",
    "terciariouniversitarioposgrado_incompleto": "secundaria",
    "terciariouniversitarioposgrado_completo": "superior",
}

# Codigos de NIVEL_ED segun el diseño de registro del INDEC.
EPH_A_COMUN = {7: "sin_primaria",  # sin instruccion
               1: "sin_primaria",  # primaria incompleta
               2: "primaria",      # primaria completa
               3: "primaria",      # secundaria incompleta
               4: "secundaria",    # secundaria completa
               5: "secundaria",    # superior incompleta
               6: "superior"}      # superior completa


def armonizar_aprender(df, bloque, salida):
    esperadas = {f"{bloque}__{c}" for c in APRENDER_A_COMUN}
    presentes = {c for c in df.columns if c.startswith(f"{bloque}__")}
    assert esperadas == presentes, f"{bloque}: categorias sin mapear"

    return pd.DataFrame({
        f"{salida}__{nivel}": df[[f"{bloque}__{cat}"
                                  for cat, n in APRENDER_A_COMUN.items()
                                  if n == nivel]].sum(axis=1)
        for nivel in NIVELES})


for bloque, salida in [("educ_madre", "educ_madre_arm"),
                       ("educ_padre", "educ_padre_arm")]:
    aprender = pd.concat([aprender, armonizar_aprender(aprender, bloque, salida)],
                         axis=1)

adultos = eph[(eph["CH06"] >= 25) & eph["NIVEL_ED"].isin(EPH_A_COMUN)].copy()
adultos["nivel"] = adultos["NIVEL_ED"].map(EPH_A_COMUN)
pesos = adultos.groupby(["provincia", "nivel"])["PONDERA"].sum().unstack(fill_value=0)
educ_eph = (pesos.div(pesos.sum(axis=1), axis=0)
            .reindex(columns=NIVELES, fill_value=0.0))
educ_eph.columns = [f"eph_educ_adultos__{n}" for n in NIVELES]
indicadores = indicadores.merge(educ_eph.reset_index(), on="provincia",
                                validate="one_to_one")

print("Escala comun:", " < ".join(NIVELES))
print(f"Adultos 25+ considerados: {len(adultos):,}")
''')

# ============================================================== 10. MAESTRO
md("""
<a name="maestro"></a>
## 9. El dataset maestro

Ahora se unen las dos partes. La unión es de **muchos a uno**: cada fila de
Aprender (un departamento) recibe los indicadores de **su provincia**, y todas
las filas de una misma provincia comparten los mismos valores.

Eso es exactamente lo que pide la consigna, y también es la principal limitación
del dataset: el contexto socioeconómico que le asignamos a un departamento no es
el de ese departamento, es el de su provincia.

Los nombres de provincia no se pueden comparar directamente porque una fuente
escribe "Córdoba" y la otra "Cordoba", así que se normalizan antes de unir.
""")

code('''
def clave_provincia(texto):
    """Normaliza el nombre para poder unir: sin tildes, sin comas, minusculas."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", str(texto))
                         if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.lower().replace(",", " ").split())


aprender["_clave"] = aprender["jurisdiccion"].map(clave_provincia)
indicadores["_clave"] = indicadores["provincia"].map(clave_provincia)

sin_par = set(aprender["_clave"]) - set(indicadores["_clave"])
assert not sin_par, f"Jurisdicciones sin indicadores: {sin_par}"

maestro = (aprender.merge(indicadores.drop(columns=["provincia"]), on="_clave",
                          how="left", validate="many_to_one")
           .drop(columns=["_clave"]))

columnas_eph = [c for c in maestro.columns if c.startswith("eph_")]

# Verificacion: dentro de una jurisdiccion, todos los indicadores de la EPH
# tienen que valer lo mismo en todas sus filas. Si alguno varia, el join
# asigno el contexto de una provincia a otra.
variacion = maestro.groupby("jurisdiccion")[columnas_eph].nunique().max().max()
assert variacion == 1, "El contexto de la EPH varia dentro de una jurisdiccion"

print(f"filas: {len(maestro):,}  (Aprender tenia {len(aprender):,})")
print(f"columnas: {maestro.shape[1]:,}")
print(f"estudiantes representados: {maestro['estudiantes'].sum():,.0f}")
print(f"filas sin contexto socioeconomico: {maestro[columnas_eph].isna().all(axis=1).sum()}")
print(f"valores distintos de un indicador dentro de una jurisdiccion: {variacion}")

maestro.to_csv("dataset_maestro_inicial.csv", index=False, encoding="utf-8")
print()
print("Guardado: dataset_maestro_inicial.csv")
''')

code('''
# ¿Cuantos estudiantes de Aprender dependen de cuantos encuestados de la EPH?
solidez = maestro.groupby("jurisdiccion").agg(
    estudiantes=("estudiantes", "sum"),
    departamentos=("departamento", "nunique"),
    encuestados_12_18=("eph_casos_12_18", "first"))
solidez["estudiantes_por_encuestado"] = (
    solidez["estudiantes"] / solidez["encuestados_12_18"])

print(solidez.sort_values("estudiantes_por_encuestado", ascending=False)
      .head(6).to_string(float_format=lambda x: f"{x:,.0f}"))
print()
print(f"Mediana nacional: {solidez['estudiantes_por_encuestado'].median():,.0f} "
      f"estudiantes por adolescente encuestado")
''')

md("""
**Qué encontramos.** El dataset queda en 1.174 filas por 131 columnas, con los
540.040 estudiantes representados intactos y ninguna fila sin contexto.

La última tabla es la más incómoda del entregable y por eso está: el contexto
socioeconómico de **306 estudiantes de CABA** sale de **110 encuestas**, y la
mediana nacional es de 79 estudiantes por adolescente encuestado. No invalida
nada, pero cambia cómo hay que leer todo lo demás.
""")

# =========================================================== 11. DICCIONARIO
md("""
<a name="diccionario"></a>
## 10. Diccionario de variables

El diccionario se genera leyendo el dataset, no se escribe a mano. Así no puede
quedar desactualizado: si el pipeline agrega o saca una columna, el diccionario
la refleja sola.

Cada variable lleva su **denominador**, que es sobre qué población se calculó.
Es el campo que más nos hubiera servido tener desde el principio.
""")

code('''
DESCRIPCIONES = {
    "sexo": "Sexo que figura en el DNI del estudiante",
    "edad": "Edad cumplida al 30 de junio de 2024, en tramos",
    "sobreedad": "Años de atraso respecto de la edad teorica del año que cursa",
    "repitencia": "Cantidad de veces que repitio de año",
    "migracion": "Configuracion familiar migrante o no migrante",
    "clima_escolar": "Indice de clima escolar del Ministerio (bajo/medio/alto)",
    "nse": "Quintil de nivel socioeconomico calculado por el Ministerio",
    "educ_madre": "Maximo nivel educativo de la madre",
    "educ_padre": "Maximo nivel educativo del padre",
    "educ_madre_arm": "Nivel educativo de la madre en la escala comun de 4 niveles",
    "educ_padre_arm": "Nivel educativo del padre en la escala comun de 4 niveles",
    "tamano_hogar": "Cantidad de personas con las que vive el estudiante",
    "libros_hogar": "Cantidad de libros en papel en el hogar, en tramos",
    "horas_estudio": "Horas semanales de estudio fuera del horario escolar",
    "inasistencias": "Cantidad de faltas en el año, en tramos",
    "asistio_jardin": "Si asistio al jardin de infantes y desde que sala",
    "desemp_lengua": "Nivel de desempeño en Lengua",
    "desemp_matematica": "Nivel de desempeño en Matematica",
}

filas_diccionario = []
for columna in maestro.columns:
    if columna in CLAVES:
        fila = ("Aprender 2024", "clave territorial", "texto", "")
    elif columna == "estudiantes":
        fila = ("Aprender 2024", "Estudiantes que representa la fila, "
                "expandidos por el ponderador", "personas", "")
    elif columna == "flag_discrepancia_bases":
        fila = ("derivada", "Marca filas donde Lengua y Matematica difieren "
                "mas de 10% en su total", "booleano", "")
    elif columna.startswith("cob__"):
        bloque = columna[5:]
        fila = ("derivada", f"Cobertura del bloque '{bloque}'", "proporcion",
                "estudiantes de la fila")
    elif columna.startswith("eph_educ_adultos__"):
        fila = ("EPH 3T 2025", "Adultos de 25+ por nivel educativo, escala "
                "comun", "proporcion", "personas de 25+ de la provincia")
    elif columna.startswith("eph_"):
        fila = ("EPH 3T 2025", "Indicador socioeconomico provincial",
                "proporcion o pesos", "poblacion de la provincia")
    else:
        bloque, categoria = columna.split("__", 1)
        fila = ("Aprender 2024",
                f"{DESCRIPCIONES[bloque]}. Categoria: {categoria.replace('_', ' ')}",
                "proporcion", f"estudiantes con respuesta en el bloque "
                f"'{bloque}' (ver cob__{bloque})")
    filas_diccionario.append((columna, *fila))

diccionario = pd.DataFrame(filas_diccionario, columns=[
    "variable", "fuente", "descripcion", "unidad", "denominador"])
assert len(diccionario) == maestro.shape[1]
diccionario.to_csv("diccionario_variables.csv", index=False, encoding="utf-8")

print(f"{len(diccionario)} variables documentadas de {maestro.shape[1]} columnas")
print()
print(diccionario.groupby("fuente").size().rename("variables").to_string())
print()
print(diccionario.head(8).to_string(index=False, max_colwidth=45))
''')

# ============================================================ 12. GRAFICOS
md("""
<a name="graficos"></a>
## 11. Qué muestran los datos

Tres preguntas, tres gráficos.
""")

code('''
AZUL, NARANJA = "#2a78d6", "#eb6834"
TINTA_SUAVE, GRIS = "#52514e", "#e3e3e0"

plt.rcParams.update({
    "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
    "axes.edgecolor": GRIS, "axes.labelcolor": TINTA_SUAVE,
    "xtick.color": TINTA_SUAVE, "ytick.color": TINTA_SUAVE,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRIS, "grid.linewidth": 0.8, "font.size": 10,
})


def promedio_ponderado(grupo, columnas):
    """Promedio de proporciones, pesado por los estudiantes de cada fila."""
    peso = grupo["estudiantes"]
    return (grupo[columnas].sum(axis=1) * peso).sum() / peso.sum()


por_provincia = maestro.groupby("jurisdiccion").apply(lambda g: pd.Series({
    "ipcf": g["eph_ipcf_mediano"].iloc[0] / 1000,
    "no_asiste": g["eph_no_asiste_12_18"].iloc[0],
    "bajo_matematica": promedio_ponderado(
        g, ["desemp_matematica__por_debajo_del_nivel_basico"]),
    "estudiantes": g["estudiantes"].sum(),
}), include_groups=False)
''')

code('''
# Grafico 1: probamos los cuatro indicadores de la EPH contra el desempeño.
# El ingreso da r = -0,82 y el proxy de abandono da r = +0,16. Van los dos:
# mostrar solo el primero seria quedarse con el resultado lindo.
fig, ejes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)

for ax, (variable, etiqueta, color, formato) in zip(ejes, [
        ("ipcf", "Ingreso per cápita familiar mediano (miles de $, EPH)",
         AZUL, lambda x, _: f"${x:.0f}k"),
        ("no_asiste", "No asiste a la escuela, 12 a 18 años (EPH)",
         NARANJA, lambda x, _: f"{x:.0%}")]):
    r = por_provincia[variable].corr(por_provincia["bajo_matematica"])
    ax.grid(zorder=0)
    ax.set_axisbelow(True)
    ax.scatter(por_provincia[variable], por_provincia["bajo_matematica"],
               s=por_provincia["estudiantes"] / 150, color=color, alpha=0.75,
               edgecolor="#fcfcfb", linewidth=2, zorder=3)

    # Etiquetamos solo los extremos y las dos provincias mas grandes: poner
    # las 24 taparia el grafico.
    destacar = (por_provincia.nlargest(2, "bajo_matematica").index.tolist()
                + por_provincia.nsmallest(2, "bajo_matematica").index.tolist()
                + por_provincia.nlargest(2, "estudiantes").index.tolist())
    for nombre in dict.fromkeys(destacar):
        fila = por_provincia.loc[nombre]
        ax.annotate(nombre.split(",")[0],
                    (fila[variable], fila["bajo_matematica"]),
                    xytext=(8, 5), textcoords="offset points",
                    fontsize=9, color=TINTA_SUAVE)

    ax.set_xlabel(etiqueta)
    ax.xaxis.set_major_formatter(formato)
    ax.set_title(f"r = {r:+.2f}", loc="left", pad=8)

ejes[0].set_ylabel("Desempeño por debajo del nivel básico\\nen Matemática (Aprender 2024)")
ejes[0].yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
fig.suptitle("Qué del contexto socioeconómico explica el rendimiento\\n"
             "cada punto es una provincia; el tamaño es la cantidad de estudiantes",
             x=0.012, ha="left", y=0.99, fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.93))
plt.show()
''')

md("""
El ingreso mediano de la provincia, medido por el INDEC en una encuesta de
hogares, se relaciona con el porcentaje de estudiantes por debajo del nivel
básico en Matemática, medido por el Ministerio en una evaluación censal, con una
correlación de **-0,82**. Son dos operativos que no se conocen entre sí.

Lo probamos de cinco maneras antes de creerlo: sin CABA da -0,73, sin CABA ni
Buenos Aires da -0,73, excluyendo las provincias donde más del 20% no declara
ingresos da -0,71, y por rangos (Spearman, que es inmune a los valores
extremos) da -0,85. Además, el porcentaje de no respuesta de ingresos
correlaciona apenas -0,13 con el desempeño, así que el resultado no es un
artefacto de dónde falta el dato.

El panel derecho es el que no funciona, y también importa: el proxy de abandono
casi no se relaciona con el rendimiento a nivel provincia.
""")

code('''
# Grafico 2: las brechas dentro del sistema educativo.
columnas_sobreedad = [c for c in maestro.columns
                      if c.startswith("sobreedad__") and "sobreedad_" in c[11:]]
columnas_repitencia = ["repitencia__repitio_1_vez",
                       "repitencia__repitio_2_veces_o_mas"]

grupos = maestro.groupby(["sector", "ambito"]).apply(lambda g: pd.Series({
    "Sobreedad (1 año o más)": promedio_ponderado(g, columnas_sobreedad),
    "Repitió alguna vez": promedio_ponderado(g, columnas_repitencia),
}), include_groups=False)
grupos.index = [f"{s}\\n{a.lower()}" for s, a in grupos.index]
grupos = grupos.sort_values("Sobreedad (1 año o más)", ascending=False)

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.grid(axis="y", zorder=0)
ax.set_axisbelow(True)
x, ancho = np.arange(len(grupos)), 0.36

for desplazamiento, (etiqueta, color) in zip(
        (-ancho / 2 - 0.01, ancho / 2 + 0.01),
        [("Sobreedad (1 año o más)", AZUL), ("Repitió alguna vez", NARANJA)]):
    barras = ax.bar(x + desplazamiento, grupos[etiqueta], ancho,
                    label=etiqueta, color=color, zorder=3)
    ax.bar_label(barras, labels=[f"{v:.0%}" for v in grupos[etiqueta]],
                 padding=3, fontsize=9, color=TINTA_SUAVE)

ax.set_xticks(x, grupos.index)
ax.set_ylabel("% de estudiantes")
ax.yaxis.set_major_formatter(lambda y, _: f"{y:.0%}")
ax.set_ylim(0, grupos.max().max() * 1.22)
ax.legend(frameon=False, loc="upper right", ncols=2)
ax.set_title("Las cuatro realidades del secundario argentino\\n"
             "atraso escolar según gestión y ámbito, Aprender 2024",
             loc="left", pad=14)
fig.tight_layout()
plt.show()
''')

md("""
La brecha que separa al sistema no es urbano contra rural: es **estatal contra
privado**. Estatal urbano y estatal rural son casi idénticos entre sí (23% y 22%
de sobreedad), y privado urbano tiene 7%. Tres veces menos.
""")

code('''
# Grafico 3: sobre cuantos casos se apoya el contexto de cada provincia.
solidez_ordenada = solidez.sort_values("estudiantes_por_encuestado")
mediana = solidez_ordenada["estudiantes_por_encuestado"].median()

fig, ax = plt.subplots(figsize=(9, 8))
ax.grid(axis="x", zorder=0)
ax.set_axisbelow(True)
barras = ax.barh([n.split(",")[0] for n in solidez_ordenada.index],
                 solidez_ordenada["estudiantes_por_encuestado"],
                 color=AZUL, height=0.68, zorder=3)
ax.bar_label(barras, labels=[f"{v:,.0f}" for v in
                             solidez_ordenada["estudiantes_por_encuestado"]],
             padding=6, fontsize=9, color=TINTA_SUAVE, zorder=5)
ax.axvline(mediana, color=NARANJA, linewidth=2, zorder=2)
ax.annotate(f"mediana: {mediana:,.0f}", (mediana, len(solidez_ordenada) - 0.2),
            xytext=(8, 0), textcoords="offset points", color=NARANJA,
            fontsize=9, va="center")
ax.set_xlabel("Estudiantes de Aprender por cada adolescente encuestado en la EPH")
ax.set_xlim(0, solidez_ordenada["estudiantes_por_encuestado"].max() * 1.16)
ax.set_title("Sobre cuántos casos se apoya el contexto de cada provincia\\n"
             "cuanto más larga la barra, más fino el hilo del que cuelga el dato",
             loc="left", pad=14)
fig.tight_layout()
plt.show()
''')

# ========================================================= 13. DIFICULTADES
md("""
<a name="dificultades"></a>
## 12. Dificultades encontradas

**El microdato a nivel estudiante no existe.** La consigna pide un dataset a
nivel estudiante y la matriz de integración dice que una fila es un estudiante
evaluado, pero las bases publicadas son agregadas y no hay otra versión: los
cinco años del portal traen lo mismo. La unidad de análisis del proyecto tuvo
que redefinirse a departamento por sector por ámbito.

**El desfasaje de años.** La consigna pide la EPH del 3er trimestre de 2024
argumentando que es la medición más cercana a Aprender, que se tomó en octubre
de 2024. En el repositorio está la EPH de 2025. Trabajamos con la que hay, pero
eso debilita justamente el argumento que la consigna usa para elegir el
trimestre, y conviene decidirlo con la mentora.

**Tres bases con tres ponderadores.** Costó entender por qué la misma celda daba
números distintos en tres archivos. Nuestra primera hipótesis (poblaciones
anidadas) era incorrecta, y la respuesta estaba en el documento metodológico del
Ministerio.

**Los vacíos no siempre significan lo mismo.** Fue el problema más recurrente.
En Aprender un vacío es un cero, y lo verificamos. Pero las columnas de "Blanco"
y "No disponible" están vacías en el 100% de sus celdas, así que un indicador de
no respuesta construido sobre ellas da 0% siempre y parece decir que la calidad
del dato es perfecta. Lo reemplazamos por la cobertura, que sí varía. Y en la
EPH, un ingreso en 0 casi siempre significa "no contestó" y no "no tiene": usar
el ponderador equivocado hacía que Buenos Aires apareciera como la provincia de
menor ingreso del país.

**Dos fuentes que no comparten ninguna clave.** Departamentos contra
aglomerados, sin correspondencia posible. La integración solo existe a nivel
provincia, y eso significa que a un departamento le asignamos el contexto de su
provincia entera.
""")

# ========================================================= 14. LIMITACIONES
md("""
<a name="limitaciones"></a>
## 13. Limitaciones y qué sigue

### Lo que este dataset no puede hacer

**Aprender no ve el abandono.** A la evaluación solo va quien está
escolarizado, así que el fenómeno que el proyecto quiere predecir es invisible
en su fuente principal. Esto no es un problema de calidad de datos: es
estructural, y define la forma que puede tener el proyecto. Los predictores
están en Aprender y el resultado a predecir tiene que venir de otro lado.

**El contexto es provincial.** Todos los departamentos de una provincia
comparten los mismos valores socioeconómicos. En provincias grandes eso mete
mucho ruido, y hay tres (La Pampa, Santa Cruz y Río Negro) donde el contexto
sale de menos de 100 encuestados.

### Dos hallazgos para el TP2

**El abandono ya existe como estadística oficial.** El Ministerio publica un
dataset llamado `Indicadores Educativos` con las tasas de Promoción Efectiva,
Repitencia, **Abandono Interanual**, Sobreedad y Escolarización, desagregadas
por nivel de enseñanza y jurisdicción, cubriendo de 2012 a 2025. Es exactamente
la variable objetivo que el proyecto necesita, al mismo nivel geográfico que ya
estamos usando, y calculada por la fuente oficial en vez de derivada por
nosotros. También existe `Base de Datos por Escuela`, con abandono a nivel
establecimiento.

**Falta identificar dos bloques del cuestionario.** El bloque de horas
trabajadas (`ap21` y `ap22`) sería probablemente el mejor predictor individual
de abandono, pero tiene diez subpreguntas con las mismas opciones de respuesta y
no se puede saber cuál es "trabajar fuera del hogar" sin el diccionario 2024, que
existe en el portal del Ministerio pero no está en el repositorio. Lo mismo pasa
con `ap11`, que tiene las mismas categorías que el tamaño del hogar y podría ser
hermanos o habitaciones.

### Tres variables a validar

`repitencia`, `clima_escolar`, `migracion` y `asistio_jardin` las incorporamos
por criterio propio, no porque la consigna las pidiera. La justificación está en
el diccionario y es honesta: nos parecieron relevantes. Cuando el TP2 tenga la
variable objetivo se puede medir si efectivamente predicen algo, y si no, se
sacan.
""")

DESTINO.parent.mkdir(exist_ok=True)
notebook = {
    "cells": celdas,
    "metadata": {
        "colab": {"provenance": [], "toc_visible": True},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}
DESTINO.write_text(json.dumps(notebook, ensure_ascii=False, indent=1),
                   encoding="utf-8")

markdown = sum(1 for c in celdas if c["cell_type"] == "markdown")
print(f"Notebook generado: {DESTINO.relative_to(BASE_DIR)}")
print(f"  {len(celdas)} celdas ({markdown} de texto, {len(celdas) - markdown} de codigo)")
print(f"  {DESTINO.stat().st_size / 1024:.0f} KB")
