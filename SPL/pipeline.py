"""Pipeline SPL: .atl -> .pre -> .asm -> .binReloc -> .bin

Uso:
    python pipeline.py <archivo.atl>
    python pipeline.py programs/factorial.atl

Los intermedios se guardan en .build_<nombre>/ junto al archivo fuente.
El binario final queda en .build_<nombre>/<nombre>.bin
"""

import os
import sys

# Agrega SPL/ al path para que los submódulos sean importables.
_SPL_DIR = os.path.dirname(os.path.abspath(__file__))
if _SPL_DIR not in sys.path:
    sys.path.insert(0, _SPL_DIR)

from preprocessor.preprocessor import preprocessor
from compiler.lexer import lexer_output
from compiler.parser import parse
from compiler.analyzer import analyze_and_generate
import assembler
import linker
from utils import ofile, ofilelines, wfilelines


def run(atl_path):
    atl_path = os.path.abspath(atl_path)
    if not os.path.exists(atl_path):
        print(f"[ERROR] Archivo no encontrado: {atl_path}")
        return None

    basename = os.path.splitext(os.path.basename(atl_path))[0]
    atl_dir  = os.path.dirname(atl_path)
    build_dir = os.path.join(atl_dir, f".build_{basename}")
    os.makedirs(build_dir, exist_ok=True)

    # ── 1. Preprocesador ─────────────────────────────────────────────────
    print(f"[1/4] Preprocesando  {os.path.basename(atl_path)}")
    lines    = ofilelines(atl_path)
    pre_lines = preprocessor(lines, base_dir=atl_dir)
    pre_path  = os.path.join(build_dir, f"{basename}.pre")
    wfilelines(pre_path, pre_lines)

    # ── 2. Lexer + Parser ────────────────────────────────────────────────
    print(f"[2/4] Compilando     {basename}.pre -> AST")
    source = ofile(pre_path)

    tok_str, _, _, _ = lexer_output(source)
    wfilelines(os.path.join(build_dir, f"{basename}.tokens"), tok_str)

    ast, parse_errors = parse(source)
    if parse_errors:
        print("\n[ERROR] Parser:")
        for e in parse_errors:
            print(f"  {e}")
        return None

    # ── 3. Semántico + Codegen ───────────────────────────────────────────
    print(f"[3/4] Generando      {basename}.asm")
    result = analyze_and_generate(ast)
    if result["errors"]:
        print("\n[ERROR] Semántico / Codegen:")
        for e in result["errors"]:
            print(f"  {e}")
        return None

    asm_path = os.path.join(build_dir, f"{basename}.asm")
    wfilelines(asm_path, result["asm"])

    # ── 4. Ensamblador ───────────────────────────────────────────────────
    print(f"[4/4] Ensamblando    {basename}.asm -> .binReloc -> .bin")
    binreloc_path = os.path.join(build_dir, f"{basename}.binReloc")
    try:
        parsed_asm   = assembler.parse(asm_path)
        translated   = assembler.translate(parsed_asm)
        assembler.write_output(translated, binreloc_path)
    except Exception as e:
        print(f"[ERROR] Ensamblador: {e}")
        return None

    # ── 5. Enlazador ─────────────────────────────────────────────────────
    bin_path = os.path.join(build_dir, f"{basename}.bin")
    try:
        parsed_reloc = linker.parse(binreloc_path)
        linked       = linker.translate(parsed_reloc)
        linker.write_output(linked, bin_path, parsed_reloc["base_address"])
    except Exception as e:
        print(f"[ERROR] Enlazador: {e}")
        return None

    print(f"\n[OK] {bin_path}")
    return bin_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python pipeline.py <archivo.atl>")
        sys.exit(1)

    result = run(sys.argv[1])
    sys.exit(0 if result else 1)
