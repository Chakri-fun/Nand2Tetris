import argparse
from my_basic_assembler import compileHACKwithoutsymbols

parser = argparse.ArgumentParser(
    prog = "My Hack Assembler",
    description = "Chakradhar's HACK assembler with no symbols"
)

parser.add_argument("file_location", help = "location of assembly file.")
parser.add_argument("-o", "--output", default = None, help = "Output hack file location.")

args = parser.parse_args()
further_stripped = []
lines = []
symbols = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15, "SCREEN": 16384, "KBD": 24576, "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4}

with open(args.file_location, 'r') as f:
    lines = [(i+1,x.strip()) for i,x in enumerate(f.readlines())]
    comments_stripped = [(line.split("//")[0].strip(),i) for i,line in lines]
    further_stripped = [(line,i) for line,i in comments_stripped if line != '']

variable_address = 16
counter = 0
for item,lineno in further_stripped:
	if item[0] == "(":
		if item[-1] == ")":
			if item[1:len(item)-1] not in symbols:
				symbols[item[1:len(item)-1]] = counter
				counter -= 1
			else:
				raise Exception(f"You are trying to override {item} - at line {lineno} - {lines[lineno-1][1]}")
		else:
			raise Exception(f"Invalid syntax {item} - at line {lineno} - {lines[lineno-1][1]}")
	counter += 1

further_stripped = [x for x in further_stripped if not x[0].startswith("(")]

for i,(item,lineno) in enumerate(further_stripped):
	if item[0] == "@":
		if not item[1].isdigit():
			if item[1:] not in symbols:
				symbols[item[1:]] = variable_address
				variable_address += 1
			further_stripped[i] = ("@" + str(symbols[item[1:]]), lineno)
		elif not item[1:].isdigit():
			raise Exception(f"Invalid symbol {item[1:]} - at line {lineno} - {lines[lineno-1][1]}")

if args.output is None:
    args.output = args.file_location.rsplit('.', 1)[0] + ".hack"
compileHACKwithoutsymbols(further_stripped, lines, args.output)
