import lexer
from parser import parser
from code_generator import compile_code
from code_executor import execute_ir
from semantic_analyzer import SemanticAnalyzer
from code_optimizer import CodeOptimizer
import sys

if len(sys.argv) < 2:
    print("Usage: python test.py <file_path>")
    sys.exit(1)

# Read the file sent from Sublime Text
file_path = sys.argv[1]
try:
    with open(file_path, 'r') as f:
        data = f.read()
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
    sys.exit(1)

print("================ Compilation Process Stated ==============")
print("")
print("================ Tokenizing Source Code ===================")
# Build lexer
lexer_ins = lexer.build_lexer(data=data)
while True:
    tok = lexer_ins.token()
    if not tok:
        break
    print(tok)

print("\n")
print("\n")
print("=============== Parsing Source Code =========================")
# Parse the input data
result = parser.parse(data)

print("Abstract Syntax Tree:")
print(result)

print("\n")
print("\n")
# Perform semantic analysis
analyzer = SemanticAnalyzer()
try:
    print("============== Semantically Analyzing Source Code ==================")
    analyzer.analyze(result)
    print("\nSemantic Analysis Successful")
    
    print("\n")
    print("\n")
    print("============== Generating Intermediate Representation ==================")
    # Compile the AST to IR
    code_gen = compile_code(result)
    print(code_gen)

    print("\n")
    print("\n")
    print("============== Optimizing Intermediate representation ====================")
    optimizer = CodeOptimizer(code_gen)
    optimized_ir = optimizer.run()
    print("\n Optimized IR:")
    print(optimized_ir)


    print("\n")
    print("\n")
    print("============== Compilation and Execution Completed ==================")
    # Execute the generated IR
    execute_ir(optimized_ir)
except Exception as e:
    print("\nSemantic Analysis Error:", e)
