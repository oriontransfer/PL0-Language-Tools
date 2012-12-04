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
This translates the compiled pl0 machine code to retroforth
instructions.
"""
from pl0_compiler import Block, Compiler
from pl0_node_visitor import *
import sys
import pl0_parser
import StringIO
import os

class RetroTranspiler(Compiler):

    def accept_variables(self, node ):
        pass

    def accept_constants(self, node):
        pass

    def accept_procedures(self, node):
        pass

    def accept_program(self, node):
        pass

    def accept_while(self, node):
        pass

    def accept_if(self, node):
        pass

    def accept_condition(self, node):
        pass

    def accept_set(self, node):
        pass

    def accept_call(self, node):
        pass

    def accept_term(self, node):
        pass

    def accept_expression(self, node):
        pass

    def accept_print(self, node):
        pass

    def accept_number(self, node):
        pass

    def accept_name(self, node):
        pass

if __name__ == '__main__':
    code = sys.stdin.read()
    parser = pl0_parser.Parser()
    parser.input(code)
    program = parser.p_program()
    compiler = RetroTranspiler()
    compiler.generate(program)
