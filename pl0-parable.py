#!/usr/bin/env python
#
# Copyright (c) 2012 Michal J Wallace. <http://www.michaljwallace.com/>
# Copyright (c) 2012, 2016 Charles R Childers
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
representation in parable ( http://forthworks.com/parable )
"""
from pl0_node_visitor import StackingNodeVisitor
import sys
import pl0_parser
import StringIO
import os
import types

# AST->parable translator for operators
ops = {
    'DIVIDE' : '/ floor',   # integer div
    'MODULO' : 'rem',
    'TIMES'  : '*',
    'PLUS'   : '+',
    'MINUS'  : '-',
}

rel_ops = {
    'LT'     : 'lt?',
    'LTE'    : 'lteq?',
    'GT'     : 'gt?',
    'GTE'    : 'gteq?',
    'E'      : 'eq?',
    'NE'     : '-eq?',
}

UNKNOWN, VAR, CONST, PROCEDURE = range(4)
CATEGORY = "UNKNOWN VAR CONST PROCEDURE".split()


class ParableTranspiler(StackingNodeVisitor):

    stacksize = 256 # cells

    def __init__(self):
        super(ParableTranspiler, self)
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
        self.proc_path = []    # for nested procedure defs
        self.local_defs = {}   # symbol table for top level / current proc
        self.scope = []        # list of symbol tables for lexical scope
        self.scope.append(self.local_defs)

    def local_vars(self):
        """
        returns a list of names of variables to preserve
        when calling functions recursively
        """
        return [ key for (key, (kind, _)) in self.local_defs.items()
                 if kind == VAR ]

    def lookup(self, name):
        for frame in reversed( self.scope ):
            if name in frame :
                return frame[ name ]
            else: pass
        else: raise LookupError( "name not found: %s. scope is %r"
                                 % ( name, self.scope ))

    def visit( self, node ):
        """like visit_node but works with generators"""
        result = self.visit_node( node )
        if isinstance( result, types.GeneratorType ):
            result = "\n".join( result )
        return result

    #-- simple numbers -----------------

    def accept_number(self, nid, value):
        if self.negate:
            print "#-{0}".format(value),
            self.negate = False
        else:
            sys.stdout.write(" #")
            print value,

    # logically, print ("!") would come much later
    # but i'm putting these in implementation order,
    # and i want this up front so i can see the
    # results of running the code.
    def accept_print(self, nid, expr):
        self.visit( expr )
        print 'PL/0.display',

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
            print "#-1 *",

    #-- named constants ----------------

    def accept_define(self, nid, name, value):
        self.local_defs[ name ] = (CONST, value)

    def accept_name(self, nid, name):
        category, value = self.lookup( name )
        if category == CONST:
            sys.stdout.write(" #{0} ".format(value))
        elif category == VAR:
            sys.stdout.write(' ')
            sys.stdout.write(self.name_op)
            if len(self.scope) > 1:
                sys.stdout.write("~" + value)
            else:
                sys.stdout.write(value)
            sys.stdout.write(' ')
        else:
            raise Exception("unhandled name: (%s:%s) . scope is: %r"
                            % [CATEGORY[category], value,
                               self.scope])


    #-- named variables & assignment ---

    def accept_variables(self, nid, *names):
        if len(self.scope) > 1:
            prefix = "~"
        else:
            prefix = ""
        sys.stdout.write('[ ')
        for nid, name in names:
            print "'" + prefix + name + "' ",
            self.local_defs[ name ] = (VAR, name)
        print '] ::\n'

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
        sys.stdout.write(' ' + rel_ops[ rel ] + ' ')

    def accept_if(self, nid, cond, stmt):
        self.visit( cond )
        sys.stdout.write(" [ ")
        self.visit( stmt )
        sys.stdout.write(" ] if-true ")

    def accept_while(self, nid, cond, stmt):
        self.visit( cond )
        print " [ [",
        self.visit( stmt )
        self.visit( cond )
        print "] while ] if-true",


    #-- procedures ---------------------

    def accept_program(self, nid, block):

        (blocknid, procs, consts, vars, stmt) = block
        sys.stdout.write("request-empty '*Output' var!\n[ &*Output push ] 'PL/0.display' :\n")
        self.visit_expressions([procs, consts, vars])
        sys.stdout.write("[ ")
        self.visit(stmt)
        sys.stdout.write(" ] 'run' :\n")
        print "run\n*Output"


    # for recursion, we need to maintain a stack
    def accept_procedure(self, nid, name, block):

        (blocknid, procs, consts, vars, stmt) = block
        self.proc_path.append(name)
        self.scope.append(self.local_defs)

        # enable recursion
        sys.stdout.write(" [ ] '" + name + "' :\n")

        self.visit_expressions([procs, consts, vars])
        sys.stdout.write("[ ")
        self.visit(stmt)
        sys.stdout.write(" ] '" + name + "' :\n")

        if self.scope > 1:
            sys.stdout.write('[ ')
            for v in self.local_defs:
                sys.stdout.write("'~" + v + "' ")
            sys.stdout.write('] hide-words\n')

        self.proc_path.pop()
        self.scope.pop()
        self.local_defs = self.scope[-1]

    def accept_call(self, nid, name):

        # this detects simple recursion
        #TODO: full recursion check
        #TODO: tail call optimization
        #TODO: only push/pop shadowed variables
        recursive = name in self.proc_path

        def call(): print name,

        keep = self.local_vars()

        if recursive:
            sys.stdout.write(' [ ')
            for ident in keep:
                 sys.stdout.write(' &' + ident)
            sys.stdout.write(' ] [ ')
            call()
            sys.stdout.write(' ] invoke<preserving> ')
#            for ident in reversed( keep ):
#                 sys.stdout.write(' !' + ident)
        else:
            call()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'PL/0 to Parable Transpiler'
        print 'Usage:'
        print '    ./pl0-parable.py input >output'
    else:
        code = open(sys.argv[1], 'r').read()
        parser = pl0_parser.Parser()
        parser.input(code)
        program = parser.p_program()
        compiler = ParableTranspiler()
        compiler.visit_node(program)

