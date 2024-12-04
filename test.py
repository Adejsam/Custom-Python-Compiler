import lexer
from parser import parser
from code_generator import compile_code
from code_executor import execute_ir
from semantic_analyzer import SemanticAnalyzer

# Test data with fixed string literals
data = '''#test

cit_lab_x = 0
stadium_x = 7
cit_lab_y = 0
stadium_y = 10
number_of_students = input("Enter the number of students:")

stride_length = 0.75

distance = (((stadium_x - cit_lab_x) ** 2) + ((stadium_y - cit_lab_y) ** 2)) ** 0.5

steps_per_student = distance / stride_length

total_steps = steps_per_student * number_of_students

average_steps = total_steps / number_of_students

print("Total distance in meteres:")
print(distance)

print("Estimated steps per student:")
print(steps_per_student)

print("Total steps walked:")
print(total_steps)

print("Average number of steps for any student:")
print(average_steps)
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

print("Parse Tree:")
print(result)

# Perform semantic analysis
analyzer = SemanticAnalyzer()
try:
    print("============Testing for errors==================")
    analyzer.analyze(result)
    print("\nSemantic Analysis Passed")
    # Compile the AST to IR
    code_gen = compile_code(result)
    print(code_gen)

    print("============Gnerated code executing now==================")
    # Execute the generated IR
    execute_ir(code_gen)
except Exception as e:
    print("\nSemantic Analysis Error:", e)