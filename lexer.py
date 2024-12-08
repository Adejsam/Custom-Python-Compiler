import ply.lex as lex  # Import the PLY lex module for lexical analysis

# Define reserved words and their corresponding token types
reserved = { 
    'if': 'IF', 
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

# List of token types, including both custom tokens and reserved words
tokens = (
    'NUMBER', 'ID', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER', 
    'LPAREN', 'RPAREN', 'EQUALS', 'GREATER', 'COLON', 'LBRACE', 
    'RBRACE', 'COMMENT', 'NEWLINE', 'LESS', 'GREATER_EQUAL', 
    'LESS_EQUAL', 'NOT_EQUAL', 'EQUAL_EQUAL', 'COMMA', 'LBRACKET', 
    'RBRACKET', 'NEW', 'SEMICOLON', 'DOT'
) + tuple(reserved.values())  # Add reserved words to the list of tokens

# Regular expression rules for simple tokens
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
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_DOT = r'\.'

# Token for identifiers (variables and reserved words)
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check if the ID is a reserved word
    return t

# Token for numbers (integers and floats)
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)  # Convert to appropriate type
    return t

# Token for boolean values
def t_TRUE(t):
    r'true'
    t.value = True
    return t

def t_FALSE(t):
    r'false'
    t.value = False
    return t

# Token for formatted strings (f-strings)
def t_FSTRING(t):
    r'f"([^"\\]*(\\.[^"\\]*)*(\{[^{}]*\}[^"\\]*)*)"'  
    if not t.value.endswith('"'):
        print(f"Warning: Unclosed f-string at line {t.lineno}")
        t.lexer.skip(len(t.value))
        return None
    t.value = t.value[2:-1]  # Remove `f` prefix and surrounding quotes
    return t

# Token for regular strings
def t_STRING(t):
    r'"([^"\\]|\\.)*"'  # Matches double-quoted strings with escape sequences
    # Pass the full quoted string to the parser
    t.value = t.value  # Keep quotes intact
    return t

# Token for comments (ignored)
def t_COMMENT(t):
    r'\#.*'
    pass  # Ignore comments

# Token for new lines
def t_newline(t):
    r'\n\n'
    t.lexer.lineno += 2
    t.value = '\n'
    t.type = 'NEWLINE'
    return t

# Token for multi-line comments
def t_MULTILINE_STRING(t):
    r'"""(.|\n)*?"""'
    t.value = t.value[3:-3]  # Remove surrounding triple quotes
    t.lexer.lineno += t.value.count('\n')  # Adjust line numbers
    return t

# Ignore spaces and tabs
t_ignore = ' \t'

# Error handling rule
def t_error(t):
    if t.value[0] == '\n':
        t.lexer.lineno += 1  # Increment line count for new lines
    else:
        print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Function to build the lexer
def build_lexer(data):
    lexer = lex.lex()  # Create a lexer instance
    lexer.input(data)  # Input data to the lexer
    return lexer  # Return the lexer instance