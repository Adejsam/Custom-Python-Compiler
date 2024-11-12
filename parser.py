import ply.yacc as yacc
from lexer import tokens  # Import tokens from lexer

# Define precedence and associativity
precedence = (
    ('right', 'POWER'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),
    ('left', 'AND', 'OR'),
    ('left', 'EQUAL_EQUAL', 'NOT_EQUAL', 'GREATER', 'GREATER_EQUAL', 'LESS', 'LESS_EQUAL'),
)

def p_program(p):
    '''program : statements'''
    p[0] = p[1]

def p_statements(p):
    '''statements : statement NEWLINE statements
                  | statement statements
                  | statement
                  | empty'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]  # Append statement to the list
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_empty(p):
    '''empty :'''
    p[0] = []

# Define grammar rules
def p_statement(p):
    '''statement : print_stmt
                 | assignment_stmt
                 | input_stmt
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | list_stmt
                 | function_def
                 | function_call
                 | return_stmt
                 | break_stmt
                 | expression'''
    p[0] = p[1]

def p_function_def(p):
    '''function_def : DEF ID LPAREN parameter_list RPAREN COLON NEWLINE statements
                   | DEF ID LPAREN RPAREN COLON NEWLINE statements'''
    if len(p) == 9:
        p[0] = ('function_def', p[2], p[4], p[8])  # name, parameters, body
    else:
        p[0] = ('function_def', p[2], [], p[7])  # function with no parameters

def p_parameter_list(p):
    '''parameter_list : ID
                     | ID COMMA parameter_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# Function Call
def p_function_call(p):
    '''function_call : ID LPAREN argument_list RPAREN
                    | ID LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = ('function_call', p[1], p[3])
    else:
        p[0] = ('function_call', p[1], [])

def p_argument_list(p):
    '''argument_list : expression
                    | expression COMMA argument_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# Return Statement
def p_return_stmt(p):
    '''return_stmt : RETURN expression
                  | RETURN'''
    if len(p) == 3:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)

# Add function call as an expression type
def p_expression_function_call(p):
    '''expression : function_call'''
    p[0] = p[1]


def p_print_stmt(p):
    '''print_stmt : PRINT LPAREN expression RPAREN'''
    p[0] = ('print', p[3])  # p[3] is the expression

def p_assignment_stmt(p):
    '''assignment_stmt : ID EQUALS expression'''
    p[0] = ('assign', p[1], p[3])  # ('assign', variable, expression)

def p_input_stmt(p):
    '''input_stmt : ID EQUALS INPUT LPAREN STRING RPAREN
                 | input_multiple'''
    if len(p) == 7:
        p[0] = ('input', p[1], p[5])
    else:
        p[0] = p[1]

def p_input_multiple(p):
    '''input_multiple : id_list EQUALS INPUT LPAREN STRING RPAREN'''
    p[0] = ('input_multiple', p[1], p[5])

def p_id_list(p):
    '''id_list : ID COMMA ID
               | ID COMMA id_list'''
    if len(p) == 4:
        p[0] = [p[1], p[3]]
    else:
        p[0] = [p[1]] + p[3]


# Add list expression to existing expression rules
def p_list_stmt(p):
    '''list_stmt : ID EQUALS LBRACKET list_elements RBRACKET
                | ID EQUALS LBRACKET RBRACKET'''
    if len(p) == 6:
        p[0] = ('list_create', p[1], p[4])
    else:
        p[0] = ('list_create', p[1], [])

def p_list_elements(p):
    '''list_elements : expression
                    | expression COMMA list_elements'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_list_operation(p):
    '''expression : ID LBRACKET expression RBRACKET
                 | ID DOT APPEND LPAREN expression RPAREN'''
    if len(p) == 5:
        p[0] = ('list_access', p[1], p[3])
    else:
        p[0] = ('list_append', p[1], p[5])


def p_break_stmt(p):
    '''break_stmt : BREAK'''
    p[0] = 'break'


def p_if_stmt(p):
    '''if_stmt : IF expression COLON NEWLINE statements elif_stmt else_stmt
               | IF expression COLON statements elif_stmt else_stmt'''
    # Group the if statement with its condition, if_body, elifs, and else in a single structure.
    if len(p) == 8:
        p[0] = ('if_stmt', ('if', p[2], p[5]), p[6], p[7])  # if with newline-separated body
    else:
        p[0] = ('if_stmt', ('if', p[2], p[4]), p[5], p[6])  # if with inline body

def p_elif_stmt(p):
    '''elif_stmt : ELIF expression COLON NEWLINE statements elif_stmt
                 | ELIF expression COLON statements elif_stmt
                 | empty'''
    # Use nested structure for elifs, so each elif has its condition, body, and optional following elif
    if len(p) == 7:
        p[0] = ('elif', p[2], p[5], p[6])  # elif with newline-separated body
    elif len(p) == 6:
        p[0] = ('elif', p[2], p[4], p[5])  # elif with inline body
    else:
        p[0] = []  # No elif

def p_else_stmt(p):
    '''else_stmt : ELSE COLON NEWLINE statements
                 | ELSE COLON statements
                 | empty'''
    if len(p) == 5:
        p[0] = ('else', p[4])  # else with newline-separated body
    elif len(p) == 4:
        p[0] = ('else', p[3])  # else with inline body
    else:
        p[0] = []  # No else

def p_while_stmt(p):
    '''while_stmt : WHILE expression COLON NEWLINE statements'''
    p[0] = ('while', p[2], p[5])  # ('while', condition, body)

def p_for_stmt(p):
    '''for_stmt : FOR ID IN RANGE LPAREN expression COMMA expression RPAREN COLON NEWLINE statements'''
    p[0] = ('for', p[2], ('range', p[6], p[8]), p[12])  # ('for', iterator variable, range(start, end), body)


def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression POWER expression
                  | expression AND expression
                  | expression OR expression
                  | expression EQUAL_EQUAL expression
                  | expression NOT_EQUAL expression
                  | expression GREATER expression
                  | expression GREATER_EQUAL expression
                  | expression LESS expression
                  | expression LESS_EQUAL expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_unary(p):
    '''expression : MINUS expression %prec UMINUS
                  | NOT expression'''
    p[0] = (p[1], p[2])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER
                  | FLOAT
                  | INT'''
    p[0] = p[1]

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = p[1]

def p_expression_boolean(p):
    '''expression : TRUE
                  | FALSE'''
    p[0] = p[1]

def p_expression_identifier(p):
    '''expression : ID'''
    p[0] = p[1]  # Return the identifier as is

def p_error(p):
    if p and p.type == 'NEWLINE':
        return  # Ignore isolated NEWLINE errors
    elif p:
        print(f"Syntax error at line {p.lineno}: {p.type} - {p.value}")
    else:
        print("Syntax error at EOF")


# Build the parser
parser = yacc.yacc()