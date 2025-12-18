import argparse
import os
from collections import defaultdict

label = 0
func_labels = defaultdict(lambda: 0)

def parseCommand(commands, filename):
    result = []
    Arithmetic_Logic_list = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
    for command in commands:
        if command[0] in ['push', 'pop']:
            result.append(MemoryAccess(command, filename))
        elif command[0] in Arithmetic_Logic_list:
            result.append(Arithmetic_Logic(command))
        elif command[0] in ["label", "goto", "if-goto"]:
            result.append(Branching_Logic(command))
        elif command[0] in ["call", "function", "return"]:
            result.append(Function_Logic(command, filename))
    return "\n".join(result)
    
def Function_Logic(command, filename):
    instruction = ""
    if command[0] == "function":
        name = command[1]
        local_vars = command[2]
        instruction = [f"({name})",]
        for _ in range(int(local_vars)):
            instruction.append(MemoryAccess(['push', 'constant', '0'], filename))
        instruction = "\n".join(instruction)
    elif command[0] == "call":
        name = command[1]
        nArgs = command[2]
        retLabel = f"{name}$ret.{func_labels[name]}"
        instruction = f"""
@{retLabel}
D=A
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@SP
A=M
M=D
@SP
M=M+1
@THIS
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
D=M
@5
D=D-A
@{nArgs}
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
@{name}
0;JMP
({retLabel})
"""
        func_labels[name] += 1
    elif command[0] == "return":
        instruction = """
@LCL
D=M
@R13
M=D
@5
A=D-A
D=M
@R14
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M+1
@SP
M=D
@R13
AM=M-1
D=M
@THAT
M=D
@R13
AM=M-1
D=M
@THIS
M=D
@R13
AM=M-1
D=M
@ARG
M=D
@R13
AM=M-1
D=M
@LCL
M=D
@R14
A=M
0;JMP
"""
    else:
        instruction = ""
    return instruction

def Branching_Logic(command):
    label = command[1]
    instruction = ""
    match command[0]:
        case "label":
            instruction = f"({label})\n"
        case "goto":
            instruction = f"""\
@{label}
0;JMP
"""
        case "if-goto":
            instruction = f"""\
@SP
AM=M-1
D=M
@{label}
D;JNE
"""
    return instruction

def MemoryAccess(command, filename):
    command_type = command[0]
    segment = command[1]
    index = command[2]
    instruction = ""
    
    segment_map = {
        'local': 'LCL',
        'argument': 'ARG',
        'this': 'THIS',
        'that': 'THAT'
    }

    if command_type == 'push':
        match segment:
            case 'constant':
                instruction = f'''\
@{index}
D=A
@SP
A=M
M=D
@SP
M=M+1
'''
            case 'local' | 'argument' | 'this' | 'that':
                base_address = segment_map[segment]
                instruction = f'''\
@{index}
D=A
@{base_address}
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
'''
            case 'temp':
                instruction = f'''\
@{index}
D=A
@5
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
'''
            case 'pointer':
                pointer_reg = 'THIS' if index == '0' else 'THAT'
                instruction = f'''\
@{pointer_reg}
D=M
@SP
A=M
M=D
@SP
M=M+1
'''
            case 'static':
                instruction = f'''\
@{filename}.{index}
D=M
@SP
A=M
M=D
@SP
M=M+1
'''
    else: # pop
        match segment:
            case 'local' | 'argument' | 'this' | 'that':
                base_address = segment_map[segment]
                instruction = f'''\
@{index}
D=A
@{base_address}
D=M+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
'''
            case 'temp':
                instruction = f'''\
@{index}
D=A
@5
D=A+D
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D
'''
            case 'pointer':
                pointer_reg = 'THIS' if index == '0' else 'THAT'
                instruction = f'''\
@SP
AM=M-1
D=M
@{pointer_reg}
M=D
'''
            case 'static':
                instruction = f'''\
@SP
AM=M-1
D=M
@{filename}.{index}
M=D
'''
    return instruction

def Arithmetic_Logic(command):
    global label
    instruction = ""
    match command[0]:
        case 'add':
            instruction = """\
@SP
AM=M-1
D=M
A=A-1
M=M+D
"""
        case 'sub':
            instruction = """\
@SP
AM=M-1
D=M
A=A-1
M=M-D
"""
        case 'and':
            instruction = """\
@SP
AM=M-1
D=M
A=A-1
M=D&M
"""
        case 'or':
            instruction = """\
@SP
AM=M-1
D=M
A=A-1
M=D|M
"""
        case 'neg':
            instruction = """\
@SP
A=M-1
M=-M
"""
        case 'not':
            instruction = """\
@SP
A=M-1
M=!M
"""
        case 'eq':
            true_label = f"JUMP_TRUE_{label}"
            instruction = f"""\
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=-1
@{true_label}
D;JEQ
@SP
A=M-1
M=0
({true_label})
"""
            label += 1
        case 'lt':
            true_label = f"JUMP_TRUE_{label}"
            instruction = f"""\
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=-1
@{true_label}
D;JLT
@SP
A=M-1
M=0
({true_label})
"""
            label += 1
        case 'gt':
            true_label = f"JUMP_TRUE_{label}"
            instruction = f"""\
@SP
AM=M-1
D=M
A=A-1
D=M-D
M=-1
@{true_label}
D;JGT
@SP
A=M-1
M=0
({true_label})
"""
            label += 1
    return instruction

def find_files_by_extension(directory_path, extension):
    found_files = []
    for filename in os.listdir(directory_path):
        if os.path.isfile(os.path.join(directory_path, filename)) and filename.endswith(extension):
            found_files.append(filename)
    return found_files

def parse_vm_file(file_path):
    commands = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
    comments_stripped = [line.split("//")[0].strip() for line in lines]
    further_stripped = [line for line in comments_stripped if line != '']
    commands = [coms.split() for coms in further_stripped]
    return commands

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="My Complete VM translator",
        description="Chakradhar's VM translator"
    )
    parser.add_argument("input_path", help="Location of the .vm file or directory.")
    parser.add_argument("-o", "--output", default=None, help="Output .asm file location.")
    args = parser.parse_args()

    input_path = args.input_path
    output_file = args.output
    
    files_to_process = []
    if os.path.isdir(input_path):
        if output_file is None:
            dir_name = os.path.basename(os.path.normpath(input_path))
            output_file = os.path.join(input_path, f"{dir_name}.asm")
        
        files_to_process = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(".vm")]
    elif os.path.isfile(input_path) and input_path.endswith(".vm"):
        if output_file is None:
            base_name = os.path.splitext(input_path)[0]
            output_file = f"{base_name}.asm"
        
        files_to_process = [input_path]
    else:
        print(f"Error: Input path '{input_path}' is not a valid .vm file or directory.")
        exit(1)

    final_asm = []
    has_sys_vm = any("Sys.vm" in os.path.basename(f) for f in files_to_process)
    
    if has_sys_vm:
        bootstrap_code = [
            "@256",
            "D=A",
            "@SP",
            "M=D",
        ]
        final_asm.append("\n".join(bootstrap_code))
        call_sys_init_asm = Function_Logic(["call", "Sys.init", "0"], "")
        final_asm.append(call_sys_init_asm)

    for vm_file in files_to_process:          
        commands = parse_vm_file(vm_file)
        filename_without_ext = os.path.splitext(os.path.basename(vm_file))[0]
        asm_from_file = parseCommand(commands, filename_without_ext)
        final_asm.append(asm_from_file)
    
    with open(output_file, "w") as f_out:
        f_out.write("\n".join(final_asm))
