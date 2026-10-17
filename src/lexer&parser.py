import sys
sys.path.insert(0, 'ply.zip')
import ply.lex as lex

# Keywords
keywords = {
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

tokens = [
    'IDENTIFIER', 'INTEGER', 'FLOAT', 'STRING', 'BOOLEAN',
    'LET', 'FUNC', 'IF', 'ELSE', 'WHILE', 'FOR', 'RETURN', 'PRINT', 'MEMORY',
    'ARRAY', 'INT_TYPE', 'FLOAT_TYPE', 'BOOL_TYPE', 'STRING_TYPE',
    'MEMORYSIZE', 'AT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
    'EQUAL', 'NOTEQUAL', 'LESSTHAN', 'GREATERTHAN',
    'LESSEQUAL', 'GREATEREQUAL', 'ASSIGN',
    'LEFTPARENTHESIS', 'RIGHTPARENTHESIS',
    'LEFTBRACE', 'RIGHTBRACE',
    'LEFTBRACKET', 'RIGHTBRACKET',
    'COMMA', 'SEMICOLON'
]

# Operators
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

# Symbols
t_LEFTPARENTHESIS = r'\('
t_RIGHTPARENTHESIS = r'\)'
t_LEFTBRACE = r'\{'
t_RIGHTBRACE = r'\}'
t_LEFTBRACKET = r'\['
t_RIGHTBRACKET = r'\]'
t_COMMA = r','
t_SEMICOLON = r';'

# Ignore spaces and tabs
t_ignore = ' \t'

# Units of memory
MEMORY_UNITS = {'b': 1, 'kb': 1024, 'mb': 1024 ** 2, 'gb': 1024 ** 3}

# Split the @memory annotations into number and unit
def t_MEMORYSIZE(t):
    r'\d+(?:kb|mb|gb|b)\b'
    digits = t.value.rstrip('kmgb')
    unit = t.value[len(digits):]
    t.value = int(digits) * MEMORY_UNITS[unit]
    return t

# Floats
def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Integers
def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Strings
def t_STRING(t):
    r'"([^"\\\n]|\\.)*"'
    t.value = t.value[1:-1]
    return t

# Check if a word is a keyword or a variable, if its a boolean it converts it to an actual boolean value
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keywords.get(t.value, 'IDENTIFIER')
    if t.type == 'BOOLEAN':
        t.value = (t.value == 'true')
    return t

# Ignore comments
def t_COMMENT(t):
    r'//[^\n]*'
    pass

# Keep track of what line we are in
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    if t.value[0] == '"':
        print(f"Error: malformed string at line {t.lineno}")
    else:
        print(f"Error: unexpected token ‘{t.value[0]}’ at line {t.lineno}")
    sys.exit(0)
    
lexer = lex.lex()

def main():
    if len(sys.argv) != 2:
        print("Use: python your_parser.py <archivo>.uedge")
        sys.exit(0)

    route = sys.argv[1]

    if not route.endswith(".uedge"):
        print("Error: the file needs .uedge extension.")
        sys.exit(0)

    try:
        with open(route, "r", encoding="utf-8") as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: file not found '{route}'")
        sys.exit(0)

    lexer.input(code)

    for token in lexer:
        pass # Pass so it doesnt print every token

    print("Parsed successfully")

if __name__ == "__main__":
    main()