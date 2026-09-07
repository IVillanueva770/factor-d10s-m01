"""Etapa 08: curar el dataset. Aplica las decisiones que salieron del perfil 07.

El principio que ordena esta etapa
----------------------------------
Cada decision de curacion se escribe UNA sola vez, en `pipeline/decisiones.py`.
De ahi salen las tres cosas: el codigo que la aplica (aca), la fila que la
etapa 09 suma al diccionario, y el informe que la justifica. No hay forma de
que el codigo haga una cosa y el informe cuente otra, porque los tres leen la
misma fuente.

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

from decisiones import DECISIONES  # noqa: E402  (fuente unica, ver el modulo)


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
    curado = aplicar(maestro)

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

    curado.to_csv(PROC / "dataset_maestro_curado.csv", index=False, encoding="utf-8")
    escribir_informe(curado, maestro, DOCS / "08_decisiones_curacion.md")

    print()
    print("  GUARDADO: data/processed/dataset_maestro_curado.csv")
    print("  GUARDADO: docs/08_decisiones_curacion.md")


if __name__ == "__main__":
    main()
