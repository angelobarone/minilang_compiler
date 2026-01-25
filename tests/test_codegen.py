import unittest
from llvmlite import ir
import src.ast_nodes as ast
from src.tokens import TokenType
from src.codegen import LLVMCodeGen

class TestLLVMCodeGen(unittest.TestCase):
    def setUp(self):
        self.codegen = LLVMCodeGen()

    def assertIRContains(self, ir_code, expected_snippet):
        if expected_snippet not in ir_code:
            self.fail(f"IR generato non contiene: '{expected_snippet}'\n\nIR Completo:\n{ir_code}")

    def test_empty_function(self):
        func_decl = ast.FunctionDecl(
            name="main",
            params=[],
            body=ast.Block(statements=[])
        )
        program = ast.Program(declarations=[func_decl])

        ir_code = self.codegen.generate_code(program)

        self.assertIRContains(ir_code, 'define i64 @"main"()')
        self.assertIRContains(ir_code, "ret i64 0")

    def test_arithmetic_ops(self):
        # return 10 + 5;
        expr = ast.BinaryExpr(
            left=ast.LiteralExpr(10),
            operator=TokenType.PLUS,
            right=ast.LiteralExpr(5)
        )
        stmt = ast.ReturnStmt(expr)
        func = ast.FunctionDecl("math_test", [], ast.Block([stmt]))
        program = ast.Program([func])

        ir_code = self.codegen.generate_code(program)

        self.assertIRContains(ir_code, "add i64 10, 5")
        self.assertIRContains(ir_code, "ret i64")

    def test_variable_declaration_and_usage(self):
        # let x = 42; return x;
        stmts = [
            ast.VarDecl(name="x", initializer=ast.LiteralExpr(42)),
            ast.ReturnStmt(ast.VariableExpr(name="x"))
        ]
        func = ast.FunctionDecl("var_test", [], ast.Block(stmts))
        program = ast.Program([func])

        ir_code = self.codegen.generate_code(program)

        self.assertIRContains(ir_code, '%"x" = alloca i64')
        self.assertIRContains(ir_code, 'store i64 42, i64* %"x"')
        self.assertIRContains(ir_code, 'load i64, i64* %"x"')

    def test_extern_call(self):
        # extern func print(n);
        # func main() { print(10); }
        extern_decl = ast.ExternDecl(name="print", params=["n"])

        call_expr = ast.CallExpr(callee="print", args=[ast.LiteralExpr(10)])
        func_decl = ast.FunctionDecl("main", [], ast.Block([ast.ExprStmt(call_expr)]))

        program = ast.Program([extern_decl, func_decl])

        ir_code = self.codegen.generate_code(program)

        self.assertIRContains(ir_code, 'declare i64 @"print"(i64 %".1")')
        self.assertIRContains(ir_code, 'call i64 @"print"(i64 10)')

    def test_if_else_logic(self):
        # if (1 < 2) { return 100; } else { return 200; }

        condition = ast.BinaryExpr(
            ast.LiteralExpr(1), TokenType.LT, ast.LiteralExpr(2)
        )

        if_stmt = ast.IfStmt(
            condition=condition,
            then_branch=ast.Block([ast.ReturnStmt(ast.LiteralExpr(100))]),
            else_branch=ast.Block([ast.ReturnStmt(ast.LiteralExpr(200))])
        )

        func = ast.FunctionDecl("cond_test", [], ast.Block([if_stmt]))
        program = ast.Program([func])

        ir_code = self.codegen.generate_code(program)

        self.assertIRContains(ir_code, "icmp slt i64 1, 2")
        self.assertIRContains(ir_code, "br i1")
        self.assertIRContains(ir_code, "then:")
        self.assertIRContains(ir_code, "else:")
        self.assertIRContains(ir_code, "if_cont:")

    def test_while_loop(self):
        # while (x > 0) { x = x - 1; }

        init = ast.VarDecl("x", ast.LiteralExpr(10))

        cond = ast.BinaryExpr(ast.VariableExpr("x"), TokenType.GT, ast.LiteralExpr(0))

        sub_op = ast.BinaryExpr(ast.VariableExpr("x"), TokenType.MINUS, ast.LiteralExpr(1))
        assign = ast.AssignExpr("x", sub_op)

        while_stmt = ast.WhileStmt(cond, ast.Block([ast.ExprStmt(assign)]))

        func = ast.FunctionDecl("loop_test", [], ast.Block([init, while_stmt]))
        program = ast.Program([func])

        ir_code = self.codegen.generate_code(program)

        self.assertIRContains(ir_code, "while_cond:")
        self.assertIRContains(ir_code, "while_body:")
        self.assertIRContains(ir_code, "while_after:")
        # loop back
        self.assertIRContains(ir_code, 'br label %"while_cond"')

if __name__ == '__main__':
    unittest.main()