import os
import re

_INCLUDE_RE = re.compile(r'^\s*#include\s+[<"](.+?)[">]\s*$')


def include(lineas, base_dir=".", _visited=None):
    if _visited is None:
        _visited = set()

    resultado = []

    for linea in lineas:
        m_inc = _INCLUDE_RE.match(linea)

        if m_inc:
            raw = m_inc.group(1)

            ruta = raw if os.path.isabs(raw) else os.path.join(base_dir, raw)
            ruta = os.path.abspath(ruta)

            # evitar ciclos
            if ruta in _visited:
                print(f"[WARN] include repetido/cíclico: {ruta}")
                continue

            if not os.path.exists(ruta):
                print(f"[ERROR] include no encontrado: {ruta}")
                continue

            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    sub = f.readlines()

                _visited.add(ruta)

                resultado.extend(
                    include(sub, base_dir=os.path.dirname(ruta), _visited=_visited)
                )

            except Exception as e:
                print(f"[ERROR] leyendo {ruta}: {e}")

            continue

        resultado.append(linea)

    return resultado
