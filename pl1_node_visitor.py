
class NodeVisitor:
	def visit_node(self, node):
		if node is None:
			return None
		
		try:
			m = getattr(self, "accept_%s" % node[0].lower())
		except AttributeError:
			return self.accept_node(node)
		else:
			return m(node)
	
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
