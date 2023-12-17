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

        m = getattr(self, "accept_%s" % node[0].lower(),
                    self.accept_node)
        return self._invoke_method(m, node)

    def _invoke_method(self, meth, node):
        """
        This is ugly. The idea here was to be able to replace
        "node" in the parameter lists with specific named arguments
        so you could say, e.g., 'block' rather than 'node[1]'.

        Unfortunately, for the moment, the graphviz walker relies
        on id(*node), so we have to allow overriding this to pass
        the actual object.

        NOTE: The graphviz issue could be fixed by moving the
        symbol name generator up into the parser, so that it always
        generates a uinque node id. ("BLOCK:0" or ("BLOCK",0) instead
        of just "BLOCK").
        """
        return meth(*node)

    def accept_node(self, *node):
        """
        The double layer of indirection here is again because
        of the different way the graph printer want to use the
        signature.
        """
        return self.visit_children(node)

    def visit_children(self, node):
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
        print("-- Stack Frame --")
        print("Constants: " + repr(self.constants))
        print("Variables: " + repr(self.variables))
        print("Procedures: " + repr(self.procedures))

    def lookup(self, name):
        if name in self.constants:
            return ('CONSTANT', self.constants[name],)
        elif name in self.variables:
            return ('VARIABLE', self.variables[name],)
        elif name in self.procedures:
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

        raise NameError("Undefined name referenced: " + repr(name))
