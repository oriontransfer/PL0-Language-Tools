#!/usr/bin/env python
#
# Copyright (c) 2012 Samuel G. D. Williams. <http://www.oriontransfer.co.nz>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import sys
import ply.lex as lex

# program = block "." .
#
# block = [ "const" ident "=" number {"," ident "=" number} ";"]
#         [ "var" ident {"," ident} ";"]
#         { "procedure" ident ";" block ";" } statement .
#
# statement = [ ident ":=" expression | "call" ident |
#             "begin" statement {";" statement } "end" |
#             "if" condition "then" statement |
#             "while" condition "do" statement ].
#
# condition = "odd" expression |
#             expression ("="|"#"|"<"|"<="|">"|">=") expression .
#
# expression = [ "+"|"-"] term { ("+"|"-") term}.
#
# term = factor {("*"|"/") factor}.
#
# factor = ident | number | "(" expression ")".

keywords = [
    'ODD', 'CALL', 'BEGIN', 'END', 'IF', 'THEN', 'WHILE', 'DO', 'CONST', 'VAR', 'PROCEDURE', 'WRITE', 'WRITELN'
]

# Special variable named 'tokens'
tokens = keywords + [
    'DOT', 'EOS', 'UPDATE',
    'COMMA', 'LPAREN', 'RPAREN',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN', 'PRINT',
    'LT', 'LTE', 'GT', 'GTE', 'E', 'NE',
    'NAME', 'NUMBER'
]

t_ignore = ' \t'

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'

    if t.value.upper() in keywords:
        t.value = t.value.upper()
        t.type = t.value

    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'\#.*'
    # No return value. Token discarded
    pass

t_DOT = r'\.'
t_EOS = r';'

t_UPDATE = r':='

t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'

t_LT = r'<'
t_LTE = r'<='
t_GT = r'>'
t_GTE = r'>='
t_E = r'=='
t_NE = r'!='

t_ODD = r'ODD'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_PRINT = r'!'

def t_NUMBER(t):
    r'\d+'

    t.value = int(t.value)

    return t

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

def create():
    return lexer.clone()

if __name__ == "__main__":
    code = sys.stdin.read()

    lex.input(code)

    while True:
        tok = lex.token()
        if not tok: break

        print(tok)
