'''
Copyright 2018 JackLiang.

generate tokenizer
'''
from enum import Enum, unique

KEYWORDS = {
    '_Alignas': 'K__ALIGNAS',
    '_Alignof': 'K__ALIGNOF',
    'auto': 'K_AUTO',
    '_Bool': 'K__BOOL',
    'break': 'K_BREAK',
    'case': 'K_CASE',
    'char': 'K_CHAR',
    '_Complex': 'K__COMPLEX',
    'const': 'K_CONST',
    'continue': 'K_CONTINUE',
    'default': 'K_DEFAULT',
    'do': 'K_DO',
    'double': 'K_DOUBLE',
    'else': 'K_ELSE',
    'enum': 'K_ENUM',
    'extern': 'K_EXTERN',
    'float': 'K_FLOAT',
    'for': 'K_FOR',
    '_Generic': 'K__GENERIC',
    'goto': 'K_GOTO',
    'if': 'K_IF',
    '_Imaginary': 'K__IMAGINARY',
    'inline': 'K_INLINE',
    'int': 'K_INT',
    'long': 'K_LONG',
    '_Noreturn': 'K__NORETURN',
    'register': 'K_REGISTER',
    'restrict': 'K_RESTRICT',
    'return': 'K_RETURN',
    '##': 'K_##',
    'short': 'K_SHORT',
    'signed': 'K_SIGNED',
    'sizeof': 'K_SIZEOF',
    'static': 'K_STATIC',
    '_Static_assert': 'K__STATIC_ASSERT',
    'struct': 'K_STRUCT',
    'switch': 'K_SWITCH',
    '...': 'K_...',
    'typedef': 'K_TYPEDEF',
    'typeof': 'K_TYPEOF',
    'union': 'K_UNION',
    'unsigned': 'K_UNSIGNED',
    'void': 'K_VOID',
    'volatile': 'K_VOLATILE',
    'while': 'K_WHILE'
}

@unique
class TokenKind(Enum):
    TIDENT = 0
    TKEYWORD = 1
    TOPERATE = 2
    TDELIMIT = 3
    TNUMBER = 4
    TCHAR = 5
    TSTRING = 6
    TEOF = 7
    TINVALID = 8

class Token(object):

    def __init__(self, kind, filename, line, column, value):
        self.kind = kind
        self.filename = filename
        self.line = line
        self.column = column
        self.value = value

    def __str__(self):
        return 'Token({}, {}, {}, {}, {})'.format(self.kind,
                                                  self.filename,
                                                  self.line,
                                                  self.column,
                                                  self.value)

class Lexer(object):

    def __init__(self, finename, content):
        self.tokens = []
        self._pos = -1
        self._filename = finename
        self._line = 1
        self._column = 1
        self._content = content
        if content is None:
            self._current_char = None
        else:
            self._advance()

    def error(self, e):
        s = 'position [{0}:{1}]: {2}'.format(self._line, self._column,e)
        raise Exception(s)

    def _advance(self):
        self._pos += 1
        if self._pos > len(self._content) - 1:
            self._current_char = None
        else:
            self._current_char = self._content[self._pos]
            if self._current_char == '\n':
                self._line += 1
                self._column = 1
            else:
                self._column += 1

    def _peek(self):
        peek_pos = self._pos + 1
        if peek_pos > len(self._content) - 1:
            return None
        else:
            return self._content[peek_pos]

    def _next_c(self, c):
        peek_pos = self._pos + 1
        if peek_pos > len(self._content) - 1:
            return False
        else:
            if self._content[peek_pos] == c:
                self._advance()
                return True
            else:
                return False


    def _is_blank(self):
        return self._current_char == ' ' or self._current_char == '\t' or self._current_char == '\n' or self._current_char == '\r'

    def _skip_blank(self):
        while self._current_char is not None and self._is_blank():
            self._advance()

    def _skip_comment(self):
        if self._current_char == '/':
            if self._next_c('/'):
                self._skip_line()
                return True
            elif self._next_c('*'):
                self._skip_block_comment()
                return True
        return False

    def _skip_line(self):
        while self._current_char != '\n':
            self._advance()
        self._advance()

    def _skip_block_comment(self):
        while True:
            if self._current_char is None:
                self.error('premature end of block comment')
            elif self._current_char == '*' and self._next_c('/'):
                self._advance()
                break

            self._advance()

    def _make_token(self, kind, value):
        self.tokens.append(Token(kind, self._filename, self._line, self._column, value))
        if kind != TokenKind.TEOF or kind != TokenKind.TINVALID:
            self._advance()

    def _read_rep(self, expect, v1, v2):
        self._make_token(TokenKind.TOPERATE, v1 if self._next_c(expect) else v2)

    def _read_rep2(self, expect1, v1, expect2, v2, els):
        if self._next_c(expect1):
            self._make_token(TokenKind.TOPERATE, v1)
        else:
            self._read_rep(expect2, v2, els)

    def _read_char(self):
        '''
        not finish,some situation not code TODO
        '''
        self._advance()
        c = self._current_char
        self._advance()
        if self._current_char != '\'':
            self.error('unterminated char')

        self._make_token(TokenKind.TCHAR, c)

    def _read_string(self):
        s = ''
        self._advance()
        while True:
            if self._current_char is None:
                self.error('unterminated string')

            if self._current_char == '"':
                self._make_token(TokenKind.TSTRING, s)
                break
            else:
                s += self._current_char
                self._advance()

    def _read_number(self):
        n = self._current_char
        while self._peek().isdigit() or self._peek() == '.':
            self._advance()
            n += self._current_char

        if n.isdigit():
            self._make_token(TokenKind.TNUMBER, n)
        else:
            if n.count('.') == 1:
                self._make_token(TokenKind.TNUMBER, n)
            else:
                self.error('error number format')

    def _read_ident(self):
        ident = self._current_char
        while self._peek().isalnum() or self._peek() == '_' or self._peek() == '$':
            self._advance()
            ident += self._current_char

        keyword = KEYWORDS.get(ident, None)
        if keyword is None:
            self._make_token(TokenKind.TIDENT, ident)
        else:
            self._make_token(TokenKind.TKEYWORD, keyword)

    def lex(self):
        while self._current_char is not None:

            self._skip_blank()
            if self._skip_comment():
                continue

            if self._current_char is None or self._is_blank():
                continue

            if self._current_char == '#':
                #TODO
                pass
            elif self._current_char == ':':
                #TODO
                pass
            elif self._current_char == '+':
                self._read_rep2('+', '++', '=', '+=', '+')
            elif self._current_char == '-':
                if self._next_c('-'):
                    self._make_token(TokenKind.TOPERATE, '--')
                elif self._next_c('>'):
                    self._make_token(TokenKind.TOPERATE, '->')
                elif self._next_c('='):
                    self._make_token(TokenKind.TOPERATE, '-=')
                else:
                    self._make_token(TokenKind.TOPERATE, '-')
            elif self._current_char == '<':
                if self._next_c('<'):
                    self._read_rep('=', '<<=', '<<')
                else:
                    self._read_rep('=', '<=', '<')
            elif self._current_char == '>':
                if self._next_c('>'):
                    self._read_rep('=', '>>=', '>>')
                else:
                    self._read_rep('=', '>=', '>')
            elif self._current_char == '*':
                self._read_rep('=', '*=' , '*')
            elif self._current_char == '=':
                self._read_rep('=', '==', '=')
            elif self._current_char == '!':
                self._read_rep('=', '!=', '!')
            elif self._current_char == '&':
                self._read_rep2('&', '&&', '=', '&=', '&')
            elif self._current_char == '|':
                self._read_rep2('|', '||', '=', '|=', '|')
            elif self._current_char == '^':
                self._read_rep('=', '^=', '^')
            elif self._current_char == '%':
                self._make_token(TokenKind.TOPERATE, '%')
            elif self._current_char == '/':
                self._read_rep('=', '/=', '/')
            elif self._current_char == '\'':
                self._read_char()
            elif self._current_char == '"':
                self._read_string()
            elif self._current_char.isalpha() or self._current_char == '_' or self._current_char == '$':
                self._read_ident()
            elif self._current_char.isdigit():
                self._read_number()
            elif self._current_char == '.':
                if self._peek().isdigit():
                    self._read_number()
                else:
                    if self._next_c('.'):
                        self._read_rep('.', '...', '..')
                self._make_token(TokenKind.TOPERATE, '.')
            elif self._current_char == '(' or self._current_char == ')' or self._current_char == '[' or self._current_char == ']' or self._current_char == '{' or self._current_char == '}' or self._current_char == ',' or self._current_char == ';' or self._current_char == '?' or self._current_char == '~':
                self._make_token(TokenKind.TDELIMIT, self._current_char)
            else:
                self._make_token(TokenKind.TINVALID, None)
                self.error('\'' + self._current_char + '\' ' + 'invalid character')

        self._make_token(TokenKind.TEOF, None)

    def see_tokens(self):
        for t in self.tokens:
            print(t)



