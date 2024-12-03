class SemanticAnalyzer:
    def __init__(self):
        # Symbol table to store variable information
        self.symbol_table = {}
        self.current_scope = [{}]  # Stack for scope management
        self.functions = {}  # Track defined functions

    def enter_scope(self):
        """Enter a new scope."""
        self.current_scope.append({})

    def leave_scope(self):
        """Exit the current scope."""
        if self.current_scope:
            self.current_scope.pop()

    def declare_variable(self, var_name, var_type):
        """Declare a variable in the current scope."""
        if var_name in self.current_scope[-1]:
            raise Exception(f"Semantic Error: Variable '{var_name}' already declared in this scope.")
        self.current_scope[-1][var_name] = var_type

    def lookup_variable(self, var_name):
        """Find a variable in the nested scopes."""
        for scope in reversed(self.current_scope):
            if var_name in scope:
                return scope[var_name]
        raise Exception(f"Semantic Error: Variable '{var_name}' not declared.")

    def declare_function(self, func_name, params, return_type=None):
        """Declare a function in the global scope."""
        if func_name in self.functions:
            raise Exception(f"Semantic Error: Function '{func_name}' already defined.")
        self.functions[func_name] = {
            'params': params,
            'return_type': return_type
        }

    def analyze(self, node):
        """Traverse and analyze the parse tree."""
        if isinstance(node, list):  # Handle a list of statements
            for sub_node in node:
                self.analyze(sub_node)
        elif isinstance(node, tuple):
            node_type = node[0]

            # List Creation
            if node_type == 'list_create':
                var_name = node[1]
                elements = node[2]
                
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
                            raise Exception(f"Semantic Error: List elements must be of the same type. " 
                                        f"Found {first_elem_type} and {elem_type}")
                    
                    self.declare_variable(var_name, list_type)

            # List Append
            elif node_type == 'list_append':
                list_name = node[1]
                element = node[2]
                
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
                list_name = node[1]
                index = node[2]
                
                # Check if list exists
                list_type = self.lookup_variable(list_name)
                
                # Verify index type
                index_type = self.evaluate_expression(index)
                if index_type != 'int':
                    raise Exception(f"Semantic Error: List index must be an integer, got {index_type}")

            # Function Definition
            elif node_type == 'function_def':
                func_name = node[1]
                params = node[2]
                func_body = node[3]
                
                # Enter function scope
                self.enter_scope()
                
                # Declare function parameters
                param_types = []
                for param in params:
                    # For simplicity, we'll use 'unknown' type for parameters
                    self.declare_variable(param, 'unknown')
                    param_types.append('unknown')
                
                # Declare function in global scope
                self.declare_function(func_name, param_types)
                
                # Analyze function body
                self.analyze(func_body)
                
                # Exit function scope
                self.leave_scope()

            # Function Call
            elif node_type == 'function_call':
                func_name = node[1]
                args = node[2]
                
                # Check if function is defined
                if func_name not in self.functions:
                    raise Exception(f"Semantic Error: Function '{func_name}' not defined.")
                
                # Check argument count
                expected_params = len(self.functions[func_name]['params'])
                if len(args) != expected_params:
                    raise Exception(f"Semantic Error: Function '{func_name}' expects {expected_params} arguments, got {len(args)}")
                
                # Validate arguments
                for arg in args:
                    self.evaluate_expression(arg)

            # Input Statement - Modified to set float type
            elif node_type == 'input':
                var_name = node[1]
                prompt = node[2]
                # Declare variable with 'float' type instead of 'str'
                self.declare_variable(var_name, 'float')

            # Multiple Input Statement - Also set to float type
            elif node_type == 'input_multiple':
                var_names = node[1]
                prompt = node[2]
                for var_name in var_names:
                    # Declare each variable with 'float' type
                    self.declare_variable(var_name, 'float')

            # Assignment
            elif node_type == 'assign':
                var_name = node[1]
                expr = node[2]
                expr_type = self.evaluate_expression(expr)
                self.declare_variable(var_name, expr_type)

            # Print Statement
            elif node_type == 'print':
                expr = node[1]
                self.evaluate_expression(expr)

            # If Statement
            elif node_type == 'if_stmt':
                # Main if block
                if_condition = node[1][1]  # Condition
                if_body = node[1][2]       # Body
                
                # Evaluate condition
                self.evaluate_expression(if_condition)
                
                # Enter new scope for if body
                self.enter_scope()
                self.analyze(if_body)
                self.leave_scope()

                # Analyze elif blocks
                elifs = node[2]
                if elifs:
                    self.analyze_elif_blocks(elifs)

                # Analyze else block
                else_block = node[3]
                if else_block:
                    self.enter_scope()
                    self.analyze(else_block[1])  # else_block is ('else', body)
                    self.leave_scope()

            # While Loop
            elif node_type == 'while':
                condition = node[1]
                body = node[2]
                
                # Evaluate condition
                self.evaluate_expression(condition)
                
                # Enter new scope for while body
                self.enter_scope()
                self.analyze(body)
                self.leave_scope()

            # For Loop
            elif node_type == 'for':
                iterator_var = node[1]
                range_expr = node[2]
                body = node[3]
                
                # Declare iterator variable
                self.declare_variable(iterator_var, 'int')
                
                # Validate range expression
                if range_expr[0] == 'range':
                    start = range_expr[1]
                    end = range_expr[2]
                    
                    # Evaluate range start and end
                    self.evaluate_expression(start)
                    self.evaluate_expression(end)
                
                # Enter new scope for for loop body
                self.enter_scope()
                self.analyze(body)
                self.leave_scope()

            else:
                raise Exception(f"Semantic Error: Unrecognized node type '{node_type}'")
        else:
            pass  # Handle base cases like literals or identifiers

    def analyze_elif_blocks(self, elifs):
        """Analyze elif blocks recursively."""
        if not elifs:
            return
        
        # Current elif block
        elif_condition = elifs[1]  # Condition
        elif_body = elifs[2]       # Body
        
        # Evaluate condition
        self.evaluate_expression(elif_condition)
        
        # Enter new scope for elif body
        self.enter_scope()
        self.analyze(elif_body)
        self.leave_scope()
        
        # Recursively analyze next elif block
        next_elifs = elifs[3]
        if next_elifs:
            self.analyze_elif_blocks(next_elifs)

    def evaluate_expression(self, expr):
        """Evaluate an expression to check semantic validity with enhanced error reporting."""
        def identify_type(value):
            # Debug print to track type resolution
            print(f"Resolving type for: {value}")
            
            # Check for string literals
            if isinstance(value, str):
                if value.startswith('"') and value.endswith('"'):
                    return 'str'
                try:
                    # Check if it's a variable
                    var_type = self.lookup_variable(value)
                    print(f"Variable {value} resolved to type: {var_type}")
                    return var_type
                except Exception:
                    # If lookup fails, assume it's a numeric type
                    try:
                        float(value)  # Try to convert to float
                        return 'float'
                    except ValueError:
                        raise Exception(f"Semantic Error: Unrecognized identifier '{value}'")
            
            # Check for numeric types
            if isinstance(value, (int, float)):
                return 'float'
            
            # Check for boolean literals
            if value is True or value is False:
                return 'bool'
            
            # Handle tuples (operations, function calls, etc.)
            if isinstance(value, tuple):
                print(f"Processing tuple: {value}")
                
                if value[0] == 'function_call':
                    func_name = value[1]
                    if func_name not in self.functions:
                        raise Exception(f"Semantic Error: Function '{func_name}' not defined")
                    func_return_type = self.functions[func_name].get('return_type', 'float')  # Default to float for input
                    print(f"Function {func_name} return type: {func_return_type}")
                    return func_return_type
                
                # Handle binary and unary operations
                if len(value) == 3:  # Binary operation
                    operator = value[0]
                    left_type = identify_type(value[1])
                    right_type = identify_type(value[2])
                    
                    print(f"Binary operation: {operator} with types {left_type} and {right_type}")
                    
                    # Arithmetic operations
                    arithmetic_ops = ['+', '-', '*', '/', '**', '^']
                    if operator in arithmetic_ops:
                        if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                            raise Exception(f"Type Error: Cannot perform {operator} on non-numeric types {left_type} and {right_type}. "
                                        f"Detailed context: Left value {value[1]}, Right value {value[2]}")
                        return 'float'  # Always return float for arithmetic operations
                    
                    # Comparison operations
                    comparison_ops = ['==', '!=', '>', '>=', '<', '<=']
                    if operator in comparison_ops:
                        if left_type not in ['int', 'float'] or right_type not in ['int', 'float']:
                            raise Exception(f"Type Error: Cannot compare non-numeric types {left_type} and {right_type}")
                        return 'bool'
                    
                    # Logical operations
                    logical_ops = ['and', 'or']
                    if operator in logical_ops:
                        if left_type != 'bool' or right_type != 'bool':
                            raise Exception(f"Type Error: Logical {operator} requires boolean operands")
                        return 'bool'
                
                # Unary operations
                elif len(value) == 2:
                    operator = value[0]
                    operand_type = identify_type(value[1])
                    
                    if operator == '-':
                        if operand_type not in ['int', 'float']:
                            raise Exception(f"Type Error: Cannot negate non-numeric type {operand_type}")
                        return operand_type
                    
                    if operator == 'not':
                        if operand_type != 'bool':
                            raise Exception(f"Type Error: 'not' requires boolean operand")
                        return 'bool'
            
            return 'unknown'

        try:
            result_type = identify_type(expr)
            print(f"Final resolved type: {result_type}")
            return result_type
        except Exception as e:
            print(f"Type resolution failed: {e}")
            raise