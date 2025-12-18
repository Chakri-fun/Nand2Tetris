import argparse
import os

label = 0

def parseCommand(commands, filename):
    result = ''
    for command in commands:
        if command[0] in ['push', 'pop']:
            result += MemoryAccess(command, filename)
        else:
            Arithmetic_Logic_list = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
            if command[0] in Arithmetic_Logic_list:
                result += Arithmetic_Logic(command)
    return result

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
    else:
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="My Basic VM translator",
        description="Chakradhar's VM translator"
    )
    parser.add_argument("file_location", help="location of VM file.")
    parser.add_argument("-o", "--output", default=None, help="Output asm file location.")
    args = parser.parse_args()
    commands = []
    with open(args.file_location, 'r') as f:
        lines = [x.strip() for x in f.readlines()]
        comments_stripped = [line.split("//")[0].strip() for line in lines]
        further_stripped = [line for line in comments_stripped if line != '']
        commands = [coms.split() for coms in further_stripped]

    filename = os.path.basename(args.file_location).rsplit('.', 1)[0]
    result = parseCommand(commands, filename)
    
    if args.output is None:
        args.output = args.file_location.rsplit('.', 1)[0] + ".asm"
        
    with open(args.output, "w") as f_out:
        f_out.write(result)
