import sys
from graphviz import Digraph
import time
sys.path.append("..")
from lex import Lexer
from parse import Parser
from astc import *

def filename(path):
    index = str(path).rfind('/') + 1
    name = path[index:]
    return name

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def see_ast(ast):
    dot = Digraph(comment='ast')
    dot.node('root', 'root')
    for node in ast:
        see_node('root', node, dot)
    dot.render('test-output/ast.gv', view=True)

def see_node(p_name, node, dot):
    name = str(int(round(time.time() * 100000)))
    if type(node) == ValueNode:
        dot.node(name, str(node.kind) + '( value:' + str(node.val) + ' )')
        dot.edge(p_name, name)
    elif type(node) == VarNode:
        dot.node(name, str(node.kind) + '( var:' + node.name + ' )')
        dot.edge(p_name, name)
    elif type(node) == DeclNode:
        dot.node(name, str(node.kind))
        dot.edge(p_name, name)
        see_node(name, node.declvar, dot)
        for n in node.declinit:
            see_node(name, n, dot)
    elif type(node) == InitNode:
        dot.node(name, str(node.kind))
        dot.edge(p_name, name)
        see_node(name, node.initval, dot)
    elif type(node) == BinaryNode:
        dot.node(name, str(node.kind))
        dot.edge(p_name, name)
        see_node(name, node.left, dot)
        see_node(name, node.right, dot)
    elif type(node) == UnaryNode:
        dot.node(name, str(node.kind))
        dot.edge(p_name, name)
        see_node(name, node.operand, dot)

if __name__ == '__main__':
    path = './t1.c'
    l = Lexer(filename(path), read_file(path))
    l.lex()
    l.see_tokens()

    p = Parser(l.tokens)
    p.parse()

    see_ast(p.ast)

