#!/usr/bin/env python
#
# Copyright (c) 2012 Michal J Wallace. <http://www.michaljwallace.com/>
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

"""
This translates the pl0 syntax tree to the equivalent
representation in retroforth ( http://retroforth.org/ )
"""
from pl0_compiler import Compiler
import sys
import pl0_parser
import StringIO
import os

class RetroTranspiler(Compiler):

    #-- simple numbers -----------------

    def accept_number(self, *node):
        pass

    # logically, print ("!") would come much later
    # but i'm putting these in implementation order,
    # and i want this up front so i can see the
    # results of running the code.
    def accept_print(self, *node):
        pass

    #-- expressions --------------------

    def accept_term(self, *node):
        pass

    def accept_expression(self, *node):
        pass

    #-- named constants ----------------

    def accept_constants(self, nid, consts):
        pass

    def accept_name(self, *node):
        pass

    #-- named variables & assignment ---

    def accept_variables(self, nid, vars):
        pass

    def accept_set(self, nid, ident, expr):
        pass

    #-- flow control -------------------

    def accept_condition(self, *node):
        pass

    def accept_if(self, *node):
        pass

    def accept_while(self, nid, expr, block):
        pass

    #-- procedures ---------------------

    def accept_procedure(self, nid, name, block):
        pass

    def accept_call(self, *node):
        pass

    def accept_program(self, nid, block):
        pass


if __name__ == '__main__':
    code = sys.stdin.read()
    parser = pl0_parser.Parser()
    parser.input(code)
    program = parser.p_program()
    compiler = RetroTranspiler()
    compiler.generate(program)
