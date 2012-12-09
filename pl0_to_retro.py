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
from pl0_node_visitor import StackingNodeVisitor
import sys
import pl0_parser
import StringIO
import os
import types

# AST->retro translator for operators
ops = {
    'DIVIDE' : '/',   # integer div
    'MODULO' : 'mod',
    'TIMES'  : '*',
    'PLUS'   : '+',
    'MINUS'  : '-',
}

class RetroTranspiler(StackingNodeVisitor):

    def visit( self, node ):
        """like visit_node but works with generators"""
        result = self.visit_node( node )
        if isinstance( result, types.GeneratorType ):
            result = "\n".join( result )
        return result

    #-- simple numbers -----------------

    def accept_number(self, nid, value):
        print value,

    # logically, print ("!") would come much later
    # but i'm putting these in implementation order,
    # and i want this up front so i can see the
    # results of running the code.
    def accept_print(self, nid, expr):
        self.visit( expr )
        print "putn"

    #-- expressions --------------------

    # example: a + b * c + d * e + f
    # becomes: a b c * + d e * + f +

    # term = factor {("*"|"/") factor}.
    def accept_term( self, nid, *factors_tup ):
        factors = list( factors_tup )
        self.visit( factors.pop( 0 ))
        for operator, operand in factors:
            self.visit( operand )
            print ops[ operator ],

    # expression = [ "+"|"-"] term { ("+"|"-") term}.
    def accept_expression(self, nid, *terms_tup):
        terms = list( terms_tup )
        self.visit( terms.pop( 0 ))
        for node in terms:
            if node[0]=="TERM":
                self.visit(node)
            else:
                operator, term = node
                self.visit( term )
                print ops[ operator ],

    #-- named constants ----------------

    def accept_define(self, nid, name, value):
        print value,
        print "constant",
        print name

    def accept_name(self, nid, name):
        print name,

"""

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
"""

if __name__ == '__main__':
    code = sys.stdin.read()
    parser = pl0_parser.Parser()
    parser.input(code)
    program = parser.p_program()
    compiler = RetroTranspiler()
    compiler.visit_node(program)
