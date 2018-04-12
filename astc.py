'''
Copyright 2018 JackLiang.

Abstract Syntax Tree
'''
from enum import Enum, unique
from ctype import *


@unique
class NodeKind(Enum):
    AST_LITERAL = 0
    AST_LVAR = 1
    AST_GVAR = 2
    AST_TYPEDEF = 3
    AST_FUNCALL = 4
    AST_FUNCPTR_CALL = 5
    AST_FUNCDESG = 6
    AST_FUNC = 7
    AST_DECL = 8
    AST_INIT = 9
    AST_CONV = 10
    AST_ADDR = 11
    AST_DEREF = 12
    AST_IF = 13
    AST_TERNARY = 14
    AST_DEFAULT = 15
    AST_RETURN = 16
    AST_COMPOUND_STMT = 17
    AST_STRUCT_REF = 18
    AST_GOTO = 19
    AST_COMPOUND_GOTO = 20
    AST_LABEL = 21
    OP_SIZEOF = 22
    OP_CAST = 23
    OP_SHR = 24
    OP_SHL = 25
    OP_A_SHR = 26
    OP_A_SHL = 27
    OP_PRE_INC = 28 # pre ++
    OP_PRE_DEC = 29 # pre --
    OP_POST_INC = 30 # post ++
    OP_POST_DEC = 31 # post --
    OP_LABEL_ADDR = 32
    OP_ARROW = 33 # ->
    OP_A_ADD = 34 # +=
    OP_A_AND = 35 # &=
    OP_A_DIV = 36 # /=
    OP_A_MOD = 37 # %=
    OP_A_MUL = 38 # *=
    OP_A_OR = 39 # |=
    OP_A_SAL = 40 # <<=
    OP_A_SAR = 41 # >>=
    OP_A_SUB = 42 # -=
    OP_A_XOR = 43 # ^=
    OP_DEC = 44 # --
    OP_EQ = 45 # ==
    OP_GE = 46 # >=
    OP_INC = 47 # ++
    OP_LE = 48 # <=
    OP_LOGAND = 49 # &&
    OP_LOGOR = 50 # ||
    OP_NE = 51 # !=
    OP_SAL = 52 # <<
    OP_SAR = 53 # >>
    OP_BITOR = 54 # |
    OP_BITXOR = 55 # ^
    OP_BITAND = 56 # &
    OP_L = 59 # <
    OP_G = 60 # >
    OP_ADD = 61 # +
    OP_SUB = 62 # -
    OP_MUL = 63 # *
    OP_DIV = 64 # /
    OP_MOD = 65 # %
    OP_ADDR = 66 # &
    OP_LOGNOT = 67 # !
    OP_MINUS = 68 # -

class Node(object):

    def __init__(self):
        self.kind = NodeKind.AST_LITERAL
        self.ty = None
        self.sourceloc = None

class ValueNode(Node):

    def __init__(self, val):
        '''
        char,int,long,float,double,char,string
        '''
        self.val = val

class VarNode(Node):

    def __init__(self, name):
        self.name = name
        self.lvarinit = []

class DeclNode(Node):

    def __init__(self, node, init_list):
        '''
        declaration
        '''
        self.declvar = node
        self.declinit = init_list

class InitNode(Node):

    def __init__(self, node, totype):
        '''
        initializer
        '''
        self.initval = node
        self.totype = totype

class BinaryNode(Node):

    def __init__(self, left, right):
        self.left = left
        self.right = right

class UnaryNode(Node):

    def __init__(self, operand):
        self.operand = operand

class FuncNode(Node):

    def __init__(self):
        self.fname = ''
        self.params = []
        self.localvars = []
        self.body = None

class CompoundStmtNode(Node):

    def __init__(self):
        self.stmts = []

class IfStmtNode(Node):

    def __init__(self):
        self.cond = None
        self.then = None
        self.els = None

class NodeFactory(object):
    '''
    produce abstract syntax tree node
    '''

    def __init__(self, sm):
        self.sm = sm #symbol manager
        self.sl = None # source location

    def _base_set(self, node):
        node.sourceloc = self.sl

    def val_node(self, ty, val):
        node = ValueNode(val)
        self._base_set(node)
        node.kind = NodeKind.AST_LITERAL
        node.ty = ty
        return node

    def var_node(self, ty, isglobal):
        node = VarNode(ty.varname)
        self._base_set(node)
        node.ty = ty
        node.kind = NodeKind.AST_GVAR if isglobal else NodeKind.AST_LVAR
        self.sm.ident_install(ty.varname)
        return node

    def decl_node(self, varnode, init_list):
        node = DeclNode(varnode, init_list)
        self._base_set(node)
        node.kind = NodeKind.AST_DECL
        return node

    def init_node(self, node, totype):
        node = InitNode(node, totype)
        self._base_set(node)
        node.kind = NodeKind.AST_INIT
        return node

    def binary_node(self, kind, ty, left, right):
        node = BinaryNode(left, right)
        self._base_set(node)
        node.kind = kind
        node.ty = ty
        return node

    def unary_node(self, kind, ty, node):
        n = UnaryNode(node)
        self._base_set(n)
        n.kind = kind
        n.ty = ty
        return n

    def conv_node(self, toty, node):
        n = UnaryNode(node)
        self._base_set(n)
        n.kind = NodeKind.AST_CONV
        n.ty = toty
        return n

    def func_node(self, ty, params, body, localvars):
        n = FuncNode()
        self._base_set(n)
        n.kind = NodeKind.AST_FUNC
        n.ty = ty
        n.fname = ty.varname
        n.params = params
        n.body = body
        n.localvars = localvars
        return n

    def compound_stmt_node(self, stmts):
        n = CompoundStmtNode()
        self._base_set(n)
        n.kind = NodeKind.AST_COMPOUND_STMT
        n.stmts = stmts
        return n

    def if_stmt_node(self, cond, then, els):
        n = IfStmtNode()
        self._base_set(n)
        n.kind = NodeKind.AST_IF
        n.cond = cond
        n.then = then
        n.els = els
        return n
