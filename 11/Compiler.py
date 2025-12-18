from Tokenizer import Tokenizer, Token, TokenType
from os import path

class CompilerError(Exception):
    def __init__(self, message="Invalid input provided"):
        self.message = message;
        self.i = 0
        super().__init__(message)

class Compiler:
    def __init__(self, file_name):
        self.file_name = file_name
        tokenizer = Tokenizer(file_name)
        tokenizer.tokenize()
        self.tokens: tuple[Token] = tokenizer.get_tokens()
        self.output = []
        self.labelNum = 0
        self.static_count = 0

    
    def compileFileAndWrite(self, file_name):
        self.compileClass()
        compiled = "\n".join(self.output)
        with open(file_name, "w") as f:
            f.write(compiled)
    
    def compileClass(self):
        self.class_symbol_table = {}
        self.field_count = 0
        self.total_count = 0
        if(self.tokens[0].Ttype != TokenType.keyword or self.tokens[0].word != "class"):
            raise CompilerError(f"The token {self.token[0].word} must be equal to 'class'. \n Line({self.token[0].lineno}): {self.token[0].line}")
        if(self.tokens[1].Ttype != TokenType.identifier or self.tokens[1].word != path.basename(self.file_name).split('.')[0]):
            raise CompilerError(f"The token {self.token[1].word} must be same as '[filename]' (The program is located in [filename].jack). \n Line({self.token[1].lineno}): {self.token[1].line}")
        if(self.tokens[2].Ttype != TokenType.symbol or self.tokens[2].word != "{"):
            raise CompilerError(f"The token {self.token[2].word} must be equal to '{{'. \n Line({self.token[2].lineno}): {self.token[2].line}")
        self.currentClassName = self.tokens[1].word
        self.class_name = self.currentClassName
        self.i = 3
        self.compileClassVarDec()
        self.compileSubroutineDec()
        if(self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "}"):
            raise CompilerError(f"The token {self.token[2].word} must be equal to '}}'. \n Line({self.token[2].lineno}): {self.token[2].line}")
        
    def compileClassVarDec(self):
        while self.i < len(self.tokens):
            if self.tokens[self.i].Ttype != TokenType.keyword or self.tokens[self.i].word not in ("static", "field"):
                return

            kind = self.tokens[self.i].word
            self.i += 1
            if self.tokens[self.i].Ttype not in (TokenType.keyword, TokenType.identifier):
                raise CompilerError(f"The token {self.tokens[self.i].word} must be a type. \n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            vtype = self.tokens[self.i].word
            self.i += 1
            if self.tokens[self.i].Ttype != TokenType.identifier:
                raise CompilerError(f"The token {self.tokens[self.i].word} must be an identifier token. \n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            name = self.tokens[self.i].word
            index = self.static_count if kind == "static" else self.field_count
            if kind == "field":
                self.class_symbol_table[name] = ("this", vtype, name, index)
            else:
                self.class_symbol_table[name] = (kind, vtype, name, index)
            if kind == "static":
                self.static_count += 1
            else:
                self.field_count += 1
            self.total_count += 1
            self.i += 1
            while self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == ",":
                self.i += 1
                if self.tokens[self.i].Ttype != TokenType.identifier:
                    raise CompilerError(f"The token {self.tokens[self.i].word} must be identifier after comma. \n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
                name = self.tokens[self.i].word
                index = self.static_count if kind == "static" else self.field_count
                if kind == "field":
                    self.class_symbol_table[name] = ("this", vtype, name, index)
                else:
                    self.class_symbol_table[name] = (kind, vtype, name, index)
                if kind == "static":
                    self.static_count += 1
                else:
                    self.field_count += 1
                self.total_count += 1
                self.i += 1
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ";":
                raise CompilerError(f"The token {self.tokens[self.i].word} must be equal to ';'. \n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1

    def compileSubroutineDec(self):
        while self.i < len(self.tokens):
            if self.tokens[self.i].Ttype != TokenType.keyword or self.tokens[self.i].word not in ("constructor", "function", "method"):
                return
            subroutine_type = self.tokens[self.i].word
            self.i += 1
            if self.tokens[self.i].Ttype != TokenType.keyword and self.tokens[self.i].Ttype != TokenType.identifier:
                raise CompilerError(f"Expected type or void, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            if self.tokens[self.i].Ttype != TokenType.identifier:
                raise CompilerError(f"Expected subroutine name, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            subroutine_name = self.tokens[self.i].word
            self.subroutine_symbol_table = {}
            self.local_count = 0
            self.argument_count = 0
            self.subroutine_total_count = 0
            self.currentSubroutineName = subroutine_name
            self.currentSubroutineType = subroutine_type
            self.i += 1
            if subroutine_type == "method":
                self.subroutine_symbol_table["this"] = ("argument", self.class_name, "this", 0)
                self.argument_count += 1
                self.subroutine_total_count += 1
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "(":
                raise CompilerError(f"Expected '(', got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            self.compileParameterList()
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ")":
                raise CompilerError(f"Expected ')', got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            self.compileSubroutineBody()
    
    def compileParameterList(self):
        if self.tokens[self.i].Ttype not in (TokenType.keyword, TokenType.identifier):
            return
        while True:
            if self.tokens[self.i].Ttype != TokenType.keyword and self.tokens[self.i].Ttype != TokenType.identifier:
                raise CompilerError(f"Expected type in parameter list, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            vtype = self.tokens[self.i].word
            self.i += 1
            if self.tokens[self.i].Ttype != TokenType.identifier:
                raise CompilerError(f"Expected parameter name, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            name = self.tokens[self.i].word
            self.subroutine_symbol_table[name] = ("argument", vtype, name, self.argument_count)
            self.argument_count += 1
            self.subroutine_total_count += 1
            self.i += 1
            if self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == ",":
                self.i += 1
                continue
            else:
                break
    
    def compileSubroutineBody(self):
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "{":
            raise CompilerError(f"Expected '{{' at subroutine body start, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.compileVarDec()
        self.output.append(f"function {self.class_name}.{self.currentSubroutineName} {self.local_count}")
        if self.currentSubroutineType == "constructor":
            self.output.append(f"push constant {self.field_count}")
            self.output.append("call Memory.alloc 1")
            self.output.append("pop pointer 0")
        if self.currentSubroutineType == "method":
            self.output.append("push argument 0")
            self.output.append("pop pointer 0")
        self.compileStatements()
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "}":
            raise CompilerError(f"Expected '}}' at end of subroutine body, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
    
    def compileVarDec(self):
        while self.tokens[self.i].Ttype == TokenType.keyword and self.tokens[self.i].word == "var":
            self.i += 1
            if self.tokens[self.i].Ttype not in (TokenType.keyword, TokenType.identifier):
                raise CompilerError(f"Expected type after 'var', got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            vtype = self.tokens[self.i].word
            self.i += 1
            if self.tokens[self.i].Ttype != TokenType.identifier:
                raise CompilerError(f"Expected variable name, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            name = self.tokens[self.i].word
            self.subroutine_symbol_table[name] = ("local", vtype, name, self.local_count)
            self.local_count += 1
            self.subroutine_total_count += 1
            self.i += 1
            while self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == ",":
                self.i += 1
                if self.tokens[self.i].Ttype != TokenType.identifier:
                    raise CompilerError(f"Expected variable name after ',', got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
                name = self.tokens[self.i].word
                self.subroutine_symbol_table[name] = ("local", vtype, name, self.local_count)
                self.local_count += 1
                self.subroutine_total_count += 1
                self.i += 1
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ";":
                raise CompilerError(f"Expected ';' at end of varDec, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1

    def compileStatements(self):
        while self.i < len(self.tokens) and self.tokens[self.i].Ttype == TokenType.keyword:
            match self.tokens[self.i].word:
                case "let":
                    self.compileLetStatement()
                case "if":
                    self.compileIfStatement()
                case "while":
                    self.compileWhileStatement()
                case "do":
                    self.compileDoStatement()
                case "return":
                    self.compileReturnStatement()
                case _:
                    return

    def lookup(self, name):
        if name in self.subroutine_symbol_table:
            return self.subroutine_symbol_table[name]
        if name in self.class_symbol_table:
            return self.class_symbol_table[name]
        raise CompilerError(f"Undeclared variable {name}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
    
    def compileLetStatement(self):
        if self.tokens[self.i].Ttype != TokenType.keyword or self.tokens[self.i].word != "let":
            raise CompilerError(f"Expected 'let' at start of letStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        if self.tokens[self.i].Ttype != TokenType.identifier:
            raise CompilerError(f"Expected variable name after let, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        var_name = self.tokens[self.i].word
        self.i += 1
        is_array = False
        if self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == "[":
            is_array = True
            self.i += 1
            self.compileExpression()
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "]":
                raise CompilerError(f"Expected ']' for array index, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            kind, _, _, index = self.lookup(var_name)
            
            self.output.append(f"push {kind} {index}")
            self.output.append("add")
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "=":
            raise CompilerError(f"Expected '=' in letStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.compileExpression()
        if is_array:
            self.output.append("pop temp 0")
            self.output.append("pop pointer 1")
            self.output.append("push temp 0")
            self.output.append("pop that 0")
        else:
            kind, _, _, index = self.lookup(var_name)
            self.output.append(f"pop {kind} {index}")
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ";":
            raise CompilerError(f"Expected ';' to end letStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1

    def compileReturnStatement(self):
        if self.tokens[self.i].Ttype != TokenType.keyword or self.tokens[self.i].word != "return":
            raise CompilerError(f"Expected 'return' at start of returnStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ";":
            self.compileExpression()
            self.output.append("return")
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ";":
                raise CompilerError(f"Expected ';' at end of returnStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
        else:
            self.output.append("push constant 0")
            self.output.append("return")
            self.i += 1

    def compileIfStatement(self):
        TlabelNum = self.labelNum
        self.labelNum += 2
        if self.tokens[self.i].Ttype != TokenType.keyword or self.tokens[self.i].word != "if":
            raise CompilerError(f"Expected 'if' at start of ifStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "(":
            raise CompilerError(f"Expected '(' after 'if', got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.compileExpression()
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ")":
            raise CompilerError(f"Expected ')' after expression in ifStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "{":
            raise CompilerError(f"Expected '{{' before if statements, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.output.append("not")
        self.output.append(f"if-goto {self.class_name}.Tlabel{TlabelNum}")
        self.compileStatements()
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "}":
            raise CompilerError(f"Expected '}}' after if statements, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.output.append(f"goto {self.class_name}.Tlabel{TlabelNum+1}")
        self.output.append(f"label {self.class_name}.Tlabel{TlabelNum}")
        if self.tokens[self.i].Ttype == TokenType.keyword and self.tokens[self.i].word == "else":
            self.i += 1
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "{":
                raise CompilerError(f"Expected '{{' before else statements, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            self.compileStatements()
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "}":
                raise CompilerError(f"Expected '}}' after else statements, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
        self.output.append(f"label {self.class_name}.Tlabel{TlabelNum+1}")

    def compileWhileStatement(self):
        TlabelNum = self.labelNum
        self.labelNum += 2
        if self.tokens[self.i].Ttype != TokenType.keyword or self.tokens[self.i].word != "while":
            raise CompilerError(f"Expected 'while' at start of whileStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "(":
            raise CompilerError(f"Expected '(' after 'while', got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.output.append(f"label {self.class_name}.Tlabel{TlabelNum}")
        self.compileExpression()
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ")":
            raise CompilerError(f"Expected ')' after expression in whileStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.output.append("not")
        self.output.append(f"if-goto {self.class_name}.Tlabel{TlabelNum+1}")
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "{":
            raise CompilerError(f"Expected '{{' before while body, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.compileStatements()
        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "}":
            raise CompilerError(f"Expected '}}' after while body, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        self.output.append(f"goto {self.class_name}.Tlabel{TlabelNum}")
        self.output.append(f"label {self.class_name}.Tlabel{TlabelNum+1}")

    def compileDoStatement(self):
        if self.tokens[self.i].Ttype != TokenType.keyword or self.tokens[self.i].word != "do":
            raise CompilerError(f"Expected 'do' at start of doStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1
        if self.tokens[self.i].Ttype != TokenType.identifier:
            raise CompilerError(f"Expected identifier after 'do', got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        id1 = self.tokens[self.i].word
        self.i += 1
        call_name = ""
        nP = 0
        if self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == ".":
            self.i += 1
            if self.tokens[self.i].Ttype != TokenType.identifier:
                raise CompilerError(f"Expected identifier after '.' in doStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            id2 = self.tokens[self.i].word
            self.i += 1
            if id1 in self.subroutine_symbol_table or id1 in self.class_symbol_table:
                kind, _, _, index = self.lookup(id1)
                self.output.append(f"push {kind} {index}")
                call_name = f"{self.lookup(id1)[1]}.{id2}"
                nP += 1
            else:
                call_name = f"{id1}.{id2}"
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "(":
                raise CompilerError(f"Expected '(' after subroutine call in doStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            n_args = self.compileExpressionList()
            nP += n_args
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ")":
                raise CompilerError(f"Expected ')' after arguments in doStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            self.output.append(f"call {call_name} {nP}")
            self.output.append("pop temp 0")
        else:
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "(":
                raise CompilerError(f"Expected '(' after subroutine name in doStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            self.output.append("push pointer 0")
            call_name = f"{self.class_name}.{id1}"
            n_args = self.compileExpressionList()
            nP = n_args + 1
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ")":
                raise CompilerError(f"Expected ')' after arguments in doStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            self.output.append(f"call {call_name} {nP}")
            self.output.append("pop temp 0")

        if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ";":
            raise CompilerError(f"Expected ';' at end of doStatement, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
        self.i += 1

    def compileExpressionList(self):
        nP = 0
        if self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == ")":
            return nP
        self.compileExpression()
        nP += 1
        while self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == ",":
            self.i += 1
            self.compileExpression()
            nP += 1
        return nP

    def compileExpression(self):
        self.compileTerm()
        while self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word in {"+", "-", "*", "/", "&", "|", ">", "<", "="}:
            op = self.tokens[self.i].word
            self.i += 1
            self.compileTerm()
            match op:
                case "+":
                    self.output.append("add")
                case "-":
                    self.output.append("sub")
                case "&":
                    self.output.append("and")
                case "|":
                    self.output.append("or")
                case ">":
                    self.output.append("gt")
                case "<":
                    self.output.append("lt")
                case "=":
                    self.output.append("eq")
                case "*":
                    self.output.append("call Math.multiply 2")
                case "/":
                    self.output.append("call Math.divide 2")

    def compileTerm(self):
        t = self.tokens[self.i]
        # unaryOp term
        if t.Ttype == TokenType.symbol and t.word in {"-", "~"}:
            op = t.word
            self.i += 1
            self.compileTerm()
            if op == "-":
                self.output.append("neg")
            if op == "~":
                self.output.append("not")
            return
        # integerConstant
        if t.Ttype == TokenType.integerConstant:
            self.output.append(f"push constant {t.word}")
            self.i += 1
            return
        # keywordConstant
        if t.Ttype == TokenType.keyword:
            match t.word:
                case "true":
                    self.output.append("push constant 0")
                    self.output.append("not")
                case "false" | "null":
                    self.output.append("push constant 0")
                case "this":
                    self.output.append("push pointer 0")
            self.i += 1
            return
        # varName (array, subroutine call, or simple variable)
        if t.Ttype == TokenType.identifier:
            name = t.word
            self.i += 1
            # array access: varName '[' expression ']'
            if self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == "[":
                self.i += 1
                self.compileExpression()
                if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "]":
                    raise CompilerError(f"Expected ']' for array index, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
                kind, _, _, index = self.lookup(name)
                self.output.append(f"push {kind} {index}")
                self.output.append("add")
                self.output.append("pop pointer 1")
                self.output.append("push that 0")
                self.i += 1
                return
            # subroutine call: varName ( '(' or '.' )
            if self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word in {"(", "."}:
                self.compileSubroutineCall(name)
                return
            # plain variable use
            kind, _, _, index = self.lookup(name)
            self.output.append(f"push {kind} {index}")
            return
        # stringConstant
        if t.Ttype == TokenType.stringConstant:
            s = t.word
            strlen = len(s)
            self.output.append(f"push constant {strlen}")
            self.output.append("call String.new 1")
            for char in s:
                self.output.append(f"push constant {ord(char)}")
                self.output.append("call String.appendChar 2")
            self.i += 1
            return
        # '(' expression ')'
        if t.Ttype == TokenType.symbol and t.word == "(":
            self.i += 1
            self.compileExpression()
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ")":
                raise CompilerError(f"Expected ')' after '(', got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            return

    def compileSubroutineCall(self, id1):
        if self.tokens[self.i].Ttype == TokenType.symbol and self.tokens[self.i].word == ".":
            self.i += 1
            if self.tokens[self.i].Ttype != TokenType.identifier:
                raise CompilerError(f"Expected identifier after '.' in subroutineCall, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            id2 = self.tokens[self.i].word
            self.i += 1
            call_name = ""
            nP = 0
            if id1 in self.subroutine_symbol_table or id1 in self.class_symbol_table:
                kind, type_, _, index = self.lookup(id1)
                self.output.append(f"push {kind} {index}")
                call_name = f"{type_}.{id2}"
                nP += 1
            else:
                call_name = f"{id1}.{id2}"
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "(":
                raise CompilerError(f"Expected '(' after subroutine name, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            n_args = self.compileExpressionList()
            nP += n_args
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ")":
                raise CompilerError(f"Expected ')' after arguments, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            self.output.append(f"call {call_name} {nP}")
            return
        else:
            call_name = f"{self.class_name}.{id1}"
            nP = 0
            self.output.append("push pointer 0")
            nP += 1
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != "(":
                raise CompilerError(f"Expected '(' after subroutine name, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            n_args = self.compileExpressionList()
            nP += n_args
            if self.tokens[self.i].Ttype != TokenType.symbol or self.tokens[self.i].word != ")":
                raise CompilerError(f"Expected ')' after arguments, got {self.tokens[self.i].word}.\n Line({self.tokens[self.i].lineno}): {self.tokens[self.i].line}")
            self.i += 1
            self.output.append(f"call {call_name} {nP}")
            return

if __name__ == "__main__":
    import argparse, os
    parser = argparse.ArgumentParser(
        prog = "My Jack language Compiler",
        description = "Chakradhar's Jack language compiler"
    )
    parser.add_argument("input_path", help = "location of Jack file.")
    args = parser.parse_args()

    input_path = args.input_path
    
    files_to_process = []
    if os.path.isdir(input_path):
        files_to_process = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(".jack")]
    elif os.path.isfile(input_path) and input_path.endswith(".jack"):
        files_to_process = [input_path]
    else:
        print(f"Error: Input path '{input_path}' is not a valid .jack file or directory.")
        exit(1)

    for file in files_to_process:
        compile = Compiler(file)
        compile.compileFileAndWrite(file[:-5] + ".vm")
