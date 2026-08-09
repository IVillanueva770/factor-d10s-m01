"""Piezas compartidas por todo el pipeline.

Existe para que ciertas reglas vivan en UN solo lugar. La normalizacion de
nombres de provincia estaba escrita dos veces (13 y 15) y la segunda copia
salio mal: Aprender escribe "Cordoba" con tilde y la tabla de correspondencia
sin tilde, asi que el join fallaba en silencio. Lo cazo un assert, pero la
causa era tener la misma regla duplicada.
"""

import unicodedata

import pandas as pd

CLAVES_TERRITORIALES = ["jurisdiccion", "departamento", "sector", "ambito"]

# Los CSV del Ministerio: separador ';', latin-1 y coma decimal. Sin declararlo
# pandas devuelve una sola columna de texto.
LECTURA_APRENDER = {"sep": ";", "encoding": "latin-1", "dtype": str}


def a_numero(serie):
    """Texto con coma decimal -> float. Los blancos (' ') quedan en NaN."""
    return pd.to_numeric(
        serie.astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )


def clave_provincia(texto):
    """Normaliza un nombre de provincia para poder unir entre fuentes.

    Aprender dice 'Córdoba' y 'Tierra del Fuego, Antártida e Islas del
    Atlántico Sur'; la tabla de aglomerados dice 'Cordoba' y 'Tierra del
    Fuego, Antartida e Islas del Atlantico Sur'. Sin normalizar, el join
    pierde filas sin avisar.
    """
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(sin_tildes.lower().replace(",", " ").split())
