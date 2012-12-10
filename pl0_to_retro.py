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

rel_ops = {
    'LT'     : '<',
    'LTE'    : '<=',
    'GT'     : '>',
    'GTE'    : '>=',
    'E'      : '=',
    'NE'     : '<>',
}

class RetroTranspiler(StackingNodeVisitor):

    stacksize = 256 # cells

    def __init__(self):
        super(RetroTranspiler, self)
        # negative signs are not included in number tokens,
        # because a lexer cannot distinguish the "-1" in
        # the expression "x-1" from "-1" as a negative numer.
        #
        # the parser does this as part of the "expression"
        # rule, so "-1" is parsed as "-(1)". As an optimization,
        # we set the following flag in accept_expression when
        # we can see that the value between the parens is a
        # numeric literal. Then we can emit a negative literal
        # rather than emittting code to multiply the positive
        # literal by -1.
        self.negate = False
        self.name_op = "@"

    def visit( self, node ):
        """like visit_node but works with generators"""
        result = self.visit_node( node )
        if isinstance( result, types.GeneratorType ):
            result = "\n".join( result )
        return result

    #-- simple numbers -----------------

    def accept_number(self, nid, value):
        if self.negate:
            print "-{0}".format(value),
            self.negate = False
        else:
            print value,

    # logically, print ("!") would come much later
    # but i'm putting these in implementation order,
    # and i want this up front so i can see the
    # results of running the code.
    def accept_print(self, nid, expr):
        self.visit( expr )
        print "putn cr",

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
    def accept_expression(self, nid, sign, *terms_tup):
        terms = list( terms_tup )

        # handle negative numbers and unary minus
        negate_value = False
        negate_after = False
        if sign == "MINUS":
            assert len(terms_tup) == 1
            if terms_tup[0][1][0] == "NUMBER":
                self.negate = True
            else:
                negate_after = True

        # generate the normal expression
        for node in terms:
            if node[0]=="TERM":
                self.visit(node)
            else:
                operator, term = node
                self.visit( term )
                print ops[ operator ],

        if negate_after:
            print "-1 *",

    #-- named constants ----------------

    def accept_define(self, nid, name, value):
        print value,
        #TODO: print "constant",
        print "variable:"
        print name

    def accept_name(self, nid, name):
        print name, self.name_op,


    #-- named variables & assignment ---

    def accept_variables(self, nid, *names):
        print "variables|",
        for nid, name in names:
            print name,
        print "|"

    def accept_set(self, nid, name, expr):
        self.visit( expr )
        self.name_op = "!"
        self.visit( name )
        self.name_op = "@"


    #-- flow control -------------------

    def accept_odd(self, nid, expr):
        self.visit( expr )
        print "odd?",

    def accept_condition(self, nid, lhs, rel, rhs):
        self.visit( lhs )
        self.visit( rhs )
        print rel_ops[ rel ]

    def accept_if(self, nid, cond, stmt):
        # retro's quotations ([..]) are high level functional constructs.
        # they are nice, but incur a small extra runtime overhead.
        # TODO: go back and use plain old jumps for speed
        self.visit( cond )
        print "[",
        self.visit( stmt )
        print "] ifTrue"

    def accept_while(self, nid, cond, stmt):
        # retro actually doesn't have a standard "loop
        # with the test at the start". the "while" word
        # it offers is more like "repeat <stmt> until not <cond>"
        # so we'll use quotations for now.
        # essentially, we're saying:
        #
        #    IF <cond> THEN REPEAT <stmt> UNTIL NOT <cond>;
        #
        # which in functional-style retro is:
        #
        #    [ <cond> ] [ [ <stmt> <cond> ] while ] ifTrue
        #
        # TODO: lower level/faster WHILE implementation
        print "[ ",
        self.visit( cond )
        print "] [ [",
        self.visit( stmt )
        self.visit( cond )
        print "] while ] ifTrue",


    #-- procedures ---------------------

    def accept_program(self, nid, block):

        print "( -- runtime library ------------ )"
        print ": odd? mod 2 1 = ;"
        print "( -- main code ------------------ )"

        (blocknid, procs, consts, vars, stmt) = block
        self.visit_expressions([procs, consts, vars])
        print ": run",
        self.visit(stmt)
        print ";"
        print
        print "( ------------------------------- )"
        print "3 [ cr ] times"
        print "run"



    proc_path = []    # for nested procedure defs
    proc_locs = {}    # map path to local names

    # for recursion, we need to maintain a stack
    def accept_procedure(self, nid, name, block):
        self.proc_locs.setdefault(name, {})
        (blocknid, procs, consts, vars, stmt) = block

        print "{{"
        self.visit_expressions([procs, consts, vars])
        print "---reveal---"
        print ":", name,
        self.visit(stmt)
        print ";"
        print "}}"

    def accept_call(self, nid, name):

        # this detects simple recursion
        #TODO: full recursion check
        #TODO: tail call optimization
        #TODO: only push/pop shadowed variables
        recursive = name in self.proc_path

        def call(): print name,

        if recursive:
            for ident in procvars:
                print ident, "@"
            call()
            for ident in procvars:
                print ident, "!"
        else:
            call()

if __name__ == '__main__':
    code = sys.stdin.read()
    parser = pl0_parser.Parser()
    parser.input(code)
    program = parser.p_program()
    compiler = RetroTranspiler()
    compiler.visit_node(program)
