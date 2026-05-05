import ply.yacc as yacc

from toolchain.compiler.lexical_analysis.lexer import errors, lexer, tokens

# ------------------ PRECEDENCIA ------------------
precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("right", "NOT"),
    ("left", "LOGOP"),
    ("left", "RELOP"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "UMINUS"),
)

# ------------------ PROGRAMA ------------------


def p_program(p):
    """program : statement_list"""
    p[0] = ("program", p[1])


def p_statement_list(p):
    """statement_list : statement_list statement
    | statement"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


# ------------------ STATEMENTS ------------------


def p_statement(p):
    """statement : decl_stmt SEMI
    | assign_stmt SEMI
    | return_stmt SEMI
    | break_stmt SEMI
    | continue_stmt SEMI
    | expr_stmt SEMI
    | if_stmt
    | while_stmt
    | for_stmt
    | func_def
    | struct_def"""
    p[0] = p[1]


# ------------------ DECLARACIONES ------------------


def p_decl_stmt(p):
    """decl_stmt : type_spec ID
    | type_spec ID ASSIGN expr
    | type_spec ID LBRACKET expr RBRACKET"""
    if len(p) == 3:
        p[0] = ("decl", p[1], p[2], None)
    elif len(p) == 5:
        p[0] = ("decl", p[1], p[2], p[4])
    else:
        p[0] = ("array_decl", p[1], p[2], p[4])


# ------------------ ASIGNACIONES ------------------


def p_assign_stmt(p):
    """assign_stmt : ID ASSIGN expr
    | ID DOT ID ASSIGN expr
    | ID LBRACKET expr RBRACKET ASSIGN expr"""
    if len(p) == 4:
        p[0] = ("assign", p[1], p[3])
    elif len(p) == 6:
        p[0] = ("assign_attr", p[1], p[3], p[5])
    else:
        p[0] = ("assign_index", p[1], p[3], p[6])


def p_expr_stmt(p):
    """expr_stmt : expr"""
    p[0] = ("expr_stmt", p[1])


def p_return_stmt(p):
    """return_stmt : RETURN expr
    | RETURN"""
    p[0] = ("return", p[2] if len(p) == 3 else None)


def p_break_stmt(p):
    """break_stmt : BREAK"""
    p[0] = ("break",)


def p_continue_stmt(p):
    """continue_stmt : CONTINUE"""
    p[0] = ("continue",)


# ------------------ IF / ELSE IF / ELSE ------------------


def p_if_stmt(p):
    """if_stmt : IF LPAREN expr RPAREN block elif_chain else_block"""
    #             1    2    3    4     5      6          7
    p[0] = ("if", p[3], p[5], p[6], p[7])


def p_elif_chain(p):
    """elif_chain : elif_chain ELIF LPAREN expr RPAREN block
    | elif_chain ELSE IF LPAREN expr RPAREN block
    | empty"""
    if len(p) == 7:
        p[0] = p[1] + [("elif", p[4], p[6])]
    elif len(p) == 8:
        p[0] = p[1] + [("elif", p[5], p[7])]
    else:
        p[0] = []


def p_else_block(p):
    """else_block : ELSE block
    | empty"""
    p[0] = ("else", p[2]) if len(p) == 3 else None


# ------------------ WHILE ------------------


def p_while_stmt(p):
    """while_stmt : WHILE LPAREN expr RPAREN block"""
    p[0] = ("while", p[3], p[5])


# ------------------ FOR ------------------


def p_for_stmt(p):
    """for_stmt : FOR LPAREN for_init SEMI expr SEMI assign_stmt RPAREN block"""
    p[0] = ("for", p[3], p[5], p[7], p[9])


def p_for_init(p):
    """for_init : decl_stmt
    | assign_stmt"""
    p[0] = p[1]


# ------------------ FUNCIONES ------------------


def p_func_def_void(p):
    """func_def : VOID ID LPAREN param_list RPAREN block"""
    p[0] = ("func_def", p[2], p[4], p[6], "void")


def p_func_def_typed(p):
    """func_def : type_spec ID LPAREN param_list RPAREN block"""
    block = p[6]
    if not _block_has_return(block):
        errors.append(
            f"\033[31mSEMANTIC:\033[0m Function '{p[2]}' with return type '{p[1]}' "
            f"must have a return statement"
        )
    p[0] = ("func_def", p[2], p[4], p[6], p[1])


def _block_has_return(block):
    """Revisa recursivamente si un bloque contiene al menos un return."""
    if not block or block[0] != "block":
        return False
    stmts = block[1]
    for stmt in stmts:
        if stmt is None:
            continue
        if stmt[0] == "return":
            return True
        # Buscar dentro de bloques anidados
        if stmt[0] in ("if", "while", "for"):
            for part in stmt[1:]:
                if isinstance(part, tuple) and part[0] == "block":
                    if _block_has_return(part):
                        return True
    return False


def p_param_list(p):
    """param_list : param_list COMA param
    | param
    | empty"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif p[1] is None:
        p[0] = []
    else:
        p[0] = [p[1]]


def p_param(p):
    """param : type_spec ID"""
    p[0] = (p[1], p[2])


# ------------------ TIPOS ------------------


def p_type_spec(p):
    """type_spec : INT
    | FLOAT
    | STRING_TYPE
    | ID"""
    p[0] = p[1]


# ------------------ STRUCT ------------------


def p_struct_def(p):
    """struct_def : STRUCT ID LBRACE struct_body RBRACE SEMI
    | STRUCT ID LBRACE struct_body RBRACE"""
    p[0] = ("struct", p[2], p[4])


def p_struct_body(p):
    """struct_body : struct_body type_spec ID SEMI
    | empty"""
    if len(p) == 5:
        p[0] = p[1] + [(p[2], p[3])]
    else:
        p[0] = []


# ------------------ BLOQUE ------------------


def p_block(p):
    """block : LBRACE statement_list RBRACE
    | LBRACE RBRACE"""
    p[0] = ("block", p[2] if len(p) == 4 else [])


# ------------------ EXPRESIONES ------------------


def p_expr_binop(p):
    """expr : expr PLUS   expr
    | expr MINUS  expr
    | expr TIMES  expr
    | expr DIVIDE expr
    | expr RELOP  expr
    | expr LOGOP  expr"""
    p[0] = ("binop", p[2], p[1], p[3])


def p_expr_and(p):
    """expr : expr AND expr"""
    p[0] = ("binop", "and", p[1], p[3])


def p_expr_or(p):
    """expr : expr OR expr"""
    p[0] = ("binop", "or", p[1], p[3])


def p_expr_not(p):
    """expr : NOT expr"""
    p[0] = ("unop", "not", p[2])


def p_expr_uminus(p):
    """expr : MINUS expr %prec UMINUS"""
    p[0] = ("uminus", p[2])


def p_expr_group(p):
    """expr : LPAREN expr RPAREN"""
    p[0] = p[2]


def p_expr_index(p):
    """expr : ID LBRACKET expr RBRACKET"""
    p[0] = ("index", p[1], p[3])


def p_expr_number(p):
    """expr : NUMBER"""
    p[0] = ("num", p[1])


def p_expr_strlit(p):
    """expr : STRLIT"""
    p[0] = ("str", p[1])


def p_expr_id(p):
    """expr : ID"""
    p[0] = ("id", p[1])


def p_expr_attr(p):
    """expr : ID DOT ID"""
    p[0] = ("attr", p[1], p[3])


def p_expr_call(p):
    """expr : ID LPAREN arg_list RPAREN"""
    p[0] = ("call", p[1], p[3])


def p_arg_list(p):
    """arg_list : arg_list COMA expr
    | expr
    | empty"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif p[1] is None:
        p[0] = []
    else:
        p[0] = [p[1]]


# ------------------ EMPTY / ERROR ------------------


def p_empty(p):
    """empty :"""
    p[0] = None


def p_error(p):
    if p:
        errors.append(
            f"\033[31mPARSER:\033[0m Unexpected token '{p.value}' at line {p.lineno}"
        )
    else:
        errors.append("\033[31mPARSER:\033[0m Unexpected end of input")


# ------------------ INSTANCIA ------------------
parser = yacc.yacc()


# ------------------ API PÚBLICA ------------------
def parse(source: str):
    lexer.lineno = 1
    ast = parser.parse(source, lexer=lexer)
    return ast, errors
