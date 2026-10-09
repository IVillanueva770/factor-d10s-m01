"""Etapa 12: baja el Relevamiento Anual consolidado, fijado a un commit.

Fuente: el repo de referencia que recomendo la mentora
(agus476/radar-trayectorias-educativas-argentinas). El lo bajo del Ministerio,
lo concateno de 2011 a 2024 y lo dejo con la misma clave territorial que
Aprender. Se usa como guia y se cita; los datos son publicos.

Se baja por commit exacto y se verifica el SHA-256 de cada archivo. Si el
archivo ya esta y el hash coincide, no se vuelve a bajar. Si no coincide, la
etapa corta: un hash distinto es otro dato, y ningun numero de abajo valdria.
"""

import hashlib
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modelado import ARCHIVOS_RELEVAMIENTO, COMMIT_REFERENCIA, REPO_REFERENCIA  # noqa: E402

BASE_DIR = Path(__file__).resolve().parents[2]
DESTINO = BASE_DIR / "data" / "raw" / "relevamiento"


def _sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nombre, (ruta_repo, esperado) in ARCHIVOS_RELEVAMIENTO.items():
        local = DESTINO / nombre
        if local.exists() and _sha256(local) == esperado:
            print(f"  {nombre}: ya estaba, hash verificado")
            continue
        url = (f"https://raw.githubusercontent.com/{REPO_REFERENCIA}/"
               f"{COMMIT_REFERENCIA}/{ruta_repo}")
        print(f"  {nombre}: bajando de {url}")
        urllib.request.urlretrieve(url, local)
        obtenido = _sha256(local)
        if obtenido != esperado:
            raise SystemExit(
                f"{nombre}: el hash no coincide ({obtenido[:12]}... contra "
                f"{esperado[:12]}...). No se sigue con un dato distinto.")
        print(f"  {nombre}: hash verificado")


if __name__ == "__main__":
    main()
