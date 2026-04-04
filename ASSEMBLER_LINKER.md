# Ensamblador y Enlazador-Cargador — Máquina sy_00

Documentación del pipeline completo de ensamblado y enlace para la
máquina virtual Von Neumann **sy_00**.

---

## Tabla de contenidos

1. [Visión general del pipeline](#1-visión-general-del-pipeline)
2. [assembly_lex.py — Ensamblador con LEX](#2-assembly_lexpy--ensamblador-con-lex)
3. [linker_loader.py — Enlazador-Cargador](#3-linker_loaderpy--enlazador-cargador)
4. [Cómo funciona PLY/lex internamente](#4-cómo-funciona-plylex-internamente)
5. [Directivas del enlazador](#5-directivas-del-enlazador)
6. [Uso desde línea de comandos](#6-uso-desde-línea-de-comandos)
7. [Ejemplo completo paso a paso](#7-ejemplo-completo-paso-a-paso)
8. [Estado actual de la máquina](#8-estado-actual-de-la-máquina)

---

## 1. Visión general del pipeline

```
 .asm ──► PREPROCESADOR ──► LEXER (PLY) ──► ENSAMBLADOR 2 pasadas ──► ObjectModule
                                                                            │
          varios .asm ─────────────────────────────────────────────────── ───┤
                                                                            ▼
                                                                       ENLAZADOR
                                                                            │
                                                                            ▼
                                                                       CARGADOR ──► .bin
```

| Etapa | Archivo | Descripción |
|-------|---------|-------------|
| Preprocesador | `assembly_lex.py` | Expande `#include` y `#define` |
| Lexer | `assembly_lex.py` / `linker_loader.py` | Tokeniza líneas usando PLY/lex |
| Ensamblador | `assembly_lex.py` | Dos pasadas: tabla de símbolos + codificación |
| Enlazador | `linker_loader.py` | Resuelve símbolos globales/externos, reubica direcciones |
| Cargador | `linker_loader.py` | Genera binario final (1 byte por línea) |

---

## 2. assembly_lex.py — Ensamblador con LEX

### 2.1. Preprocesador

Expande directivas antes de que el lexer las vea:

| Directiva | Efecto |
|-----------|--------|
| `#include <archivo>` | Inserta el contenido del archivo referenciado |
| `#define NOMBRE VALOR` | Sustituye textualmente `NOMBRE` por `VALOR` en líneas posteriores |

Soporta hasta 10 niveles de `#include` anidado.

### 2.2. Analizador léxico (PLY/lex)

El lexer reconoce las siguientes **categorías léxicas** (tokens):

| Token | Patrón | Ejemplo | Valor resultante |
|-------|--------|---------|------------------|
| `INSTRUCCION` | Mnemonic válido | `mov`, `add`, `jmp` | string lowercase |
| `REGISTRO` | `r0`…`r15` | `R8` | int (8) |
| `NUMERO_HEX` | `0x[0-9A-Fa-f]+` | `0x1A3F` | int |
| `NUMERO_BIN` | `0b[01]+` | `0b1010` | int |
| `NUMERO_FLOAT` | `[0-9]+.[0-9]+` | `3.14` | float |
| `NUMERO_INT` | `[0-9]+` | `42` | int |
| `ETIQUETA_DEF` | `nombre:` | `LOOP:` | string sin `:` |
| `IDENTIFICADOR` | `[A-Za-z_]\w*` | `LOOP` | string |
| `DIRECTIVA` | `#include ...` | — | string completo |
| `COMA` | `,` | — | — |
| `COMENTARIO` | `# ...` | descartado | — |

**Orden de prioridad**: las reglas de función se evalúan por longitud de docstring
(mayor primero); las reglas de string se evalúan por longitud del patrón.
Esto garantiza que `0x1A` se reconozca como `NUMERO_HEX` antes que como `NUMERO_INT`.

### 2.3. Ensamblador de dos pasadas

**Pasada 1 — Tabla de símbolos:**
Recorre el código línea por línea; cada instrucción ocupa 8 bytes (64 bits).
Las etiquetas (`nombre:`) se registran con su dirección (posición × 8).

**Pasada 2 — Codificación:**
Cada instrucción se codifica según su formato (F1–F5) usando los encoders
correspondientes (`encode_f1` … `encode_f5`).

### 2.4. Formatos de instrucción

Todas las instrucciones son de **64 bits** (8 bytes). Existen 5 formatos:

#### F1 — Aritmético/Lógico (`pre = 0001`)
```
[pre(4)][opcode(10)][modo(6)][rd(4)][r1(4)][r2(4)][inmediato(32)]
```
Instrucciones: `mov`, `add`, `sub`, `mul`, `div`, `inc`, `dec`, `neg`,
`and`, `or`, `xor`, `not`, `shl`, `shr`, `rol`, `ror`, `cmp`, `test`,
`push`, `pop`, `xchg`, `mod`, `addi`, `subi`, `muli`, `divi`, `modi`

#### F2 — Memoria (`pre = 0010`)
```
[pre(4)][opcode(8)][modo(6)][r1(4)][base(4)][index(4)][scale(2)][offset(32)]
```
Instrucciones: `load`, `store`, `lea`

> **Nota**: LOAD y STORE operan sobre **1 byte** (8 bits), no sobre 8 bytes.

#### F3 — Salto (`pre = 0011`)
```
[pre(4)][opcode(10)][modo(6)][r1(4)][r2(4)][offset(32)][flags(4)]
```
Instrucciones: `jmp`, `jz`, `jnz`, `jc`, `jn`, `call`, `jg`, `jge`, `jne`,
`jmpr`, `jzr`, `jnzr`, `jcr`, `jnr`

> **Nota importante sobre flags**:
> - `jnz` = salta si N **o** Z están activos (no es "not zero")
> - `jne` = salta si Z **no** está activo (este es el "not equal / not zero")

#### F4 — Control (`pre = 0000`)
```
[pre(4)][opcode(6)][modo(6)][inmediato(32)][padding(16)]
```
Instrucciones: `nop`, `halt`, `inti`, `ret`, `iret`

#### F5 — FPU (`pre = 0100`)
```
[pre(4)][opcode(10)][modo(6)][rd(4)][r1(4)][r2(4)][inmediato(32)]
```
Instrucciones: `fmov`, `fadd`, `fsub`, `fmul`, `fdiv`, `fcmp`, `fabs`,
`fneg`, `fsqrt`, `fi2f`, `ff2i`

---

## 3. linker_loader.py — Enlazador-Cargador

### 3.1. Motivación

Cuando un programa se divide en varios archivos `.asm` (librerías reutilizables,
módulos independientes), cada archivo se ensambla por separado con direcciones
relativas empezando en 0. El enlazador se encarga de:

- **Unificar** el código de todos los módulos en un espacio de memoria contiguo
- **Resolver** referencias entre módulos (símbolos globales/externos)
- **Reubicar** direcciones para que apunten a la posición final correcta

### 3.2. Pipeline de 5 fases

#### Fase 1 — Ensamblado individual (`ensamblar_modulo`)

Cada archivo `.asm` pasa por:
1. Lectura del fuente
2. Preprocesamiento (`#include`, `#define`)
3. Extracción de directivas `.global` / `.extern`
4. Pasada 1: tabla de símbolos locales (etiqueta → dirección relativa)
5. Pasada 2: codificación de instrucciones + registro de reubicaciones

Resultado: un `ObjectModule` con código binario, símbolos y reubicaciones.

#### Fase 2 — Layout (`enlazar`, paso 1)

Los módulos se colocan secuencialmente en memoria a partir de la dirección 0:

```
┌──────────────────┐ 0x0000
│   Módulo 1       │
│   (N₁ bytes)     │
├──────────────────┤ 0x0000 + N₁
│   Módulo 2       │
│   (N₂ bytes)     │
├──────────────────┤ 0x0000 + N₁ + N₂
│   Módulo 3       │
│   ...            │
└──────────────────┘
```

El **primer archivo** pasado en la línea de comandos queda al inicio de la memoria
y es donde comienza la ejecución (PC = 0). Por eso el módulo `main` debe pasarse
primero.

#### Fase 3 — Tabla de símbolos global (`enlazar`, paso 2-3)

Se construye una tabla global unificada:
- Símbolos `SYM_GLOBAL`: accesibles desde cualquier módulo
- Símbolos `SYM_LOCAL`: prefijados con `modulo::nombre` para evitar colisiones
- Símbolos `SYM_EXTERN`: se buscan en la tabla global; si no se encuentran, se
  reporta error

Se verifican errores:
- Símbolo global duplicado (definido en más de un módulo)
- Símbolo externo sin resolución (no existe en ningún módulo)

#### Fase 4 — Reubicación (`enlazar`, paso 4)

Para cada instrucción que referencia un símbolo se calcula la dirección final:

- **Dirección absoluta** (`REL_ABS`): `patch_value = dirección_final_del_símbolo`
- **Dirección relativa** (`REL_REL`): `patch_value = dir_símbolo - dir_instrucción`

La función `_parchear_instruccion` reemplaza el campo de offset/inmediato
según el formato:

| Formato | Bits parcheados | Campo |
|---------|----------------|-------|
| F1 | bits[32:64] | inmediato (32 bits) |
| F2 | bits[32:64] | offset (32 bits) |
| F3 | bits[28:60] | offset (32 bits) |
| F4 | bits[16:48] | inmediato (32 bits) |
| F5 | bits[32:64] | inmediato (32 bits) |

#### Fase 5 — Cargador (`generar_binario`)

El código enlazado se escribe en formato binario de texto:
- Cada instrucción de 64 bits se divide en 8 bytes
- Cada byte (8 bits) se escribe en una línea
- El archivo resultante `.bin` es cargable directamente por `main.py`

### 3.3. Lexer extendido

El linker tiene su propio lexer PLY que extiende el del ensamblador con dos
tokens adicionales:

| Token | Patrón | Descripción |
|-------|--------|-------------|
| `DIR_GLOBAL` | `.global` | Marca un símbolo como exportado |
| `DIR_EXTERN` | `.extern` | Declara una referencia a símbolo de otro módulo |

También reconoce `#define` además de `#include` en la regla de `DIRECTIVA`.

### 3.4. Estructura ObjectModule

```python
class ObjectModule:
    nombre      : str               # Nombre del archivo fuente
    code        : list[str]         # Lista de strings binarios de 64 bits
    symbols     : dict              # {nombre: {address, binding}}
    relocations : list[dict]        # [{offset, symbol, rel_type, instr_index, formato}]
    size        : int               # Tamaño total en bytes
```

Cada reubicación contiene:
- `offset`: dirección relativa de la instrucción dentro del módulo
- `symbol`: nombre del símbolo referenciado
- `rel_type`: `REL_ABS` (0) o `REL_REL` (1)
- `instr_index`: índice en la lista `code`
- `formato`: formato de instrucción (1–5)
- `opcode`: código de operación

---

## 4. Cómo funciona PLY/lex internamente

**PLY** (Python Lex-Yacc) es una implementación de las herramientas clásicas
lex/yacc para Python. El módulo `ply.lex` implementa el analizador léxico.

### 4.1. Definición de tokens

Los tokens se definen como:
- **Variables de módulo** con nombre `t_NOMBRE` para patrones simples (ej: `t_COMA = r','`)
- **Funciones** con nombre `t_NOMBRE` cuyo docstring es el regex (ej: `def t_REGISTRO(t): r'...'`)

### 4.2. Prioridad de reglas

PLY determina el orden de evaluación así:
1. **Funciones**: se ordenan por la longitud del patrón regex en el docstring
   (más largo primero). Esto asegura que `0x1A` se reconozca como hex antes que como int.
2. **Strings**: se ordenan por longitud del string (más largo primero).
3. Las funciones siempre tienen prioridad sobre las strings.

### 4.3. Flujo de tokenización

```
Texto fuente
    │
    ▼
lex.input(texto)           ← alimenta el lexer con el texto
    │
    ▼
while tok = lex.token():   ← extrae tokens uno por uno
    │
    ├── Intenta cada regex en orden de prioridad
    ├── El primer match genera el token con (type, value, lineno, lexpos)
    ├── Si es función-token, puede modificar valor o tipo (ej: INSTRUCCION_O_ID)
    ├── Si la función no hace return, el token se descarta (ej: COMENTARIO)
    └── t_error() se invoca si ningún patrón reconoce el carácter
```

### 4.4. Tokens especiales

- `t_ignore`: string de caracteres a ignorar silenciosamente (espacios, tabs)
- `t_error(t)`: función invocada cuando ningún patrón reconoce un carácter
- `t_NEWLINE`: maneja el conteo de líneas (`t.lexer.lineno`)

### 4.5. Constructor

```python
lexer = lex.lex(debug=False, errorlog=lex.NullLogger(), outputdir='/tmp')
```

PLY inspecciona las variables y funciones del módulo que siguen la convención
`t_*`, construye un autómata con los regexes compilados, y retorna un objeto
lexer listo para usar.

---

## 5. Directivas del enlazador

### `.global NOMBRE`

Exporta un símbolo (etiqueta) para que otros módulos puedan referenciarlo.
Se coloca al inicio del archivo, antes del código.

```asm
.global FACTORIAL

FACTORIAL:
    mov  R1, 1
    ...
    ret
```

### `.extern NOMBRE`

Declara que el módulo necesita un símbolo definido en otro archivo.
El enlazador resolverá la dirección real durante el enlace.

```asm
.extern FACTORIAL

MAIN:
    mov  R0, 5
    call FACTORIAL     # el enlazador escribe aquí la dirección real
    halt
```

### Reglas

- Todo módulo que define una función usable desde fuera **debe** tener `.global`
- Todo módulo que llama funciones de otro **debe** declarar `.extern`
- Un programa enlazado **debe** terminar con `halt` (generalmente en el `main`)
- El módulo `main` debe ser el **primer archivo** en la línea de comandos
  (la ejecución empieza en dirección 0 = inicio del primer módulo)

---

## 6. Uso desde línea de comandos

### Ensamblador simple (un solo archivo)

```bash
python assembly/assembly_lex.py data/ejemplo.asm data/ejemplo.bin
```

### Enlazador-cargador (múltiples archivos)

```bash
# Enlazar y generar binario
python assembly/linker_loader.py data/main_tres.asm data/lib_euclides.asm \
    data/lib_factorial.asm data/lib_fibo.asm -o data/tres.bin

# Mostrar análisis léxico (tokens reconocidos)
python assembly/linker_loader.py data/main_tres.asm data/lib_euclides.asm --lexico

# Generar mapa de enlace (JSON con direcciones y símbolos)
python assembly/linker_loader.py data/main_tres.asm data/lib_euclides.asm \
    data/lib_factorial.asm data/lib_fibo.asm --mapa -o data/tres.bin
```

### Ejecutar el binario en la máquina

```bash
python main.py
# En la interfaz: cargar el archivo .bin generado
```

### Opciones del enlazador

| Opción | Descripción |
|--------|-------------|
| `-o <archivo>` | Ruta del binario de salida |
| `--lexico` | Muestra los tokens reconocidos por el lexer para cada archivo |
| `--mapa` | Genera un archivo `.map.json` con las direcciones y símbolos |

---

## 7. Ejemplo completo paso a paso

### Archivos fuente

**`lib_euclides.asm`** — exporta `GCD`:
```asm
.global GCD

GCD:
GCD_LOOP:
    cmp  R0, R1
    jz   GCD_END
    jn   GCD_B_MAYOR
GCD_A_MAYOR:
    sub  R0, R1
    jmp  GCD_LOOP
GCD_B_MAYOR:
    sub  R1, R0
    jmp  GCD_LOOP
GCD_END:
    ret
```

**`main_tres.asm`** — importa y usa `GCD`, `FACTORIAL`, `FIBONACCI`:
```asm
.extern GCD
.extern FACTORIAL
.extern FIBONACCI

MAIN:
    mov  R0, 48
    mov  R1, 18
    call GCD
    mov  R8, R0        # R8 = gcd(48,18) = 6
    ...
    halt
```

### Comando de enlace

```bash
python assembly/linker_loader.py data/main_tres.asm data/lib_euclides.asm \
    data/lib_factorial.asm data/lib_fibo.asm -o data/tres.bin --mapa
```

### Lo que sucede internamente

1. **Ensambla `main_tres.asm`**: genera ObjectModule con `call GCD` apuntando a
   dirección 0 (placeholder). Registra reubicación para `GCD`, `FACTORIAL`, `FIBONACCI`.

2. **Ensambla `lib_euclides.asm`**: genera ObjectModule con `GCD` en dirección 0
   relativa. Marca símbolo `GCD` como `SYM_GLOBAL`.

3. **Layout**: main_tres queda en `0x0000`, lib_euclides en `0x00C8` (por ejemplo),
   lib_factorial en `0x0110`, lib_fibo en `0x0148`.

4. **Tabla global**: `GCD → 0x00C8`, `FACTORIAL → 0x0110`, `FIBONACCI → 0x0148`.

5. **Reubicación**: la instrucción `call GCD` en main_tres se parchea con la
   dirección absoluta `0x00C8` en el campo offset de F3 (bits[28:60]).

6. **Binario**: se escribe `tres.bin` con 1 byte por línea, listo para cargar.

### Resultados verificados

| Cómputo | Resultado | Registro |
|---------|-----------|----------|
| gcd(48, 18) | 6 | R8 |
| gcd(100, 75) | 25 | R9 |
| 5! | 120 | R10 |
| 7! | 5040 | R11 |
| fib(7) | 13 | R12 |
| fib(10) | 55 | R13 |

---

## 8. Estado actual de la máquina

### Arquitectura

| Componente | Descripción |
|------------|-------------|
| Tipo | Von Neumann (memoria unificada código + datos) |
| Palabra | 64 bits |
| Direcciones | 32 bits |
| RAM | 6048 bytes (0x0000 – 0x179F), byte-addressable |
| Registros | R0–R15 (64 bits, propósito general) |
| PC | 32 bits, inicia en 0 |
| SP | Inicia en 5000 |
| Flags | Z (zero), N (negativo), C (carry), V (overflow) |
| Instrucciones | 64 bits, 5 formatos (F1–F5) |
| FPU | Formato F5 con operaciones flotantes |

### Módulos del simulador

| Archivo | Función |
|---------|---------|
| `main.py` | Punto de entrada, carga binario en RAM y ejecuta |
| `CPU/cpu.py` | Ciclo fetch-decode-execute |
| `CPU/ram.py` | Memoria principal (6048 bytes) |
| `CPU/registers.py` | Banco de registros y flags |
| `CPU/instructions.py` | Implementación de cada instrucción |
| `CPU/buses.py` | Buses de datos, direcciones y control |
| `assembly/assembly_lex.py` | Ensamblador con PLY/lex (un archivo) |
| `assembly/linker_loader.py` | Enlazador-cargador multi-archivo |
| `interfaz/interfaz.py` | Interfaz gráfica |
| `stdlib/vecmat.asm` | Librería estándar de vectores/matrices |

### Librerías de ejemplo (enlazables)

| Archivo | Exporta | Descripción |
|---------|---------|-------------|
| `data/lib_euclides.asm` | `GCD` | GCD por restas sucesivas |
| `data/lib_factorial.asm` | `FACTORIAL` | Factorial iterativo |
| `data/lib_fibo.asm` | `FIBONACCI` | Fibonacci iterativo |
| `data/mod_mergesort.asm` | `MERGESORT` | MergeSort bottom-up en memoria |

### Programas de ejemplo

| Archivo | Descripción |
|---------|-------------|
| `data/main_tres.asm` | Main que enlaza euclides + factorial + fibonacci |
| `data/main_test_link.asm` | Main que enlaza euclides + mergesort |
| `data/ejemplo.asm` | Programa de ejemplo básico |
| `data/sqrt_heron.asm` | Raíz cuadrada por método de Herón |
| `data/test_vecmat.asm` | Pruebas de vectores/matrices |

### Capacidad de enlace

La RAM tiene 6048 bytes. El enlazador coloca todos los módulos secuencialmente
desde la dirección 0. Tamaño máximo del binario enlazado: **6048 bytes**
(756 instrucciones). No hay límite artificial en la cantidad de archivos a
enlazar, solo el espacio disponible en RAM.
