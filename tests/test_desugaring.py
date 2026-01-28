import unittest
import src.ast_nodes as ast
from src.tokens import TokenType
from src.desugaring import Desugarer

class TestDesugaring(unittest.TestCase):
    def setUp(self):
        self.desugarer = Desugarer()

    def test_desugaring_pipe_LiteralExpr(self):
        # x |> f  ->  f(x)
        pipe_expr = ast.PipeExpr(
            left=ast.VariableExpr("x"),
            right=ast.VariableExpr("f")
        )

        res = self.desugarer.visit_PipeExpr(pipe_expr)

        self.assertIsInstance(res, ast.CallExpr)
        self.assertEqual(res.callee, "f")
        self.assertEqual(res.args[0].name, "x")

    def test_desugaring_pipe_CallExpr(self):
        # x |> f(y)  ->  f(x, y)
        pipe_expr = ast.PipeExpr(
            left=ast.VariableExpr("x"),
            right=ast.CallExpr("f", [ast.VariableExpr("y")])
        )
        res = self.desugarer.visit_PipeExpr(pipe_expr)

        self.assertIsInstance(res, ast.CallExpr)
        self.assertEqual(res.callee, "f")
        self.assertEqual(len(res.args), 2)
        self.assertEqual(res.args[0].name, "x")

    def test_desugaring_repeat(self):
        # repeat(5) { body } -> var decl + while
        repeat_node = ast.RepeatStmt(
            count=ast.LiteralExpr(5),
            body=ast.Block([])
        )

        stmts = self.desugarer.visit_RepeatStmt(repeat_node)

        self.assertEqual(len(stmts), 2)
        self.assertIsInstance(stmts[0], ast.VarDecl)
        self.assertIsInstance(stmts[1], ast.WhileStmt)

        while_stmt = stmts[1]
        self.assertEqual(while_stmt.condition.operator, TokenType.LT)

    def test_pipe_invalid_right_operand(self):
        # x |> 5 -> Errore, 5 non è chiamabile
        pipe_expr = ast.PipeExpr(
            left=ast.VariableExpr("x"),
            right=ast.LiteralExpr(5)
        )
        with self.assertRaises(ValueError) as cm:
            self.desugarer.visit_PipeExpr(pipe_expr)

if __name__ == '__main__':
    unittest.main()