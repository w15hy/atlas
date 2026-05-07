"""Analizador semántico del lenguaje Atlas.

Recorre el AST producido por el parser y comprueba:
    - Declaración antes de uso
    - Redeclaraciones en el mismo ámbito
    - Compatibilidad de tipos en asignaciones, expresiones y retornos
    - Aridad y tipo de argumentos en llamadas a función
    - Acceso a campos de struct y a índices de arreglo
    - break/continue solo dentro de bucles
    - return obligatorio en funciones tipadas (parser ya marca ausencia,
      aquí también validamos el tipo)

Devuelve la tupla (ast_anotado, symbol_table, errores). El AST anotado es el
mismo árbol con un campo extra `_type` agregado a las expresiones para que
el generador de código no tenga que reinferir tipos.
"""

from compiler.symbol_table import Symbol, SymbolTable
from compiler.types import (
    BOOL,
    FLOAT,
    INT,
    STRING,
    UNKNOWN,
    VOID,
    ArrayType,
    StructType,
    common_numeric,
    is_assignable,
    is_numeric,
    type_name,
)


class SemanticAnalyzer:
    def __init__(self):
        self.table = SymbolTable()
        self.errors = []
        # Pila de tipos de retorno de funciones en curso (para validar return).
        self._return_types = []
        # Profundidad de bucles (para validar break/continue).
        self._loop_depth = 0
        # Anotaciones por nodo: {id(node): tipo}
        self.type_annotations = {}

    # -------------------- API pública --------------------
    def analyze(self, ast):
        if ast is None or ast[0] != "program":
            self.errors.append("\033[31mSEMANTIC:\033[0m AST inválido o vacío")
            return ast, self.table, self.errors

        # Primera pasada: registrar structs y firmas de funciones.
        # Esto permite llamadas a funciones declaradas más abajo en el archivo.
        self._collect_top_level(ast[1])

        # Segunda pasada: visitar todos los statements en orden.
        for stmt in ast[1]:
            self._visit_stmt(stmt)

        return ast, self.table, self.errors

    # -------------------- pasada de cabeceras --------------------
    def _collect_top_level(self, stmts):
        for stmt in stmts:
            if stmt is None:
                continue
            tag = stmt[0]
            if tag == "struct":
                _, name, fields = stmt
                normalized = []
                for ftype, fname in fields:
                    normalized.append((self._resolve_type(ftype), fname))
                stype = StructType(name, normalized)
                if not self.table.declare_struct(name, stype):
                    self._error(f"struct '{name}' redefinido")
            elif tag == "func_def":
                _, name, params, _block, ret_type = stmt
                resolved_params = [
                    (self._resolve_type(ptype), pname) for ptype, pname in params
                ]
                resolved_ret = self._resolve_type(ret_type)
                fsym = Symbol(
                    name,
                    "func",
                    resolved_ret,
                    params=resolved_params,
                    ret_type=resolved_ret,
                )
                if not self.table.declare_function(name, fsym):
                    self._error(f"función '{name}' redefinida")

    # -------------------- statements --------------------
    def _visit_stmt(self, stmt):
        if stmt is None:
            return
        tag = stmt[0]
        handler = getattr(self, f"_stmt_{tag}", None)
        if handler is None:
            self._error(f"nodo no soportado: {tag}")
            return
        handler(stmt)

    def _stmt_decl(self, stmt):
        _, type_spec, name, init = stmt
        vtype = self._resolve_type(type_spec)
        if not self.table.declare(Symbol(name, "var", vtype)):
            self._error(f"variable '{name}' ya declarada en este ámbito")
        if init is not None:
            init_type = self._visit_expr(init)
            if init_type != UNKNOWN and not is_assignable(vtype, init_type):
                self._error(
                    f"no se puede inicializar '{name}' de tipo {type_name(vtype)} "
                    f"con expresión de tipo {type_name(init_type)}"
                )

    def _stmt_array_decl(self, stmt):
        _, type_spec, name, size_expr = stmt
        elem_type = self._resolve_type(type_spec)
        size_type = self._visit_expr(size_expr)
        if size_type != INT:
            self._error(
                f"tamaño de arreglo '{name}' debe ser int, no {type_name(size_type)}"
            )
        # Si el tamaño es literal lo guardamos para reservar memoria luego.
        size_val = size_expr[1] if size_expr[0] == "num" else None
        atype = ArrayType(elem_type, size_val)
        if not self.table.declare(Symbol(name, "var", atype)):
            self._error(f"variable '{name}' ya declarada en este ámbito")

    def _stmt_assign(self, stmt):
        _, name, expr = stmt
        sym = self.table.lookup(name)
        if sym is None:
            self._error(f"variable '{name}' no declarada")
            self._visit_expr(expr)
            return
        rhs = self._visit_expr(expr)
        if rhs != UNKNOWN and not is_assignable(sym.type, rhs):
            self._error(
                f"no se puede asignar {type_name(rhs)} a '{name}' "
                f"de tipo {type_name(sym.type)}"
            )

    def _stmt_assign_attr(self, stmt):
        _, obj_name, attr, expr = stmt
        sym = self.table.lookup(obj_name)
        if sym is None:
            self._error(f"variable '{obj_name}' no declarada")
            self._visit_expr(expr)
            return
        if not isinstance(sym.type, StructType):
            self._error(f"'{obj_name}' no es un struct, no tiene campos")
            self._visit_expr(expr)
            return
        if attr not in sym.type.field_map:
            self._error(f"campo '{attr}' no existe en {type_name(sym.type)}")
            self._visit_expr(expr)
            return
        field_type = sym.type.field_map[attr]
        rhs = self._visit_expr(expr)
        if rhs != UNKNOWN and not is_assignable(field_type, rhs):
            self._error(
                f"no se puede asignar {type_name(rhs)} al campo "
                f"'{obj_name}.{attr}' de tipo {type_name(field_type)}"
            )

    def _stmt_assign_index(self, stmt):
        _, name, idx, expr = stmt
        sym = self.table.lookup(name)
        if sym is None:
            self._error(f"variable '{name}' no declarada")
            self._visit_expr(idx)
            self._visit_expr(expr)
            return
        if not isinstance(sym.type, ArrayType):
            self._error(f"'{name}' no es un arreglo, no se puede indexar")
            self._visit_expr(idx)
            self._visit_expr(expr)
            return
        if self._visit_expr(idx) != INT:
            self._error(f"índice de '{name}' debe ser int")
        rhs = self._visit_expr(expr)
        if rhs != UNKNOWN and not is_assignable(sym.type.element_type, rhs):
            self._error(
                f"no se puede asignar {type_name(rhs)} a '{name}[]' "
                f"de tipo {type_name(sym.type.element_type)}"
            )

    def _stmt_expr_stmt(self, stmt):
        self._visit_expr(stmt[1])

    def _stmt_return(self, stmt):
        _, expr = stmt
        if not self._return_types:
            self._error("'return' fuera de una función")
            if expr is not None:
                self._visit_expr(expr)
            return
        expected = self._return_types[-1]
        if expr is None:
            if expected != VOID:
                self._error(
                    f"'return' sin valor en función que devuelve {type_name(expected)}"
                )
            return
        actual = self._visit_expr(expr)
        if expected == VOID:
            self._error("'return' con valor en función void")
        elif actual != UNKNOWN and not is_assignable(expected, actual):
            self._error(
                f"tipo de retorno {type_name(actual)} incompatible con "
                f"{type_name(expected)} declarado"
            )

    def _stmt_break(self, _stmt):
        if self._loop_depth == 0:
            self._error("'break' fuera de un bucle")

    def _stmt_continue(self, _stmt):
        if self._loop_depth == 0:
            self._error("'continue' fuera de un bucle")

    def _stmt_if(self, stmt):
        _, cond, block, elif_chain, else_block = stmt
        ctype = self._visit_expr(cond)
        if ctype not in (INT, BOOL, FLOAT) and ctype != UNKNOWN:
            self._error(f"condición de 'if' debe ser numérica, no {type_name(ctype)}")
        self._visit_block(block)
        for branch in elif_chain or []:
            _, ec, eb = branch
            ect = self._visit_expr(ec)
            if ect not in (INT, FLOAT) and ect != UNKNOWN:
                self._error(f"condición de 'elif' debe ser numérica, no {type_name(ect)}")
            self._visit_block(eb)
        if else_block is not None:
            self._visit_block(else_block[1])

    def _stmt_while(self, stmt):
        _, cond, block = stmt
        ctype = self._visit_expr(cond)
        if ctype not in (INT, FLOAT) and ctype != UNKNOWN:
            self._error(f"condición de 'while' debe ser numérica, no {type_name(ctype)}")
        self._loop_depth += 1
        self._visit_block(block)
        self._loop_depth -= 1

    def _stmt_for(self, stmt):
        _, init, cond, update, block = stmt
        # El for introduce un ámbito propio para la variable de inicialización.
        self.table.enter_scope()
        self._visit_stmt(init)
        ctype = self._visit_expr(cond)
        if ctype not in (INT, FLOAT) and ctype != UNKNOWN:
            self._error(f"condición de 'for' debe ser numérica, no {type_name(ctype)}")
        self._visit_stmt(update)
        self._loop_depth += 1
        self._visit_block(block)
        self._loop_depth -= 1
        self.table.exit_scope()

    @staticmethod
    def _block_has_return(block):
        if not block or block[0] != "block":
            return False
        for stmt in block[1]:
            if stmt is None:
                continue
            if stmt[0] == "return":
                return True
            if stmt[0] in ("if", "while", "for"):
                for part in stmt[1:]:
                    if isinstance(part, tuple) and part[0] == "block":
                        if SemanticAnalyzer._block_has_return(part):
                            return True
        return False

    def _stmt_func_def(self, stmt):
        _, name, params, block, ret_type = stmt
        fsym = self.table.lookup_function(name)
        if fsym is None:
            # Pudo haber fallado en la pasada de cabeceras por redefinición; no se reintenta.
            return
        resolved_ret = fsym.extra.get("ret_type", VOID)
        if resolved_ret != VOID and not self._block_has_return(block):
            self._error(
                f"función '{name}' con tipo de retorno '{type_name(resolved_ret)}' "
                f"no tiene sentencia return"
            )
        self.table.enter_scope()
        for ptype, pname in fsym.extra.get("params", []):
            if not self.table.declare(Symbol(pname, "param", ptype)):
                self._error(f"parámetro '{pname}' duplicado en '{name}'")
        self._return_types.append(fsym.extra.get("ret_type", VOID))
        # No se llama _visit_block para no abrir otro ámbito redundante;
        # los parámetros y locales comparten el ámbito de la función.
        for s in block[1]:
            self._visit_stmt(s)
        self._return_types.pop()
        self.table.exit_scope()

    def _stmt_struct(self, _stmt):
        # Ya registrado en _collect_top_level.
        return

    def _visit_block(self, block):
        if block is None or block[0] != "block":
            return
        self.table.enter_scope()
        for s in block[1]:
            self._visit_stmt(s)
        self.table.exit_scope()

    # -------------------- expresiones --------------------
    def _visit_expr(self, expr):
        if expr is None:
            return UNKNOWN
        tag = expr[0]
        handler = getattr(self, f"_expr_{tag}", None)
        if handler is None:
            self._error(f"expresión no soportada: {tag}")
            return UNKNOWN
        t = handler(expr)
        self.type_annotations[id(expr)] = t
        return t

    def _expr_num(self, expr):
        v = expr[1]
        return FLOAT if isinstance(v, float) else INT

    def _expr_str(self, _expr):
        return STRING

    def _expr_id(self, expr):
        name = expr[1]
        sym = self.table.lookup(name)
        if sym is None:
            self._error(f"identificador '{name}' no declarado")
            return UNKNOWN
        return sym.type

    def _expr_attr(self, expr):
        _, obj, attr = expr
        sym = self.table.lookup(obj)
        if sym is None:
            self._error(f"variable '{obj}' no declarada")
            return UNKNOWN
        if not isinstance(sym.type, StructType):
            self._error(f"'{obj}' no es un struct")
            return UNKNOWN
        if attr not in sym.type.field_map:
            self._error(f"campo '{attr}' no existe en {type_name(sym.type)}")
            return UNKNOWN
        return sym.type.field_map[attr]

    def _expr_index(self, expr):
        _, name, idx = expr
        sym = self.table.lookup(name)
        if sym is None:
            self._error(f"variable '{name}' no declarada")
            self._visit_expr(idx)
            return UNKNOWN
        if not isinstance(sym.type, ArrayType):
            self._error(f"'{name}' no es un arreglo")
            return UNKNOWN
        if self._visit_expr(idx) != INT:
            self._error(f"índice de '{name}' debe ser int")
        return sym.type.element_type

    def _expr_binop(self, expr):
        _, op, lhs, rhs = expr
        lt = self._visit_expr(lhs)
        rt = self._visit_expr(rhs)
        if lt == UNKNOWN or rt == UNKNOWN:
            return UNKNOWN
        if op in ("+", "-", "*", "/"):
            if not (is_numeric(lt) and is_numeric(rt)):
                self._error(
                    f"operador '{op}' requiere operandos numéricos, "
                    f"no {type_name(lt)} y {type_name(rt)}"
                )
                return UNKNOWN
            return common_numeric(lt, rt)
        if op in ("<", "<=", ">", ">=", "==", "!="):
            if not (is_numeric(lt) and is_numeric(rt)) and lt != rt:
                self._error(
                    f"operador '{op}' no aplica entre {type_name(lt)} y {type_name(rt)}"
                )
                return UNKNOWN
            return INT
        if op in ("and", "or", "&&", "||"):
            return INT
        self._error(f"operador binario desconocido: '{op}'")
        return UNKNOWN

    def _expr_unop(self, expr):
        _, op, e = expr
        t = self._visit_expr(e)
        if op in ("not", "!"):
            return INT
        return t

    def _expr_uminus(self, expr):
        t = self._visit_expr(expr[1])
        if t != UNKNOWN and not is_numeric(t):
            self._error(f"operador unario '-' requiere numérico, no {type_name(t)}")
            return UNKNOWN
        return t

    def _expr_call(self, expr):
        _, name, args = expr
        # Built-ins reconocidos:
        if name in ("print", "out"):
            for a in args:
                self._visit_expr(a)
            return VOID
        if name == "input":
            if args:
                self._error("'input' no recibe argumentos")
            return INT
        # Constructor de tipo: int(x), float(x), string(x)
        if name in (INT, FLOAT, STRING):
            if len(args) != 1:
                self._error(f"conversión '{name}()' requiere 1 argumento")
            else:
                self._visit_expr(args[0])
            return name

        fsym = self.table.lookup_function(name)
        if fsym is None:
            self._error(f"función '{name}' no declarada")
            for a in args:
                self._visit_expr(a)
            return UNKNOWN
        params = fsym.extra.get("params", [])
        if len(args) != len(params):
            self._error(
                f"'{name}' espera {len(params)} argumento(s), recibió {len(args)}"
            )
        for i, a in enumerate(args):
            at = self._visit_expr(a)
            if i < len(params):
                ptype, _ = params[i]
                if at != UNKNOWN and not is_assignable(ptype, at):
                    self._error(
                        f"argumento {i+1} de '{name}': se esperaba "
                        f"{type_name(ptype)}, llegó {type_name(at)}"
                    )
        return fsym.extra.get("ret_type", VOID)

    # -------------------- tipos --------------------
    def _resolve_type(self, type_spec):
        """Convierte el nombre de tipo del AST en el objeto de tipo correspondiente."""
        if type_spec in (INT, FLOAT, STRING, VOID):
            return type_spec
        # 'def' es el keyword de función sin tipo explícito (lo lexea como ID).
        # Lo tratamos como tipo "any" para no obstruir la compilación.
        if type_spec == "def":
            from compiler.types import ANY
            return ANY
        # Puede ser el nombre de un struct.
        st = self.table.lookup_struct(type_spec)
        if st is not None:
            return st
        # Aún no está declarado: lo dejamos como nombre y avisamos.
        self._error(f"tipo '{type_spec}' no declarado")
        return UNKNOWN

    # -------------------- utilidades --------------------
    def _error(self, msg):
        self.errors.append(f"\033[31mSEMANTIC:\033[0m {msg}")


def analyze(ast):
    """API pública: devuelve (ast, symbol_table, errores)."""
    sa = SemanticAnalyzer()
    return sa.analyze(ast)
