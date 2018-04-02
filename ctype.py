'''
Copyright 2018 JackLiang.

C Type
'''
from enum import Enum, unique
from utils.singleton import *

@unique
class TypeKind(Enum):
    VOID = 0
    BOOL = 1
    CHAR = 2
    SHORT = 3
    INT = 4
    LONG = 5
    LLONG = 6
    FLOAT = 7
    DOUBLE = 8
    LDOUBLE = 9
    ARRAY = 10
    ENUM = 11
    PTR = 12
    STRUCT = 13
    FUNC = 14

@unique
class SClass(Enum):
    S_TYPEDEF = 1
    S_EXTERN = 2
    S_STATIC = 3
    S_AUTO = 4
    S_REGISTER = 5

class Type(object):

    def __init__(self):
        self.kind = TypeKind.VOID
        self.size = 1
        self.align = 1
        self.usig = False
        self.isstatic = False
        self.scalss = SClass.S_AUTO

        self.varname = '' # store variable name

        self.ptr = None #pointer or array
        self.array_len = 0 # array length

        #function
        self.ret_type = None
        self.params = []
        self.hasva = False # for have variable parameter

    def is_arithtype(self):
        return self.is_inttype() or self.is_floattype()

    def is_inttype(self):
        if self.kind == TypeKind.INT or self.kind == TypeKind.CHAR or self.kind == TypeKind.BOOL or self.kind == TypeKind.SHORT or self.kind == TypeKind.LLONG or self.kind == TypeKind.LLONG:
            return True
        return False

    def is_floattype(self):
        if self.kind == TypeKind.FLOAT or self.kind == TypeKind.DOUBLE or self.kind == TypeKind.LDOUBLE:
            return True
        return False

class TypeMaker(Singleton):

    def type_void(self):
        t = Type()
        t.kind = TypeKind.VOID
        t.size = 0
        t.align = 0
        return t

    def type_bool(self):
        t = Type()
        t.kind = TypeKind.BOOL
        t.size = 1
        t.align = 1
        t.usig = True
        return t

    def type_char(self):
        t = Type()
        t.kind = TypeKind.CHAR
        t.size = 1
        t.align = 1
        return t

    def type_short(self):
        t = Type()
        t.kind = TypeKind.SHORT
        t.size = 2
        t.align = 2
        return t

    def type_int(self):
        t = Type()
        t.kind = TypeKind.INT
        t.size = 4
        t.align = 4
        return t

    def type_long(self):
        t = Type()
        t.kind = TypeKind.LONG
        t.size = 8
        t.align = 8
        return t

    def type_llong(self):
        t = Type()
        t.kind = TypeKind.LLONG
        t.size = 8
        t.align = 8
        return t

    def type_uchar(self):
        t = Type()
        t.kind = TypeKind.CHAR
        t.size = 1
        t.align = 1
        t.usig = True
        return t

    def type_unshort(self):
        t = Type()
        t.kind = TypeKind.SHORT
        t.size = 2
        t.align = 2
        t.usig = True
        return t

    def type_uint(self):
        t = Type()
        t.kind = TypeKind.INT
        t.size = 4
        t.align = 4
        t.usig = True
        return t

    def type_ulong(self):
        t = Type()
        t.kind = TypeKind.LONG
        t.size = 8
        t.align = 8
        t.usig = True
        return t

    def type_ullong(self):
        t = Type()
        t.kind = TypeKind.LLONG
        t.size = 8
        t.align = 8
        t.usig = True
        return t

    def type_float(self):
        t = Type()
        t.kind = TypeKind.FLOAT
        t.size = 4
        t.align = 4
        return t

    def type_double(self):
        t = Type()
        t.kind = TypeKind.DOUBLE
        t.size = 8
        t.align = 8
        return t

    def type_ldouble(self):
        t = Type()
        t.kind = TypeKind.LDOUBLE
        t.size = 8
        t.align = 8
        return t

    def type_enum(self):
        t = Type()
        t.kind = TypeKind.ENUM
        t.size = 4
        t.align = 4
        return t

    def make_num_type(self, kind, usig):
        t = Type()
        t.kind = kind
        t.usig = usig
        if kind == TypeKind.VOID:
            t.size = 0
            t.align = 0
        elif kind == TypeKind.CHAR:
            t.size = 1
            t.align = 1
        elif kind == TypeKind.SHORT:
            t.size = 2
            t.align = 2
        elif kind == TypeKind.INT:
            t.size = 4
            t.align = 4
        elif kind == TypeKind.LONG:
            t.size = 8
            t.align = 8
        elif kind == TypeKind.LLONG:
            t.size = 8
            t.align = 8
        elif kind == TypeKind.FLOAT:
            t.size = 4
            t.align = 4
        elif kind == TypeKind.DOUBLE:
            t.size = 8
            t.align = 8
        return t

    def make_ptr_type(self, ty):
        t = Type()
        t.kind = TypeKind.PTR
        t.size = 8
        t.align = 8
        t.ptr = ty
        return t

    def make_func_type(self, ret_type, params_type, hasva):
        t = Type()
        t.kind = TypeKind.FUNC
        t.ret_type = ret_type
        t.params = params_type
        t.hasva = hasva
        return t
