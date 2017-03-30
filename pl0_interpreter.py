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

import os
import sys
import StringIO
import pl0_parser
from pl0_node_visitor import StackingNodeVisitor

class Procedure:

    def __init__(self, name, node, block):
        self.name = name
        self.node = node
        self.block = block

class Interpreter(StackingNodeVisitor):

    def evaluate(self, node):
        self.push()
        result = self.visit_node(node)
        return [self.pop(), result]


    def accept_variables(self, *node):
        for var in node[1:]:
            self.stack[-1].update(var[1], 0)

    def accept_constants(self, *node):
        for var in node[1:]:
            self.stack[-1].define(var[1], var[2])

    def accept_procedures(self, *node):
        for proc in node[1:]:
            self.stack[-1].procedures[proc[1]] = Procedure(proc[1], proc[2], self.stack[-1])

    def accept_set(self, *node):
        name = node[1][1]
        block, result = self.evaluate(node[2])

        defined, value, level = self.find(name)
        self.stack[level].update(name, result)

    def accept_while(self, *node):
        condition = node[1]
        loop = node[2]

        while True:
            block, result = self.evaluate(condition)

            if not result:
                break

            self.evaluate(loop)

    def accept_if(self, *node):
        condition = node[1]
        body = node[2]

        block, result = self.evaluate(condition)

        if result:
            self.evaluate(body)

    def accept_odd(self, nid, expr):
        block, result = self.evaluate(expr)
        return result % 2 != 0

    def accept_condition(self, *node):
        operator = node[2]
        lhs = self.evaluate(node[1])
        rhs = self.evaluate(node[3])

        if operator == 'LT':
            return lhs[1] < rhs[1]
        if operator == 'LTE':
            return lhs[1] <= rhs[1]
        if operator == 'GT':
            return lhs[1] > rhs[1]
        if operator == 'GTE':
            return lhs[1] >= rhs[1]
        if operator == 'EQ':
            return lhs[1] == rhs[1]

        raise ArithmeticError("Unknown comparison operator " + operator)

    def accept_number(self, *node):
        return node[1]

    def accept_name(self, *node):
        defined, value, level = self.find(node[1])

        return value

    def accept_call(self, *node):
        defined, value, level = self.find(node[1])

        if defined != 'PROCEDURE':
            raise NameError("Expecting procedure but got: " + defined)

        block, result = self.evaluate(value.node)
        return result

    def accept_term(self, *node):
        block, total = self.evaluate(node[1])

        for term in node[2:]:
            block, result = self.evaluate(term[1])

            if term[0] == 'TIMES':
                total = total * result
            elif term[0] == 'DIVIDES':
                total = total / result

        return total

    def accept_expression(self, *node):
        block, total = self.evaluate(node[2])

        for term in node[3:]:
            block, result = self.evaluate(term[1])

            if term[0] == 'PLUS':
                total = total + result
            elif term[0] == 'MINUS':
                total = total - result

        if node[1] == 'MINUS':
            total = total * -1;

        return total

    def accept_print(self, *node):
        block, result = self.evaluate(node[1])

        print `result`

if __name__ == '__main__':
    code = sys.stdin.read()
    parser = pl0_parser.Parser()
    parser.input(code)
    program = parser.p_program()

    interpreter = Interpreter()
    result, value = interpreter.evaluate(program)

    result.debug()
