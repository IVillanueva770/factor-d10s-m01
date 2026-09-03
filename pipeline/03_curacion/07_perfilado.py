"""Etapa 07: perfilar el dataset maestro. MIDE, no decide.

Que hace
--------
Recorre las 131 columnas del dataset maestro y reporta que hay: tipos, valores
faltantes, rangos, duplicados, categorias, variabilidad y valores imposibles.
Produce una tabla con una fila por columna y un informe legible con los
problemas ordenados por cuantas filas afectan.

Que NO hace, a proposito
------------------------
No corrige nada. La curacion es la etapa 08 y sus decisiones se toman mirando
este informe, no antes. Separarlas es lo que permite justificar cada decision:
el informe es la evidencia y la etapa 08 es la respuesta.

Lo que este instrumento NO puede ver
------------------------------------
Cada chequeo imprime su denominador y, donde corresponde, que se le escapa.
Los limites conocidos:

  · No sabe si un valor es correcto, solo si es POSIBLE. Una proporcion de 0,97
    es valida aunque sea un error de carga.
  · No compara contra la fuente original. Si el pipeline calculo mal una
    proporcion pero la dejo dentro de [0,1], este perfil la da por buena. Eso
    lo cubren los invariantes de tests/, que contrastan contra los crudos.
  · La deteccion de extremos usa el rango intercuartil, que asume una sola
    poblacion. En un dataset con 1.174 filas que mezclan departamentos de
    500.000 habitantes con departamentos rurales de 800, un valor "extremo"
    puede ser simplemente un departamento chico.
  · No mide sesgo de cobertura. Que una columna no tenga faltantes no dice que
    represente bien a los estudiantes: para eso estan las columnas `cob__`.

Categorias estructurales del dataset (importan para no dar falsos positivos)
---------------------------------------------------------------------------
Un chequeo generico de "poca variabilidad" marcaria las columnas `eph_` como
sospechosas, y seria un error: son indicadores PROVINCIALES repetidos en cada
departamento de la provincia, asi que por construccion tienen a lo sumo 24
valores distintos sobre 1.174 filas. Eso no es un problema de calidad, es el
diseno del dataset (y su limitacion principal, ya declarada en el TP1). El
perfil clasifica cada columna en su familia antes de juzgarla.
"""

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"
INTERIM = BASE_DIR / "data" / "interim"
DOCS = BASE_DIR / "docs"

CLAVES = ["jurisdiccion", "departamento", "sector", "ambito"]

# Umbrales, con su porque. Ninguno es magico: son puntos de corte para ORDENAR
# los hallazgos, no para decidir. La decision es de la etapa 08.
FALTANTES_ALTO = 0.30      # arriba de esto, la columna aporta poco al modelado
CASI_CONSTANTE = 0.99      # un solo valor en >=99% de las filas
TOLERANCIA = 1e-9          # los flotantes no dan exactamente 0 ni 1


def familia_de(columna: str) -> str:
    """Clasifica cada columna por su rol en el dataset.

    Sin esto, los chequeos genericos producen falsos positivos: las `eph_` son
    constantes dentro de cada provincia por construccion, y las `cob__` son
    metadatos de calidad, no variables de analisis.
    """
    if columna in CLAVES:
        return "clave"
    if columna == "estudiantes":
        return "peso"
    if columna.startswith("flag_"):
        # Banderas derivadas de control (ej. flag_discrepancia_bases, que marca
        # 5 filas de 1.174 donde Lengua y Matematica difieren mas de 10%).
        # Existen para poder repetir un analisis sin esas filas y ver si el
        # resultado cambia. Que sean casi constantes NO es un defecto: es su
        # razon de ser. El chequeo de "casi constante" las marcaba, y era un
        # falso positivo del instrumento, no un problema del dato.
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


def bloque_de(columna: str) -> str | None:
    """El bloque al que pertenece una proporcion ('sexo__femenino' -> 'sexo')."""
    if "__" not in columna or columna.startswith(("cob__", "eph_")):
        return None
    return columna.split("__")[0]


def perfilar(maestro: pd.DataFrame) -> pd.DataFrame:
    """Una fila por columna del dataset, con todo lo medible de esa columna."""
    filas = []
    total = len(maestro)
    for col in maestro.columns:
        serie = maestro[col]
        faltantes = int(serie.isna().sum())
        unicos = int(serie.nunique(dropna=True))
        fila = {
            "columna": col,
            "familia": familia_de(col),
            "bloque": bloque_de(col),
            "tipo": str(serie.dtype),
            "faltantes": faltantes,
            "pct_faltantes": round(faltantes / total, 4),
            "valores_unicos": unicos,
        }
        if pd.api.types.is_numeric_dtype(serie):
            validos = serie.dropna()
            fila.update({
                "minimo": validos.min() if len(validos) else np.nan,
                "maximo": validos.max() if len(validos) else np.nan,
                "media": validos.mean() if len(validos) else np.nan,
                "mediana": validos.median() if len(validos) else np.nan,
                "desvio": validos.std() if len(validos) else np.nan,
            })
            # Un solo valor domina casi toda la columna: aporta poco al modelo.
            if len(validos):
                dominante = validos.value_counts(normalize=True).iloc[0]
                fila["frac_valor_dominante"] = round(float(dominante), 4)
        else:
            fila["ejemplos"] = " | ".join(
                str(v) for v in serie.dropna().unique()[:3])
        filas.append(fila)
    return pd.DataFrame(filas)


def buscar_problemas(maestro: pd.DataFrame, perfil: pd.DataFrame) -> list[dict]:
    """Los chequeos de calidad. Cada uno devuelve su hallazgo con denominador.

    Devuelve una lista de dicts para que el informe los pueda ordenar por
    impacto en vez de por el orden en que se escribieron los chequeos.
    """
    total = len(maestro)
    hallazgos = []

    def anotar(chequeo, severidad, afectadas, de, detalle, columnas=()):
        hallazgos.append({
            "chequeo": chequeo,
            "severidad": severidad,
            "afectadas": afectadas,
            "de": de,
            "detalle": detalle,
            "columnas": list(columnas),
        })

    # --- 1. Duplicados en la clave territorial -------------------------------
    dup = maestro.duplicated(subset=CLAVES).sum()
    anotar("clave territorial duplicada",
           "alta" if dup else "ok", int(dup), total,
           "cada fila tiene que ser un jurisdiccion x departamento x sector x "
           "ambito unico; si se repite, el dataset cuenta el mismo grupo dos veces")

    # --- 2. Filas enteramente duplicadas -------------------------------------
    dup_full = maestro.duplicated().sum()
    anotar("fila completa duplicada",
           "alta" if dup_full else "ok", int(dup_full), total,
           "filas identicas en las 131 columnas")

    # --- 3. Proporciones fuera de [0, 1] -------------------------------------
    props = perfil[perfil["familia"].isin(
        ["proporcion", "cobertura", "armonizada"])]["columna"].tolist()
    fuera = []
    for col in props:
        s = maestro[col].dropna()
        if len(s) and (s.lt(-TOLERANCIA).any() or s.gt(1 + TOLERANCIA).any()):
            fuera.append(col)
    anotar("proporcion fuera de [0,1]",
           "alta" if fuera else "ok", len(fuera), len(props),
           "una proporcion negativa o mayor que 1 es imposible por definicion",
           fuera)

    # --- 4. Bloques de proporciones que no suman 1 ---------------------------
    bloques = sorted({b for b in perfil["bloque"].dropna().unique()})
    rotos = []
    for bloque in bloques:
        cols = [c for c in maestro.columns
                if bloque_de(c) == bloque and familia_de(c) == "proporcion"]
        if len(cols) < 2:
            continue
        suma = maestro[cols].sum(axis=1)
        con_dato = suma > TOLERANCIA
        malas = int((con_dato & (suma - 1).abs().gt(1e-6)).sum())
        if malas:
            rotos.append(f"{bloque} ({malas} filas)")
    anotar("bloque de proporciones que no suma 1",
           "alta" if rotos else "ok", len(rotos), len(bloques),
           "cada bloque reparte el 100% de una poblacion; si no suma 1 se "
           "perdio o se duplico una categoria", rotos)

    # --- 5. Faltantes altos ---------------------------------------------------
    altos = perfil[perfil["pct_faltantes"] > FALTANTES_ALTO]
    anotar("columna con muchos faltantes",
           "media" if len(altos) else "ok", len(altos), len(perfil),
           f"mas del {FALTANTES_ALTO:.0%} de las filas sin dato",
           [f"{r.columna} ({r.pct_faltantes:.0%})"
            for r in altos.itertuples()])

    # --- 6. Variables sin variabilidad ---------------------------------------
    # Se excluyen las de contexto provincial: son constantes por provincia POR
    # CONSTRUCCION, no por un problema de datos.
    # Se excluyen tres familias porque su baja variabilidad es estructural:
    # las de contexto son constantes por provincia, las claves son texto, y
    # las de control existen justamente para marcar unas pocas filas.
    candidatas = perfil[
        ~perfil["familia"].isin(["contexto_provincial", "clave", "control"])
    ]
    constantes = candidatas[candidatas["valores_unicos"] <= 1]
    anotar("columna constante o vacia",
           "alta" if len(constantes) else "ok", len(constantes), len(candidatas),
           "un solo valor (o ninguno) en las 1.174 filas: no aporta nada a "
           "ningun modelo",
           constantes["columna"].tolist())

    casi = candidatas[
        (candidatas["valores_unicos"] > 1)
        & (candidatas.get("frac_valor_dominante", pd.Series(dtype=float))
           > CASI_CONSTANTE)
    ]
    anotar("columna casi constante",
           "media" if len(casi) else "ok", len(casi), len(candidatas),
           f"un mismo valor en mas del {CASI_CONSTANTE:.0%} de las filas",
           [f"{r.columna} ({r.frac_valor_dominante:.1%})"
            for r in casi.itertuples()])

    # --- 7. Categorias con espacios o mayusculas inconsistentes --------------
    inconsistentes = []
    for col in CLAVES:
        valores = maestro[col].dropna().astype(str)
        con_espacios = valores[valores != valores.str.strip()]
        normalizados = valores.str.strip().str.upper()
        colisiones = normalizados.nunique() != valores.str.strip().nunique()
        if len(con_espacios) or colisiones:
            inconsistentes.append(
                f"{col} (espacios: {len(con_espacios)}, "
                f"colisiones al normalizar: {colisiones})")
    anotar("categoria con formato inconsistente",
           "media" if inconsistentes else "ok", len(inconsistentes), len(CLAVES),
           "espacios al borde o valores que solo difieren en mayusculas: hacen "
           "que un join o un group by parta el mismo grupo en dos",
           inconsistentes)

    # --- 8. Cobertura baja: el dato existe pero representa poco --------------
    cobs = [c for c in maestro.columns if c.startswith("cob__")]
    bajas = []
    for col in cobs:
        s = maestro[col].dropna()
        n = int((s < 0.5).sum())
        if n:
            bajas.append(f"{col} ({n} filas bajo 50%)")
    anotar("bloque con cobertura menor al 50%",
           "media" if bajas else "ok", len(bajas), len(cobs),
           "la proporcion es real pero se calculo sobre menos de la mitad de "
           "los estudiantes de esa fila: el numero existe y significa poco",
           bajas)

    # --- 9. Filas sin ningun dato util ---------------------------------------
    analiticas = perfil[perfil["familia"].isin(
        ["proporcion", "armonizada"])]["columna"].tolist()
    vacias = int(maestro[analiticas].isna().all(axis=1).sum())
    anotar("fila sin ninguna variable analitica",
           "alta" if vacias else "ok", vacias, total,
           "una fila sin ninguna proporcion no aporta al analisis")

    # --- 10. Extremos por rango intercuartil ---------------------------------
    # Ver el docstring: en un dataset que mezcla departamentos de tamanos muy
    # distintos, "extremo" no equivale a "erroneo". Se reporta para mirar, no
    # para borrar.
    numericas = perfil[perfil["familia"].isin(
        ["proporcion", "armonizada", "peso"])]["columna"].tolist()
    con_extremos = []
    for col in numericas:
        s = maestro[col].dropna()
        if len(s) < 20:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        if iqr <= TOLERANCIA:
            continue
        n = int(((s < q1 - 3 * iqr) | (s > q3 + 3 * iqr)).sum())
        if n:
            con_extremos.append((col, n))
    con_extremos.sort(key=lambda x: -x[1])
    anotar("columna con valores extremos (3x IQR)",
           "baja" if con_extremos else "ok", len(con_extremos), len(numericas),
           "valores muy lejos del cuerpo de la distribucion. NO son "
           "necesariamente errores: pueden ser departamentos chicos",
           [f"{c} ({n})" for c, n in con_extremos[:12]])

    return hallazgos


def escribir_informe(hallazgos, perfil, maestro, destino: Path) -> None:
    """El informe legible. Ordenado por severidad y por cuantas filas afecta."""
    orden = {"alta": 0, "media": 1, "baja": 2, "ok": 3}
    hallazgos = sorted(hallazgos, key=lambda h: (orden[h["severidad"]], -h["afectadas"]))

    lineas = [
        "# Perfil de calidad del dataset maestro",
        "",
        "Generado por `pipeline/03_curacion/07_perfilado.py`. **Mide, no corrige.**",
        "Las decisiones de curacion se toman mirando esto y se aplican en la etapa 08.",
        "",
        "## El dataset",
        "",
        f"- **{len(maestro):,} filas x {maestro.shape[1]:,} columnas**",
        f"- Cada fila es un grupo *jurisdiccion x departamento x sector x ambito*, "
        f"no un estudiante.",
        f"- Estudiantes representados: **{maestro['estudiantes'].sum():,.0f}**",
        "",
        "### Columnas por familia",
        "",
        "| Familia | Columnas | Que son |",
        "|---|---|---|",
    ]
    glosario = {
        "clave": "identifican la fila",
        "peso": "cuantos estudiantes representa la fila",
        "proporcion": "reparto de una poblacion dentro de la fila (suman 1 por bloque)",
        "cobertura": "que fraccion de la fila quedo representada en ese bloque",
        "contexto_provincial": "indicador de la EPH, **igual para toda la provincia**",
        "control": "bandera derivada para analisis de sensibilidad (es rara a proposito)",
        "armonizada": "llevada a escala comparable entre Aprender y la EPH",
        "otra": "sin clasificar",
    }
    for familia, n in perfil["familia"].value_counts().items():
        lineas.append(f"| `{familia}` | {n} | {glosario.get(familia, '')} |")

    lineas += ["", "## Hallazgos", "",
               "Cada chequeo con su denominador. `ok` = el chequeo corrio y no "
               "encontro nada.", ""]

    for h in hallazgos:
        marca = {"alta": "ALTA", "media": "MEDIA", "baja": "BAJA", "ok": "ok"}[h["severidad"]]
        lineas.append(f"### [{marca}] {h['chequeo']}")
        lineas.append("")
        lineas.append(f"**{h['afectadas']} de {h['de']}**. {h['detalle']}.")
        if h["columnas"]:
            lineas.append("")
            for c in h["columnas"][:25]:
                lineas.append(f"- `{c}`")
            if len(h["columnas"]) > 25:
                lineas.append(f"- ... y {len(h['columnas']) - 25} mas "
                              f"(estan todas en `perfil_columnas.csv`)")
        lineas.append("")

    lineas += [
        "## Lo que este perfil NO puede ver",
        "",
        "- No sabe si un valor es **correcto**, solo si es **posible**.",
        "- No compara contra los datos crudos: eso lo hacen los 41 invariantes "
        "de `tests/test_invariantes.py`.",
        "- Los extremos se detectan con rango intercuartil, que asume una sola "
        "poblacion. Este dataset mezcla departamentos de tamanos muy distintos, "
        "asi que un extremo puede ser simplemente un departamento chico.",
        "- Que una columna no tenga faltantes no significa que represente bien a "
        "los estudiantes de la fila: eso lo dicen las columnas `cob__`.",
        "",
    ]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main():
    maestro = pd.read_csv(PROC / "dataset_maestro_inicial.csv")

    perfil = perfilar(maestro)
    hallazgos = buscar_problemas(maestro, perfil)

    print("=" * 74)
    print("PERFIL DEL DATASET MAESTRO")
    print("=" * 74)
    print(f"  {len(maestro):,} filas x {maestro.shape[1]:,} columnas")
    print(f"  estudiantes representados: {maestro['estudiantes'].sum():,.0f}")
    print()
    print("  columnas por familia:")
    for familia, n in perfil["familia"].value_counts().items():
        print(f"    {familia:<22} {n:>4}")

    print()
    print("=" * 74)
    print("CHEQUEOS DE CALIDAD  (cada uno con su denominador)")
    print("=" * 74)
    orden = {"alta": 0, "media": 1, "baja": 2, "ok": 3}
    for h in sorted(hallazgos, key=lambda x: (orden[x["severidad"]], -x["afectadas"])):
        marca = h["severidad"].upper() if h["severidad"] != "ok" else "ok  "
        print(f"  [{marca:<5}] {h['chequeo']:<45} {h['afectadas']:>4} de {h['de']}")
        for c in h["columnas"][:6]:
            print(f"             · {c}")
        if len(h["columnas"]) > 6:
            print(f"             · ... y {len(h['columnas']) - 6} mas")

    INTERIM.mkdir(parents=True, exist_ok=True)
    perfil.to_csv(INTERIM / "perfil_columnas.csv", index=False, encoding="utf-8")
    escribir_informe(hallazgos, perfil, maestro, DOCS / "07_perfil_calidad.md")

    print()
    print(f"  GUARDADO: data/interim/perfil_columnas.csv "
          f"({len(perfil)} filas, una por columna)")
    print(f"  GUARDADO: docs/07_perfil_calidad.md")


if __name__ == "__main__":
    main()
