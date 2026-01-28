from src.ast_nodes import NodeVisitor
import src.ast_nodes as ast
from src.tokens import TokenType

class Desugarer(NodeVisitor):
    def __init__(self):
        self.counter_id = 0
        self.generated_functions = [] #lambda

    def _get_unique_var(self):
        name = f"__repeat_counter_{self.counter_id}"
        self.counter_id += 1
        return name

    def visit_Program(self, node):
        node.declarations = [self.visit(decl) for decl in node.declarations]
        node.declarations.extend(self.generated_functions)
        return node

    def visit_FunctionDecl(self, node):
        node.body = self.visit(node.body)
        return node

    def visit_Block(self, node):
        new_stmts = []
        for stmt in node.statements:
            desugared = self.visit(stmt)
            if isinstance(desugared, list):
                new_stmts.extend(desugared)
            else:
                new_stmts.append(desugared)
        node.statements = new_stmts
        return node

    def visit_RepeatStmt(self, node):
        counter_name = self._get_unique_var()

        # Inizializzazione
        init_decl = ast.VarDecl(name=counter_name, initializer=ast.LiteralExpr(0))

        # Condizione
        condition = ast.BinaryExpr(
            left=ast.VariableExpr(counter_name),
            operator=TokenType.LT,
            right=self.visit(node.count)
        )

        # Incremento
        increment = ast.ExprStmt(
            expr=ast.AssignExpr(
                name=counter_name,
                value=ast.BinaryExpr(
                    left=ast.VariableExpr(counter_name),
                    operator=TokenType.PLUS,
                    right=ast.LiteralExpr(1)
                )
            )
        )

        # Controllo di sicurezza
        visited_body = self.visit(node.body)
        if isinstance(visited_body, ast.Block):
            new_body_stmts = visited_body.statements
        else:
            new_body_stmts = [visited_body]

        # While
        new_body_stmts.append(increment)
        while_node = ast.WhileStmt(condition=condition, body=ast.Block(new_body_stmts))

        return [init_decl, while_node]

    def visit_PipeExpr(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Il figlio destro è una chiamata a funzione
        if isinstance(right, ast.CallExpr):
            right.args.insert(0, left)
            return right

        # Il figlio destro è una variabile
        if isinstance(right, ast.VariableExpr):
            return ast.CallExpr(callee=right.name, args=[left])

        raise ValueError(f"Lato destro del pipe '|>' invalido. Attesa funzione o chiamata, trovato: {type(right).__name__}")

    def visit_VarDecl(self, node):
        node.initializer = self.visit(node.initializer)
        return node

    def visit_ReturnStmt(self, node):
        node.value = self.visit(node.value)
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

    def visit_BinaryExpr(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        return node

    def visit_AssignExpr(self, node):
        node.value = self.visit(node.value)
        return node

    def visit_CallExpr(self, node):
        node.args = [self.visit(arg) for arg in node.args]
        return node

    def visit_LambdaExpr(self, node):
        # Generiamo una nuova funzione
        func_name = f"__lambda_{self.counter_id}"
        self.counter_id += 1
        visited_body_expr = self.visit(node.body)
        return_stmt = ast.ReturnStmt(value=visited_body_expr)

        func_body_block = ast.Block(statements=[return_stmt])
        new_func = ast.FunctionDecl(
            name=func_name,
            params=node.params,
            body=func_body_block
        )
        self.generated_functions.append(new_func)
        return ast.VariableExpr(name=func_name)


    def visit_LiteralExpr(self, node): return node
    def visit_VariableExpr(self, node): return node
    def visit_UnaryExpr(self, node):
        node.operand = self.visit(node.operand)
        return node
    def visit_ExprStmt(self, node):
        node.expr = self.visit(node.expr)
        return node
    def visit_ExternDecl(self, node): return node
