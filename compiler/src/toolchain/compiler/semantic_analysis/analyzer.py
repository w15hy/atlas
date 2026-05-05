"""Punto de entrada del análisis semántico + generación de código.

Encadena:
    AST  →  semantic.analyze()  →  (ast, table, errores)
              ↓
            codegen.generate()  →  .asm

API pública:
    analyze_and_generate(ast) -> {
        'asm': str | None,           # contenido del .asm si no hubo errores
        'errors': list[str],         # errores semánticos
        'symbol_table': SymbolTable, # tabla resultante
    }
"""

from toolchain.compiler.semantic_analysis import codegen, semantic


def analyze_and_generate(ast):
    sa = semantic.SemanticAnalyzer()
    annotated_ast, table, errors = sa.analyze(ast)

    asm_text = None
    if not errors:
        try:
            asm_text = codegen.generate(annotated_ast, table, sa.type_annotations)
        except codegen.CodeGenError as e:
            errors.append(f"\033[31mCODEGEN:\033[0m {e}")

    return {
        "asm": asm_text,
        "errors": errors,
        "symbol_table": table,
    }
