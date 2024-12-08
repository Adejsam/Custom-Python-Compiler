class SemanticAnalyzer:
    def __init__(self):
        # Symbol table to store variable information
        self.symbol_table = {}
        self.current_scope = [{}]  # Stack for scope management
        self.functions = {}  # Track defined functions

    def enter_scope(self):
        """Enter a new scope."""
        self.current_scope.append({})  # Push a new scope onto the stack

    def leave_scope(self):
        """Exit the current scope."""
        if self.current_scope:
            self.current_scope.pop()  # Pop the current scope from the stack

    def declare_variable(self, var_name, var_type):
        """Declare a variable in the current scope."""
        if var_name in self.current_scope[-1]:
            raise Exception(f"Semantic Error: Variable '{var_name}' already declared in this scope.")
        self.current_scope[-1][var_name] = var_type  # Add variable to the current scope

    def lookup_variable(self, var_name):
        """Find a variable in the nested scopes."""
        for scope in reversed(self.current_scope):
            if var_name in scope:
                return scope[var_name]  # Return variable type if found
        raise Exception(f"Semantic Error: Variable '{var_name}' not declared.")  # Raise error if not found

    def declare_function(self, func_name, params, return_type=None):
        """Declare a function in the global scope."""
        if func_name in self.functions:
            raise Exception(f"Semantic Error: Function '{func_name}' already defined.")
        self.functions[func_name] = {
            'params': params,  # Store function parameters
            'return_type': return_type  # Store return type
        }

    def analyze(self, node):
        """Traverse and analyze the parse tree."""
        if isinstance(node, list):  # Handle a list of statements
            for sub_node in node:
                self.analyze(sub_node)  # Recursively analyze each statement
        elif isinstance(node, tuple):
            node_type = node[0]  # Get the type of the node

            # Function Definition
            if node_type == 'function_def':
                func_name = node[1]  # Function name
                params = node[2]  # Function parameters
                func_body = node[3]  # Function body
                
                # Enter function scope
                self.enter_scope()
                
                # Declare function parameters
                param_types = []
                for param in params:
                    # For simplicity, we'll use 'unknown' type for parameters
                    self.declare_variable(param, 'unknown')
                    param_types.append('unknown')
                
                # Declare function in global scope
                self.declare_function(func_name, param_types)  # Register the function with its parameters
                
                # Analyze function body
                self.analyze(func_body)  # Recursively analyze the function's body
                
                # Exit function scope
                self.leave_scope()  # Clean up the scope after analyzing the function

            # Function Call
            elif node_type == 'function_call':
                func_name = node[1]  # Name of the function being called
                args = node[2]  # Arguments passed to the function
                
                # Check if function is defined
                if func_name not in self.functions:
                    raise Exception(f"Semantic Error: Function '{func_name}' not defined.")
                
                # Check argument count
                expected_params = len(self.functions[func_name]['params'])  # Expected number of parameters
                if len(args) != expected_params:
                    raise Exception(f"Semantic Error: Function '{func_name}' expects {expected_params} arguments, got {len(args)}")
                
                # Validate arguments
                for arg in args:
                    self.evaluate_expression(arg)  # Ensure each argument is valid

            # List Creation
            elif node_type == 'list_create':
                var_name = node[1]  # Variable name for the list
                elements = node[2]  # Elements of the list
                
                # Determine list element type
                if not elements:
                    # Empty list, use 'unknown' type
                    self.declare_variable(var_name, 'list[unknown]')
                else:
                    # Infer type from first element
                    first_elem_type = self.evaluate_expression(elements[0])
                    
                    # Check if all elements have the same type
                    list_type = f'list[{first_elem_type}]'
                    for elem in elements[1:]:
                        elem_type = self.evaluate_expression(elem)
                        if elem_type != first_elem_type:
                            raise Exception(f"Semantic Error: List elements must be of the same type. Found {first_elem_type} and {elem_type}")
                    
                    self.declare_variable(var_name, list_type)  # Declare the list variable

            # List Append
            elif node_type == 'list_append':
                list_name = node[1]  # Name of the list
                element = node[2]  # Element to append
                
                # Check if list exists
                list_type = self.lookup_variable(list_name)
                
                # Extract expected element type
                if list_type.startswith('list['):
                    expected_type = list_type[5:-1]  # Extract type between list[ and ]
                    
                    # Check if appended element matches list type
                    actual_type = self.evaluate_expression(element)
                    if actual_type != expected_type and expected_type != 'unknown':
                        raise Exception(f"Semantic Error: Cannot append {actual_type} to list of {expected_type}")

            # List Access
            elif node_type == 'list_access':
                list_name = node[1]  # Name of the list
                index = node[2]  # Index to access
                
                # Check if list exists
                list_type = self.lookup_variable(list_name)
                
                # Verify index type
                index_type = self.evaluate_expression(index)
                if index_type != 'int':
                    raise Exception(f"Semantic Error: List index must be an integer, got {index_type}")

            # Input Statement
            elif node_type == 'input':
                var_name = node[1]  # Variable name for input
                prompt = node[2]  # Prompt message
                self.declare_variable(var_name, 'float')  # Assume input variables are floats

            # Multiple Input Statement
            elif node_type == 'input_multiple':
                var_names = node[1]  # List of variable names for input
                prompt = node[2]  # Prompt message
                for var_name in var_names:
                    self.declare_variable(var_name, 'float')  # Assume each input variable is a float

            # Assignment
            elif node_type == 'assign':
                var_name = node[1]  # Variable name for assignment
                expr = node[2]  # Expression being assigned
                expr_type = self.evaluate_expression(expr)  # Evaluate the expression to get its type
                self.declare_variable(var_name, expr_type)  # Declare the variable with the evaluated type

            # Print Statement
            # Print Statement
            elif node_type == 'print':
                print_args = node[1]  # Extract arguments for the print statement
                for arg in print_args:
                    resolved_type = self.evaluate_expression(arg)  # Resolve the type of each argument
                    if resolved_type == 'unknown':
                        raise Exception(f"Semantic Error: Unable to resolve type for print argument '{arg}'")

            # If Statement
            elif node_type == 'if_stmt':
                # Main if block
                if_condition = node[1][1]  # Condition of the if statement
                if_body = node[1][2]       # Body of the if statement
                
                # Evaluate condition
                self.evaluate_expression(if_condition)  # Check the validity of the condition
                
                # Enter new scope for if body
                self.enter_scope()
                self.analyze(if_body)  # Analyze the body of the if statement
                self.leave_scope()  # Exit the scope after analyzing

                # Analyze elif blocks
                elifs = node[2]  # Elif blocks
                if elifs:
                    self.analyze_elif_blocks(elifs)  # Analyze any elif blocks

                # Analyze else block
                else_block = node[3]  # Else block
                if else_block:
                    self.enter_scope()
                    self.analyze(else_block[1])  # Analyze the body of the else block
                    self.leave_scope()  # Exit the scope after analyzing

            # While Loop
            elif node_type == 'while':
                condition = node[1]  # Condition of the while loop
                body = node[2]  # Body of the while loop
                
                # Evaluate condition
                self.evaluate_expression(condition)  # Check the validity of the condition
                
                # Enter new scope for while body
                self.enter_scope()
                self.analyze(body)  # Analyze the body of the while loop
                self.leave_scope()  # Exit the scope after analyzing

            # For Loop
            elif node_type == 'for':
                iterator_var = node[1]  # Iterator variable name
                range_expr = node[2]  # Range expression
                body = node[3]  # Body of the for loop
                
                # Declare iterator variable
                self.declare_variable(iterator_var, 'int')  # Set type for the iterator variable
                
                # Validate range expression
                if range_expr[0] == 'range':
                    start = range_expr[1]  # Start of the range
                    end = range_expr[2]  # End of the range
                    
                    # Evaluate range start and end
                    self.evaluate_expression(start)  # Check validity of start
                    self.evaluate_expression(end)  # Check validity of end
                
                # Enter new scope for for loop body
                self.enter_scope()
                self.analyze(body)  # Analyze the body of the for loop
                self.leave_scope()  # Exit the scope after analyzing

            else:
                raise Exception(f"Semantic Error: Unrecognized node type '{node_type}'")  # Handle unrecognized node types
        else:
            pass  # Handle base cases like literals or identifiers

    def evaluate_expression(self, expr):
        """Evaluate an expression to determine its type."""
        def identify_type(value):
            # Debug print to track type resolution
            print(f"Resolving type for: {value}")
            
            # Check for string literals
            if isinstance(value, str):
                if value.startswith('"') and value.endswith('"'):
                    return 'str'  # Return string type
                try:
                    # Check if it's a variable
                    var_type = self.lookup_variable(value)  # Look up variable type
                    print(f"Variable {value} resolved to type: {var_type}")
                    return var_type  # Return variable type
                except Exception:
                    # If lookup fails, raise error
                    raise Exception(f"Semantic Error: Unrecognized identifier '{value}'")
            
            # Check for numeric literals
            if isinstance(value, (int, float)):
                return 'float'  # Return float type for numeric literals
            
            # Check for boolean literals
            if value is True or value is False:
                return 'bool'  # Return boolean type
            
            # Handle tuples (operations, function calls, etc.)
            if isinstance(value, tuple):
                print(f"Processing tuple: {value}")
                
                if value[0] == 'function_call':
                    func_name = value[1]  # Function name
                    if func_name not in self.functions:
                        raise Exception(f"Semantic Error: Function '{func_name}' not defined")
                    func_return_type = self.functions[func_name].get('return_type', 'float')  # Default to float for input
                    print(f"Function {func_name} return type: {func_return_type}")
                    return func_return_type  # Return function return type
                
                # Handle binary and unary operations
                if len(value) == 3:  # Binary operation
                    operator = value[0]  # Operator
                    left_type = identify_type(value[1])  # Left operand type
                    right_type = identify_type(value[2])  # Right operand type
                    
                    print(f"Binary operation: {operator} with types {left_type} and {right_type}")
                    
                    # Division by Zero Check
                    if operator in ['/', '//']:
                        if (isinstance(value[2], (int, float)) and value[2] == 0) or \
                        (isinstance(value[2], str) and value[2] == '0'):
                            raise Exception("Semantic Error: Division by zero")
                    
                    # Arithmetic operations
                    arithmetic_ops = ['+', '-', '*', '/', '//', '**', '^']
                    if operator in arithmetic_ops:
                        if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                            raise Exception(f"Type Error: Cannot perform {operator} on non-numeric types {left_type} and {right_type}.")
                        return 'float'  # Return float for arithmetic operations
                    
                    # Comparison operations
                    comparison_ops = ['==', '!=', '>', '>=', '<', '<=']
                    if operator in comparison_ops:
                        if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                            raise Exception(f"Type Error: Cannot compare non-numeric types {left_type} and {right_type}")
                        return 'bool'  # Return boolean for comparison operations
                    
                    # Logical operations
                    logical_ops = ['and', 'or']
                    if operator in logical_ops:
                        if left_type != 'bool' or right_type != 'bool':
                            raise Exception(f"Type Error: Logical {operator} requires boolean operands")
                        return 'bool'  # Return boolean for logical operations
                
                # Unary operations
                elif len(value) == 2:
                    operator = value[0]  # Operator
                    operand_type = identify_type(value[1])  # Operand type
                    
                    if operator == '-':
                        if operand_type not in ['int', 'float']:
                            raise Exception(f"Type Error: Cannot negate non-numeric type {operand_type}")
                        return operand_type  # Return type of the operand
                    
                    if operator == 'not':
                        if operand_type != 'bool':
                            raise Exception(f"Type Error: 'not' requires boolean operand")
                        return 'bool'  # Return boolean for 'not' operation
            
            return 'unknown'  # Default return type if none matched

        try:
            result_type = identify_type(expr)  # Identify the type of the expression
            print(f"Final resolved type: {result_type}")  # Debug print for final type
            return result_type  # Return the resolved type
        except Exception as e:
            print(f"Type resolution failed: {e}")  # Debug print for errors
            raise  # Raise the exception for further handling

    def analyze_elif_blocks(self, elifs):
        """Analyze elif blocks recursively."""
        if not elifs:
            return  # Base case: no more elif blocks
        
        # Current elif block
        elif_condition = elifs[1]  # Condition of the elif block
        elif_body = elifs[2]       # Body of the elif block
        
        # Evaluate condition
        self.evaluate_expression(elif_condition)  # Check the validity of the condition
        
        # Enter new scope for elif body
        self.enter_scope()
        self.analyze(elif_body)  # Analyze the body of the elif block
        self.leave_scope()  # Exit the scope after analyzing
        
        # Recursively analyze next elif block
        next_elifs = elifs[3]  # Next elif blocks
        if next_elifs:
            self.analyze_elif_blocks(next_elifs)  # Continue analyzing