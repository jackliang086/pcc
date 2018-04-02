'''
Copyright 2018 JackLiang.

parse grammer
'''
from enum import Enum, unique
from lex import TokenKind
from ctype import *
from csymbol import *
from astc import *

@unique
class DeclType(Enum):
    BODY = 1
    PARAM = 2
    PARAM_TYPE_ONLY = 3
    CAST = 4

class Parser(object):
    '''
    C89 BNF
    '''

    TYPETOKENS = [
        'K_VOID',
        'K_SHORT',
        'K_INT',
        'K_LONG',
        'K_FLOAT',
        'K_DOUBLE',
        'K_CHAR',
        'K_SIGNED',
        'K_UNSIGNED',
        'K_STRUCT',
        'K_UNION',
        'K_ENUM'
    ]

    def __init__(self, tokens):
        self._tokens = tokens
        self._pos = -1
        self._is_record = False
        self._record = 0 #for rollback step
        self._current_token = None
        self._sourceloc = None

        self._tm = TypeMaker() #make type
        self._sm = SymbolManager() #Symbol Manager
        self._nf = NodeFactory(self._sm)

        self.ast = [] # AST

    def _error(self, e, is_token=True):
        if is_token:
            s = 'file {0} line:{1} {2}'.format(self._current_token.filename, self._current_token.line, e)
            raise Exception(s)
        else:
            raise Exception(e)

    def _warning(self):
        pass

    def _advance(self):
        if self._pos >= len(self._tokens) - 1:
            self._pos = len(self._tokens) - 1
        else:
            self._pos += 1
            if self._is_record:
                self._record += 1
        self._current_token = self._tokens[self._pos]

        self._sourceloc = Coordinate(self._current_token.filename, self._current_token.line, self._current_token.column)
        self._nf.sl = self._sourceloc

        return self._current_token

    def _back(self):
        if self._pos > -1:
            self._pos -= 1
            self._current_token = self._tokens[self._pos]


    def _rollback(self, i=1):
        self._pos -= self._record
        self._current_token = self._tokens[self._pos]
        self._record = 0
        self._is_record = False

    def _peek(self, i=1):
        if self._pos + i <= len(self._tokens) - 1:
            peek_pos = self._pos + i
            token = self._tokens[peek_pos]
            return token
        else:
            return self._tokens[len(self._tokens) - 1]

    def _next_t(self, value):
        token = self._peek()
        if token.value == value:
            self._advance()
            return True
        return False

    def _expect(self, c):
        c_t = self._advance()
        if c != c_t.value:
            self._error('[{}] expected,but got {}'.format(c, c_t.value))

    def _is_type(self, token):
        if token.kind != TokenKind.TKEYWORD:
            return False
        for value in Parser.TYPETOKENS:
            if value == token.value:
                return True
        return False

    def _is_funcdef(self):
        '''
        is_funcdef returns true if we are at beginning of a function definition
        '''
        self._is_record = True
        r = False
        while True:
            c_t = self._advance()
            if c_t.kind == TokenKind.TEOF:
                self._error('premature end of input')
            if c_t.value == ';':
                break
            if self._is_type(c_t):
                continue
            if c_t.value == '(':
                self._skip_parenteses()
                continue
            if c_t.kind == TokenKind.TIDENT:
                continue
            r = self._peek().value == '{'

        self._rollback()
        return r

    def _skip_parenteses(self):
        while True:
            c_t = self._advance()
            if c_t.kind == TokenKind.TEOF:
                self._error('premature end of input')
            if c_t.value == ')':
                break
            if c_t.value == ')':
                self._skip_parenteses()

    def _skip_type_qualifiers(self):
        while self._next_t('K_CONST'):
            pass

    def _ensure_not_void(self, ty):
        if ty is None:
            self._error('internal error')
        if ty.kind == TypeKind.VOID:
            self._error('void is not allowed')

    def _ensure_arithtype(self, node):
        ty = node.ty
        if not ty.is_arithtype():
            self._error('arithmetic type expected,but got {}'.format(self._current_token.value))

    def _ensure_lvalue(self, node):
        kind = node.kind
        if kind == NodeKind.AST_LVAR or kind == NodeKind.AST_GVAR or kind == NodeKind.AST_DEREF or kind == NodeKind.AST_STRUCT_REF:
            return
        self._error('lvalue expected,but got {}'.format(self._current_token.value))

    def _conv(self, node):
        '''
        type coversion
        '''
        if node is None:
            return None
        ty = node.ty
        if ty.kind == TypeKind.ARRAY:
            #TODO
            pass
        elif ty.kind == TypeKind.FUNC:
            #TODO
            pass
        elif ty.kind == TypeKind.CHAR or ty.kind == TypeKind.SHORT or ty.kind == TypeKind.BOOL:
            return self._nf.conv_node(self._tm.type_int(), node)
        elif ty.kind == TypeKind.INT:
            #TODO maybe need add bit scope judgement
            return self._nf.conv_node(self._tm.type_int(), node)
        return node

    def _binop(self, kind, lnode, rnode):
        #TODO many thing
        return self._nf.binary_node(kind, self._tm.type_int(), lnode, rnode)

    def _read_decl_spec(self):
        '''
        declaration specifiers
        '''
        #TODO not finish
        if not self._is_type(self._peek()):
            self._error('type name expected, but got {}'.format(self._current_token.value))

        kind = -1
        scalss = -1
        usig = None
        err = False

        while True:
            c_t = self._advance()
            if c_t.kind == TokenKind.TEOF:
                self._error('premature end of input')

            if c_t.kind != TokenKind.TKEYWORD:
                self._back()
                break

            if c_t.value == 'K_TYPEDEF':
                if scalss != -1:
                    err = True
                    break
                scalss = SClass.S_TYPEDEF
            elif c_t.value == 'K_EXTERN':
                if scalss != -1:
                    err = True
                    break
                scalss = SClass.S_EXTERN
            elif c_t.value == 'K_STATIC':
                if scalss != -1:
                    err = True
                    break
                scalss = SClass.S_STATIC
            elif c_t.value == 'K_AUTO':
                if scalss != -1:
                    err = True
                    break
                scalss = SClass.S_AUTO
            elif c_t.value == 'K_REGISTER':
                if scalss != -1:
                    err = True
                    break
                scalss = SClass.S_REGISTER
            elif c_t.value == 'K_CONST':
                pass
            elif c_t.value == 'K_VOID':
                if kind != -1:
                    err = True
                    break
                kind = TypeKind.VOID
            elif c_t.value == 'K_CHAR':
                if kind != -1:
                    err = True
                    break
                kind = TypeKind.CHAR
            elif c_t.value == 'K_INT':
                if kind != -1:
                    err = True
                    break
                kind = TypeKind.INT
            elif c_t.value == 'K_FLOAT':
                if kind != -1:
                    err = True
                    break
                kind = TypeKind.FLOAT
            elif c_t.value == 'K_DOUBLE':
                if kind != -1:
                    err = True
                    break
                kind = TypeKind.DOUBLE
            elif c_t.value == 'K_SHORT':
                if kind != -1:
                    err = True
                    break
                kind = TypeKind.SHORT
            elif c_t.value == 'K_LONG':
                if kind == -1:
                    kind = TypeKind.LONG
                elif kind == TypeKind.LONG:
                    kind = TypeKind.LLONG
                else:
                    err = True
                    break
            elif c_t.value == 'K_SIGNED':
                if not usig is None:
                    err = True
                    break
                usig = False
            elif c_t.value == 'K_UNSIGNED':
                if not usig is None:
                    err = True
                    break
                usig = True
            elif c_t.value == 'K_STRUCT':
                pass
            elif c_t.value == 'K_UNION':
                pass
            elif c_t.value == 'K_ENUM':
                pass
            else:
                self._back()

            #check error
            if (kind == TypeKind.VOID or kind == TypeKind.FLOAT or kind == TypeKind.DOUBLE) and not usig is None:
                err = True
                break

        if err:
            self._error('type mismatch: {}'.format(self._current_token.value))
        else:
            ty = self._tm.make_num_type(kind, False if usig is None else usig)
            ty.scalss = SClass.S_AUTO if scalss == -1 else scalss
            return ty

    def _read_declarator(self, basety, params, decltype=DeclType.BODY):
        '''
        read declarators
        '''
        if self._next_t('('):
            #TODO
            return None
        if self._next_t('*'):
            self._skip_type_qualifiers()
            return self._read_declarator(self._tm.make_ptr_type(basety), params, decltype)
        c_t = self._advance()
        if c_t.kind == TokenKind.TIDENT:
            if decltype == DeclType.CAST:
                self._error('identifier is not expected,but got {}'.format(c_t.value))
            basety.varname = c_t.value
            return self._read_declarator_tail(basety, params)

        #TODO some judgement

        self._back()
        return self._read_declarator_tail(basety, params)

    def _read_declarator_tail(self, basety, params):
        if self._next_t('['):
            # array
            return self._read_declarator_array(basety)
        if self._next_t('('):
            # function
            return self._read_declarator_func(basety, params)
        return basety

    def _read_declarator_func(self, basety, params):
        if basety.kind == TypeKind.FUNC:
            self._error('function returning a function')
        if basety.kind == TypeKind.ARRAY:
            self._error('function returning a array')
        return self._read_func_param_list(basety, params)

    def _read_declarator_array(self, basety):
        #TODO array
        pass

    def _read_func_param_list(self, ret_type, param_vars):
        '''
        only new style parameters list
        '''
        c_t = self._advance()
        if c_t.value == 'K_VOID' and self._next_t(')'):
            return self._tm.make_func_type(basety, [], False)

        if c_t.value == ')':
            return self._tm.make_func_type(basety, [], False)

        self._back()
        p_t = self._peek()
        if p_t.value == '...':
            self._error('at least one parameters is required before ...')
        if self._is_type(p_t):
            params_type = []
            isellipsis = self._read_declarator_params(params_type, param_vars)
            return self._tm.make_func_type(ret_type, params_type, isellipsis)

    def _read_declarator_params(self, params_type, param_vars):
        '''
        read parameters
        return is_ellipsis
        '''
        is_typeonly = True if param_vars is None else False
        while True:
            if self._next_t('...'):
                if len(params_type) == 0:
                    self._error('at least one parameter is required before ...')
                self._expect(')')
                return True

            ty = self._read_func_param(is_typeonly)
            self._ensure_not_void(ty)
            params_type.append(ty)
            if not is_typeonly:
                param_vars.append(self._nf.var_node(ty, False))
            c_t = self._advance()
            if c_t.value == ')':
                return False
            if c_t.value != ',':
                self._error('comma expected, but got {}'.format(c_t.value))

    def _read_func_param(self, is_typeonly):
        basety = self._tm.type_int()
        p_t = self._peek()
        if self._is_type(p_t):
            basety = self._read_decl_spec()
        elif is_typeonly:
            self._error('type expected, but got {}'.format(p_t.value))
        ty = self._read_declarator(basety, None, DeclType.PARAM_TYPE_ONLY if is_typeonly else DeclType.PARAM)

        if ty.kind == TypeKind.ARRAY:
            #TODO
            pass

        if ty.kind == TypeKind.FUNC:
            return self._tm.make_ptr_type(ty)

        return ty

    def _read_func_body(self, functype, params):
        pass

    def _read_abstract_declarator(self, basety):
        '''
        read a type name.used for casting
        '''
        return self._read_declarator(basety, None, DeclType.CAST)

    def _read_decl_init(self, ty):
        r = []
        if self._peek().value == '{':
            #TODO read initializer list
            pass
        else:
            #read assignment expression
            node = self._conv(self._read_assignment_expr()) # need coversion
            #TODO some judgement
            r.append(self._nf.init_node(node, ty))
        return r

    def _read_assignment_expr(self):
        '''
        assignment expression
        '''
        node = self._read_logor_expr()
        #TODO '?' operation

        #TODO '=' operation

        return node


    def _read_logor_expr(self):
        '''
        logical or expression
        '''
        node = self._read_logand_expr()
        while self._next_t('||'):
            node = self._nf.binary_node(NodeKind.OP_LOGOR, self._tm.type_int(), node, self._read_logand_expr())
        return node

    def _read_logand_expr(self):
        '''
        logical and expression
        '''
        node = self._read_bitor_expr()
        while self._next_t('&&'):
            node = self._nf.binary_node(NodeKind.OP_LOGAND, self._tm.type_int, node, self._read_bitor_expr())
        return node

    def _read_bitor_expr(self):
        '''
        bit or expression | operation
        '''
        node = self._read_bitxor_expr()
        while self._next_t('|'):
            node = self._binop(NodeKind.OP_BITOR, self._conv(node), self._conv(self._read_bitxor_expr()))
        return node

    def _read_bitxor_expr(self):
        '''
        bit xor expression ^ operation
        '''
        node = self._read_bitand_expr()
        while self._next_t('^'):
            node = self._binop(NodeKind.OP_BITXOR, self._conv(node), self._conv(self._read_bitand_expr()))
        return node

    def _read_bitand_expr(self):
        '''
        bit and expression & operation
        '''
        node = self._read_equlity_expr()
        while self._next_t('&'):
            node = self._binop(NodeKind.OP_BITAND, self._conv(node), self._conv(self._read_equlity_expr()))
        return node

    def _read_equlity_expr(self):
        '''
        == or != operation
        '''
        node = self._read_relational_expr()
        if self._next_t('=='):
            node = self._binop(NodeKind.OP_EQ, self._conv(node), self._conv(self._read_relational_expr()))
        elif self._next_t('!='):
            node = self._binop(NodeKind.OP_NE, self._conv(node), self._conv(self._read_relational_expr()))
        return node

    def _read_relational_expr(self):
        '''
        < > <= >= operation
        '''
        node = self._read_shift_expr()
        while True:
            if self._next_t('<'):
                node = self._binop(NodeKind.OP_L, self._conv(node), self._conv(self._read_shift_expr()))
            elif self._next_t('>'):
                node = self._binop(NodeKind.OP_L, self._conv(self._read_shift_expr()), self._conv(node))
            elif self._next_t('<='):
                node = self._binop(NodeKind.OP_LE, self._conv(node), self._conv(self._read_shift_expr()))
            elif self._next_t('>='):
                node = self._binop(NodeKind.OP_LE, self._conv(self._read_shift_expr()), self._conv(node))
            else:
                return node

    def _read_shift_expr(self):
        '''
        << or >> shift operation
        '''
        #TODO something
        node = self._read_additive_expr()
        while True:
            if self._next_t('<<'):
                node = self._binop(NodeKind.OP_SAL, self._conv(node), self._conv(self._read_additive_expr()))
            elif self._next_t('>>'):
                node = self._binop(NodeKind.OP_SAL, self._conv(node), self._conv(self._read_additive_expr()))
            else:
                break
        return node

    def _read_additive_expr(self):
        '''
        + or - operation
        '''
        node = self._read_multiply_expr()
        while True:
            if self._next_t('+'):
                node = self._binop(NodeKind.OP_ADD, self._conv(node), self._conv(self._read_multiply_expr()))
            elif self._next_t('-'):
                node = self._binop(NodeKind.OP_SUB, self._conv(node), self._conv(self._read_multiply_expr()))
            else:
                return node

    def _read_multiply_expr(self):
        '''
        * , / or % operation
        '''
        node = self._read_cast_expr()
        while True:
            if self._next_t('*'):
                node = self._binop(NodeKind.OP_MUL, self._conv(node), self._conv(self._read_cast_expr()))
            elif self._next_t('/'):
                node = self._binop(NodeKind.OP_DIV, self._conv(node), self._conv(self._read_cast_expr()))
            elif self._next_t('%'):
                node = self._binop(NodeKind.OP_MOD, self._conv(node), self._conv(self._read_cast_expr()))
            else:
                return node

    def _read_cast_expr(self):
        '''
        cast operation
        '''
        c_t = self._advance()
        if c_t.value == '(' and self._is_type(self._peek()):
            ty = self._read_cast_type()
            self._expect(')')
            if self._peek().value == '{':
                #TODO
                pass
            return self._nf.unary_node(NodeKind.OP_CAST, ty, self._read_cast_expr())

        self._back()
        return self._read_unary_expr()

    def _read_cast_type(self):
        return self._read_abstract_declarator(self._read_decl_spec())

    def _read_unary_expr(self):
        '''
        unary operation
        '''
        #TODO
        c_t = self._advance()
        if c_t.kind == TokenKind.TKEYWORD or c_t.kind == TokenKind.TOPERATE:
            if c_t.value == 'K_SIZEOF':
                pass
            elif c_t.value == 'K_ALIGNOF':
                pass
            elif c_t.value == '++':
                pass
            elif c_t.value == '--':
                pass
            elif c_t.value == '&':
                pass
            elif c_t.value == '*':
                pass
            elif c_t.value == '+':
                return self._read_cast_expr()
            elif c_t.value == '-':
                return self._read_unary_minus()
            elif c_t.value == '~':
                pass
            elif c_t.value == '!':
                return self._read_unary_lognot()

        self._back()
        return self._read_postfix_expr()

    def _read_unary_lognot(self):
        '''
        ! operation
        '''
        node = self._read_cast_expr()
        return self._nf.unary_node(NodeKind.OP_LOGNOT, self._tm.type_int(), self._conv(node))

    def _read_unary_minus(self):
        node = self._read_cast_expr()
        self._ensure_arithtype(node)
        return self._nf.unary_node(NodeKind.OP_MINUS, node.ty, node)

    def _read_postfix_expr(self):
        '''
        postfix expression
        '''
        node = self._read_primary_expr()
        return self._read_postfix_expr_tail(node)

    def _read_postfix_expr_tail(self, node):
        while True:
            if self._next_t('('):
                #TODO function call
                continue
            if self._next_t('['):
                #TODO
                continue
            if self._next_t('.'):
                #TODO
                continue
            if self._next_t('->'):
                #TODO
                continue
            p_t = self._peek()
            if p_t.value == '++' or p_t.value == '--':
                self._ensure_lvalue(node)
                self._advance()
                op = NodeKind.OP_POST_INC if p_t.value == '++' else NodeKind.OP_POST_DEC
                return self._nf.unary_node(op, node.ty, node)
            return node


    def _read_primary_expr(self):
        '''
        primary expression
        '''
        c_t = self._advance()
        if c_t.kind == TokenKind.TEOF:
            return None
        if c_t.value == '(':
            #TODO
            return None

        if c_t.kind == TokenKind.TIDENT:
            #TODO
            return None
        elif c_t.kind == TokenKind.TNUMBER:
            return self._read_number(c_t)
        elif c_t.kind == TokenKind.TCHAR:
            #TODO
            return None
        elif c_t.kind == TokenKind.TSTRING:
            #TODO
            return None
        else:
            self._error('internal error: unknown token kind {}'.format(c_t.kind))

    def _read_number(self, tok):
        v = tok.value
        if v.isdigit():
            return self._read_int(tok)
        else:
            return self._read_float(tok)

    def _read_float(self, tok):
        #TODO double float type
        return self._nf.val_node(self._tm.type_float(), float(tok.value))

    def _read_int(self, tok):
        #TODO int uint long ulong
        return self._nf.val_node(self._tm.type_int(), int(tok.value))

    def _read_decl(self, isglobal=True):
        '''
        declaration
        '''
        basetype = self._read_decl_spec()
        if self._next_t(';'):
            return

        while True:
            ty = self._read_declarator(basetype, None)
            #TODO sclass,typedef

            self._ensure_not_void(ty)
            node = self._nf.var_node(ty, True)
            if self._next_t('='):
                # decl init
                self.ast.append(self._nf.decl_node(node, self._read_decl_init(ty)))
            elif ty.kind != TypeKind.FUNC:
                # decl not init
                self.ast.append(self._nf.decl_node(node, None))

            if self._next_t(';'):
                return

    def _read_funcdef(self):
        '''
        function declaration
        return ast node
        '''
        #TODO
        basety = self._read_decl_spec()
        self._sm.enter_scope()
        params = [] # store parameters node
        functype = self._read_declarator(basety, params, DeclType.BODY)
        self._expect('{')
        node = self._read_func_body(functype, params)
        self._sm.exit_scope()
        self._nf.var_node()
        return node

    def parse(self):
        while True:
            if self._peek() is None or self._peek().kind == TokenKind.TEOF:
                break;
            if self._is_funcdef():
                #TODO read function definition
                pass
            else:
                self._read_decl()
