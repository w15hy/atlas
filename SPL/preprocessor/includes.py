"""Resolución de directivas #include.

Sintaxis aceptada:
    #include <ruta>     -> busca primero en stdlib_dir, luego en base_dir
    #include "ruta"     -> busca solo en base_dir (relativa al archivo actual)
"""

import os
import re

_INCLUDE_SYS_RE = re.compile(r'^\s*#include\s+<(.+?)>\s*$')
_INCLUDE_LOCAL_RE = re.compile(r'^\s*#include\s+"(.+?)"\s*$')


def _resolve(raw, base_dir, stdlib_dir, is_system):
    """Devuelve la ruta absoluta del include, o None si no existe."""
    if os.path.isabs(raw):
        return raw if os.path.exists(raw) else None

    if is_system and stdlib_dir is not None:
        ruta = os.path.abspath(os.path.join(stdlib_dir, raw))
        if os.path.exists(ruta):
            return ruta

    ruta = os.path.abspath(os.path.join(base_dir, raw))
    if os.path.exists(ruta):
        return ruta
    return None


def include(lineas, base_dir=".", stdlib_dir=None, _visited=None):
    if _visited is None:
        _visited = set()

    resultado = []

    for linea in lineas:
        m_sys = _INCLUDE_SYS_RE.match(linea)
        m_local = _INCLUDE_LOCAL_RE.match(linea) if not m_sys else None
        m = m_sys or m_local

        if not m:
            resultado.append(linea)
            continue

        raw = m.group(1)
        ruta = _resolve(raw, base_dir, stdlib_dir, is_system=bool(m_sys))

        if ruta is None:
            print(f"[ERROR] include no encontrado: {raw}")
            continue

        if ruta in _visited:
            print(f"[WARN] include repetido/cíclico: {ruta}")
            continue

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                sub = f.readlines()

            _visited.add(ruta)
            resultado.extend(
                include(sub, base_dir=os.path.dirname(ruta),
                        stdlib_dir=stdlib_dir, _visited=_visited)
            )

        except Exception as e:
            print(f"[ERROR] leyendo {ruta}: {e}")

    return resultado
