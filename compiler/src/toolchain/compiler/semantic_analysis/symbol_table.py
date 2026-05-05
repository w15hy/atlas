"""Tabla de símbolos con cadena de ámbitos (scope chain).

Cada ámbito es un diccionario `nombre -> Symbol`. Los ámbitos se apilan al
entrar a un bloque/función y se desapilan al salir. La búsqueda recorre la
pila desde el más interno al global, lo que da semántica de shadowing.
"""


class Symbol:
    """Entrada de la tabla de símbolos.

    kind: "var" | "param" | "func" | "struct"
    type: tipo del lenguaje (str primitivo, StructType o ArrayType)
    extra: dict opcional con metadatos (params, ret_type, address, ...)
    """

    def __init__(self, name, kind, type_, **extra):
        self.name = name
        self.kind = kind
        self.type = type_
        self.extra = extra

    def __repr__(self):
        return f"<{self.kind} {self.name}: {self.type}>"


class SymbolTable:
    def __init__(self):
        # Ámbito 0 = global. Siempre presente.
        self._scopes = [{}]
        # Tabla de structs separada (los structs son tipos, no valores).
        self.structs = {}
        # Tabla de funciones (atajo, también viven en el ámbito global).
        self.functions = {}

    # ---------------- ámbitos ----------------
    def enter_scope(self):
        self._scopes.append({})

    def exit_scope(self):
        if len(self._scopes) == 1:
            raise RuntimeError("No se puede salir del ámbito global")
        return self._scopes.pop()

    @property
    def current_scope(self):
        return self._scopes[-1]

    @property
    def depth(self):
        return len(self._scopes) - 1

    # ---------------- declaraciones ----------------
    def declare(self, symbol):
        """Inserta un símbolo en el ámbito actual. Falla si ya existe en el mismo ámbito."""
        scope = self.current_scope
        if symbol.name in scope:
            return False
        scope[symbol.name] = symbol
        return True

    def declare_struct(self, name, struct_type):
        if name in self.structs:
            return False
        self.structs[name] = struct_type
        return True

    def declare_function(self, name, symbol):
        if name in self.functions:
            return False
        self.functions[name] = symbol
        # Las funciones también son visibles en el ámbito global por nombre.
        self._scopes[0][name] = symbol
        return True

    # ---------------- búsquedas ----------------
    def lookup(self, name):
        """Busca un símbolo en la cadena de ámbitos (interno → global)."""
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_struct(self, name):
        return self.structs.get(name)

    def lookup_function(self, name):
        return self.functions.get(name)

    def is_declared_in_current_scope(self, name):
        return name in self.current_scope
