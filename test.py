import lexer
from parser import parser
from ir_generator import compile_code
from code_generator import execute_ir

# Test data with fixed string literals
data = '''#test
print("hello")
a = input("Enter a number:")
print(a+1)

if a == 2: print("yh") else: print("done") 

for i in range(1, 10): 
    print(i)
'''

# Build lexer
lexer_ins = lexer.build_lexer(data=data)
while True:
    tok = lexer_ins.token()
    if not tok:
        break
    print(tok)

# Parse the input data
result = parser.parse(data)

print("==============================")
print(f"Parse Result: {result}")
print("==============================")

# Compile the AST to IR
ir = compile_code(result)
print(ir)

print("==============================")
# Execute the generated IR
execute_ir(ir)