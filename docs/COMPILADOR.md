# Compilador SPL — Análisis Léxico, Sintáctico y Semántico

Este documento describe en detalle las tres primeras fases del compilador SPL
de Atlas: el analizador léxico (lexer), el sintáctico (parser) y el semántico
(SemanticAnalyzer). Cada fase está implementada en un módulo independiente
dentro de [SPL/compiler/](../SPL/compiler/) y se encadena desde
[SPL/compiler/analyzer.py](../SPL/compiler/analyzer.py), que a su vez es
invocado por [SPL/pipeline.py](../SPL/pipeline.py).

---

## 1. Visión general del pipeline

```
   archivo.atl
      │
      ▼
┌─────────────────┐
│ Preprocesador   │  expande #include, #define, comentarios
│ (preprocessor)  │
└─────────────────┘
      │   archivo.pre
      ▼
┌─────────────────┐
│ A. LÉXICO       │  texto  →  flujo de tokens
│ (lexer.py, PLY) │
└─────────────────┘
      │   stream de tokens (LexToken)
      ▼
┌─────────────────┐
│ A. SINTÁCTICO   │  tokens →  AST (tuplas anidadas)
│ (parser.py,     │
│  PLY yacc)      │
└─────────────────┘
      │   ast = ('program', [ ... ])
      ▼
┌─────────────────┐
│ A. SEMÁNTICO    │  AST  →  AST anotado + SymbolTable + errores
│ (semantic.py)   │
└─────────────────┘
      │
      ▼
   codegen.py  →  archivo.asm  →  ensamblador  →  enlazador  →  archivo.bin
```

El orquestador [analyzer.analyze_and_generate](../SPL/compiler/analyzer.py)
encadena el semántico con el codegen; el lexer y el parser son invocados
directamente por [pipeline.run](../SPL/pipeline.py#L31).

Una característica importante: **las tres fases producen un objeto `errors`
acumulativo** y solo el pipeline decide abortar. El parser/semántico siguen
visitando el resto del archivo aunque encuentren un error, para reportar
varios problemas en la misma compilación.

---

## 2. Análisis Léxico — [`lexer.py`](../SPL/compiler/lexer.py)

### 2.1 Herramienta

Se usa [PLY](https://www.dabeaz.com/ply/) (Python Lex Yacc), un port de
lex/yacc a Python. PLY descubre las reglas por convención de nombres:

- `t_<TOKEN>` puede ser una **string** (regex simple, p. ej. `t_PLUS = r"\+"`)
  o una **función** con la regex en su docstring (`def t_NUMBER(t): r"…"`).
- Las funciones permiten transformar `t.value` antes de devolverlo.
- `t_ignore` y `t_ignore_COMMENT` descartan caracteres sin emitir token.

Una vez declaradas las reglas, `lex.lex()` construye el autómata y devuelve
una instancia [`lexer`](../SPL/compiler/lexer.py#L156) reutilizable.

### 2.2 Categorías de tokens

| Categoría        | Tokens                                                        |
|------------------|---------------------------------------------------------------|
| Identificadores  | `ID`                                                          |
| Literales        | `NUMBER` (int o float), `STRLIT`                              |
| Asignación / op. | `ASSIGN`, `RELOP` (`<`, `<=`, `>`, `>=`, `==`, `!=`)           |
| Lógicos          | `AND_OP` (`&&`), `OR_OP` (`\|\|`), `BANG` (`!`), `AND`/`OR`/`NOT` |
| Aritméticos      | `PLUS`, `MINUS`, `TIMES`, `DIVIDE`                             |
| Delimitadores    | `LPAREN`, `RPAREN`, `LBRACKET`, `RBRACKET`, `LBRACE`, `RBRACE`, `SEMI`, `COMA`, `DOT` |
| Reservadas       | `IF`, `ELSE`, `ELIF`, `WHILE`, `FOR`, `BREAK`, `CONTINUE`, `VOID`, `RETURN`, `INT`, `FLOAT`, `STRING_TYPE`, `STRUCT`, `AND`, `OR`, `NOT` |

La lista final se ensambla en [lexer.py:39-61](../SPL/compiler/lexer.py#L39-L61)
combinando `tokens` con los valores del diccionario `reserved`.

### 2.3 Reglas relevantes

#### Identificadores y palabras reservadas

```python
identifier = letter + r"(" + letter + r"|" + digit + r")*"

@TOKEN(identifier)
def t_ID(t):
    t.type = reserved.get(t.value, "ID")
    if t.type == "ID" and t.value not in symbol_table:
        symbol_table[t.value] = {"type": "unknown", "value": None}
    return t
```

[lexer.py:88-93](../SPL/compiler/lexer.py#L88-L93). Todo identificador entra
primero por esta regla; si está en el diccionario `reserved` se reclasifica
como token de palabra reservada. La tabla local `symbol_table` aquí es
**solo informativa** (estadísticas del lexer); el semántico mantiene su
propia [`SymbolTable`](../SPL/compiler/symbol_table.py).

#### Números

```python
def t_NUMBER(t):
    r"(\d+\.\d*|\.\d+|\d+)([eE][+-]?\d+)?"
    val = float(t.value) if ("." in t.value or "e" in t.value.lower()) else int(t.value)
    t.value = val
    ...
```

[lexer.py:96-102](../SPL/compiler/lexer.py#L96-L102). La regex acepta:
- enteros: `42`
- flotantes: `3.14`, `.5`, `2.`
- notación científica: `1e10`, `2.5e-3`

El `t.value` se convierte aquí mismo a `int` o `float`, lo que permite que
el semántico determine después el tipo del literal con un simple
`isinstance(v, float)` ([semantic.py:326-328](../SPL/compiler/semantic.py#L326-L328)).

#### Strings

```python
def t_STRLIT(t):
    r"\"([^\\\n]|(\\.))*?\""
    t.value = t.value[1:-1]
    ...
```

[lexer.py:105-110](../SPL/compiler/lexer.py#L105-L110). Permite secuencias de
escape (`\n`, `\"`, `\\`, …) y prohíbe el salto de línea sin escapar.
Se quitan las comillas en el `t.value`.

#### Comentarios y espacios

```python
t_ignore = " \t"
t_ignore_COMMENT = r"\#.*"
```

[lexer.py:82-83](../SPL/compiler/lexer.py#L82-L83). Estilo Python: `#` hasta
fin de línea. Espacios y tabs no producen token.

#### Saltos de línea

```python
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)
```

[lexer.py:143-145](../SPL/compiler/lexer.py#L143-L145). Mantiene `lineno` al
día para que los errores reporten la línea correcta.

#### Errores

```python
def t_error(t):
    errors.append(f"... Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)
```

[lexer.py:148-152](../SPL/compiler/lexer.py#L148-L152). El lexer **no aborta**:
acumula el error en `errors` y salta el carácter ofensivo.

### 2.4 Estado global y `reset()`

El lexer mantiene cuatro listas/dicts globales:

| Estructura       | Contenido                                |
|------------------|------------------------------------------|
| `symbol_table`   | identificadores vistos                    |
| `number_table`   | literales numéricos únicos                |
| `string_table`   | literales de cadena únicos                |
| `errors`         | errores léxicos                           |

Como el módulo PLY es global, [`reset()`](../SPL/compiler/lexer.py#L160-L166)
limpia esas listas y `lexer.lineno = 1` antes de cada compilación. El
pipeline lo invoca al inicio de cada `run()` ([pipeline.py:52](../SPL/pipeline.py#L52)).

### 2.5 Ejemplo

Fuente:
```c
int x = 3 + 5;
```

Tokens emitidos:
```
LexToken(INT,'int',1,0)
LexToken(ID,'x',1,4)
LexToken(ASSIGN,'=',1,6)
LexToken(NUMBER,3,1,8)
LexToken(PLUS,'+',1,10)
LexToken(NUMBER,5,1,12)
LexToken(SEMI,';',1,13)
```

Para inspeccionar tokens en una compilación real, el pipeline guarda el
volcado en [`<basename>.tokens`](../SPL/pipeline.py#L55) dentro de
`.build_<nombre>/`.

---

## 3. Análisis Sintáctico — [`parser.py`](../SPL/compiler/parser.py)

### 3.1 Herramienta

PLY yacc construye un parser **LALR(1)** a partir de las funciones `p_*`
cuyas docstrings contienen las reglas BNF. La gramática es ambigua para
expresiones binarias, así que se usa una tabla de **precedencias** que
PLY consume directamente:

```python
precedence = (
    ("left",  "OR",   "OR_OP"),
    ("left",  "AND",  "AND_OP"),
    ("right", "NOT",  "BANG"),
    ("left",  "RELOP"),
    ("left",  "PLUS", "MINUS"),
    ("left",  "TIMES","DIVIDE"),
    ("right", "UMINUS"),
)
```

[parser.py:8-16](../SPL/compiler/parser.py#L8-L16). El orden va de menor a
mayor precedencia. `UMINUS` es una precedencia "virtual" que se aplica con
`%prec UMINUS` en la regla `p_expr_uminus`.

PLY genera la tabla LALR la primera vez y la cachea en `parsetab.py`
([parser.py:330-331](../SPL/compiler/parser.py#L330-L331)).

### 3.2 Gramática (resumen)

Símbolo de inicio: `program`.

```
program          : statement_list

statement_list   : statement_list statement
                 | statement

statement        : decl_stmt SEMI
                 | assign_stmt SEMI
                 | return_stmt SEMI
                 | break_stmt SEMI
                 | continue_stmt SEMI
                 | expr_stmt SEMI
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | func_def
                 | struct_def

decl_stmt        : type_spec ID
                 | type_spec ID ASSIGN expr
                 | type_spec ID LBRACKET expr RBRACKET           # int v[10];

assign_stmt      : ID ASSIGN expr
                 | ID DOT ID ASSIGN expr                          # n.value = ...
                 | ID LBRACKET expr RBRACKET ASSIGN expr          # v[i] = ...

if_stmt          : IF LPAREN expr RPAREN block elif_chain else_block
elif_chain       : elif_chain ELIF LPAREN expr RPAREN block
                 | elif_chain ELSE IF LPAREN expr RPAREN block
                 | empty
else_block       : ELSE block | empty

while_stmt       : WHILE LPAREN expr RPAREN block
for_stmt         : FOR LPAREN for_init SEMI expr SEMI assign_stmt RPAREN block

func_def         : VOID ID LPAREN param_list RPAREN block
                 | type_spec ID LPAREN param_list RPAREN block

param            : type_spec ID
                 | type_spec ID LBRACKET RBRACKET                 # parámetro arreglo

struct_def       : STRUCT ID LBRACE struct_body RBRACE [SEMI]

block            : LBRACE statement_list RBRACE
                 | LBRACE RBRACE

expr             : expr (PLUS|MINUS|TIMES|DIVIDE|RELOP|AND_OP|OR_OP) expr
                 | expr AND expr | expr OR expr
                 | NOT expr | BANG expr
                 | MINUS expr               %prec UMINUS
                 | LPAREN expr RPAREN
                 | ID LBRACKET expr RBRACKET            # v[i]
                 | ID LPAREN arg_list RPAREN            # f(args)
                 | ID DOT ID                            # obj.field
                 | NUMBER | STRLIT | ID
```

### 3.3 Forma del AST

Cada regla `p_*` ensambla `p[0]` con una **tupla** cuyo primer elemento es
una etiqueta de nodo. Esto evita definir clases ad-hoc y hace el AST
fácil de imprimir y comparar.

| Nodo                | Forma                                             |
|---------------------|---------------------------------------------------|
| Programa            | `('program', [stmt, stmt, …])`                    |
| Declaración escalar | `('decl', type, name, init_expr_or_None)`         |
| Declaración array   | `('array_decl', type, name, size_expr)`           |
| Asignación          | `('assign', name, expr)`                          |
| Asign. campo        | `('assign_attr', obj, attr, expr)`                |
| Asign. índice       | `('assign_index', name, idx_expr, expr)`          |
| Bloque              | `('block', [stmt, …])`                            |
| If                  | `('if', cond, block, [('elif', c, b)…], else_block)` |
| While               | `('while', cond, block)`                          |
| For                 | `('for', init, cond, update, block)`              |
| Return              | `('return', expr_or_None)`                        |
| Break / continue    | `('break',)` / `('continue',)`                    |
| Función             | `('func_def', name, params, block, ret_type)`     |
| Struct              | `('struct', name, [(type, fname), …])`            |
| Llamada             | `('call', name, [arg_expr, …])`                   |
| Index               | `('index', name, idx_expr)`                       |
| Atributo            | `('attr', obj, field)`                            |
| BinOp               | `('binop', op, lhs, rhs)`                         |
| UnOp                | `('unop', op, expr)`                              |
| Negativo unario     | `('uminus', expr)`                                |
| Literal             | `('num', valor)` / `('str', valor)` / `('id', name)` |

Los **parámetros tipo arreglo** se distinguen con un marcador anidado en
el campo de tipo: `(('array', elem_type), name)`
([parser.py:178-185](../SPL/compiler/parser.py#L178-L185)). El semántico
lo destila a `ArrayType(..., is_pointer=True)` en
[semantic.py:454-456](../SPL/compiler/semantic.py#L454-L456).

### 3.4 Ejemplo

Para
```c
int sum(int a, int b) {
    return a + b;
}
```
el AST es:
```python
('func_def',
  'sum',
  [('int', 'a'), ('int', 'b')],
  ('block',
    [('return', ('binop', '+', ('id', 'a'), ('id', 'b')))]),
  'int')
```

### 3.5 Manejo de errores

```python
def p_error(p):
    if p:
        errors.append(f"... Unexpected token '{p.value}' at line {p.lineno}")
    else:
        errors.append("... Unexpected end of input")
```

[parser.py:320-326](../SPL/compiler/parser.py#L320-L326). El parser **no
implementa modo pánico ni recuperación** explícita: PLY hace su propio
intento de resincronización pero, si la gramática es ambigua después de
un error, suelen aparecer varios `Unexpected token` en cadena.

El pipeline aborta en cuanto `parse_errors` está vacío o no
([pipeline.py:57-62](../SPL/pipeline.py#L57-L62)):

```python
ast, parse_errors = parse(source)
if parse_errors:
    print("\n[ERROR] Parser:")
    for e in parse_errors:
        print(f"  {e}")
    return None
```

---

## 4. Análisis Semántico — [`semantic.py`](../SPL/compiler/semantic.py)

### 4.1 Responsabilidades

El semántico recorre el AST y comprueba todo lo que la gramática no puede
expresar localmente. En concreto:

1. **Declaración antes de uso** — todo identificador (variable, función,
   struct, parámetro) debe estar declarado antes de su referencia.
2. **Redeclaraciones** — error si una variable o parámetro se declara dos
   veces en el mismo ámbito.
3. **Compatibilidad de tipos** — en asignaciones, expresiones, parámetros y
   retornos, aplicando promociones int→float donde proceda.
4. **Aridad y tipo de argumentos** — `f(x, y)` debe coincidir con la firma
   declarada.
5. **Acceso correcto a structs y arreglos** — `obj.field` exige que `obj`
   sea un struct con ese campo; `v[i]` exige `v` arreglo e `i` entero.
6. **break/continue solo dentro de bucles** — controlado con un contador
   `_loop_depth`.
7. **return obligatorio en funciones tipadas** — toda función con tipo de
   retorno distinto de `void` debe contener (al menos) un `return`.

### 4.2 Estructura del recorrido

El analizador hace **dos pasadas** sobre el cuerpo del programa:

```python
def analyze(self, ast):
    ...
    self._collect_top_level(ast[1])   # 1) cabeceras: structs y firmas
    for stmt in ast[1]:                # 2) cuerpo: visitar todos los stmts
        self._visit_stmt(stmt)
    return ast, self.table, self.errors
```

[semantic.py:47-60](../SPL/compiler/semantic.py#L47-L60).

#### Pasada 1 — Cabeceras

[`_collect_top_level`](../SPL/compiler/semantic.py#L63-L90) registra:

- Cada `('struct', name, fields)` como un `StructType` en
  `table.structs`.
- Cada `('func_def', …)` como `Symbol(kind="func")` en `table.functions`.

Esto permite que **una función llame a otra declarada más abajo** en el
archivo (forward reference) sin necesidad de prototipos.

#### Pasada 2 — Recorrido

Despachado por nombre con `getattr(self, f"_stmt_{tag}")` y
`f"_expr_{tag}"`. Cada handler:

1. Hace sus comprobaciones locales.
2. Recorre los hijos relevantes.
3. Devuelve el tipo (si es expresión), que se anota en
   `self.type_annotations[id(expr)]`.

### 4.3 Sistema de tipos — [`types.py`](../SPL/compiler/types.py)

Tipos primitivos representados como **strings**: `"int"`, `"float"`,
`"string"`, `"void"`, más `"unknown"` (placeholder cuando ya se reportó
un error y queremos seguir analizando) y `"any"` (comodín bidireccional).

Tipos compuestos como **clases**:

- [`StructType`](../SPL/compiler/types.py#L25-L35) — `name` + lista
  ordenada de `(field_type, field_name)` y un `field_map` para acceso
  rápido por nombre.
- [`ArrayType`](../SPL/compiler/types.py#L38-L52) — `element_type`,
  `size` (None si es desconocido) y `is_pointer` (True para parámetros
  tipo arreglo, donde el slot guarda la dirección base, no los datos).

Reglas centralizadas:

```python
def is_numeric(t):       # int o float
def common_numeric(a, b):# promoción: si alguno es float → float; si no, int
def is_assignable(target, source):
    # mismo tipo, o int→float, o ArrayType con mismo elem_type, o ANY
```

[types.py:55-82](../SPL/compiler/types.py#L55-L82). Estas tres funciones
son la única fuente de verdad sobre compatibilidad: el semántico **no
debería** decidir tipos por su cuenta.

### 4.4 Tabla de símbolos — [`symbol_table.py`](../SPL/compiler/symbol_table.py)

Implementa una **cadena de ámbitos** (scope chain):

```python
self._scopes = [{}]   # ámbito 0 = global
```

- `enter_scope()` apila un dict vacío al entrar a un bloque/función/for.
- `exit_scope()` lo desapila al salir; nunca destruye el global.
- `lookup(name)` recorre los ámbitos del más interno al global (semántica
  estándar de **shadowing**).
- `declare(symbol)` falla si el nombre ya existe en el ámbito actual.

Estructuras paralelas:

| Tabla         | Contenido                          |
|---------------|------------------------------------|
| `_scopes`     | pila de dicts `name → Symbol`      |
| `structs`     | tipos struct (no son valores)      |
| `functions`   | atajo a las funciones globales     |

Cada [`Symbol`](../SPL/compiler/symbol_table.py#L9-L24) lleva `kind`
(`"var"`, `"param"`, `"func"`, `"struct"`), `type` y un `extra` libre
donde las funciones guardan `params=[(type, name), …]` y `ret_type`.

### 4.5 Reglas de visita por nodo (selección)

#### Declaraciones

- `decl` ([semantic.py:103-114](../SPL/compiler/semantic.py#L103-L114)) —
  declara el símbolo y, si hay `init`, comprueba `is_assignable(vtype, init_type)`.
- `array_decl` ([semantic.py:116-128](../SPL/compiler/semantic.py#L116-L128)) —
  el tamaño debe ser `int`. Si es literal, se guarda en el `ArrayType` para
  que el codegen reserve memoria.

#### Asignaciones

Tres formas diferenciadas: a variable, a campo, a índice
([semantic.py:130-187](../SPL/compiler/semantic.py#L130-L187)). Todas
exigen que el lado izquierdo exista, sea del tipo adecuado, y validan
`is_assignable(target_type, rhs_type)`.

#### Control de flujo

`if`, `while`, `for` exigen condición numérica. `for` introduce un
**ámbito propio** para la variable de inicialización
([semantic.py:247-259](../SPL/compiler/semantic.py#L247-L259)):

```python
self.table.enter_scope()
self._visit_stmt(init)
...
self.table.exit_scope()
```

`break` y `continue` chequean `self._loop_depth > 0`.

#### Funciones

[`_stmt_func_def`](../SPL/compiler/semantic.py#L277-L299) crea un nuevo
ámbito, declara los parámetros como `Symbol(kind="param")`, apila el tipo
de retorno esperado en `_return_types`, y visita el cuerpo. El recorrido
**no** llama a `_visit_block` (eso abriría otro ámbito redundante);
parámetros y locales comparten ámbito.

Antes del recorrido se valida que toda función tipada contenga al menos
un `return`, recorriendo recursivamente con
[`_block_has_return`](../SPL/compiler/semantic.py#L261-L275).

#### Expresiones binarias

[`_expr_binop`](../SPL/compiler/semantic.py#L369-L393) decide el tipo
resultante según la operación:

| Operador               | Resultado                                |
|------------------------|------------------------------------------|
| `+`, `-`, `*`, `/`     | `common_numeric(lhs, rhs)`               |
| `<`, `<=`, `>`, `>=`, `==`, `!=` | `INT` (0/1)                       |
| `and`, `or`, `&&`, `||`| `INT`                                    |

Si los operandos no son numéricos para los aritméticos, se reporta error
y se devuelve `UNKNOWN` para no propagar más errores espurios.

#### Llamadas

[`_expr_call`](../SPL/compiler/semantic.py#L409-L448) reconoce **built-ins**:

- `print` / `out` — aceptan cualquier número de argumentos, devuelven `void`.
- `input` — sin argumentos, devuelve `int`.
- `int(x)`, `float(x)`, `string(x)` — conversiones de tipo.

Para llamadas a funciones del usuario, busca `lookup_function`, comprueba
aridad y aplica `is_assignable(param_type, arg_type)` argumento por
argumento.

### 4.6 Anotaciones por nodo

`self.type_annotations` es un dict `id(nodo) → tipo`. El generador de
código lo recibe como parámetro y lo usa para decidir, por ejemplo, si
emitir `add` o `fadd`, `out` o `fout`. Esto evita reinferir tipos en
codegen y mantiene una sola fuente de verdad.

Por ejemplo, en [codegen.py](../SPL/compiler/codegen.py):

```python
a_type = self.types.get(id(a))
if a_type == STRING:
    self._emit(f"    outs R{ra}    # print string")
elif a_type == FLOAT:
    self._emit(f"    fout R{ra}    # print float")
else:
    self._emit(f"    out R{ra}    # print")
```

### 4.7 Recolección y formato de errores

Los errores se acumulan en `self.errors` con el prefijo coloreado
`SEMANTIC:` para que destaquen en consola/UI:

```python
def _error(self, msg):
    self.errors.append(f"\033[31mSEMANTIC:\033[0m {msg}")
```

[semantic.py:473-474](../SPL/compiler/semantic.py#L473-L474). El semántico
**nunca aborta** ante un error; sigue visitando para reportar la mayor
cantidad posible. La política la fija el orquestador
[`analyze_and_generate`](../SPL/compiler/analyzer.py): si hay errores, no
se llama al codegen.

### 4.8 Ejemplos

#### Error: redeclaración

```c
int main() {
    int x = 1;
    int x = 2;   // duplicada en el mismo ámbito
}
```
Salida:
```
SEMANTIC: variable 'x' ya declarada en este ámbito
```

#### Error: tipo incompatible

```c
int main() {
    string s = 5;   // int no es asignable a string
}
```
Salida:
```
SEMANTIC: no se puede inicializar 's' de tipo string con expresión de tipo int
```

#### Error: aridad de función

```c
int sum(int a, int b) { return a + b; }
int main() {
    print(sum(1));    // falta un argumento
}
```
Salida:
```
SEMANTIC: 'sum' espera 2 argumento(s), recibió 1
```

#### Promoción int→float

```c
int main() {
    float z = 3 + 0.5;    // OK: 3 se promueve a float
    print(z);             // codegen emite fout porque z es float
}
```
No produce errores. La anotación de tipo del binop guardada en
`type_annotations` permite que codegen elija `fadd`+`fi2f` en lugar de
`add`.

---

## 5. Punto de unión: [`analyzer.py`](../SPL/compiler/analyzer.py)

```python
def analyze_and_generate(ast, *, org=0):
    sa = semantic.SemanticAnalyzer()
    annotated_ast, table, errors = sa.analyze(ast)

    asm_text = None
    if not errors:
        try:
            asm_text = codegen.generate(
                annotated_ast, table, sa.type_annotations, org=org
            )
        except codegen.CodeGenError as e:
            errors.append(f"CODEGEN: {e}")

    return {"asm": asm_text, "errors": errors, "symbol_table": table}
```

Tres invariantes a notar:

1. **Solo se genera código si no hay errores semánticos.** Esto evita que
   codegen tropiece con tipos `UNKNOWN`.
2. La tabla de símbolos final (`table`) y el dict de tipos
   (`sa.type_annotations`) viajan juntos al codegen — el codegen depende
   de ambos.
3. Los errores de codegen también se vuelcan en el mismo `errors` para
   que el pipeline los muestre con un único formato.

---

## 6. Cómo inspeccionar cada fase desde la UI

[`ui/atlas_ide.py`](../ui/atlas_ide.py) muestra el resultado de cada
etapa en un panel:

| Panel                    | Archivo                        | Generado por           |
|--------------------------|--------------------------------|------------------------|
| 1. Código fuente (.atl)  | el archivo cargado             | usuario                |
| 2. Preprocesado (.pre)   | `.build_<n>/<n>.pre`           | preprocesador          |
| 3. Ensamblado (.asm)     | `.build_<n>/<n>.asm`           | codegen tras léxico+sintáctico+semántico |
| 4. Reubicable (.binReloc)| `.build_<n>/<n>.binReloc`      | ensamblador            |
| 5. Binario final (.bin)  | `.build_<n>/<n>.bin`           | enlazador              |

Los **tokens** se vuelcan en `.build_<n>/<n>.tokens`
([pipeline.py:55](../SPL/pipeline.py#L55)) — útil para depurar el lexer
sin abrir Python.

Los errores de cada fase aparecen en el panel "Log de compilación / sistema"
de la UI, ya que el pipeline canaliza todo a `stdout` y la UI lo redirige
a ese panel mientras dura la compilación.
