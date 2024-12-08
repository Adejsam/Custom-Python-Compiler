from llvmlite import ir
import llvmlite.binding as llvm

class CodeGenerator:
    def __init__(self):
        self.module = ir.Module(name="main")
        self.builder = None
        self.declare_printf()
        self.declare_scanf()
        self.func_ty = ir.FunctionType(ir.VoidType(), [])
        self.main = ir.Function(self.module, self.func_ty, name="main")
        self.entry_block = self.main.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(self.entry_block)
        self.variables = {}
        self.string_counter = 0
        self.strings = {}
        self.loop_stack = []
    

    def declare_printf(self):
        printf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, name="printf")

    def declare_exit(self):
        exit_ty = ir.FunctionType(ir.VoidType(), [])
        self.exit = ir.Function(self.module, exit_ty, name="exit")

    def declare_scanf(self):
        scanf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        self.scanf = ir.Function(self.module, scanf_ty, name="scanf")
    
    def create_error_handling_printf(self, error_msg):
        """Create a printf for error messages"""
        error_str = self.create_string_constant(error_msg + "\n")
        error_ptr = self.builder.bitcast(error_str, ir.PointerType(ir.IntType(8)))
        self.builder.call(self.printf, [error_ptr])
        # Create an exit function call to terminate the program
        exit_ty = ir.FunctionType(ir.VoidType(), [])
        if 'exit' not in self.module.globals:
            exit_func = ir.Function(self.module, exit_ty, 'exit')
        else:
            exit_func = self.module.globals['exit']
        self.builder.call(exit_func, [])

    def create_string_constant(self, string):
        if string in self.strings:
            return self.strings[string]
        name = f"str_{self.string_counter}"
        self.string_counter += 1
        string_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(string) + 1),
                                   bytearray(string.encode('utf8')) + b'\0')
        global_string = ir.GlobalVariable(self.module, string_const.type, name=name)
        global_string.global_constant = True
        global_string.initializer = string_const
        self.strings[string] = global_string
        return global_string


    def generate_code(self, ast):
        """Enhanced code generation with better block handling"""
        if isinstance(ast, list):
            for node in ast:
                if not self.builder.block.is_terminated:
                    self.visit(node)
        else:
            self.visit(ast)
        
        # Only add return if we're at the end of the main function
        if not self.builder.block.is_terminated:
            self.builder.ret_void()

    def visit(self, node):
        """Enhanced visit method with better handling of nested structures"""
        if isinstance(node, list):
            last_result = None
            for item in node:
                if not self.builder.block.is_terminated:  # Only visit if block isn't terminated
                    last_result = self.visit(item)
            return last_result
        
        if isinstance(node, tuple):
            method_name = f'visit_{node[0]}'
            if hasattr(self, method_name):
                return getattr(self, method_name)(node)
        return None
    
    def visit_print(self, node):
        """Enhanced print implementation to avoid duplicate outputs."""
        _, args = node
        format_parts = []
        value_parts = []

        for arg in args:
            if isinstance(arg, str) and arg.startswith('"') and arg.endswith('"'):
                # String literal
                format_parts.append(arg[1:-1])  # Remove quotes
            else:
                # Float or variable to print
                value = self.visit_expression(arg)
                format_parts.append("%.2f")
                value_parts.append(value)

        # Combine format parts into a single format string
        combined_format = " ".join(format_parts) + "\n"
        format_str = self.create_string_constant(combined_format)
        format_ptr = self.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))

        # Call printf with the combined format string and all values
        self.builder.call(self.printf, [format_ptr, *value_parts])


    def visit_input(self, node):
        """Generate code for input statements"""
        print(f"visit_input node: {node}")  # Debugging line
        # Check the structure of the node
        if len(node) == 3:
            _, var_name, prompt = node
        else:
            raise ValueError(f"Unexpected input node structure: {node}")
        
        # Print the prompt
        prompt_str = self.create_string_constant(prompt)
        prompt_ptr = self.builder.bitcast(prompt_str, ir.PointerType(ir.IntType(8)))
        self.builder.call(self.printf, [prompt_ptr])
        
        # Create format string for scanf
        format_str = self.create_string_constant("%lf")  # Use %lf for double
        format_ptr = self.builder.bitcast(format_str, ir.PointerType(ir.IntType(8)))
        
        # Create variable if it doesn't exist
        if var_name not in self.variables:
            with self.builder.goto_entry_block():
                var_addr = self.builder.alloca(ir.DoubleType(), name=var_name)
            self.variables[var_name] = var_addr
        
        # Get pointer to variable
        var_ptr = self.variables[var_name]
        
        # Call scanf
        self.builder.call(self.scanf, [format_ptr, var_ptr])

    def visit_assign(self, node):
        _, var_name, value = node
        if var_name not in self.variables:
            with self.builder.goto_entry_block():
                var_addr = self.builder.alloca(ir.DoubleType(), name=var_name)
            self.variables[var_name] = var_addr
        
        value_val = self.visit_expression(value)
        self.builder.store(value_val, self.variables[var_name])

    def visit_for(self, node):
        """Fixed for loop implementation with proper block handling"""
        _, iterator, range_info, body = node
        
        # Extract range start and end
        _, start, end = range_info
        
        # Save current block
        current_block = self.builder.block
        
        # Allocate iterator variable in entry block
        with self.builder.goto_entry_block():
            iter_var = self.builder.alloca(ir.DoubleType(), name=iterator)
        self.variables[iterator] = iter_var
        
        # Create the loop blocks
        loop_cond = self.main.append_basic_block(name="for.cond")
        loop_body = self.main.append_basic_block(name="for.body")
        loop_inc = self.main.append_basic_block(name="for.inc")
        loop_end = self.main.append_basic_block(name="for.end")
        
        # Save loop info for break statements
        self.loop_stack.append((loop_cond, loop_end))
        
        # Initialize iterator
        start_val = self.visit_expression(start)
        self.builder.store(start_val, iter_var)
        
        # Branch from current block to condition
        self.builder.branch(loop_cond)
        
        # Condition block
        self.builder.position_at_start(loop_cond)
        current_val = self.builder.load(iter_var)
        end_val = self.visit_expression(end)
        cond = self.builder.fcmp_ordered('<', current_val, end_val)
        self.builder.cbranch(cond, loop_body, loop_end)
        
        # Body block
        self.builder.position_at_start(loop_body)
        self.visit(body)
        if not self.builder.block.is_terminated:
            self.builder.branch(loop_inc)
        
        # Increment block
        self.builder.position_at_start(loop_inc)
        current_val = self.builder.load(iter_var)
        one = ir.Constant(ir.DoubleType(), 1.0)
        next_val = self.builder.fadd(current_val, one)
        self.builder.store(next_val, iter_var)
        self.builder.branch(loop_cond)
        
        # Continue building after loop
        self.builder.position_at_start(loop_end)
        self.loop_stack.pop()

    def visit_while(self, node):
        """Fixed while loop implementation with proper block handling"""
        _, condition, body = node
        
        # Save current block
        current_block = self.builder.block
        
        # Create the basic blocks for the loop
        while_cond = self.main.append_basic_block(name="while.cond")
        while_body = self.main.append_basic_block(name="while.body")
        while_end = self.main.append_basic_block(name="while.end")
        
        # Save loop info for break statements
        self.loop_stack.append((while_cond, while_end))
        
        # Branch to condition check from current block
        self.builder.branch(while_cond)
        
        # Emit condition
        self.builder.position_at_start(while_cond)
        cond_val = self.visit_expression(condition)
        if isinstance(cond_val.type, ir.DoubleType):
            zero = ir.Constant(ir.DoubleType(), 0.0)
            cond_val = self.builder.fcmp_ordered('!=', cond_val, zero)
        self.builder.cbranch(cond_val, while_body, while_end)
        
        # Emit loop body
        self.builder.position_at_start(while_body)
        self.visit(body)
        if not self.builder.block.is_terminated:
            self.builder.branch(while_cond)
        
        # Continue building after loop
        self.builder.position_at_start(while_end)
        self.loop_stack.pop()


    def visit_function_call(self, node):
        _, func_name, args = node
        param_types = [ir.DoubleType()] * len(args)
        func_ty = ir.FunctionType(ir.DoubleType(), param_types)
        func = self.module.get_global(func_name)
        if func is None:
            func = ir.Function(self.module, func_ty, name=func_name)
        arg_values = [self.visit_expression(arg) for arg in args]
        return self.builder.call(func, arg_values)
    
    def visit_if_stmt(self, node):
        """Implementation of if-elif-else that handles multiple elif statements"""
        _, if_part, elif_parts, else_body = node
        
        # Create basic blocks
        if_then_bb = self.main.append_basic_block(name="if.then")
        merge_bb = self.main.append_basic_block(name="if.end")
        next_block = self.main.append_basic_block(name="if.next")

        # Generate if condition and branch
        if_condition = if_part[1]  # Get condition
        if_body = if_part[2]      # Get body
        
        cond_val = self.visit_expression(if_condition)
        if isinstance(cond_val.type, ir.DoubleType):
            zero = ir.Constant(ir.DoubleType(), 0.0)
            cond_val = self.builder.fcmp_ordered('!=', cond_val, zero)
        self.builder.cbranch(cond_val, if_then_bb, next_block)

        # Generate if body
        self.builder.position_at_start(if_then_bb)
        self.generate_code(if_body)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_bb)

        # Process elif blocks
        current_block = next_block
        
        def process_elif(elif_part, current_block):
            """Helper function to process a single elif part"""
            if isinstance(elif_part, tuple) and elif_part[0] == 'elif':
                elif_cond = elif_part[1]
                elif_body = elif_part[2]
                next_elif = elif_part[3] if len(elif_part) > 3 else []
                
                # Create blocks for this elif
                elif_then_bb = self.main.append_basic_block(name="elif.then")
                next_block = self.main.append_basic_block(name="elif.next")

                # Generate elif condition code
                self.builder.position_at_start(current_block)
                elif_cond_val = self.visit_expression(elif_cond)
                if isinstance(elif_cond_val.type, ir.DoubleType):
                    zero = ir.Constant(ir.DoubleType(), 0.0)
                    elif_cond_val = self.builder.fcmp_ordered('!=', elif_cond_val, zero)
                self.builder.cbranch(elif_cond_val, elif_then_bb, next_block)

                # Generate elif body
                self.builder.position_at_start(elif_then_bb)
                self.generate_code(elif_body)
                if not self.builder.block.is_terminated:
                    self.builder.branch(merge_bb)

                return next_block, next_elif
            return current_block, []

        # Process all elif parts recursively
        next_elif = elif_parts
        while next_elif:
            current_block, next_elif = process_elif(next_elif, current_block)

        # Process else block
        self.builder.position_at_start(current_block)
        if else_body:
            else_statements = else_body[1]
            self.generate_code(else_statements)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_bb)
        else:
            self.builder.branch(merge_bb)

        # Continue building code after the if-elif-else structure
        self.builder.position_at_start(merge_bb)


    def visit_expression(self, node):
        """Enhanced expression handling"""
        if isinstance(node, tuple):
            if len(node) == 3:  # Binary operations
                return self.visit_binop(node)
            elif len(node) == 2:  # Unary operations
                return self.visit_unary(node)
        elif isinstance(node, (int, float)):
            return ir.Constant(ir.DoubleType(), float(node))
        elif isinstance(node, str):
            if node in self.variables:
                return self.builder.load(self.variables[node])
            try:
                return ir.Constant(ir.DoubleType(), float(node))
            except ValueError:
                pass
        return None  # Default return for unresolved expressions

    def visit_binop(self, node):
        """Binary operator handling with division by zero check"""
        op, left, right = node
        
        if op in ['==', '!=', '>', '>=', '<', '<=']:
            # Handle comparison operators
            return self.visit_comparison((op, left, right))
        
        # Handle arithmetic operators
       # Handle arithmetic operators
        left_val = self.visit_expression(left)
        right_val = self.visit_expression(right)
        
        if op == '/':
            # Create basic blocks for division
            div_check_block = self.main.append_basic_block(name="div_check")
            div_ok_block = self.main.append_basic_block(name="div_ok")
            div_error_block = self.main.append_basic_block(name="div_error")
            div_continue_block = self.main.append_basic_block(name="div_continue")
            
            # Branch to division check
            self.builder.branch(div_check_block)
            
            # Division by zero check
            self.builder.position_at_start(div_check_block)
            zero = ir.Constant(ir.DoubleType(), 0.0)
            is_zero = self.builder.fcmp_ordered('==', right_val, zero)
            self.builder.cbranch(is_zero, div_error_block, div_ok_block)
            
            # Division error block
            self.builder.position_at_start(div_error_block)
            self.create_error_handling_printf("Error: Division by zero!")
            self.builder.branch(div_continue_block)
            
            # OK block - perform division
            self.builder.position_at_start(div_ok_block)
            div_result = self.builder.fdiv(left_val, right_val)
            self.builder.branch(div_continue_block)
            
            # Continue block
            self.builder.position_at_start(div_continue_block)
            phi = self.builder.phi(ir.DoubleType())
            phi.add_incoming(ir.Constant(ir.DoubleType(), 0.0), div_error_block)
            phi.add_incoming(div_result, div_ok_block)
            return phi
        
        # Handle other arithmetic operations
        if op == '+':
            return self.builder.fadd(left_val, right_val)
        elif op == '-':
            return self.builder.fsub(left_val, right_val)
        elif op == '*':
            return self.builder.fmul(left_val, right_val)
        elif op in ('**', '^'):
            # Handle exponentiation
            pow_func_type = ir.FunctionType(ir.DoubleType(), [ir.DoubleType(), ir.DoubleType()])
            pow_func = self.module.globals.get('pow') or ir.Function(self.module, pow_func_type, 'pow')
            return self.builder.call(pow_func, [left_val, right_val])
        
    def visit_comparison(self, node):
        """Comparison operator handling"""
        op, left_val, right_val = node
        
        # Get the values for comparison
        left_val = self.visit_expression(left_val)
        right_val = self.visit_expression(right_val)
        
        # Ensure we're comparing doubles
        if not isinstance(left_val.type, ir.DoubleType):
            left_val = self.builder.sitofp(left_val, ir.DoubleType())
        if not isinstance(right_val.type, ir.DoubleType):
            right_val = self.builder.sitofp(right_val, ir.DoubleType())
        
        # Map comparison operators to LLVM fcmp predicates
        op_map = {
            '==': 'oeq',  # ordered and equal
            '!=': 'one',  # ordered and not equal
            '<': 'olt',   # ordered and less than
            '<=': 'ole',  # ordered and less than or equal
            '>': 'ogt',   # ordered and greater than
            '>=': 'oge'   # ordered and greater than or equal
        }
        
        # Perform the comparison and return a double (1.0 for true, 0.0 for false)
        comparison = self.builder.fcmp_ordered(op_map[op], left_val, right_val)
        result = self.builder.uitofp(comparison, ir.DoubleType())
        return result

    
    def visit_unary(self, node):
        op, operand = node
        expr_val = self.visit_expression(operand)
        if op == '-':
            zero = ir.Constant(ir.DoubleType(), 0.0)
            return self.builder.fsub(zero, expr_val)
        elif op == 'not':
            return self.builder.not_(expr_val)
        return None
    
    def visit_break(self, node):
        if self.loop_stack:
            _, end_block = self.loop_stack[-1]
            self.builder.branch(end_block)

def compile_code(ast):
    codegen = CodeGenerator()
    codegen.generate_code(ast)
    return str(codegen.module)