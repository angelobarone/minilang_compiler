from src.tokens import TokenType, Token

KEYWORDS = {
    'let': TokenType.LET,
    'func': TokenType.FUNC,
    'extern': TokenType.EXTERN,
    'return': TokenType.RETURN,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'repeat': TokenType.REPEAT
}

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def error(self):
        raise Exception(f"Carattere non valido: '{self.current_char}' alla posizione {self.pos}")

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indica EOF
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def _id(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        token_type = KEYWORDS.get(result, TokenType.ID)
        return Token(token_type, result)

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())

            if self.current_char.isalpha():
                return self._id()

            # Gestione operatori doppi
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token(TokenType.EQ, '==')
                elif self.peek() == '>':
                    self.advance(); self.advance()
                    return Token(TokenType.ARROW, '=>')
                else:
                    self.advance()
                    return Token(TokenType.ASSIGN, '=')

            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token(TokenType.NE, '!=')
                else:
                    self.advance()
                    return Token(TokenType.NOT, '!')

            if self.current_char == '<':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token(TokenType.LE, '<=')
                else:
                    self.advance()
                    return Token(TokenType.LT, '<')

            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token(TokenType.GE, '>=')
                else:
                    self.advance()
                    return Token(TokenType.GT, '>')

            if self.current_char == '|':
                peek_char = self.peek()
                if peek_char == '>':
                    self.advance(); self.advance()
                    return Token(TokenType.PIPE, '|>')
                elif peek_char == '|':
                    self.advance(); self.advance()
                    return Token(TokenType.OR, '||')
                else:
                    self.error()

            if self.current_char == '&':
                if self.peek() == '&':
                    self.advance(); self.advance()
                    return Token(TokenType.AND, '&&')
                else:
                    self.error()

            # Gestione Operatori Singoli
            if self.current_char == '+':
                self.advance(); return Token(TokenType.PLUS, '+')
            if self.current_char == '-':
                self.advance(); return Token(TokenType.MINUS, '-')
            if self.current_char == '*':
                self.advance(); return Token(TokenType.MUL, '*')
            if self.current_char == '/':
                self.advance(); return Token(TokenType.DIV, '/')
            if self.current_char == '(':
                self.advance(); return Token(TokenType.LPAREN, '(')
            if self.current_char == ')':
                self.advance(); return Token(TokenType.RPAREN, ')')
            if self.current_char == '{':
                self.advance(); return Token(TokenType.LBRACE, '{')
            if self.current_char == '}':
                self.advance(); return Token(TokenType.RBRACE, '}')
            if self.current_char == ',':
                self.advance(); return Token(TokenType.COMMA, ',')
            if self.current_char == ';':
                self.advance(); return Token(TokenType.SEMI, ';')
            self.error()

        return Token(TokenType.EOF, None)