import sys
sys.path.append("..")
from lex import Lexer

def filename(path):
    index = str(path).rfind('/') + 1
    name = path[index:]
    return name

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

if __name__ == '__main__':
    path = './t1.c'
    lexer = Lexer(filename(path), read_file(path))
    lexer.lex()
    lexer.see_tokens()

