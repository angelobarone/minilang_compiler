import unittest
from src.tokens import TokenType, Token
from src.parser import Parser
import src.ast_nodes as ast

class TestParser(unittest.TestCase):

    def setUp(self):
        pass

    def create_parser(self, tokens):
        if not tokens or tokens[-1].type != TokenType.EOF:
            tokens.append(Token(TokenType.EOF))
        return Parser(tokens)

    def test_precedenza(self):
        # Test: 1 + 2 * 3
        tokens = [
            Token(TokenType.INTEGER, 1),
            Token(TokenType.PLUS, '+'),
            Token(TokenType.INTEGER, 2),
            Token(TokenType.MUL, '*'),
            Token(TokenType.INTEGER, 3),
            Token(TokenType.SEMI, ';')
        ]
        parser = self.create_parser(tokens)
        stmt = parser.parse_stmt()

        self.assertIsInstance(stmt, ast.ExprStmt)
        expr = stmt.expr
        self.assertIsInstance(expr, ast.BinaryExpr)
        self.assertEqual(expr.operator, TokenType.PLUS)

        self.assertIsInstance(expr.right, ast.BinaryExpr)
        self.assertEqual(expr.right.operator, TokenType.MUL)
        self.assertEqual(expr.right.left.value, 2)
        self.assertEqual(expr.right.right.value, 3)

    def test_operatore_pipe(self):
        # Test: a |> b
        tokens = [
            Token(TokenType.ID, "a"),
            Token(TokenType.PIPE, "|>"),
            Token(TokenType.ID, "b"),
            Token(TokenType.SEMI, ';')
        ]
        parser = self.create_parser(tokens)
        stmt = parser.parse_stmt()

        self.assertIsInstance(stmt.expr, ast.PipeExpr)
        self.assertEqual(stmt.expr.left.name, "a")
        self.assertEqual(stmt.expr.right.name, "b")

    def test_dichiarazione_variabile(self):
        # Test: let x = 10;
        tokens = [
            Token(TokenType.LET),
            Token(TokenType.ID, "x"),
            Token(TokenType.ASSIGN),
            Token(TokenType.INTEGER, 10),
            Token(TokenType.SEMI)
        ]
        parser = self.create_parser(tokens)
        node = parser.parse_decl()

        self.assertIsInstance(node, ast.VarDecl)
        self.assertEqual(node.name, "x")
        self.assertEqual(node.initializer.value, 10)

    def test_dichiarazione_funzione(self):
        # Test: func add(a, b) { return a + b; }
        tokens = [
            Token(TokenType.FUNC),
            Token(TokenType.ID, "add"),
            Token(TokenType.LPAREN),
            Token(TokenType.ID, "a"),
            Token(TokenType.COMMA),
            Token(TokenType.ID, "b"),
            Token(TokenType.RPAREN),
            Token(TokenType.LBRACE),
            Token(TokenType.RETURN),
            Token(TokenType.ID, "a"),
            Token(TokenType.PLUS),
            Token(TokenType.ID, "b"),
            Token(TokenType.SEMI),
            Token(TokenType.RBRACE)
        ]
        parser = self.create_parser(tokens)
        node = parser.parse_decl()

        self.assertIsInstance(node, ast.FunctionDecl)
        self.assertEqual(node.name, "add")
        self.assertEqual(node.params, ["a", "b"])
        self.assertIsInstance(node.body, ast.Block)
        self.assertIsInstance(node.body.statements[0], ast.ReturnStmt)

    def test_dichiarazione_funzione_esterna(self):
        # Test: extern func print(n);
        tokens = [
            Token(TokenType.EXTERN),
            Token(TokenType.FUNC),
            Token(TokenType.ID, "print"),
            Token(TokenType.LPAREN),
            Token(TokenType.ID, "n"),
            Token(TokenType.RPAREN),
            Token(TokenType.SEMI)
        ]
        parser = self.create_parser(tokens)
        node = parser.parse_decl()

        self.assertIsInstance(node, ast.ExternDecl)
        self.assertEqual(node.name, "print")
        self.assertEqual(node.params, ["n"])

    # Statement e Loop Speciali
    def test_reapeat(self):
        # Test: repeat(5) { ... }
        tokens = [
            Token(TokenType.REPEAT),
            Token(TokenType.LPAREN),
            Token(TokenType.INTEGER, 5),
            Token(TokenType.RPAREN),
            Token(TokenType.LBRACE),
            # body vuoto
            Token(TokenType.RBRACE)
        ]
        parser = self.create_parser(tokens)
        stmt = parser.parse_stmt()

        self.assertIsInstance(stmt, ast.RepeatStmt)
        self.assertIsInstance(stmt.count, ast.LiteralExpr)
        self.assertEqual(stmt.count.value, 5)

    def test_while(self):
        # Test: while(x < 10) { ... }
        tokens = [
            Token(TokenType.WHILE),
            Token(TokenType.LPAREN),
            Token(TokenType.ID, "x"),
            Token(TokenType.LT),
            Token(TokenType.INTEGER, 10),
            Token(TokenType.RPAREN),
            Token(TokenType.LBRACE),
            Token(TokenType.RBRACE)
        ]
        parser = self.create_parser(tokens)
        stmt = parser.parse_stmt()

        self.assertIsInstance(stmt, ast.WhileStmt)
        self.assertIsInstance(stmt.condition, ast.BinaryExpr)

    # Il parser deve essere in grado di distinguere una variabile tra parentesi e l'espressione lambda
    def test_espressione_con_parentesi(self):
        # Test: (x)
        tokens = [
            Token(TokenType.LPAREN),
            Token(TokenType.ID, "x"),
            Token(TokenType.RPAREN),
            Token(TokenType.SEMI)
        ]
        parser = self.create_parser(tokens)
        stmt = parser.parse_stmt()

        self.assertIsInstance(stmt.expr, ast.VariableExpr)
        self.assertEqual(stmt.expr.name, "x")

    def test_espressione_lambda(self):
        # Test: (x) => x + 1
        tokens = [
            Token(TokenType.LPAREN),
            Token(TokenType.ID, "x"),
            Token(TokenType.RPAREN),
            Token(TokenType.ARROW, "=>"),
            Token(TokenType.ID, "x"),
            Token(TokenType.PLUS),
            Token(TokenType.INTEGER, 1),
            Token(TokenType.SEMI)
        ]
        parser = self.create_parser(tokens)
        stmt = parser.parse_stmt() # Lambda è una Expr

        self.assertIsInstance(stmt.expr, ast.LambdaExpr)
        self.assertEqual(stmt.expr.params, ["x"])
        self.assertIsInstance(stmt.expr.body, ast.BinaryExpr)

    def test_lambda_vuota(self):
        # Test: () => 0
        tokens = [
            Token(TokenType.LPAREN),
            Token(TokenType.RPAREN),
            Token(TokenType.ARROW, "=>"),
            Token(TokenType.INTEGER, 0),
            Token(TokenType.SEMI)
        ]
        parser = self.create_parser(tokens)
        stmt = parser.parse_stmt()

        self.assertIsInstance(stmt.expr, ast.LambdaExpr)
        self.assertEqual(stmt.expr.params, [])

    def test_errore_sintattico(self):
        # Test: let x = 5 (manca il punto e virgola)
        tokens = [
            Token(TokenType.LET),
            Token(TokenType.ID, "x"),
            Token(TokenType.ASSIGN),
            Token(TokenType.INTEGER, 5),
            Token(TokenType.EOF)
        ]
        parser = self.create_parser(tokens)

        with self.assertRaises(SyntaxError):
            parser.parse_decl()

if __name__ == '__main__':
    unittest.main()