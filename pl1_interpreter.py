#!/usr/bin/env python

from pl1_node_visitor import *
import pl1_parser
import sys
import StringIO
import os

class Procedure:
	def __init__(self, name, node, block):
		self.name = name
		self.node = node
		self.block = block

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

class Interpreter(NodeVisitor):
	def __init__(self):
		self.stack = []
	
	def find(self, name):
		for x in range(1, len(self.stack) + 1):
			defined, value = self.stack[-x].lookup(name)
			
			if defined:
				return (defined, value, -x,)
		
		raise NameError("Undefined name referenced: " + `name`)
	
	def evaluate(self, node):
		self.push()
		result = self.visit_node(node)
		return [self.pop(), result]
	
	def push(self):
		self.stack.append(Block())
	
	def pop(self):
		return self.stack.pop()
	
	def accept_variables(self, node):
		for var in node[1:]:
			self.stack[-1].update(var[1], 0)
	
	def accept_procedures(self, node):
		for proc in node[1:]:
			self.stack[-1].procedures[proc[1]] = Procedure(proc[1], proc[2], self.stack[-1])
	
	def accept_set(self, node):
		name = node[1][1]
		block, result = self.evaluate(node[2])
		
		defined, value, level = self.find(name)
		self.stack[level].update(name, result)
	
	def accept_while(self, node):
		condition = node[1]
		loop = node[2]
		
		while True:
			block, result = self.evaluate(condition)
			
			if not result:
				break
			
			self.evaluate(loop)
	
	def accept_if(self, node):
		condition = node[1]
		body = node[2]
		
		block, result = self.evaluate(condition)
		
		if result:
			self.evaluate(body)
	
	def accept_condition(self, node):
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
	
	def accept_number(self, node):
		return node[1]
	
	def accept_name(self, node):
		defined, value, level = self.find(node[1])
		
		return value
	
	def accept_call(self, node):
		defined, value, level = self.find(node[1])
		
		if defined != 'PROCEDURE':
			raise NameError("Expecting procedure but got: " + defined)
		
		block, result = self.evaluate(value.node)
		return result
	
	def accept_term(self, node):
		block, total = self.evaluate(node[1])
		
		for term in node[2:]:
			block, result = self.evaluate(term[1])
			
			if term[0] == 'TIMES':
				total = total * result
			elif term[0] == 'DIVIDES':
				total = total / result
			
		return total
	
	def accept_expression(self, node):
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
	
	def accept_print(self, node):
		block, result = self.evaluate(node[1])
		
		print `result`

if __name__ == '__main__':
	code = sys.stdin.read()
	parser = pl1_parser.Parser()
	parser.input(code)
	program = parser.p_program()
	
	interpreter = Interpreter()
	result, value = interpreter.evaluate(program)
	
	result.debug()