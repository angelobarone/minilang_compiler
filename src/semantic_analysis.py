from src.ast_nodes import NodeVisitor
import src.ast_nodes as ast

class SemanticError(Exception):
    pass

class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        # mappa nome_funzione -> numero_argomenti
        self.functions_arity = {}
        # set di variabili definite nella funzione corrente
        self.current_scope = set()

    def visit_Program(self, node):
        for decl in node.declarations:
            if isinstance(decl, ast.FunctionDecl):
                self.functions_arity[decl.name] = len(decl.params)
            elif isinstance(decl, ast.ExternDecl):
                self.functions_arity[decl.name] = len(decl.params)

        for decl in node.declarations:
            if isinstance(decl, ast.FunctionDecl):
                self.visit(decl)
        return node

    def visit_FunctionDecl(self, node):
        previous_scope = self.current_scope
        self.current_scope = set()

        for param in node.params:
            if param in self.current_scope:
                raise SemanticError(f"Parametro duplicato '{param}' nella funzione '{node.name}'")
            self.current_scope.add(param)

        self.visit(node.body)
        self.current_scope = previous_scope

    def visit_Block(self, node):
        # Flat Scope
        for stmt in node.statements:
            self.visit(stmt)

    def visit_VarDecl(self, node):
        self.visit(node.initializer)
        self.current_scope.add(node.name)

    def visit_VariableExpr(self, node):
        if node.name not in self.current_scope:
            raise SemanticError(f"Variabile non definita: '{node.name}'")

    def visit_CallExpr(self, node):
        if node.callee not in self.functions_arity:
            raise SemanticError(f"Funzione non definita: '{node.callee}'")

        expected_arity = self.functions_arity[node.callee]
        actual_arity = len(node.args)

        if expected_arity != actual_arity:
            raise SemanticError(
                f"Errore di Arity per '{node.callee}': attesi {expected_arity} argomenti, ricevuti {actual_arity}"
            )

        for arg in node.args:
            self.visit(arg)

    def visit_AssignExpr(self, node):
        if node.name not in self.current_scope:
            raise SemanticError(f"Impossibile assegnare a variabile non definita: '{node.name}'")
        self.visit(node.value)

    # Metodi di visita per propagare l'analisi nei figli
    def visit_IfStmt(self, node):
        self.visit(node.condition)
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_WhileStmt(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_RepeatStmt(self, node):
        self.visit(node.count)
        self.visit(node.body)

    def visit_ReturnStmt(self, node):
        self.visit(node.value)

    def visit_ExprStmt(self, node):
        self.visit(node.expr)

    def visit_BinaryExpr(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryExpr(self, node):
        self.visit(node.operand)

    def visit_PipeExpr(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_LiteralExpr(self, node):
        pass