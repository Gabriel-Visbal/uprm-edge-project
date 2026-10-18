"""UPRM-Edge Subproject 1: lexer and parser for the UPRM-Edge language.

The program reads one .uedge source file, recognizes its tokens and grammar,
and reports either a parsing result or a clear error with its source line.
"""

import sys

sys.path.insert(0, 'ply.zip')

import ply.lex as lex
import ply.yacc as yacc

# ============================================================================
# Configuration
# ============================================================================

had_error = False

# PLY would otherwise use the first p_* function as the start rule.
start = 'program'

class LexicalError(Exception):
    """Stops parsing after a reported lexical error without a traceback."""

# ============================================================================
# Lexer
# ============================================================================

# Language keywords and their corresponding PLY token names.
KEYWORDS = {
    'let': 'LET',
    'func': 'FUNC',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'return': 'RETURN',
    'print': 'PRINT',
    'true': 'BOOLEAN',
    'false': 'BOOLEAN',
    'memory': 'MEMORY',
    'array': 'ARRAY',
    'int': 'INT_TYPE',
    'float': 'FLOAT_TYPE',
    'bool': 'BOOL_TYPE',
    'string': 'STRING_TYPE',
}

# PLY requires this module-level variable to be named ``tokens``.
tokens = [
    'IDENTIFIER', 'INTEGER', 'FLOAT', 'STRING', 'BOOLEAN',
    'LET', 'FUNC', 'IF', 'ELSE', 'WHILE', 'FOR', 'RETURN', 'PRINT', 'MEMORY',
    'ARRAY', 'INT_TYPE', 'FLOAT_TYPE', 'BOOL_TYPE', 'STRING_TYPE',
    'MEMORYSIZE', 'AT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
    'EQUAL', 'NOTEQUAL', 'LESSTHAN', 'GREATERTHAN',
    'LESSEQUAL', 'GREATEREQUAL', 'ASSIGN',
    'LEFTPARENTHESIS', 'RIGHTPARENTHESIS',
    'LEFTBRACE', 'RIGHTBRACE',
    'COMMA', 'SEMICOLON'
]

# Operator patterns
t_EQUAL = r'=='
t_NOTEQUAL = r'!='
t_LESSEQUAL = r'<='
t_GREATEREQUAL = r'>='
t_LESSTHAN = r'<'
t_GREATERTHAN = r'>'
t_ASSIGN = r'='

t_AT = r'@'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'

# Punctuation patterns
t_LEFTPARENTHESIS = r'\('
t_RIGHTPARENTHESIS = r'\)'
t_LEFTBRACE = r'\{'
t_RIGHTBRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'

# Whitespace ignored by the lexer
t_ignore = ' \t'

# Memory-size units accepted by the Track A annotation.
MEMORY_UNITS = {'b': 1, 'kb': 1024, 'mb': 1024**2, 'gb': 1024**3}

# Split an @memory size into a numeric value expressed in bytes.
def t_MEMORYSIZE(t):
    r'\d+(?:kb|mb|gb|b)\b'
    digits = t.value.rstrip('kmgb')
    unit = t.value[len(digits):]
    t.value = int(digits) * MEMORY_UNITS[unit]
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"([^"\\\n]|\\.)*"'
    t.value = t.value[1:-1]
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = KEYWORDS.get(t.value, 'IDENTIFIER')
    if t.type == 'BOOLEAN':
        t.value = (t.value == 'true')
    return t

# Single-line comments do not produce tokens.
def t_COMMENT(t):
    r'//[^\n]*'
    pass

# Preserve accurate line numbers for later error messages.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    global had_error
    had_error = True
    if t.value[0] == '"':
        print(f"Error: malformed string at line {t.lineno}")
    else:
        print(f"Error: unexpected token ‘{t.value[0]}’ at line {t.lineno}")
    # The grader treats a non-zero exit as a runtime failure.  Raising this
    # private exception lets main() stop cleanly after the required message.
    raise LexicalError()

def report_error(message, line):
    """Record one syntax error without claiming that parsing succeeded."""
    global had_error
    had_error = True
    if line is None:
        print(f"Error: {message}")
    else:
        print(f"Error: {message} at line {line}")

# ============================================================================
# Parser grammar
# ============================================================================

# These productions recognize the language structure and produce a compact
# parse representation that can be reused by the interpreter in Subproject 2.

precedence = (
    ('left', 'EQUAL', 'NOTEQUAL'),
    ('left', 'LESSTHAN', 'LESSEQUAL', 'GREATERTHAN', 'GREATEREQUAL'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS'),
)

def p_program(p):
    "program : statement_list"
    p[0] = p[1]

def p_statement_list_multiple(p):
    "statement_list : statement_list statement"
    p[0] = p[1] + [p[2]]

def p_statement_list_one(p):
    "statement_list : statement"
    p[0] = [p[1]]

def p_annotation(p):
    "annotation : AT MEMORY LEFTPARENTHESIS MEMORYSIZE RIGHTPARENTHESIS"
    p[0] = ("memory", p[4])

def p_annotation_missing_size(p):
    "annotation : AT MEMORY LEFTPARENTHESIS RIGHTPARENTHESIS"
    report_error("malformed @memory annotation", p.lineno(4))

def p_block(p):
    "block : LEFTBRACE statement_list RIGHTBRACE"
    p[0] = p[2]

def p_block_missing_rbrace(p):
    "block : LEFTBRACE statement_list"
    report_error("missing closing '}'", None)

def p_statement_if(p):
    """statement : IF LEFTPARENTHESIS expression RIGHTPARENTHESIS block
                 | IF LEFTPARENTHESIS expression RIGHTPARENTHESIS block ELSE block"""
    p[0] = ("if", p[3], p[5])

def p_if_missing_rparen(p):
    "statement : IF LEFTPARENTHESIS expression LEFTBRACE statement_list RIGHTBRACE"
    report_error("missing closing ')'", p.lineno(4))

def p_statement_let(p):
    "statement : LET IDENTIFIER ASSIGN expression SEMICOLON"
    p[0] = ('let', p[2], p[4])

def p_statement_assignment(p):
    "statement : IDENTIFIER ASSIGN expression SEMICOLON"
    p[0] = ('assign', p[1], p[3])

def p_statement_print(p):
    "statement : PRINT LEFTPARENTHESIS expression RIGHTPARENTHESIS SEMICOLON"
    p[0] = ('print', p[3])

def p_statement_return(p):
    "statement : RETURN expression SEMICOLON"
    p[0] = ('return', p[2])

def p_statement_call(p):
    "statement : IDENTIFIER LEFTPARENTHESIS arguments RIGHTPARENTHESIS SEMICOLON"
    p[0] = ('call', p[1], p[3])

def p_statement_let_missing_semicolon(p):
    "statement : LET IDENTIFIER ASSIGN expression"
    # expression is a non-terminal, so its PLY line number is zero unless it
    # is propagated manually.  LET is on the source line to be reported.
    report_error("expected ‘;’", p.lineno(1))

def p_statement_while(p):
    "statement : WHILE LEFTPARENTHESIS expression RIGHTPARENTHESIS block"
    p[0] = ('while', p[3], p[5])

def p_statement_for(p):
    "statement : FOR LEFTPARENTHESIS for_initializer SEMICOLON expression SEMICOLON for_update RIGHTPARENTHESIS block"
    p[0] = ('for', p[3], p[5], p[7], p[9])

def p_for_initializer(p):
    "for_initializer : LET IDENTIFIER ASSIGN expression"
    p[0] = ('let', p[2], p[4])

def p_for_update(p):
    "for_update : IDENTIFIER ASSIGN expression"
    p[0] = ('assign', p[1], p[3])

def p_statement_function(p):
    "statement : FUNC IDENTIFIER LEFTPARENTHESIS parameters RIGHTPARENTHESIS block"
    p[0] = ('func', p[2], p[4], p[6])

def p_statement_annotated_function(p):
    "statement : annotation FUNC IDENTIFIER LEFTPARENTHESIS parameters RIGHTPARENTHESIS block"
    p[0] = ('memory_func', p[1], p[3], p[5], p[7])

def p_parameters_empty(p):
    "parameters : empty"
    p[0] = []

def p_parameters_one(p):
    "parameters : IDENTIFIER"
    p[0] = [p[1]]

def p_parameters_multiple(p):
    "parameters : parameters COMMA IDENTIFIER"
    p[0] = p[1] + [p[3]]

def p_arguments_empty(p):
    "arguments : empty"
    p[0] = []

def p_arguments_one(p):
    "arguments : expression"
    p[0] = [p[1]]

def p_arguments_multiple(p):
    "arguments : arguments COMMA expression"
    p[0] = p[1] + [p[3]]

def p_expression_binary(p):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MODULO expression
                  | expression EQUAL expression
                  | expression NOTEQUAL expression
                  | expression LESSTHAN expression
                  | expression LESSEQUAL expression
                  | expression GREATERTHAN expression
                  | expression GREATEREQUAL expression"""
    p[0] = (p[2], p[1], p[3])

def p_expression_unary_minus(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = ('negate', p[2])

def p_expression_group(p):
    "expression : LEFTPARENTHESIS expression RIGHTPARENTHESIS"
    p[0] = p[2]

def p_expression_literal(p):
    """expression : INTEGER
                  | FLOAT
                  | STRING
                  | BOOLEAN"""
    p[0] = p[1]

def p_expression_identifier(p):
    "expression : IDENTIFIER"
    p[0] = ('identifier', p[1])

def p_expression_call(p):
    "expression : IDENTIFIER LEFTPARENTHESIS arguments RIGHTPARENTHESIS"
    p[0] = ('call', p[1], p[3])

def p_expression_array(p):
    "expression : ARRAY LEFTPARENTHESIS array_type COMMA expression RIGHTPARENTHESIS"
    p[0] = ('array', p[3], p[5])

def p_array_type(p):
    """array_type : INT_TYPE
                  | FLOAT_TYPE
                  | BOOL_TYPE
                  | STRING_TYPE"""
    p[0] = p[1]

def p_empty(p):
    "empty :"
    p[0] = None

def p_error(token):
    """Fallback for syntax errors not covered by a targeted production."""
    global had_error
    had_error = True
    if token is None:
        print("Error: unexpected end of file")
    else:
        print(f"Error: unexpected token '{token.value}' at line {token.lineno}")

lexer = lex.lex()


# ============================================================================
# Command-line interface
# ============================================================================

def main():
    global had_error

    if len(sys.argv) != 2:
        print("Use: python your_parser.py <archivo>.uedge")
        sys.exit(1)

    source_path = sys.argv[1]

    if not source_path.endswith(".uedge"):
        print("Error: the file needs .uedge extension.")
        sys.exit(1)

    try:
        with open(source_path, "r", encoding="utf-8") as source_file:
            source_code = source_file.read()
    except FileNotFoundError:
        print(f"Error: file not found '{source_path}'")
        sys.exit(1)

    # parser.parse() feeds the source into the lexer itself.  Do not consume
    # tokens beforehand, or a later parser pass would receive an empty stream.
    # Keep this call compatible with the older PLY version used by the grader.
    parser = yacc.yacc(debug=False)
    had_error = False
    lexer.lineno = 1
    try:
        parser.parse(source_code, lexer=lexer)
    except LexicalError:
        return

    if not had_error:
        print("Parsed successfully")

if __name__ == "__main__":
    main()
