A_COMP = {"0": 42, "1": 63, "-1": 58, "D": 12, "A": 48, "M": 112, "!D": 13, "!A": 49, "!M": 113, "-D": 15, "-A": 51,"-M": 115, "D+1" : 31, "A+1": 55, "M+1": 119, "D-1": 14, "A-1": 50, "M-1": 114, "D+A": 2, "D+M": 66, "D-A": 19, "D-M": 83, "A-D": 7, "M-D": 71, "D&A": 0, "D&M": 64, "D|A":21, "D|M":85}

DEST = {"":0, "M": 1, "D": 2, "DM": 3, "MD": 3, "A": 4, "AM": 5, "MA" : 5, "AD": 6, "DA": 6, "ADM": 7}

JUMP = {"":0,"JGT": 1, "JEQ": 2, "JGE": 3, "JLT": 4, "JNE": 5, "JLE": 6, "JMP": 7}

def compileHACKwithoutsymbols(further_stripped, lines, output):
    compiled_HACK = ""
    for item,lineno in further_stripped:
        if item[0] == "@":
            if not item[1:].isdigit() or int(item[1:]) > (1 << 16 - 1):
                print(lineno)
                raise Exception(f"Invalid number {item[1:]} - at line {lineno} - {lines[lineno-1][1]}")
            compiled_HACK += (str(format(int(item[1:]), "016b")) +"\n")
        else:
            comp = dest = jump = ""
            if ';' in item:
                item, jump = item.split(';')
            if '=' in item:
                dest, comp = item.split('=')
            else:
                comp = item
            comp = comp.strip()
            dest = dest.strip()
            jump = jump.strip()
            compiled_HACK += "1"*3 + format(A_COMP[comp], "07b") + format(DEST[dest], "03b") + format(JUMP[jump], "03b")+"\n"
    if output:
        with open(output, "w") as f:
            f.write(compiled_HACK)
    else:
        print(compiled_HACK)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog = "My Basic Hack Assembler",
        description = "Chakradhar's HACK assembler with no symbols"
    )
    parser.add_argument("file_location", help = "location of assembly file.")
    parser.add_argument("-o", "--output", default = None, help = "Output hack file location.")
    args = parser.parse_args()
    further_stripped = []
    lines = []
    with open(args.file_location, 'r') as f:
        lines = [(i+1,x.strip()) for i,x in enumerate(f.readlines())]
        comments_stripped = [(line.split("//")[0],i) for i,line in lines]
        further_stripped = [(line,i) for line,i in comments_stripped if line != '']
    compileHACKwithoutsymbols(further_stripped, lines, args.output)
