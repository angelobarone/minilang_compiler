from src.ast_nodes import NodeVisitor
import src.ast_nodes as ast
from src.tokens import TokenType

class ConstantFolder(NodeVisitor):

    def visit_Program(self, node):
        node.declarations = [self.visit(decl) for decl in node.declarations]
        return node

    def visit_FunctionDecl(self, node):
        node.body = self.visit(node.body)
        return node

    def visit_ExternDecl(self, node):
        return node

    def visit_Block(self, node):
        node.statements = [self.visit(stmt) for stmt in node.statements]
        return node

    def visit_ReturnStmt(self, node):
        node.value = self.visit(node.value)
        return node

    def visit_ExprStmt(self, node):
        node.expr = self.visit(node.expr)
        return node

    def visit_VarDecl(self, node):
        node.initializer = self.visit(node.initializer)
        return node

    def visit_IfStmt(self, node):
        node.condition = self.visit(node.condition)
        node.then_branch = self.visit(node.then_branch)
        if node.else_branch:
            node.else_branch = self.visit(node.else_branch)
        return node

    def visit_WhileStmt(self, node):
        node.condition = self.visit(node.condition)
        node.body = self.visit(node.body)
        return node

    def visit_RepeatStmt(self, node):
        node.count = self.visit(node.count)
        node.body = self.visit(node.body)
        return node

    def visit_BinaryExpr(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        if isinstance(node.left, ast.LiteralExpr) and isinstance(node.right, ast.LiteralExpr):
            val_left = node.left.value
            val_right = node.right.value

            if node.operator == TokenType.PLUS:
                return ast.LiteralExpr(val_left + val_right)
            elif node.operator == TokenType.MINUS:
                return ast.LiteralExpr(val_left - val_right)
            elif node.operator == TokenType.MUL:
                return ast.LiteralExpr(val_left * val_right)
            elif node.operator == TokenType.DIV:
                if val_right == 0:
                    raise ZeroDivisionError("Divisione per zero rilevata durante Constant Folding")
                return ast.LiteralExpr(int(val_left / val_right))

        return node

    def visit_UnaryExpr(self, node):
        node.operand = self.visit(node.operand)

        if isinstance(node.operand, ast.LiteralExpr):
            if node.operator == TokenType.MINUS:
                return ast.LiteralExpr(-node.operand.value)

        return node

    def visit_LiteralExpr(self, node): return node
    def visit_VariableExpr(self, node): return node
    def visit_AssignExpr(self, node):
        node.value = self.visit(node.value)
        return node
    def visit_CallExpr(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        return node
    def visit_PipeExpr(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        return node