"""Generador de codigo Atlas -> ensamblador (.asm) para SPL_New.

Modelo de maquina (validado contra CPU/registers.py, CPU/instructions.py,
CPU/formats.py y main.py de la maquina):

    RAM           : 65536 bytes direccionables por byte
    Registros GP  : R0..R15 (64 bits)
    PC            : 32 bits, inicia en 0 (donde se carga el .bin)
    SP            : inicia en 60000, crece hacia abajo (implicito en call/ret/push/pop)
    Instruccion   : 64 bits = 8 bytes; PC avanza 8 por step
    loadw/storew  : leen/escriben 8 bytes (palabra completa)
    load/store    : leen/escriben 1 byte
    halt          : imprime R14 como float y detiene

Mapa de memoria (dinamico, sin zonas fijas):
    [org .. code_end)   codigo   (code_end = org + n_instrucciones * 8)
    [code_end .. str_base)  variables globales y locales (8 bytes c/u)
    [str_base .. SP)    literales string (interned)
    [60000 .. 65536)    pila (SP_INIT del CPU)

Convencion de llamada:
    R0..R5  argumentos (max 6); R0 valor de retorno
    R6..R13 pool de temporales para expresiones
    R14, R15 reservados (R14 lo usa halt para imprimir; SP implicito)

Limitaciones conocidas:
    - Las locales se mangleian por nombre de funcion ("fn::var"); no hay
      stack frame real, asi que la recursion no funciona.
    - El analisis ya valido tipos; el codegen confia en type_annotations
      para despachar entero vs float (add vs fadd, cmp vs fcmp).
    - Mezcla int/float promueve el operando int con fi2f.
"""

import re

from compiler.types import (
    FLOAT,
    INT,
    STRING,
    ArrayType,
    StructType,
)


# ---- constantes del hardware (solo las que no cambian) ----
STACK_LIMIT = 60000  # SP arranca aqui en el CPU
WORD_SIZE = 8        # loadw/storew mueven 8 bytes (64 bits)

# Patrones de placeholder para direcciones pendientes de resolucion.
# Se insertan en el ASM generado y se reemplazan por enteros reales
# despues de contar las instrucciones de codigo.
_DA_PAT = re.compile(r'__DA_(\d+)__')   # data region
_DS_PAT = re.compile(r'__DS_(\d+)__')   # string region

# Replica exacta de los patrones que usa first_pass() en el ensamblador
# para distinguir instrucciones de comentarios / etiquetas / directivas.
_ORG_RE = re.compile(r'^\s*\.org\s+(\d+)\s*(?:#.*)?$', re.IGNORECASE)
_DATA_DIR_RE = re.compile(r'^\s*\.(fill|byte|string)\b', re.IGNORECASE)
_LABEL_ID_RE = re.compile(r'[A-Za-z_]\w*')


class CodeGenError(Exception):
    pass


class CodeGenerator:
    def __init__(self, symbol_table, type_annotations, org=0):
        self.table = symbol_table
        self.types = type_annotations
        self._org = org

        self.lines = []
        self._label_counter = 0

        # mangled_name -> byte offset DENTRO de la region de datos
        # (relativo a data_base, que se calcula despues de generar el codigo)
        self.var_addresses = {}
        # mangled_name -> tipo del lenguaje (str, StructType, ArrayType)
        self.var_types = {}
        self._next_data_offset = 0  # proximo offset libre en la region de datos

        # str literal -> byte offset dentro de la region de strings
        self.string_pool = {}
        self._next_str_offset = 0

        self._free_regs = list(range(6, 14))  # R6..R13
        self._func_stack = []                  # nombres de funcion en curso
        self._loop_stack = []                  # [(label_continue, label_break)]

    # ===================================================================
    # Helpers de direccionamiento con placeholder
    # ===================================================================
    def _da(self, offset):
        """Placeholder para una direccion en la region de datos."""
        return f"__DA_{offset}__"

    def _ds(self, offset):
        """Placeholder para una direccion en la region de strings."""
        return f"__DS_{offset}__"

    # ===================================================================
    # API publica
    # ===================================================================
    def generate(self, ast):
        if ast is None or ast[0] != "program":
            raise CodeGenError("AST invalido para codegen")

        # Pre-asigna offsets y tipos de TODA la jerarquia (incluyendo
        # locales dentro de funciones). Esto compensa que el analizador haya
        # cerrado los scopes al terminar.
        self._preallocate(ast[1])

        self._comment("=" * 72)
        self._comment("  Compilado por Atlas Compiler - codegen")
        self._comment("[HEADER_INFO]")   # sera reemplazado en _resolve_addresses
        self._comment("=" * 72)
        self._emit(f".org {self._org}")
        self._emit("")

        # ---------- entry point ----------
        global_stmts = [s for s in ast[1] if s and s[0] not in ("func_def", "struct")]
        for s in global_stmts:
            self._gen_stmt(s)

        if self.table.lookup_function("main") is not None:
            self._emit("    call main")
        self._emit("    halt")
        self._emit("")

        # ---------- cuerpos de funcion ----------
        for s in ast[1]:
            if s and s[0] == "func_def":
                self._gen_func(s)

        # ---------- resolver direcciones reales ----------
        data_base, str_base = self._resolve_addresses()

        # Actualizar linea de informacion del mapa de memoria
        code_end = data_base
        for i, line in enumerate(self.lines):
            if "[HEADER_INFO]" in line:
                self.lines[i] = (
                    f"#   code=[{self._org}..{code_end})  "
                    f"data=[{data_base}..{str_base})  "
                    f"strings=[{str_base}..{STACK_LIMIT})  SP={STACK_LIMIT}"
                )
                break

        # ---------- emisión de la región de datos (zero-init) ----------
        # Las directivas .fill / .string que siguen producen bytes crudos en
        # el .binReloc; gracias a ellas las cadenas terminan en RAM en la
        # dirección absoluta calculada arriba (str_base + offset).
        # Se emiten DESPUÉS de _resolve_addresses para que esas líneas no
        # cuenten como instrucciones de 8 bytes en _count_instructions.
        if self._next_data_offset > 0:
            self._emit("")
            self._comment("-" * 72)
            self._comment(f" Sección de datos (variables)  [{data_base}..{str_base})")
            self._comment("-" * 72)
            self._emit(f"    .fill {self._next_data_offset}")

        # ---------- emisión de la región de strings ----------
        if self.string_pool:
            self._emit("")
            self._comment("-" * 72)
            self._comment(f" Sección de strings  [{str_base}..)")
            self._comment("-" * 72)
            # Recorrer el pool en orden de offset para mantener la
            # correspondencia con __DS_<offset>__.
            for s, offset in sorted(self.string_pool.items(), key=lambda kv: kv[1]):
                escaped = (
                    s.replace('\\', '\\\\')
                     .replace('"', '\\"')
                     .replace('\n', '\\n')
                     .replace('\t', '\\t')
                     .replace('\r', '\\r')
                )
                self._comment(f"  [{str_base + offset}] = {s!r}")
                self._emit(f'    .string "{escaped}"')

        return "\n".join(self.lines) + "\n"

    # ===================================================================
    # Resolucion de direcciones (post-codegen)
    # ===================================================================
    def _count_instructions(self):
        """Replica la logica de first_pass() del ensamblador para contar
        instrucciones (cada una ocupa 8 bytes en memoria)."""
        count = 0
        for line in self.lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            if '#' in stripped:
                stripped = stripped.split('#', 1)[0].strip()
            if not stripped or _ORG_RE.match(stripped):
                continue
            # Etiqueta sola
            if stripped.endswith(':') and ' ' not in stripped:
                continue
            # Etiqueta con instruccion en la misma linea
            if ':' in stripped:
                parts = stripped.split(':', 1)
                if _LABEL_ID_RE.fullmatch(parts[0].strip()):
                    remainder = parts[1].strip()
                    if not remainder:
                        continue
                    stripped = remainder
            # Las directivas de datos no son instrucciones; emiten bytes.
            if _DATA_DIR_RE.match(stripped):
                continue
            count += 1
        return count

    def _resolve_addresses(self):
        """Reemplaza __DA_N__ y __DS_N__ por direcciones absolutas reales
        una vez que se conoce el tamano del codigo."""
        n_instrs = self._count_instructions()
        data_base = self._org + n_instrs * WORD_SIZE
        str_base = data_base + self._next_data_offset

        if str_base + self._next_str_offset > STACK_LIMIT:
            raise CodeGenError(
                f"Memoria insuficiente: el programa necesita hasta "
                f"{str_base + self._next_str_offset} bytes pero SP={STACK_LIMIT}"
            )

        def replace_da(m):
            return str(data_base + int(m.group(1)))

        def replace_ds(m):
            return str(str_base + int(m.group(1)))

        for i, line in enumerate(self.lines):
            if '__DA_' in line:
                line = _DA_PAT.sub(replace_da, line)
            if '__DS_' in line:
                line = _DS_PAT.sub(replace_ds, line)
            self.lines[i] = line

        return data_base, str_base

    # ===================================================================
    # Pre-asignacion de offsets y tipos
    # ===================================================================
    def _preallocate(self, stmts):
        for s in stmts:
            self._prealloc_stmt(s, prefix="")

    def _prealloc_stmt(self, s, prefix):
        if s is None:
            return
        tag = s[0]
        if tag == "decl":
            _, ttype, name, _init = s
            rtype = self._resolve_type(ttype)
            self._alloc_var(prefix + name, self._type_size(rtype), rtype)
        elif tag == "array_decl":
            _, ttype, name, size_expr = s
            n = size_expr[1] if size_expr and size_expr[0] == "num" else 16
            elem_type = self._resolve_type(ttype)
            atype = ArrayType(elem_type, int(n))
            self._alloc_var(prefix + name, WORD_SIZE * int(n), atype)
        elif tag == "func_def":
            _, fname, params, block, _ret = s
            for ptype, pname in params:
                rtype = self._resolve_type(ptype)
                # Parámetros arreglo guardan solo la dirección base (8 bytes).
                self._alloc_var(f"{fname}::{pname}", WORD_SIZE, rtype)
            self._prealloc_block(block, prefix=f"{fname}::")
        elif tag == "if":
            _, _c, b, elif_chain, else_block = s
            self._prealloc_block(b, prefix)
            for branch in elif_chain or []:
                self._prealloc_block(branch[2], prefix)
            if else_block is not None:
                self._prealloc_block(else_block[1], prefix)
        elif tag == "while":
            self._prealloc_block(s[2], prefix)
        elif tag == "for":
            _, init, _c, _u, b = s
            self._prealloc_stmt(init, prefix)
            self._prealloc_block(b, prefix)

    def _prealloc_block(self, block, prefix):
        if block is None or block[0] != "block":
            return
        for s in block[1]:
            self._prealloc_stmt(s, prefix)

    def _alloc_var(self, mangled, size, vtype):
        if mangled in self.var_addresses:
            return self.var_addresses[mangled]
        offset = self._next_data_offset
        self.var_addresses[mangled] = offset
        self.var_types[mangled] = vtype
        bumped = ((size + WORD_SIZE - 1) // WORD_SIZE) * WORD_SIZE
        self._next_data_offset += bumped
        return offset

    def _type_size(self, rtype):
        if isinstance(rtype, StructType):
            return WORD_SIZE * len(rtype.fields)
        if isinstance(rtype, ArrayType):
            n = rtype.size if rtype.size is not None else 16
            return WORD_SIZE * int(n)
        return WORD_SIZE

    def _resolve_type(self, ttype):
        # Marcador del parser para parámetros tipo arreglo.
        if isinstance(ttype, tuple) and ttype and ttype[0] == "array":
            elem = self._resolve_type(ttype[1])
            return ArrayType(elem, size=None, is_pointer=True)
        if ttype in (INT, FLOAT, STRING):
            return ttype
        st = self.table.lookup_struct(ttype)
        if st is not None:
            return st
        return INT

    # ===================================================================
    # Statements
    # ===================================================================
    def _gen_stmt(self, s):
        if s is None:
            return
        tag = s[0]
        handler = getattr(self, f"_gs_{tag}", None)
        if handler is None:
            self._comment(f"; nodo no implementado en codegen: {tag}")
            return
        handler(s)

    def _gs_decl(self, s):
        _, _t, name, init = s
        if init is None:
            return
        offset = self._addr_of(name)
        r = self._gen_expr(init)
        self._emit(f"    storew R{r}, {self._da(offset)}    # {name} = ...")
        self._free_reg(r)

    def _gs_array_decl(self, s):
        _, _t, name, _size = s
        self._comment(f"; arreglo {name} base={self._da(self._addr_of(name))}")

    def _gs_assign(self, s):
        _, name, expr = s
        offset = self._addr_of(name)
        r = self._gen_expr(expr)
        self._emit(f"    storew R{r}, {self._da(offset)}    # {name} = ...")
        self._free_reg(r)

    def _gs_assign_attr(self, s):
        _, obj, attr, expr = s
        offset = self._field_addr(obj, attr)
        r = self._gen_expr(expr)
        self._emit(f"    storew R{r}, {self._da(offset)}    # {obj}.{attr} = ...")
        self._free_reg(r)

    def _gs_assign_index(self, s):
        _, name, idx_expr, expr = s
        base_offset = self._addr_of(name)
        vtype = self._type_of(name)
        ridx = self._gen_expr(idx_expr)
        rval = self._gen_expr(expr)
        self._emit(f"    muli R{ridx}, {WORD_SIZE}    # idx * word")
        if isinstance(vtype, ArrayType) and vtype.is_pointer:
            # Parámetro arreglo: el slot guarda la dirección base.
            rbase = self._alloc_reg()
            self._emit(f"    loadw R{rbase}, {self._da(base_offset)}    # base de {name} (ptr)")
            self._emit(f"    add R{ridx}, R{rbase}    # idx*word + base")
            self._free_reg(rbase)
        else:
            self._emit(f"    addi R{ridx}, {self._da(base_offset)}    # +base de {name}")
        self._emit(f"    storew R{rval}, R{ridx}    # {name}[idx] = ...")
        self._free_reg(ridx)
        self._free_reg(rval)

    def _gs_expr_stmt(self, s):
        r = self._gen_expr(s[1])
        if r is not None:
            self._free_reg(r)

    def _gs_return(self, s):
        _, expr = s
        if expr is not None:
            r = self._gen_expr(expr)
            if r != 0:
                self._emit(f"    mov R0, R{r}    # valor de retorno")
            self._free_reg(r)
        self._emit("    ret")

    def _gs_break(self, _s):
        if not self._loop_stack:
            return
        _, lend = self._loop_stack[-1]
        self._emit(f"    jmp {lend}    # break")

    def _gs_continue(self, _s):
        if not self._loop_stack:
            return
        lcont, _ = self._loop_stack[-1]
        self._emit(f"    jmp {lcont}    # continue")

    def _gs_if(self, s):
        _, cond, block, elif_chain, else_block = s
        l_end = self._new_label("if_end")
        l_next = self._new_label("if_next")
        self._gen_cond_jump_if_false(cond, l_next)
        self._gen_block(block)
        self._emit(f"    jmp {l_end}")
        self._label(l_next)
        for branch in elif_chain or []:
            _, ec, eb = branch
            l_after = self._new_label("if_next")
            self._gen_cond_jump_if_false(ec, l_after)
            self._gen_block(eb)
            self._emit(f"    jmp {l_end}")
            self._label(l_after)
        if else_block is not None:
            self._gen_block(else_block[1])
        self._label(l_end)

    def _gs_while(self, s):
        _, cond, block = s
        l_start = self._new_label("while_start")
        l_end = self._new_label("while_end")
        self._label(l_start)
        self._gen_cond_jump_if_false(cond, l_end)
        self._loop_stack.append((l_start, l_end))
        self._gen_block(block)
        self._loop_stack.pop()
        self._emit(f"    jmp {l_start}")
        self._label(l_end)

    def _gs_for(self, s):
        _, init, cond, update, block = s
        self._gen_stmt(init)
        l_start = self._new_label("for_start")
        l_update = self._new_label("for_update")
        l_end = self._new_label("for_end")
        self._label(l_start)
        self._gen_cond_jump_if_false(cond, l_end)
        self._loop_stack.append((l_update, l_end))
        self._gen_block(block)
        self._loop_stack.pop()
        self._label(l_update)
        self._gen_stmt(update)
        self._emit(f"    jmp {l_start}")
        self._label(l_end)

    def _gs_struct(self, _s):
        return

    def _gen_block(self, block):
        if block is None or block[0] != "block":
            return
        for s in block[1]:
            self._gen_stmt(s)

    # ===================================================================
    # Funciones
    # ===================================================================
    def _gen_func(self, s):
        _, name, params, block, _ret = s
        self._func_stack.append(name)
        self._comment("")
        self._comment(f"--- funcion {name}({', '.join(p[1] for p in params)}) ---")
        self._label(name)
        for i, (_ptype, pname) in enumerate(params):
            offset = self._addr_of(pname)
            self._emit(f"    storew R{i}, {self._da(offset)}    # parametro {pname}")
        for st in block[1]:
            self._gen_stmt(st)
        if not self.lines or self.lines[-1].strip() != "ret":
            self._emit("    ret")
        self._func_stack.pop()

    # ===================================================================
    # Expresiones
    # ===================================================================
    def _gen_expr(self, expr):
        tag = expr[0]
        handler = getattr(self, f"_ge_{tag}", None)
        if handler is None:
            self._comment(f"; expr no implementada: {tag}")
            r = self._alloc_reg()
            self._emit(f"    mov R{r}, 0")
            return r
        return handler(expr)

    def _ge_num(self, expr):
        v = expr[1]
        r = self._alloc_reg()
        if isinstance(v, float):
            self._emit(f"    fmov R{r}, {v}    # literal float")
        else:
            self._emit(f"    mov R{r}, {int(v)}")
        return r

    def _ge_str(self, expr):
        v = expr[1]
        str_offset = self._intern_string(v)
        r = self._alloc_reg()
        self._emit(f"    mov R{r}, {self._ds(str_offset)}    # &\"{v[:20]}\"")
        return r

    def _ge_id(self, expr):
        name = expr[1]
        offset = self._addr_of(name)
        vtype = self._type_of(name)
        r = self._alloc_reg()
        if isinstance(vtype, ArrayType) and not vtype.is_pointer:
            # Arreglo declarado localmente: el "valor" del nombre es la
            # dirección base del buffer.
            self._emit(f"    mov R{r}, {self._da(offset)}    # &{name}")
        else:
            # Escalar o parámetro arreglo (slot guarda la dirección).
            self._emit(f"    loadw R{r}, {self._da(offset)}    # {name}")
        return r

    def _ge_attr(self, expr):
        _, obj, attr = expr
        offset = self._field_addr(obj, attr)
        r = self._alloc_reg()
        self._emit(f"    loadw R{r}, {self._da(offset)}    # {obj}.{attr}")
        return r

    def _ge_index(self, expr):
        _, name, idx = expr
        base_offset = self._addr_of(name)
        vtype = self._type_of(name)
        ridx = self._gen_expr(idx)
        self._emit(f"    muli R{ridx}, {WORD_SIZE}")
        if isinstance(vtype, ArrayType) and vtype.is_pointer:
            rbase = self._alloc_reg()
            self._emit(f"    loadw R{rbase}, {self._da(base_offset)}    # base de {name} (ptr)")
            self._emit(f"    add R{ridx}, R{rbase}")
            self._free_reg(rbase)
        else:
            self._emit(f"    addi R{ridx}, {self._da(base_offset)}")
        rdst = self._alloc_reg()
        self._emit(f"    loadw R{rdst}, R{ridx}    # {name}[idx]")
        self._free_reg(ridx)
        return rdst

    def _ge_binop(self, expr):
        _, op, lhs, rhs = expr
        if op in ("and", "&&"):
            return self._gen_short_circuit(lhs, rhs, is_and=True)
        if op in ("or", "||"):
            return self._gen_short_circuit(lhs, rhs, is_and=False)

        lt = self.types.get(id(lhs))
        rt = self.types.get(id(rhs))
        use_float = (lt == FLOAT) or (rt == FLOAT)

        rl = self._gen_expr(lhs)
        if use_float and lt == INT:
            self._emit(f"    fi2f R{rl}    # promote int->float")
        rr = self._gen_expr(rhs)
        if use_float and rt == INT:
            self._emit(f"    fi2f R{rr}    # promote int->float")

        if op == "+":
            self._emit(f"    {'fadd' if use_float else 'add'} R{rl}, R{rr}")
        elif op == "-":
            self._emit(f"    {'fsub' if use_float else 'sub'} R{rl}, R{rr}")
        elif op == "*":
            self._emit(f"    {'fmul' if use_float else 'mul'} R{rl}, R{rr}")
        elif op == "/":
            self._emit(f"    {'fdiv' if use_float else 'div'} R{rl}, R{rr}")
        elif op in ("<", "<=", ">", ">=", "==", "!="):
            return self._gen_compare(op, rl, rr, use_float)
        else:
            self._comment(f"; op '{op}' no soportado")
        self._free_reg(rr)
        return rl

    def _gen_compare(self, op, rl, rr, use_float):
        if use_float:
            self._emit(f"    fcmp R{rl}, R{rr}")
        else:
            self._emit(f"    cmp R{rl}, R{rr}")
        self._free_reg(rr)
        l_true = self._new_label("cmp_t")
        l_end = self._new_label("cmp_e")
        if op == "==":
            self._emit(f"    jz {l_true}")
        elif op == "!=":
            self._emit(f"    jne {l_true}")
        elif op == "<":
            self._emit(f"    jn {l_true}")
        elif op == "<=":
            l_eq = self._new_label("cmp_eq")
            self._emit(f"    jz {l_eq}")
            self._emit(f"    jn {l_true}")
            self._emit(f"    mov R{rl}, 0")
            self._emit(f"    jmp {l_end}")
            self._label(l_eq)
            self._label(l_true)
            self._emit(f"    mov R{rl}, 1")
            self._label(l_end)
            return rl
        elif op == ">":
            self._emit(f"    jg {l_true}")
        elif op == ">=":
            self._emit(f"    jge {l_true}")
        self._emit(f"    mov R{rl}, 0")
        self._emit(f"    jmp {l_end}")
        self._label(l_true)
        self._emit(f"    mov R{rl}, 1")
        self._label(l_end)
        return rl

    def _gen_short_circuit(self, lhs, rhs, is_and):
        rl = self._gen_expr(lhs)
        l_short = self._new_label("sc_short")
        l_end = self._new_label("sc_end")
        rzero = self._alloc_reg()
        self._emit(f"    mov R{rzero}, 0")
        self._emit(f"    cmp R{rl}, R{rzero}")
        self._free_reg(rzero)
        if is_and:
            self._emit(f"    jz {l_short}")
        else:
            self._emit(f"    jne {l_short}")
        rr = self._gen_expr(rhs)
        self._emit(f"    mov R{rl}, R{rr}")
        self._free_reg(rr)
        self._emit(f"    jmp {l_end}")
        self._label(l_short)
        if is_and:
            self._emit(f"    mov R{rl}, 0")
        else:
            self._emit(f"    mov R{rl}, 1")
        self._label(l_end)
        return rl

    def _ge_unop(self, expr):
        _, op, e = expr
        r = self._gen_expr(e)
        if op in ("not", "!"):
            l_zero = self._new_label("not_z")
            l_end = self._new_label("not_e")
            rzero = self._alloc_reg()
            self._emit(f"    mov R{rzero}, 0")
            self._emit(f"    cmp R{r}, R{rzero}")
            self._free_reg(rzero)
            self._emit(f"    jz {l_zero}")
            self._emit(f"    mov R{r}, 0")
            self._emit(f"    jmp {l_end}")
            self._label(l_zero)
            self._emit(f"    mov R{r}, 1")
            self._label(l_end)
        return r

    def _ge_uminus(self, expr):
        et = self.types.get(id(expr[1]))
        r = self._gen_expr(expr[1])
        self._emit(f"    {'fneg' if et == FLOAT else 'neg'} R{r}")
        return r

    def _ge_call(self, expr):
        _, name, args = expr
        if name in ("print", "out"):
            for a in args:
                ra = self._gen_expr(a)
                # Si el argumento es un string el registro contiene una
                # dirección al pool de strings; usamos outs para imprimir
                # la cadena ASCII en lugar del valor numérico del puntero.
                a_type = self.types.get(id(a))
                if a_type == STRING:
                    self._emit(f"    outs R{ra}    # print string")
                elif a_type == FLOAT:
                    self._emit(f"    fout R{ra}    # print float")
                else:
                    self._emit(f"    out R{ra}    # print")
                self._free_reg(ra)
            r = self._alloc_reg()
            self._emit(f"    mov R{r}, 0")
            return r
        if name == "input":
            r = self._alloc_reg()
            self._comment("; input() sin HW; deja 0")
            self._emit(f"    mov R{r}, 0")
            return r
        if name in (INT, FLOAT, STRING):
            arg = args[0]
            arg_t = self.types.get(id(arg))
            r = self._gen_expr(arg)
            if name == FLOAT and arg_t == INT:
                self._emit(f"    fi2f R{r}")
            elif name == INT and arg_t == FLOAT:
                self._emit(f"    ff2i R{r}")
            return r

        if len(args) > 6:
            raise CodeGenError(
                f"Llamada a '{name}' con mas de 6 argumentos no soportada"
            )
        # Cada argumento se evalúa y se vuelca a la pila inmediatamente.
        # Esto preserva los argumentos ya evaluados ante llamadas anidadas
        # dentro de la evaluación de los argumentos siguientes (las funciones
        # clobbean R6..R13 sin avisar; sin spill perderíamos esos valores).
        for a in args:
            r = self._gen_expr(a)
            self._emit(f"    push R{r}    # spill arg para {name}")
            self._free_reg(r)
        # Recuperar en R(N-1)..R0 (orden inverso al push) para que el
        # primer argumento quede en R0.
        for i in range(len(args) - 1, -1, -1):
            self._emit(f"    pop R{i}    # arg{i + 1}")
        self._emit(f"    call {name}")
        rdst = self._alloc_reg()
        if rdst != 0:
            self._emit(f"    mov R{rdst}, R0    # retorno de {name}")
        return rdst

    # ===================================================================
    # Saltos condicionales
    # ===================================================================
    def _gen_cond_jump_if_false(self, cond, label):
        if cond[0] == "binop" and cond[1] in ("<", "<=", ">", ">=", "==", "!="):
            _, op, lhs, rhs = cond
            lt = self.types.get(id(lhs))
            rt = self.types.get(id(rhs))
            use_float = (lt == FLOAT) or (rt == FLOAT)
            rl = self._gen_expr(lhs)
            if use_float and lt == INT:
                self._emit(f"    fi2f R{rl}")
            rr = self._gen_expr(rhs)
            if use_float and rt == INT:
                self._emit(f"    fi2f R{rr}")
            if use_float:
                self._emit(f"    fcmp R{rl}, R{rr}")
            else:
                self._emit(f"    cmp R{rl}, R{rr}")
            self._free_reg(rl)
            self._free_reg(rr)
            if op == "==":
                self._emit(f"    jne {label}")
            elif op == "!=":
                self._emit(f"    jz {label}")
            elif op == "<":
                self._emit(f"    jge {label}")
            elif op == "<=":
                self._emit(f"    jg {label}")
            elif op == ">":
                l_skip = self._new_label("sk")
                self._emit(f"    jg {l_skip}")
                self._emit(f"    jmp {label}")
                self._label(l_skip)
            elif op == ">=":
                self._emit(f"    jn {label}")
            return
        r = self._gen_expr(cond)
        rzero = self._alloc_reg()
        self._emit(f"    mov R{rzero}, 0")
        self._emit(f"    cmp R{r}, R{rzero}")
        self._free_reg(rzero)
        self._free_reg(r)
        self._emit(f"    jz {label}")

    # ===================================================================
    # Auxiliares
    # ===================================================================
    def _emit(self, line):
        self.lines.append(line)

    def _label(self, name):
        self.lines.append(f"{name}:")

    def _comment(self, txt):
        self.lines.append(txt if txt.startswith("#") else f"# {txt}")

    def _new_label(self, prefix):
        self._label_counter += 1
        return f"{prefix}_{self._label_counter}"

    def _alloc_reg(self):
        if not self._free_regs:
            raise CodeGenError(
                "Pool de registros temporales agotado; expresion demasiado compleja"
            )
        return self._free_regs.pop(0)

    def _free_reg(self, r):
        if 6 <= r <= 13 and r not in self._free_regs:
            self._free_regs.append(r)

    def _addr_of(self, name):
        """Offset (en bytes desde data_base) para la variable indicada."""
        if self._func_stack:
            mangled = f"{self._func_stack[-1]}::{name}"
            if mangled in self.var_addresses:
                return self.var_addresses[mangled]
        if name in self.var_addresses:
            return self.var_addresses[name]
        return self._alloc_var(name, WORD_SIZE, INT)

    def _type_of(self, name):
        if self._func_stack:
            mangled = f"{self._func_stack[-1]}::{name}"
            if mangled in self.var_types:
                return self.var_types[mangled]
        return self.var_types.get(name)

    def _field_addr(self, obj, field):
        """Offset (en bytes desde data_base) del campo `field` dentro del struct `obj`."""
        base_offset = self._addr_of(obj)
        otype = self._type_of(obj)
        if not isinstance(otype, StructType):
            return base_offset
        field_offset = 0
        for _ftype, fname in otype.fields:
            if fname == field:
                break
            field_offset += WORD_SIZE
        return base_offset + field_offset

    def _intern_string(self, s):
        if s in self.string_pool:
            return self.string_pool[s]
        offset = self._next_str_offset
        self.string_pool[s] = offset
        size = ((len(s) + 1 + WORD_SIZE - 1) // WORD_SIZE) * WORD_SIZE
        self._next_str_offset += size
        return offset


def generate(ast, symbol_table, type_annotations, org=0):
    cg = CodeGenerator(symbol_table, type_annotations, org=org)
    return cg.generate(ast)
