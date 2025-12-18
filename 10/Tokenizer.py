from enum import StrEnum, auto
from dataclasses import dataclass
import xml.etree.ElementTree as ET
import re

class TokenizerError(Exception):
    def __init__(self, message="Invalid input provided"):
        self.message = message;
        super().__init__(message)


class TokenType(StrEnum):
    keyword = auto()
    symbol = auto()
    integerConstant = auto()
    stringConstant = auto()
    identifier = auto()

    def __str__(self):
        return self.name


@dataclass(frozen=True)
class Token():
    Ttype  : TokenType
    word   : str
    line   : str
    lineno : int


class Tokenizer:
    def __init__(self, file_name):
        self.file_name = file_name
        self.tokens = ()
    
    def get_tokens(self):
        return self.tokens
    
    def write_to_xml(self, file_name):
        root = ET.Element("tokens")
        for token in self.tokens:
            tmp = ET.SubElement(root, token.Ttype.__str__())
            tmp.text = f" {token.word} "
        tree = ET.ElementTree(root)
        ET.indent(tree, space="")
        tree.write(file_name, encoding="utf-8")
    
    def tokenize_helper(self):
        in_multiline_comment = False
        comment_pattern = re.compile(r'(/\*|//|\*/)')
        with open(self.file_name, "r") as f:
            for line_num, original_line in enumerate(f, 1):
                processed_line = ""
                parts = comment_pattern.split(original_line)
                for part in parts:
                    if in_multiline_comment:
                        if part == '*/':
                            in_multiline_comment = False
                    else:
                        if part == '//':
                            break
                        elif part == '/*':
                            in_multiline_comment = True
                        elif part:
                            processed_line += part
                final_line = processed_line.strip()
                if final_line:
                    yield (line_num, final_line)

    def find_all_tokens(self, line):
        tokens = []
        i = 0
        n = len(line)
        symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}
        while i < n:
            char = line[i]
            if char.isspace():
                i += 1
                continue

            if char in symbols:
                tokens.append(char)
                i += 1
                continue

            if char == '"':
                start = i
                i += 1
                while i < n and line[i] != '"':
                    i += 1
                i += 1
                tokens.append(line[start:i])
                continue

            if char.isdigit():
                start = i
                while i < n and line[i].isdigit():
                    i += 1
                tokens.append(line[start:i])
                continue

            if char.isalpha() or char == '_':
                start = i
                while i < n and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                tokens.append(line[start:i])
                continue
            i += 1
        return tokens

    def tokenize(self):
        lines = list(self.tokenize_helper())
        res = []
        for i, line in lines:
            linetokens = (toks for toks in self.find_all_tokens(line))
            res.extend((self.tokenclassifier(a, line, i) for a in linetokens if a))
        self.tokens = tuple(res)

    def tokenclassifier(self, s:str, line: str, lineno: int):
        match s:
            case 'class' | 'constructor' | 'function' | 'method' | 'field' | 'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' | 'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 'while' | 'return' :
                return Token(TokenType.keyword, s, line, lineno)
            case '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' :
                return Token(TokenType.symbol, s, line, lineno)
        if s.isnumeric():
            if int(s) < 32768:
                return Token(TokenType.integerConstant, s, line, lineno)
            else:
                raise TokenizerError(f"The integer {s} is not within the bounds 0 .. 32767.\n Line({lineno}): {line}")
        elif s.startswith('"') and s.endswith('"'):
            return Token(TokenType.stringConstant, s[1:-1], line, lineno)
        elif s.isidentifier():
            return Token(TokenType.identifier, s, line, lineno)
        else:
            raise TokenizerError(f"The token {s} couldn't parsed. \n Line({lineno}): {line}")
        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog = "My Jack language Tokenizer",
        description = "Chakradhar's Jack language tokenizer"
    )
    parser.add_argument("file_location", help = "location of assembly file.")
    parser.add_argument("-o", "--output", default = None, help = "Output hack file location.")
    args = parser.parse_args()
    if args.output is None:
        args.output = args.file_location.rsplit('.', 1)[0] + "T2.xml"
    tokenizer = Tokenizer(args.file_location)
    tokenizer.tokenize()
    tokenizer.write_to_xml(args.output)
