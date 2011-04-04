#!/usr/bin/env python

from pl1_node_visitor import *
import sys
import pl1_parser
import StringIO
import os

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

class Compiler(NodeVisitor):
	def __init__(self):
		self.stack = []
		self.label_id = 0
	
	def intermediate_label(self, hint = ''):
		self.label_id += 1
		return 't_' + hint + '_' + `self.label_id`
	
	def find(self, name):
		for x in range(0, len(self.stack)):
			defined, value = self.stack[-x].lookup(name)
			
			if defined:
				return (defined, value, -x,)
		
		raise "Undefined name referenced: " + `node`
	
	def generate(self, node):
		self.push()
		result = self.visit_node(node)
		return [self.pop(), result]
	
	def push(self):
		self.stack.append(Block())
	
	def pop(self):
		return self.stack.pop()
	
	def accept_variables(self, node):
		for var in node[1:]:
			print var[1] + ":"
			print "	NOP"
	
	def accept_program(self, node):
		print "JMP main"
		
		block = node[1]
		NodeVisitor.visit_expressions(self, block[1:4])
		
		print "main:"
		NodeVisitor.visit_node(self, block[4])
	
	def accept_while(self, node):
		top_label = self.intermediate_label("while_start")
		bottom_label = self.intermediate_label("while_end")
		
		condition = node[1]
		loop = node[2]
		
		print '#' + `condition`
		print top_label + ":"
		# Result of condition is on top of stack
		NodeVisitor.visit_node(self, condition)
		
		print "\tJE " + bottom_label
		
		NodeVisitor.visit_node(self, loop)
		
		print "\tJMP " + top_label
		print bottom_label + ":"
	
	def accept_condition(self, node):
		operator = node[2]
		lhs = node[1]
		rhs = node[3]

		NodeVisitor.visit_node(self, lhs)
		NodeVisitor.visit_node(self, rhs)

		print "\tCMP" + operator
	
	def accept_set(self, node):
		name = node[1][1]
		print '#' + `node`
		
		NodeVisitor.visit_node(self, node[2])
		
		print "\tSAVE " + node[1][1]

	def accept_term(self, node):
		NodeVisitor.visit_node(self, node[1])

		for term in node[2:]:
			NodeVisitor.visit_node(self, term[1])

			if term[0] == 'TIMES':
				print "\tMUL"
			elif term[0] == 'DIVIDES':
				print "\tDIV"

	def accept_expression(self, node):
		# Result of this expression will be on the top of stack
		NodeVisitor.visit_node(self, node[2])

		for term in node[3:]:
			NodeVisitor.visit_node(self, term[1])

			if term[0] == 'PLUS':
				print "\tADD"
			elif term[0] == 'MINUS':
				print "\tSUB"

		if node[1] == 'MINUS':
			print "\tPUSH -1"
			print "\tMUL"

	def accept_print(self, node):
		NodeVisitor.visit_node(self, node[1])
		print "\tPRINT"
		print "\tPOP"
	
	def accept_number(self, node):
		print "\tPUSH " + `node[1]`

	def accept_name(self, node):
		# defined, value, level = self.find(node[1])
		print "\tLOAD " + node[1]
		
if __name__ == '__main__':
	code = sys.stdin.read()
	parser = pl1_parser.Parser()
	parser.input(code)
	program = parser.p_program()

	compiler = Compiler()
	compiler.generate(program)
