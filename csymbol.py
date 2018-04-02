'''
Copyright 2018 JackLiang.

scope symbol
'''
from utils.hashmap import *

CONSTANTS = 1
LABELS = 2
GLOBAL = 3
PARAM = 4
LOCAL = 5

class Coordinate(object):

    def __init__(self, filename, line, column):
        self.filename = filename
        self.line = line
        self.column = column

class Symbol(object):

    def __init__(self):
        self.name = ''
        self.scope = 0
        self.src = None
        self.up = None
        self.uses = []
        self.sclass = 0
        self.c_type = None #ctype

    def __str__(self):
        return 'Symbol({}, {})'.format(self.name,
                                       self.scope)



class SymbolTable(object):

    def __init__(self, tp, level):
        self.level = level
        self.pre = tp
        self.buckets = HashMap(256) #store symbol
        self.head = None #head symbol

    def install(self, name, level):
        tp = self
        head = tp.head
        h = self.buckets.hash(name)
        if level > 0 and self.level < level:
            tp = SymbolTable(tp, level)

        s = Symbol()
        s.name = name
        s.scope = level
        s.up = head
        tp.head = s
        tp.buckets[h].append(s)
        return (s, tp)

    def lookup(self, name):
        tp = self
        while not tp is None:
            h = tp.buckets.hash(name)
            for s in tp.buckets[h]:
                return s
            tp = tp.pre
        return None


class SymbolManager(object):

    def __init__(self):
        self.constants = SymbolTable(None, CONSTANTS)
        self.externals = SymbolTable(None, GLOBAL)
        self.identifiers = SymbolTable(None, GLOBAL)
        self.types = SymbolTable(None, GLOBAL)

        self.ident_level = GLOBAL #global level

    def enter_scope(self):
        self.ident_level += 1

    def exit_scope(self):
        '''
        when exit scope need delete the same level types table and identifiers table
        '''
        #TODO types table
        if self.identifiers.level == self.ident_level:
            self.identifiers = self.identifiers.pre
        if self.ident_level >= GLOBAL:
            self.ident_level -= 1

    def ident_install(self, name):
        r = self.identifiers.install(name, self.ident_level)
        self.identifiers = r[1]
        return r[0]

    def lookup(self, tp, name):
        return tp.lookup(name)

    def see_all(self, tp):
        while not tp is None:
            for l in tp.buckets:
                for s in l:
                    print(s)
            tp = tp.pre

        # s = tp.head
        # while not s is None:
        #     print(s)
        #     s = s.up

