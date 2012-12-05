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

class NodeVisitor(object):

    def visit_node(self, node):
        if node is None:
            return None

        try:
            m = getattr(self, "accept_%s" % node[0].lower())
        except AttributeError:
            return self.accept_node(node)
        else:
            return m(*node)

    def accept_node(self, node):
        return self.visit_expressions(node[1:])

    def visit_expressions(self, expressions):
        results = []

        for expr in expressions:
            if type(expr) in [list, tuple]:
                result = self.visit_node(expr)
                results.append(result)

        if len(results) == 1:
            return results[0]
        else:
            return results


class Block:
    def __init__(self):
        self.constants = {}
        self.variables  = {}
        self.procedures = {}

    def define(self, name, value):
        # if self.constants.has_key(name)
        self.constants[name] = value

    def update(self, name, value):
        self.variables[name] = value

    def declare(self, name, value):
        self.procedures[name] = value

    def debug(self):
        print "-- Stack Frame --"
        print "Constants: " + `self.constants`
        print "Variables: " + `self.variables`
        print "Procedures: " + `self.procedures`

    def lookup(self, name):
        if self.constants.has_key(name):
            return ('CONSTANT', self.constants[name],)
        elif self.variables.has_key(name):
            return ('VARIABLE', self.variables[name],)
        elif self.procedures.has_key(name):
            return ('PROCEDURE', self.procedures[name],)
        else:
            return (False, None,)

class StackingNodeVisitor(NodeVisitor):

    def __init__(self):
        self.stack = []

    def push(self):
        self.stack.append(Block())

    def pop(self):
        return self.stack.pop()

    def find(self, name):
        for x in range(1, len(self.stack) + 1):
            defined, value = self.stack[-x].lookup(name)

            if defined:
                return (defined, value, -x,)

        raise NameError("Undefined name referenced: " + `name`)
