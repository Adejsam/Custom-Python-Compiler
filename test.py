import lexer
from parser import parser
from ir_generator import compile_code
from code_generator import execute_ir

# Test data with fixed string literals
data = '''#test

cit_lab_x = 0
stadium_x = 7
cit_lab_y = 0
stadium_y = 10
number_of_students = 90

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

print("==============================")
print(f"Parse Result: {result}")
print("==============================")

# Compile the AST to IR
ir = compile_code(result)
print(ir)

print("==============================")
# Execute the generated IR
execute_ir(ir)