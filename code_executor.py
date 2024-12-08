import llvmlite.binding as llvm
import ctypes
from ctypes import CFUNCTYPE, c_int32, c_char_p, POINTER
from llvmlite import ir
import platform



def execute_ir(ir_code):
    # Initialize LLVM
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    try:
        # Create module from IR
        module = llvm.parse_assembly(ir_code)
        module.verify()  # Verify the module
        
        # Create execution engine
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        target_machine.set_asm_verbosity(True)
        
        # Create execution engine
        backing_mod = llvm.parse_assembly("")
        engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
        
        # Add the module and make sure it is ready for execution
        engine.add_module(module)
        engine.finalize_object()
        
        # Get C library for printf
        if platform.system() == 'Windows':
            c_lib = ctypes.CDLL('msvcrt')
        else:
            if platform.system() == 'Darwin':
                c_lib = ctypes.CDLL('libc.dylib')
            else:
                c_lib = ctypes.CDLL('libc.so.6')
        
        # Set up printf
        printf = c_lib.printf
        printf.argtypes = [c_char_p]
        printf.restype = c_int32
        
        # Get main function pointer
        func_ptr = engine.get_function_address("main")
        
        # Create callable
        cfunc = CFUNCTYPE(None)(func_ptr)
        
        # Call main function
        cfunc()
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        raise