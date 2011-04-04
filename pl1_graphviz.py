#!/usr/bin/env python

from pl1_node_visitor import *
import sys
import pl1_parser
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

class GraphPrinter(NodeVisitor):
	def __init__(self):
		self.buf = None
		self.next = 0
		self.nodes = {}
		self.stack = []
		self.procedures = {}
	
	def push(self, node):
		self.stack.append(node)
		
		if not self.nodes.has_key(id(node)):
			self.nodes[id(node)] = "%s_%d" % (node[0], self.next,)
			self.next += 1
		
		return self.nodes[id(node)]
	
	def parent_id(self):
		parent = self.stack[-2]
		return self.nodes[id(parent)]
	
	def pop(self):
		self.stack.pop()
	
	def generate_graph(self, program):
		self.buf = StringIO.StringIO()
		self.buf.write(GraphHeader)
		self.visit_node(program)
		self.buf.write(GraphFooter)
		
		contents = self.buf.getvalue()
		
		self.buf.close
		self.buf = None
		
		return contents
	
	def accept_program(self, node):
		node_id = self.push(node)
		self.buf.write("	node [shape=doublecircle,label=\"%s\",color=green]; %s;\n" % (node[0], node_id,))
		NodeVisitor.accept_node(self, node)
		self.pop()
	
	def accept_node(self, node):
		node_id = self.push(node)
		parent_id = self.parent_id()
		self.buf.write("	node [shape=circle,label=\"%s\",color=black]; %s -> %s;\n" % (node[0], parent_id, node_id,))
		NodeVisitor.accept_node(self, node)
		self.pop()
	
	def accept_define(self, node):
		node_id = self.push(node)
		parent_id = self.parent_id()
		label = "%s = %d" % node[1:]
		self.buf.write("	node [shape=circle,label=\"%s\",color=black]; %s -> %s;\n" % (label, parent_id, node_id,))
		NodeVisitor.accept_node(self, node)
		self.pop()
	
	def accept_condition(self, node):
		node_id = self.push(node)
		parent_id = self.parent_id()
		self.buf.write("	node [shape=diamond,label=\"%s\",color=orange]; %s -> %s;\n" % (node[2], parent_id, node_id,))
		NodeVisitor.accept_node(self, node)
		self.pop()
	
	def accept_name(self, node):
		node_id = self.push(node)
		parent_id = self.parent_id()
		self.buf.write("	node [shape=square,label=\"%s\",color=blue]; %s -> %s;\n" % (node[1], parent_id, node_id,))
		self.pop()
	
	def accept_number(self, node):
		node_id = self.push(node)
		parent_id = self.parent_id()
		self.buf.write("	node [shape=square,label=\"%d\",color=blue]; %s -> %s;\n" % (node[1], parent_id, node_id,))
		self.pop()
	
	def accept_procedure(self, node):
		node_id = self.push(node)
		self.procedures[node[1]] = node_id
		parent_id = self.parent_id()
		self.buf.write("	node [shape=trapezium,label=\"%s\",color=purple]; %s -> %s;\n" % (node[1], parent_id, node_id,))
		NodeVisitor.accept_node(self, node)
		self.pop()
	
	def accept_expression(self, node):
		node_id = self.push(node)
		parent_id = self.parent_id()
		self.buf.write("	node [shape=circle,label=\"EXPR\",color=blue]; %s -> %s;\n" % (parent_id, node_id,))
		NodeVisitor.accept_node(self, node)
		self.pop()
	
	def accept_call(self, node):
		node_id = self.push(node)
		parent_id = self.parent_id()
		proc_id = self.procedures[node[1]]
		label = "CALL |{%s}" % node[1]
		self.buf.write("	node [shape=record,label=\"%s\",color=purple]; %s -> %s;\n" % (label, parent_id, node_id,))
		self.pop()
	
	def accept_term(self, node):
		NodeVisitor.accept_node(self, node)

if __name__ == '__main__':
	code = sys.stdin.read()
	parser = pl1_parser.Parser()
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
