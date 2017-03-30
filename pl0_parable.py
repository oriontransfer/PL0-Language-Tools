#!/usr/bin/env python
#
# Copyright (c) 2012 Samuel G. D. Williams. <http://www.oriontransfer.co.nz>
# Copyright (c) 2012 Michal J Wallace. <http://www.michaljwallace.com/>
# Copyright (c) 2012, 2016 Charles Childers <http://forthworks.com/>
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

import os
import sys
#import StringIO
import pl0_parser
from pl0_node_visitor import StackingNodeVisitor

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

class Compiler(StackingNodeVisitor):

    def __init__(self):
        super(Compiler, self).__init__()
        self.label_id = 0

    def intermediate_label(self, hint = ''):
        self.label_id += 1
        return 't_' + hint + '_' + repr(self.label_id)

    def generate(self, node):
        self.push()
        result = self.visit_node(node)
        return [self.pop(), result]

    def accept_variables(self, *node):
        for var in node[1:]:
            # Generate a unique name for the variable
            variable_name = self.intermediate_label('var_' + var[1])

            # Save the unique name for loading this variable in the future.
            self.stack[-1].update(var[1], variable_name)

            # Allocate static storage space for the variable
            print("'" + variable_name + "' var")
#            print "    0"

    def accept_constants(self, *node):
        for var in node[1:]:
            self.stack[-1].define(var[1], var[2])

    def accept_procedures(self, *node):
        for proc in node[1:]:
            # Generate a unique name for the procedure
            proc_name = self.intermediate_label('proc_' + proc[1])

            # Save the unique procedure name on the lexical stack
            self.stack[-1].declare(proc[1], proc_name)

            # Define a new lexical scope
            self.push()

            # Generate any static storage required by the procedure
            print("\"Procedure " + proc[1] + "\"")
            self.visit_expressions(proc[2][1:3])

            # Generate the code for the procedure
            print("[ ] '" + proc_name + "' :")
            print("[")
            self.visit_node(proc[2][4])
            print("] '" + proc_name + "' :")

            # Finished with lexical scope
            self.pop()

    def accept_program(self, *node):
#        print "JMP main"
        print("'Output' var\n&Output pop drop")

        block = node[1]
        self.visit_expressions(block[1:4])

        print("[")
        self.visit_node(block[4])
        print("] 'main' :")
        print('main Output')

    def accept_while(self, *node):
        top_label = self.intermediate_label("while_start")
        bottom_label = self.intermediate_label("while_end")

        condition = node[1]
        loop = node[2]

        print("[")
#        print top_label + ":"
        # Result of condition is on top of stack

#        print "\tJE " + bottom_label

        self.visit_node(loop)

#        print "\tJMP " + top_label
#        print bottom_label + ":"
        self.visit_node(condition)
        print("] while")


    def accept_if(self, *node):
        false_label = self.intermediate_label("if_false")

        condition = node[1]
        body = node[2]

        self.visit_node(condition)
        print("[")
#        print "\tJE " + false_label

        self.visit_node(body)

        print("] if-true")

#        print false_label + ":"

    def accept_condition(self, *node):
        operator = node[2]
        lhs = node[1]
        rhs = node[3]

        self.visit_node(lhs)
        self.visit_node(rhs)

#        print "\tCMP" + operator
        print(" " + rel_ops[operator])

    def accept_set(self, *node):
        name = node[1][1]

        self.visit_node(node[2])

        assign_to = node[1][1]
        defined, value, level = self.find(assign_to)

        if defined != 'VARIABLE':
            raise NameError("Invalid assignment to non-variable " + assign_to + " of type " + defined)

        print(" !" + str(value))

    def accept_call(self, *node):
        defined, value, level = self.find(node[1])

        if defined != 'PROCEDURE':
            raise NameError("Expecting procedure but got: " + defined)

        print(" |" + value)

    def accept_term(self, *node):
        self.visit_node(node[1])

        for term in node[2:]:
            self.visit_node(term[1])

            if term[0] == 'TIMES':
                print(" *")
            elif term[0] == 'DIVIDES':
                print(" / floor")

    def accept_expression(self, *node):
        # Result of this expression will be on the top of stack
        self.visit_node(node[2])

        for term in node[3:]:
            self.visit_node(term[1])

            if term[0] == 'PLUS':
                print(" +")
            elif term[0] == 'MINUS':
                print(" -")

        if node[1] == 'MINUS':
            print(" -1 *")

    def accept_print(self, *node):
        self.visit_node(node[1])
        print(" &Output push")
#        print "\tPOP"

    def accept_number(self, *node):
        print(" #" + repr(node[1]))

    def accept_name(self, *node):
        defined, value, level = self.find(node[1])

        if defined == 'VARIABLE':
            print(" @" + value)
        elif defined == 'CONSTANT':
            print(" " + str(value))
        else:
            raise NameError("Invalid value name " + node[1] + " of type " + defined)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('PL/0 to Parable Transpiler')
        print('Usage:')
        print('    ./pl0-parable.py input >output')
    else:
        code = open(sys.argv[1], 'r').read()
        parser = pl0_parser.Parser()
        parser.input(code)
        program = parser.p_program()
        compiler = Compiler()
        compiler.generate(program)
