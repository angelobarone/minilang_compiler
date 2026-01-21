import unittest
from src.tokens import TokenType, Token
from src.lexer import Lexer

class TestLexer(unittest.TestCase):

    def test_keywords_and_identifiers(self):
        input_text = "let func extern return if else while repeat myVar"
        lexer = Lexer(input_text)

        self.assertEqual(lexer.get_next_token().type, TokenType.LET)
        self.assertEqual(lexer.get_next_token().type, TokenType.FUNC)
        self.assertEqual(lexer.get_next_token().type, TokenType.EXTERN)
        self.assertEqual(lexer.get_next_token().type, TokenType.RETURN)
        self.assertEqual(lexer.get_next_token().type, TokenType.IF)
        self.assertEqual(lexer.get_next_token().type, TokenType.ELSE)
        self.assertEqual(lexer.get_next_token().type, TokenType.WHILE)
        self.assertEqual(lexer.get_next_token().type, TokenType.REPEAT)
        token = lexer.get_next_token()
        self.assertEqual(token.type, TokenType.ID)
        self.assertEqual(token.value, "myVar")

    def test_numbers(self):
        input_text = "123 0 9999"
        lexer = Lexer(input_text)

        t1 = lexer.get_next_token()
        self.assertEqual(t1.type, TokenType.INTEGER)
        self.assertEqual(t1.value, 123)

        self.assertEqual(lexer.get_next_token().value, 0)
        self.assertEqual(lexer.get_next_token().value, 9999)

    def test_relational_operators(self):
        input_text = "< <= > >="
        lexer = Lexer(input_text)

        self.assertEqual(lexer.get_next_token().type, TokenType.LT)
        self.assertEqual(lexer.get_next_token().type, TokenType.LE)
        self.assertEqual(lexer.get_next_token().type, TokenType.GT)
        self.assertEqual(lexer.get_next_token().type, TokenType.GE)

    def test_equality_operators(self):
        input_text = "= == ! !="
        lexer = Lexer(input_text)

        self.assertEqual(lexer.get_next_token().type, TokenType.ASSIGN)
        self.assertEqual(lexer.get_next_token().type, TokenType.EQ)
        self.assertEqual(lexer.get_next_token().type, TokenType.NOT)
        self.assertEqual(lexer.get_next_token().type, TokenType.NE)

    def test_logical_operators_and_pipe(self):
        input_text = "&& || |>"
        lexer = Lexer(input_text)

        self.assertEqual(lexer.get_next_token().type, TokenType.AND)
        self.assertEqual(lexer.get_next_token().type, TokenType.OR)

        token_pipe = lexer.get_next_token()
        self.assertEqual(token_pipe.type, TokenType.PIPE)
        self.assertEqual(token_pipe.value, "|>")

    def test_arrow_function(self):
        input_text = "=> ="
        lexer = Lexer(input_text)

        self.assertEqual(lexer.get_next_token().type, TokenType.ARROW)
        self.assertEqual(lexer.get_next_token().type, TokenType.ASSIGN)

    def test_real_code_snippet(self):
        input_text = "repeat(count) { print(100); }"
        lexer = Lexer(input_text)

        expected_types = [
            TokenType.REPEAT,
            TokenType.LPAREN,
            TokenType.ID,
            TokenType.RPAREN,
            TokenType.LBRACE,
            TokenType.ID,
            TokenType.LPAREN,
            TokenType.INTEGER,
            TokenType.RPAREN,
            TokenType.SEMI,
            TokenType.RBRACE,
            TokenType.EOF
        ]

        for exp_type in expected_types:
            token = lexer.get_next_token()
            self.assertEqual(token.type, exp_type, f"Atteso {exp_type}, ricevuto {token.type}")

    def test_error_handling(self):
        lexer = Lexer("&")
        with self.assertRaises(Exception):
            lexer.get_next_token()

if __name__ == '__main__':
    unittest.main()