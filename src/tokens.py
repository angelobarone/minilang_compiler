from enum import Enum, auto

class TokenType(Enum):
    # Letterali
    INTEGER = auto()
    ID = auto()

    # Keywords
    LET = auto()
    FUNC = auto()
    EXTERN = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    REPEAT = auto()

    # Operatori Aritmetici
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()

    # Operatori Logici
    AND = auto()       # &&
    OR = auto()        # ||
    NOT = auto()       # !

    # Operatori di Confronto
    EQ = auto()        # ==
    NE = auto()        # !=
    LT = auto()        # <
    GT = auto()        # >
    LE = auto()        # <=
    GE = auto()        # >=

    # Operatori Speciali
    ASSIGN = auto()    # =
    PIPE = auto()      # |>
    ARROW = auto()     # =>

    #Simboli
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    SEMI = auto()

    EOF = auto()


class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        val_str = f", {repr(self.value)}" if self.value is not None else ""
        return f"Token({self.type.name}{val_str})"