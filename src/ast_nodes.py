from dataclasses import dataclass
from typing import List, Optional, Union, Any

@dataclass
class ASTNode:
    pass

@dataclass
class Expr(ASTNode):
    pass

@dataclass
class LiteralExpr(Expr):
    value: int

@dataclass
class VariableExpr(Expr):
    name: str

@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: Any
    right: Expr

@dataclass
class UnaryExpr(Expr):
    operator: Any
    operand: Expr

@dataclass
class PipeExpr(Expr):
    left: Expr
    right: Expr

@dataclass
class AssignExpr(Expr):
    name: str
    value: Expr

@dataclass
class CallExpr(Expr):
    callee: str
    args: List[Expr]

@dataclass
class LambdaExpr(Expr):
    params: List[str]
    body: Expr

@dataclass
class Stmt(ASTNode):
    pass

@dataclass
class ReturnStmt(Stmt):
    value: Expr

@dataclass
class ExprStmt(Stmt):
    expr: Expr

@dataclass
class VarDecl(Stmt):
    name: str
    initializer: Expr

@dataclass
class Block(Stmt):
    statements: List[Stmt]

@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Block
    else_branch: Optional[Block]

@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Block

@dataclass
class RepeatStmt(Stmt):
    count: Expr
    body: Block

@dataclass
class FunctionDecl(ASTNode):
    name: str
    params: List[str]
    body: Block

@dataclass
class ExternDecl(ASTNode):
    name: str
    params: List[str]

@dataclass
class Program(ASTNode):
    declarations: List[Union[FunctionDecl, ExternDecl, VarDecl]]

class NodeVisitor:
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')