"""Etapa 08: curar el dataset. Aplica las decisiones que salieron del perfil 07.

El principio que ordena esta etapa
----------------------------------
Cada decision de curacion se escribe UNA sola vez, en la lista DECISIONES de
abajo. De ahi salen las tres cosas: el codigo que la aplica, la fila que se
suma al diccionario de variables, y el informe que la justifica. No hay forma
de que el codigo haga una cosa y el informe cuente otra, porque los dos leen
la misma fuente.

Que se decidio, y el criterio comun
-----------------------------------
Ninguna decision borra filas ni modifica valores. Las cuatro son de la misma
familia: HACER VISIBLE un problema en vez de taparlo, para que cualquier
analisis posterior lo pueda excluir con una condicion explicita y medir si
excluirlo cambia el resultado.

El criterio detras, discutido con el equipo: los tres problemas encontrados
(clima escolar mal cubierto, departamentos enmascarados, valores extremos)
afectan sobre todo a los grupos CHICOS y RURALES. Esa es exactamente la
poblacion con mayor riesgo de abandono, o sea el objeto de estudio del
proyecto. Limpiar por el camino facil (borrar filas, recortar valores) habria
sesgado el dataset contra lo que el proyecto viene a estudiar.

Lo que esta etapa NO hace
-------------------------
No imputa. No recorta. No borra filas. Si en el TP3 un modelo necesita una
version sin esas filas, la produce filtrando por las columnas que esta etapa
agrega, y queda escrito en el modelo cual fue el filtro.
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
PROC = BASE_DIR / "data" / "processed"
DOCS = BASE_DIR / "docs"

UMBRAL_COBERTURA = 0.50
CENTINELA_DEPARTAMENTO = "ENMASCARADO"


# ---------------------------------------------------------------------------
# Las decisiones. Fuente unica: codigo, diccionario e informe salen de aca.
# ---------------------------------------------------------------------------

def _clima_escolar_calidad(maestro: pd.DataFrame) -> pd.Series:
    """Tres estados, porque los dos problemas son disjuntos y distintos.

    MEDIDO: 96 filas no tienen NINGUN dato de clima escolar (las tres columnas
    clima_escolar__* vacias, verificado en las 96) y otras 91 lo tienen
    calculado sobre menos de la mitad de sus estudiantes. Son conjuntos
    disjuntos: la interseccion es 0. Un booleano las juntaria y perderia la
    diferencia entre "no hay dato" y "el dato es flojo", que no son lo mismo
    ni para un modelo ni para una conclusion.
    """
    cobertura = maestro["cob__clima_escolar"]
    calidad = pd.Series("ok", index=maestro.index, dtype="object")
    calidad[cobertura < UMBRAL_COBERTURA] = "cobertura_baja"
    calidad[cobertura.isna()] = "sin_dato"
    return calidad


def _es_agregado_provincial(maestro: pd.DataFrame) -> pd.Series:
    """True donde el departamento viene enmascarado en la fuente.

    MEDIDO: 63 filas en 23 de las 24 jurisdicciones. El Ministerio enmascara
    el nombre del departamento cuando el grupo es tan chico que identificaria
    a la escuela. Esas filas NO son un departamento: son el resto de los
    departamentos chicos de esa provincia, juntos.
    """
    return (maestro["departamento"].astype(str).str.strip().str.upper()
            == CENTINELA_DEPARTAMENTO)


DECISIONES = [
    {
        "id": "clima_escolar_calidad",
        "titulo": "Clima escolar: se marca la calidad del dato, no se toca el dato",
        "tipo": "columna nueva",
        "columna": "clima_escolar_calidad",
        "calcular": _clima_escolar_calidad,
        "hallazgo": (
            "Es el unico bloque con problemas de cobertura: los otros 15 estan "
            "entre 0,98 y 1,00. Tiene 96 filas sin ningun dato y 91 con el dato "
            "calculado sobre menos de la mitad de los estudiantes de la fila. "
            "Los dos conjuntos son disjuntos, asi que son 187 filas (15,9%) y "
            "9.808 estudiantes (1,8%)."
        ),
        "por_que_importa": (
            "El problema NO es aleatorio. La cobertura mediana cae de 0,921 en "
            "el quintil de grupos mas grandes a 0,722 en el mas chico, y por "
            "ambito va de 0,921 urbano a 0,744 rural: 155 de las 187 filas "
            "afectadas son rurales. Es decir que el clima escolar esta peor "
            "medido justo en las escuelas rurales chicas, que son las de mayor "
            "riesgo de abandono. Un modelo que use esta variable va a tener "
            "menos informacion precisamente donde mas la necesita, y eso hay "
            "que poder decirlo, no descubrirlo despues."
        ),
        "decision": (
            "Se conservan las tres columnas clima_escolar__* sin modificar y se "
            "agrega una columna con tres estados: 'ok', 'cobertura_baja' y "
            "'sin_dato'. Permite repetir cualquier analisis excluyendo las "
            "filas flojas y comprobar si el resultado cambia."
        ),
        "descartado": (
            "Imputar: inventaria valores justo en el segmento donde el sesgo "
            "vive, que es el peor lugar posible. Poner en NaN las 91 filas de "
            "baja cobertura: perderia dato real sin dejar rastro visible de la "
            "perdida. Sacar el bloque: tira una variable central del marco "
            "teorico por un problema que toca al 1,8% de los estudiantes."
        ),
        "dimension": "calidad",
        "unidad": "categorica (ok / cobertura_baja / sin_dato)",
    },
    {
        "id": "es_agregado_provincial",
        "titulo": "Departamentos enmascarados: se identifican, no se borran",
        "tipo": "columna nueva",
        "columna": "es_agregado_provincial",
        "calcular": _es_agregado_provincial,
        "hallazgo": (
            "63 filas de 1.174 tienen departamento = 'Enmascarado', en 23 de "
            "las 24 jurisdicciones, con 10.444 estudiantes (1,9%). El "
            "Ministerio enmascara el nombre cuando el grupo es tan chico que "
            "identificaria a la escuela."
        ),
        "por_que_importa": (
            "Rompe el significado de la clave territorial. Si el mismo texto "
            "aparece en 23 jurisdicciones, esas filas no son un departamento: "
            "son el agregado de los departamentos chicos de cada provincia. "
            "Nada avisaba: el chequeo de duplicados da 0 porque cada "
            "combinacion jurisdiccion + Enmascarado + sector + ambito es unica, "
            "y el de formato tampoco lo veia porque 'Enmascarado' esta bien "
            "escrito. Quien agrupe por departamento sin saberlo va a mezclar 23 "
            "provincias bajo un mismo nombre."
        ),
        "decision": (
            "Se conservan las 63 filas y se agrega una columna booleana que las "
            "identifica. Un analisis por departamento filtra "
            "es_agregado_provincial == False; uno por provincia usa todas, que "
            "es donde estas filas SI suman bien y donde sacarlas romperia los "
            "totales contra la fuente."
        ),
        "descartado": (
            "Borrarlas: se irian 10.444 estudiantes de los departamentos mas "
            "chicos del pais, que es el perfil de mayor riesgo, y los totales "
            "por provincia dejarian de cerrar contra Aprender. Solo "
            "documentarlo: deja la trampa disponible para el que no lea el doc."
        ),
        "dimension": "territorio",
        "unidad": "booleano",
    },
    {
        "id": "extremos_sin_tocar",
        "titulo": "Valores extremos: no se tocan, y el chequeo se corrigio",
        "tipo": "decision sin cambio en el dataset",
        "columna": None,
        "calcular": None,
        "hallazgo": (
            "75 de 94 columnas numericas tienen valores a mas de 3 rangos "
            "intercuartiles del cuerpo de la distribucion. La peor, "
            "edad__21_anos, marca 138 filas."
        ),
        "por_que_importa": (
            "Al traducir la proporcion a personas se ve que no son errores. En "
            "edad__21_anos el 70% de las filas vale exactamente 0, lo que "
            "aplasta el rango intercuartil a 0,0020 y deja el umbral de extremo "
            "en 0,0078; un solo estudiante de 21 anos en un grupo de 118 da "
            "0,0085 y ya lo supera. La mediana de estudiantes detras de las 138 "
            "filas marcadas es 2,3 personas, y 84 de 138 tienen menos de 3. El "
            "chequeo estaba marcando 'aca hay un estudiante de 21 anos'. "
            "Ademas la senal es real: ponderando por estudiantes, la tasa de 21 "
            "anos va de 0,55% en estatal rural a 0,06% en privado urbano, nueve "
            "veces, la misma brecha de gestion que el TP1 encontro en sobreedad."
        ),
        "decision": (
            "No se recorta ni se winsoriza nada. Se corrigio el instrumento: el "
            "perfil ahora reporta cuantas personas hay detras de cada extremo, "
            "porque sin ese numero el chequeo mentia por omision."
        ),
        "descartado": (
            "Winsorizar a los percentiles 1 y 99: modificaria datos correctos y "
            "borraria justamente los casos de sobreedad extrema, que son los "
            "que el proyecto viene a estudiar."
        ),
        "dimension": None,
        "unidad": None,
    },
    {
        "id": "cob_sexo_se_queda",
        "titulo": "cob__sexo se conserva pese a tener varianza cero",
        "tipo": "decision sin cambio en el dataset",
        "columna": None,
        "calcular": None,
        "hallazgo": (
            "cob__sexo vale exactamente 1,0 en las 1.174 filas: todos los "
            "estudiantes respondieron sexo."
        ),
        "por_que_importa": (
            "Una columna constante no aporta a un modelo, pero esta no es una "
            "variable predictiva: es metadato de cobertura, de la misma familia "
            "que las otras 15 columnas cob__. Nunca iba a entrar a un modelo."
        ),
        "decision": (
            "Se conserva. Mantiene simetrica la familia cob__ (un bloque, una "
            "cobertura) y su valor constante es en si mismo una verificacion: "
            "si alguna vez deja de ser 1,0, algo cambio en la fuente o en el "
            "pipeline. La seleccion de variables para el modelo es del TP3 y "
            "ahi las de varianza cero se descartan solas."
        ),
        "descartado": (
            "Sacarla del dataset: ahorra una columna de 131 y rompe la simetria "
            "de la familia por un beneficio que no existe en esta etapa."
        ),
        "dimension": None,
        "unidad": None,
    },
]


# ---------------------------------------------------------------------------

def aplicar(maestro: pd.DataFrame) -> pd.DataFrame:
    """Aplica las decisiones que agregan columnas. No modifica ninguna existente."""
    curado = maestro.copy()
    for decision in DECISIONES:
        if decision["calcular"] is None:
            continue
        curado[decision["columna"]] = decision["calcular"](maestro)

    # El invariante de esta etapa: curar no puede cambiar lo que ya habia.
    originales = list(maestro.columns)
    assert list(curado.columns)[:len(originales)] == originales, \
        "La curacion reordeno o renombro columnas existentes"
    for col in originales:
        assert curado[col].equals(maestro[col]), \
            f"La curacion modifico la columna existente '{col}'"
    assert len(curado) == len(maestro), \
        "La curacion cambio la cantidad de filas"
    return curado


def extender_diccionario(dicc: pd.DataFrame) -> pd.DataFrame:
    """Suma al diccionario existente una fila por columna nueva.

    Va al MISMO diccionario y no a uno aparte: la regla del proyecto es una
    fila por cada columna del dataset entregado. Dos diccionarios se
    desincronizan y despues nadie sabe cual manda.
    """
    filas = []
    for decision in DECISIONES:
        if decision["columna"] is None:
            continue
        filas.append({
            "variable": decision["columna"],
            "fuente": "derivada (etapa 08, curacion)",
            "variable_origen": None,
            "bloque": "calidad",
            "dimension": decision["dimension"],
            "descripcion": decision["decision"],
            "unidad": decision["unidad"],
            "denominador": None,
            "justificacion": decision["por_que_importa"],
            "limitaciones": decision["hallazgo"],
        })
    return pd.concat([dicc, pd.DataFrame(filas)], ignore_index=True)


def escribir_informe(curado: pd.DataFrame, maestro: pd.DataFrame, destino: Path):
    """El resumen de decisiones. Sale de DECISIONES, no se escribe a mano."""
    lineas = [
        "# Decisiones de curacion",
        "",
        "Generado por `pipeline/03_curacion/08_curar.py`. Cada decision de este "
        "informe sale de la misma estructura de datos que la aplica, asi que el "
        "codigo y el texto no pueden divergir.",
        "",
        "## El criterio comun",
        "",
        "**Ninguna decision borra filas ni modifica valores.** Las cuatro hacen "
        "lo mismo: vuelven visible un problema en vez de taparlo, para que "
        "cualquier analisis posterior lo pueda excluir con una condicion "
        "explicita y medir si excluirlo cambia el resultado.",
        "",
        "La razon es que los tres problemas encontrados (clima escolar mal "
        "cubierto, departamentos enmascarados, valores extremos) golpean sobre "
        "todo a los grupos **chicos y rurales**, que son exactamente la "
        "poblacion con mayor riesgo de abandono. Limpiar por el camino facil "
        "habria sesgado el dataset contra su propio objeto de estudio.",
        "",
        f"**Resultado:** {len(maestro):,} x {maestro.shape[1]} -> "
        f"{len(curado):,} x {curado.shape[1]}. Mismas filas, "
        f"{curado.shape[1] - maestro.shape[1]} columnas nuevas, "
        f"ninguna columna existente modificada (verificado por assert).",
        "",
    ]
    for i, d in enumerate(DECISIONES, 1):
        lineas += [
            f"## {i}. {d['titulo']}",
            "",
            f"*{d['tipo']}*" + (f" · `{d['columna']}`" if d["columna"] else ""),
            "",
            f"**Que se encontro.** {d['hallazgo']}",
            "",
            f"**Por que importa.** {d['por_que_importa']}",
            "",
            f"**Que se decidio.** {d['decision']}",
            "",
            f"**Que se descarto, y por que.** {d['descartado']}",
            "",
        ]
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main():
    maestro = pd.read_csv(PROC / "dataset_maestro_inicial.csv")
    dicc = pd.read_csv(PROC / "diccionario_variables.csv")

    curado = aplicar(maestro)
    dicc_curado = extender_diccionario(dicc)

    print("=" * 74)
    print("CURACION DEL DATASET MAESTRO")
    print("=" * 74)
    print(f"  entrada: {len(maestro):,} filas x {maestro.shape[1]} columnas")
    print(f"  salida : {len(curado):,} filas x {curado.shape[1]} columnas")
    print(f"  filas borradas: 0 · valores modificados: 0")
    print()
    for i, d in enumerate(DECISIONES, 1):
        print(f"  {i}. {d['titulo']}")
        if d["columna"]:
            conteo = curado[d["columna"]].value_counts(dropna=False)
            for valor, n in conteo.items():
                est = curado.loc[curado[d["columna"]] == valor, "estudiantes"].sum()
                print(f"       {str(valor):<16} {n:>5} filas   "
                      f"{est:>10,.0f} estudiantes "
                      f"({100 * est / curado['estudiantes'].sum():>4.1f}%)")
        else:
            print(f"       (sin cambios en el dataset)")
    print()

    # El diccionario tiene que seguir teniendo una fila por columna, ni una mas.
    assert set(dicc_curado["variable"]) == set(curado.columns), \
        "El diccionario y el dataset curado no coinciden columna a columna"
    assert len(dicc_curado) == curado.shape[1], \
        "El diccionario tiene filas repetidas o de mas"
    print(f"  diccionario: {len(dicc)} -> {len(dicc_curado)} filas "
          f"(una por columna del dataset curado, verificado)")

    curado.to_csv(PROC / "dataset_maestro_curado.csv", index=False, encoding="utf-8")
    dicc_curado.to_csv(PROC / "diccionario_curado.csv", index=False, encoding="utf-8")
    escribir_informe(curado, maestro, DOCS / "08_decisiones_curacion.md")

    print()
    print("  GUARDADO: data/processed/dataset_maestro_curado.csv")
    print("  GUARDADO: data/processed/diccionario_curado.csv")
    print("  GUARDADO: docs/08_decisiones_curacion.md")


if __name__ == "__main__":
    main()
