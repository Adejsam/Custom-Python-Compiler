import ply.lex as lex

# A list of tokens which are always required
tokens = ('NUMBER', 'ID', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER', 'LPAREN', 'RPAREN', 'EQUALS', 
          'GREATER', 'COLON', 'LBRACE', 'RBRACE', 'COMMENT', 'NEWLINE', 'LESS', 'GREATER_EQUAL', 
          'LESS_EQUAL', 'NOT_EQUAL', 'EQUAL_EQUAL', 'COMMA', 'LBRACKET', 'RBRACKET', 'NEW', 
          'SEMICOLON', 'DOT')

# Reserved words
reserved = { 
    'if':'IF', 
    'else': 'ELSE', 
    'while': 'WHILE', 
    'return': 'RETURN', 
    'and': 'AND', 
    'or': 'OR', 
    'for': 'FOR', 
    'true': 'TRUE', 
    'false': 'FALSE', 
    'not': 'NOT', 
    'print': 'PRINT', 
    'int': 'INT', 
    'float': 'FLOAT', 
    'def': 'DEF',  
    'str': 'STRING', 
    'type': 'TYPE', 
    'range': 'RANGE', 
    'elif': 'ELIF',
    'in': 'IN',
    'break': 'BREAK',
    'input': 'INPUT',
    'append': 'APPEND'
}

tokens += tuple(reserved.values())

# Regular expression rules
t_POWER = r'\*\*'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQUALS = r'='
t_GREATER = r'>'
t_LESS = r'<'
t_COLON = r':'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_GREATER_EQUAL = r'>='
t_LESS_EQUAL = r'<='
t_NOT_EQUAL = r'!='
t_SEMICOLON = r';'
t_EQUAL_EQUAL = r'=='
t_RETURN = r'return'
# t_IF = r'if'
# t_ELSE = r'else'
# t_ELIF = r'elif'
# t_IN = r'in'
t_WHILE = r'while'
t_FOR = r'for'
t_TYPE = r'type'
t_INT = r'int'
t_FLOAT = r'float'
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_DEF = r'def'
t_NEW = r'new'
t_PRINT = r'print'
t_RANGE = r'range'
t_INPUT = r'input'
t_APPEND = r'append'
t_DOT = r'\.'


# Identifying IDs like variables and reserved words
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t

# Identifying integer and floating point numbers
def t_NUMBER(t):
    r'\d+(\.\d+)?'  # Matches integers and floats
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

# Handling boolean values
def t_TRUE(t):
    r'true'
    t.value = True
    return t

def t_FALSE(t):
    r'false'
    t.value = False
    return t

# Handling strings
def t_STRING(t):
    r'\"([^\\\"]|\\.)*\"'
    return t

# For comments to be ignored
def t_COMMENT(t):
    r'\#.*'
    pass  # Ignore comments

# To track new lines
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = 'NEWLINE'
    return t

# Ignoring spaces and tabs
t_ignore = ' \t'

# Error handling rule
def t_error(t):
    print(f'illegal character {t.value[0]}')
    t.lexer.skip(1)

# Build the lexer
def build_lexer(data):
    lexer = lex.lex()
    lexer.input(data)
    return lexer