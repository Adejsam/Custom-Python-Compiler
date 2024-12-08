import ply.yacc as yacc
from lexer import tokens  # Import tokens from lexer

# Define precedence and associativity
# These rules dictate the order of operations and associativity for operators
precedence = (
    ('right', 'POWER'),  # Right associativity for exponentiation
    ('left', 'PLUS', 'MINUS'),  # Addition and subtraction
    ('left', 'TIMES', 'DIVIDE'),  # Multiplication and division
    ('right', 'UMINUS'),  # Unary minus has higher precedence
    ('left', 'AND', 'OR'),  # Logical AND and OR
    ('left', 'EQUAL_EQUAL', 'NOT_EQUAL', 'GREATER', 'GREATER_EQUAL', 'LESS', 'LESS_EQUAL'),  # Comparisons
)

# Define the program structure
def p_program(p):
    '''program : statements'''
    p[0] = p[1]  # A program consists of multiple statements

# Define rules for multiple statements
def p_statements(p):
    '''statements : statement NEWLINE statements
                  | statement statements
                  | statement
                  | empty'''
    # Build a list of statements based on the input
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

# Handle empty productions
def p_empty(p):
    '''empty :'''
    p[0] = []  # Represents an empty input

# Define a generic statement rule
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
    p[0] = p[1]  # Delegate processing to specific statement rules

# Define a function definition
def p_function_def(p):
    '''function_def : DEF ID LPAREN parameter_list RPAREN COLON NEWLINE statements
                   | DEF ID LPAREN RPAREN COLON NEWLINE statements'''
    # Functions can have parameters or be parameter-less
    if len(p) == 9:
        p[0] = ('function_def', p[2], p[4], p[8])  # Function name, parameters, body
    else:
        p[0] = ('function_def', p[2], [], p[7])  # Function with no parameters

# Define a parameter list for functions
def p_parameter_list(p):
    '''parameter_list : ID
                     | ID COMMA parameter_list'''
    # Build a list of parameters
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# Define function call syntax
def p_function_call(p):
    '''function_call : ID LPAREN argument_list RPAREN
                    | ID LPAREN RPAREN'''
    # Functions can be called with or without arguments
    if len(p) == 5:
        p[0] = ('function_call', p[1], p[3])
    else:
        p[0] = ('function_call', p[1], [])

# Define arguments for function calls
def p_argument_list(p):
    '''argument_list : expression
                    | expression COMMA argument_list'''
    # Build a list of arguments
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# Define return statement syntax
def p_return_stmt(p):
    '''return_stmt : RETURN expression
                  | RETURN'''
    # Return statement can optionally have an expression
    if len(p) == 3:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)

# Define a print statement
def p_print_stmt(p):
    '''print_stmt : PRINT LPAREN expression RPAREN'''
    p[0] = ('print', p[3])  # Print the evaluated expression

def p_print_arguments(p):
    '''print_arguments : expression
                       | expression COMMA print_arguments'''
    # This rule handles multiple arguments separated by commas
    if len(p) == 2:
        p[0] = [p[1]]  # Single argument
    else:
        p[0] = [p[1]] + p[3]  # Combine the first argument with the rest

# Define assignment statements
def p_assignment_stmt(p):
    '''assignment_stmt : ID EQUALS expression'''
    p[0] = ('assign', p[1], p[3])  # Variable assignment

# Define input statements
def p_input_stmt(p):
    '''input_stmt : ID EQUALS INPUT LPAREN STRING RPAREN
                 | input_multiple'''
    if len(p) == 7:
        p[0] = ('input', p[1], p[5])  # Single input assignment
    else:
        p[0] = p[1]

# Define rules for multiple inputs
def p_input_multiple(p):
    '''input_multiple : id_list EQUALS INPUT LPAREN STRING RPAREN'''
    p[0] = ('input_multiple', p[1], p[5])  # Input for multiple variables

# Define a list of IDs
def p_id_list(p):
    '''id_list : ID COMMA ID
               | ID COMMA id_list'''
    if len(p) == 4:
        p[0] = [p[1], p[3]]  # Build a list of IDs
    else:
        p[0] = [p[1]] + p[3]
# Define list creation and operations
def p_list_stmt(p):
    '''list_stmt : ID EQUALS LBRACKET list_elements RBRACKET
                | ID EQUALS LBRACKET RBRACKET'''
    # List creation with or without elements
    if len(p) == 6:
        p[0] = ('list_create', p[1], p[4])  # List with elements
    else:
        p[0] = ('list_create', p[1], [])  # Empty list

# Define elements inside a list
def p_list_elements(p):
    '''list_elements : expression
                    | expression COMMA list_elements'''
    # Build a list of expressions
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

# Define list access and modification operations
def p_list_operation(p):
    '''expression : ID LBRACKET expression RBRACKET
                 | ID DOT APPEND LPAREN expression RPAREN'''
    # Access list elements or append to a list
    if len(p) == 5:
        p[0] = ('list_access', p[1], p[3])  # Access a specific index
    else:
        p[0] = ('list_append', p[1], p[5])  # Append to the list

# Define a break statement
def p_break_stmt(p):
    '''break_stmt : BREAK'''
    p[0] = 'break'  # Break statement for loops

# Define if-elif-else statements
def p_if_stmt(p):
    '''if_stmt : IF expression COLON NEWLINE statements elif_stmt else_stmt
               | IF expression COLON statements elif_stmt else_stmt'''
    # Group condition, if body, elif clauses, and else body
    if len(p) == 8:
        p[0] = ('if_stmt', ('if', p[2], p[5]), p[6], p[7])  # Multi-line if body
    else:
        p[0] = ('if_stmt', ('if', p[2], p[4]), p[5], p[6])  # Inline if body

# Define elif clauses
def p_elif_stmt(p):
    '''elif_stmt : ELIF expression COLON NEWLINE statements elif_stmt
                 | ELIF expression COLON statements elif_stmt
                 | empty'''
    # Handle nested elif clauses
    if len(p) == 7:
        p[0] = ('elif', p[2], p[5], p[6])  # Multi-line elif body
    elif len(p) == 6:
        p[0] = ('elif', p[2], p[4], p[5])  # Inline elif body
    else:
        p[0] = []  # No elif

# Define else clause
def p_else_stmt(p):
    '''else_stmt : ELSE COLON NEWLINE statements
                 | ELSE COLON statements
                 | empty'''
    # Else clause with or without a body
    if len(p) == 5:
        p[0] = ('else', p[4])  # Multi-line else body
    elif len(p) == 4:
        p[0] = ('else', p[3])  # Inline else body
    else:
        p[0] = []  # No else

# Define while loop statement
def p_while_stmt(p):
    '''while_stmt : WHILE expression COLON NEWLINE statements'''
    p[0] = ('while', p[2], p[5])  # While loop with condition and body

# Define for loop statement
def p_for_stmt(p):
    '''for_stmt : FOR ID IN RANGE LPAREN expression COMMA expression RPAREN COLON NEWLINE statements'''
    p[0] = ('for', p[2], ('range', p[6], p[8]), p[12])  # For loop with range and body

# Define binary operations for expressions
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
    p[0] = (p[2], p[1], p[3])  # Operator and operands

# Define unary operations for expressions
def p_expression_unary(p):
    '''expression : MINUS expression %prec UMINUS
                  | NOT expression'''
    p[0] = (p[1], p[2])  # Operator and operand

# Define grouping of expressions
def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]  # Return the grouped expression

# Define numeric literals
def p_expression_number(p):
    '''expression : NUMBER
                  | FLOAT
                  | INT'''
    p[0] = p[1]  # Return the numeric value

# Define string literals
def p_expression_string(p):
    '''expression : STRING'''
    p[0] = p[1]  # Return the string value

# Define boolean literals
def p_expression_boolean(p):
    '''expression : TRUE
                  | FALSE'''
    p[0] = p[1]  # Return the boolean value

# Define identifier usage
def p_expression_identifier(p):
    '''expression : ID'''
    p[0] = p[1]  # Return the identifier

# Handle syntax errors
def p_error(p):
    if p and p.type == 'NEWLINE':
        return  # Ignore isolated newline errors
    elif p:
        print(f"Syntax error at line {p.lineno}: {p.type} - {p.value}")
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc()
