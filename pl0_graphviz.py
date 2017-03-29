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

from pl0_node_visitor import *
import sys
import pl0_parser
import StringIO
import os

GraphHeader = '''
digraph finite_state_machine {
	rankdir=TB;
	size="8,5"
'''

GraphFooter = '''
}
'''

class GraphPrinter(StackingNodeVisitor):
    def __init__(self):
        super(GraphPrinter, self).__init__()
        self.buf = None
        self.next = 0
        self.nodes = {}
        self.procedures = {}

    #override
    def _invoke_method(self, meth, node):
        return meth(node)

    #override
    def push(self, node):
        self.stack.append(node)

        if not self.nodes.has_key(id(node)):
            self.nodes[id(node)] = "%s_%d" % (node[0], self.next,)
            self.next += 1

        return self.nodes[id(node)]

    def parent_id(self):
        parent = self.stack[-2]
        return self.nodes[id(parent)]

    def generate_graph(self, program):
        self.buf = StringIO.StringIO()
        self.buf.write(GraphHeader)
        self.accept_program(program)
        self.buf.write(GraphFooter)

        contents = self.buf.getvalue()

        self.buf.close
        self.buf = None

        return contents

    def accept_program(self, node):
        node_id = self.push(node)
        self.buf.write("\tnode [shape=doublecircle,label=\"%s\",color=green]; %s;\n"
                       % (node[0], node_id,))
        self.visit_children(node)
        self.pop()

    # override
    # !! Also note that the method signature has changed from the parent class. :/
    #    TODO: See docstrings in parent for note on how to bring graphviz in line with others.
    def accept_node(self, node):
        node_id = self.push(node)
        parent_id = self.parent_id()
        self.buf.write("\tnode [shape=circle,label=\"%s\",color=black]; %s -> %s;\n"
                       % (node[0], parent_id, node_id,))
        self.visit_children(node)
        self.pop()

    def accept_define(self, node):
        node_id = self.push(node)
        parent_id = self.parent_id()
        label = "%s = %d" % node[1:]
        self.buf.write("\tnode [shape=circle,label=\"%s\",color=black]; %s -> %s;\n"
                       % (label, parent_id, node_id,))
        self.visit_children(node)
        self.pop()

    def accept_condition(self, node):
        node_id = self.push(node)
        parent_id = self.parent_id()
        self.buf.write("\tnode [shape=diamond,label=\"%s\",color=orange]; %s -> %s;\n"
                       % (node[2], parent_id, node_id,))
        self.visit_children(node)
        self.pop()

    def accept_name(self, node):
        node_id = self.push(node)
        parent_id = self.parent_id()
        self.buf.write("\tnode [shape=square,label=\"%s\",color=blue]; %s -> %s;\n"
                       % (node[1], parent_id, node_id,))
        self.pop()

    def accept_number(self, node):
        node_id = self.push(node)
        parent_id = self.parent_id()
        self.buf.write("\tnode [shape=square,label=\"%d\",color=blue]; %s -> %s;\n"
                       % (node[1], parent_id, node_id,))
        self.pop()

    def accept_procedure(self, node):
        node_id = self.push(node)
        self.procedures[node[1]] = node_id
        parent_id = self.parent_id()
        self.buf.write("\tnode [shape=trapezium,label=\"%s\",color=purple]; %s -> %s;\n"
                       % (node[1], parent_id, node_id,))
        self.visit_children(node)
        self.pop()

    def accept_expression(self, node):
        node_id = self.push(node)
        parent_id = self.parent_id()
        self.buf.write("\tnode [shape=circle,label=\"EXPR\",color=blue]; %s -> %s;\n"
                       % (parent_id, node_id,))
        self.visit_children(node)
        self.pop()

    def accept_call(self, node):
        node_id = self.push(node)
        parent_id = self.parent_id()
        proc_id = self.procedures[node[1]]
        label = "CALL |{%s}" % node[1]
        self.buf.write("\tnode [shape=record,label=\"%s\",color=purple]; %s -> %s;\n"
                       % (label, parent_id, node_id,))
        self.pop()

    def accept_term(self, node):
        self.visit_children(node)

if __name__ == '__main__':
    code = sys.stdin.read()
    parser = pl0_parser.Parser()
    parser.input(code)
    program = parser.p_program()

    visitor = GraphPrinter()
    contents = visitor.generate_graph(program)

    with open('graph.dot', 'w') as f:
        f.write(contents)

    print "Generating Graph..."
    os.system("dot -v -Tpdf -ograph.pdf graph.dot")

    print "Opening Graph..."
    os.system("open graph.pdf")
