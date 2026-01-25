from llvmlite import ir
from src.ast_nodes import NodeVisitor
from src.tokens import TokenType
import src.ast_nodes as ast

class LLVMCodeGen(NodeVisitor):
    def __init__(self):
        self.module = ir.Module(name="main_module")
        self.module.triple = "x86_64-pc-linux-gnu"
        self.builder = None
        self.func_symtab = {}
        self.functions = {}

        # Tipi
        self.i64 = ir.IntType(64)
        self.i1 = ir.IntType(1)
        self.void = ir.VoidType()

    def generate_code(self, node):
        self.visit(node)
        return str(self.module)

    def visit_Program(self, node):
        # Raccolta delle dichiarazioni di tutte le funzioni
        for decl in node.declarations:
            func_name = decl.name

            arg_types = [self.i64 for _ in decl.params]

            # i64 per default
            func_type = ir.FunctionType(self.i64, arg_types)

            if isinstance(decl, ast.ExternDecl):
                func = ir.Function(self.module, func_type, name=func_name)
                self.functions[func_name] = func

            elif isinstance(decl, ast.FunctionDecl):
                func = ir.Function(self.module, func_type, name=func_name)
                self.functions[func_name] = func

        # Generazione del corpo delle funzioni definite
        for decl in node.declarations:
            if isinstance(decl, ast.FunctionDecl):
                self.visit(decl)

        return self.module

    def visit_ExternDecl(self, node):
        pass

    def visit_FunctionDecl(self, node):
        func = self.functions[node.name]

        # entry block
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        # gestione della memoria
        self.func_symtab = {}
        for i, arg in enumerate(func.args):
            arg.name = node.params[i]
            alloca = self.builder.alloca(self.i64, name=arg.name)
            self.builder.store(arg, alloca)
            self.func_symtab[arg.name] = alloca

        self.visit(node.body)

        # return implicito
        if not self.builder.block.is_terminated:
            self.builder.ret(ir.Constant(self.i64, 0))

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)
            if self.builder.block.is_terminated:
                break

    def visit_VarDecl(self, node):
        init_val = self.visit(node.initializer)

        alloca = self.builder.alloca(self.i64, name=node.name)
        self.builder.store(init_val, alloca)

        self.func_symtab[node.name] = alloca

    def visit_AssignExpr(self, node):
        new_val = self.visit(node.value)

        if node.name not in self.func_symtab:
            raise Exception(f"Variabile non definita nel codegen: {node.name}")

        alloca = self.func_symtab[node.name]
        self.builder.store(new_val, alloca)
        return new_val

    def visit_VariableExpr(self, node):
        if node.name not in self.func_symtab:
            raise Exception(f"Variabile non trovata: {node.name}")

        alloca = self.func_symtab[node.name]
        return self.builder.load(alloca, name=node.name)

    def visit_LiteralExpr(self, node):
        return ir.Constant(self.i64, node.value)

    def visit_ReturnStmt(self, node):
        retval = self.visit(node.value)
        self.builder.ret(retval)

    def visit_IfStmt(self, node):
        cond_val = self.visit(node.condition)
        cond_bool = self.builder.icmp_signed('!=', cond_val, ir.Constant(self.i64, 0))

        then_block = self.builder.append_basic_block(name="then")
        merge_block = self.builder.append_basic_block(name="if_cont")

        if node.else_branch:
            else_block = self.builder.append_basic_block(name="else")
            self.builder.cbranch(cond_bool, then_block, else_block)

            # Genera codice Else
            self.builder.position_at_start(else_block)
            self.visit(node.else_branch)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_block)
        else:
            self.builder.cbranch(cond_bool, then_block, merge_block)

        # Genera codice Then
        self.builder.position_at_start(then_block)
        self.visit(node.then_branch)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_block)

        self.builder.position_at_start(merge_block)

    def visit_WhileStmt(self, node):
        cond_block = self.builder.append_basic_block(name="while_cond")
        body_block = self.builder.append_basic_block(name="while_body")
        after_block = self.builder.append_basic_block(name="while_after")

        self.builder.branch(cond_block)

        # Blocco Condizione
        self.builder.position_at_start(cond_block)
        cond_val = self.visit(node.condition)
        cond_bool = self.builder.icmp_signed('!=', cond_val, ir.Constant(self.i64, 0))
        self.builder.cbranch(cond_bool, body_block, after_block)

        # Blocco Corpo
        self.builder.position_at_start(body_block)
        self.visit(node.body)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_block)

        # Dopo il While
        self.builder.position_at_start(after_block)


    def visit_BinaryExpr(self, node):
        lhs = self.visit(node.left)
        rhs = self.visit(node.right)

        op = node.operator

        if op == TokenType.PLUS:
            return self.builder.add(lhs, rhs, name="addtmp")
        elif op == TokenType.MINUS:
            return self.builder.sub(lhs, rhs, name="subtmp")
        elif op == TokenType.MUL:
            return self.builder.mul(lhs, rhs, name="multmp")
        elif op == TokenType.DIV:
            return self.builder.sdiv(lhs, rhs, name="divtmp")

        elif op in (TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.EQ, TokenType.NE):
            cmp_map = {
                TokenType.LT: '<', TokenType.GT: '>',
                TokenType.LE: '<=', TokenType.GE: '>=',
                TokenType.EQ: '==', TokenType.NE: '!='
            }
            res_i1 = self.builder.icmp_signed(cmp_map[op], lhs, rhs, name="cmptmp")
            return self.builder.zext(res_i1, self.i64, name="bool_cast")

        elif op == TokenType.AND:
            return self.builder.and_(lhs, rhs, name="andtmp")
        elif op == TokenType.OR:
            return self.builder.or_(lhs, rhs, name="ortmp")

        raise Exception(f"Operatore non supportato in CodeGen: {op}")

    def visit_UnaryExpr(self, node):
        operand = self.visit(node.operand)
        if node.operator == TokenType.MINUS:
            return self.builder.neg(operand, name="negtmp")
        elif node.operator == TokenType.NOT:
            is_zero = self.builder.icmp_signed('==', operand, ir.Constant(self.i64, 0))
            return self.builder.zext(is_zero, self.i64, name="nottmp")
        return None

    def visit_CallExpr(self, node):
        callee_func = self.functions.get(node.callee)
        if not callee_func:
            raise Exception(f"Funzione sconosciuta: {node.callee}")

        args = [self.visit(arg) for arg in node.args]
        return self.builder.call(callee_func, args, name="calltmp")

    def visit_ExprStmt(self, node):
        self.visit(node.expr)

    def visit_RepeatStmt(self, node):
        raise NotImplementedError("RepeatStmt deve essere rimosso dal Desugarer prima del CodeGen")

    def visit_PipeExpr(self, node):
        raise NotImplementedError("PipeExpr deve essere rimosso dal Desugarer prima del CodeGen")

