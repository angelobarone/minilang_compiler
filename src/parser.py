from src.tokens import TokenType
import src.ast_nodes as ast

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume(self, expected_type=None):
        token = self.peek()
        if not token or token.type == TokenType.EOF:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, found {token.type} at position {self.pos}")

        self.pos += 1
        return token

    def check(self, token_type):
        token = self.peek()
        return token and token.type == token_type

    def match(self, *types):
        for t in types:
            if self.check(t):
                self.consume()
                return True
        return False

    def parse(self):
        decls = []
        while self.peek() and not self.check(TokenType.EOF):
            decls.append(self.parse_decl())
        return ast.Program(decls)

    def parse_decl(self):
        if self.check(TokenType.EXTERN):
            return self.parse_extern_decl()
        elif self.check(TokenType.FUNC):
            return self.parse_func_decl()
        elif self.check(TokenType.LET):
            return self.parse_var_decl()
        else:
            raise SyntaxError(f"Unexpected token at global scope: {self.peek()}")

    def parse_extern_decl(self):
        self.consume(TokenType.EXTERN)
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.ID).value
        self.consume(TokenType.LPAREN)
        params = self.parse_params()
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.SEMI)
        return ast.ExternDecl(name, params)

    def parse_func_decl(self):
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.ID).value
        self.consume(TokenType.LPAREN)
        params = self.parse_params()
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.LBRACE)
        body = self.parse_stmts()
        self.consume(TokenType.RBRACE)
        return ast.FunctionDecl(name, params, ast.Block(body))

    def parse_var_decl(self):
        self.consume(TokenType.LET)
        name = self.consume(TokenType.ID).value
        self.consume(TokenType.ASSIGN)
        expr = self.parse_expr()
        self.consume(TokenType.SEMI)
        return ast.VarDecl(name, expr)

    def parse_params(self):
        params = []
        if self.check(TokenType.ID):
            params.append(self.consume(TokenType.ID).value)
            while self.match(TokenType.COMMA):
                params.append(self.consume(TokenType.ID).value)
        return params

    def parse_stmts(self):
        stmts = []
        while self.peek() and not self.check(TokenType.RBRACE) and not self.check(TokenType.EOF):
            stmts.append(self.parse_stmt())
        return stmts

    def parse_stmt(self):
        if self.check(TokenType.LET):
            return self.parse_var_decl()
        elif self.check(TokenType.RETURN):
            self.consume(TokenType.RETURN)
            expr = self.parse_expr()
            self.consume(TokenType.SEMI)
            return ast.ReturnStmt(expr)
        elif self.check(TokenType.IF):
            return self.parse_if_stmt()
        elif self.check(TokenType.WHILE):
            return self.parse_while_stmt()
        elif self.check(TokenType.REPEAT):
            return self.parse_repeat_stmt()
        else:
            expr = self.parse_expr()
            self.consume(TokenType.SEMI)
            return ast.ExprStmt(expr)

    def parse_if_stmt(self):
        self.consume(TokenType.IF)
        self.consume(TokenType.LPAREN)
        cond = self.parse_expr()
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.LBRACE)
        then_stmts = self.parse_stmts()
        self.consume(TokenType.RBRACE)

        else_block = None
        if self.match(TokenType.ELSE):
            self.consume(TokenType.LBRACE)
            else_stmts = self.parse_stmts()
            self.consume(TokenType.RBRACE)
            else_block = ast.Block(else_stmts)

        return ast.IfStmt(cond, ast.Block(then_stmts), else_block)

    def parse_while_stmt(self):
        self.consume(TokenType.WHILE)
        self.consume(TokenType.LPAREN)
        cond = self.parse_expr()
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.LBRACE)
        body = self.parse_stmts()
        self.consume(TokenType.RBRACE)
        return ast.WhileStmt(cond, ast.Block(body))

    def parse_repeat_stmt(self):
        self.consume(TokenType.REPEAT)
        self.consume(TokenType.LPAREN)
        count = self.parse_expr()
        self.consume(TokenType.RPAREN)
        self.consume(TokenType.LBRACE)
        body = self.parse_stmts()
        self.consume(TokenType.RBRACE)
        return ast.RepeatStmt(count, ast.Block(body))

    def parse_expr(self):
        return self.parse_pipe_expr()

    def parse_pipe_expr(self):
        left = self.parse_assign_expr()
        if self.match(TokenType.PIPE):
            right = self.parse_pipe_expr()
            return ast.PipeExpr(left, right)
        return left

    def parse_assign_expr(self):
        if self.check(TokenType.ID) and self.peek(1) and self.peek(1).type == TokenType.ASSIGN:
            name = self.consume(TokenType.ID).value
            self.consume(TokenType.ASSIGN)
            value = self.parse_logic_expr()
            return ast.AssignExpr(name, value)
        return self.parse_logic_expr()

    def parse_logic_expr(self):
        left = self.parse_equality_expr()
        while self.check(TokenType.AND) or self.check(TokenType.OR):
            op = self.consume().type
            right = self.parse_equality_expr()
            left = ast.BinaryExpr(left, op, right)
        return left

    def parse_equality_expr(self):
        left = self.parse_rel_expr()
        while self.check(TokenType.EQ) or self.check(TokenType.NE):
            op = self.consume().type
            right = self.parse_rel_expr()
            left = ast.BinaryExpr(left, op, right)
        return left

    def parse_rel_expr(self):
        left = self.parse_add_expr()
        while self.check(TokenType.LT) or self.check(TokenType.GT) or \
                self.check(TokenType.LE) or self.check(TokenType.GE):
            op = self.consume().type
            right = self.parse_add_expr()
            left = ast.BinaryExpr(left, op, right)
        return left

    def parse_add_expr(self):
        left = self.parse_mul_expr()
        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            op = self.consume().type
            right = self.parse_mul_expr()
            left = ast.BinaryExpr(left, op, right)
        return left

    def parse_mul_expr(self):
        left = self.parse_unary_expr()
        while self.check(TokenType.MUL) or self.check(TokenType.DIV):
            op = self.consume().type
            right = self.parse_unary_expr()
            left = ast.BinaryExpr(left, op, right)
        return left

    def parse_unary_expr(self):
        if self.check(TokenType.MINUS) or self.check(TokenType.NOT):
            op = self.consume().type
            operand = self.parse_unary_expr()
            return ast.UnaryExpr(op, operand)
        return self.parse_primary()

    # Lambda Lookahead
    def is_lambda_lookahead(self):
        offset = 1
        if self.peek(offset) and self.peek(offset).type == TokenType.RPAREN:
            return self.peek(offset + 1) and self.peek(offset + 1).type == TokenType.ARROW

        if self.peek(offset) and self.peek(offset).type == TokenType.ID:
            offset += 1
            while True:
                token = self.peek(offset)
                if not token: return False

                if token.type == TokenType.RPAREN:
                    return self.peek(offset + 1) and self.peek(offset + 1).type == TokenType.ARROW

                elif token.type == TokenType.COMMA:
                    offset += 1
                    if not (self.peek(offset) and self.peek(offset).type == TokenType.ID):
                        return False
                    offset += 1
                else:
                    return False
        return False

    def parse_primary(self):
        if self.check(TokenType.INTEGER):
            return ast.LiteralExpr(self.consume().value)

        elif self.check(TokenType.ID):
            if self.peek(1) and self.peek(1).type == TokenType.LPAREN:
                return self.parse_call()
            else:
                return ast.VariableExpr(self.consume(TokenType.ID).value)

        elif self.check(TokenType.LPAREN):
            if self.is_lambda_lookahead():
                self.consume(TokenType.LPAREN)
                params = self.parse_params()
                self.consume(TokenType.RPAREN)
                self.consume(TokenType.ARROW)
                body = self.parse_expr()
                return ast.LambdaExpr(params, body)
            else:
                self.consume(TokenType.LPAREN)
                expr = self.parse_expr()
                self.consume(TokenType.RPAREN)
                return expr

        raise SyntaxError(f"Unexpected token in expression: {self.peek()}")

    def parse_call(self):
        name = self.consume(TokenType.ID).value
        self.consume(TokenType.LPAREN)
        args = []
        if not self.check(TokenType.RPAREN):
            args.append(self.parse_expr())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expr())
        self.consume(TokenType.RPAREN)
        return ast.CallExpr(name, args)