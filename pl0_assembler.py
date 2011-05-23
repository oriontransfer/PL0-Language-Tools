#!/usr/bin/env python

import pl0_machine
import sys
import StringIO
import re

label_re = re.compile('\s*(.*?):')
whitespace_re = re.compile('\s+')
comment_re = re.compile('^\s*#.*$')

def is_integer(string):
	try:
		int(string)
	except ValueError:
		return False
	return True

def assemble(input):
	buffer = []
	labels = {}
	for line in input:
		if comment_re.match(line):
			continue
		
		match = label_re.match(line)
		
		line = line.strip()
		
		if line == '':
			continue
		
		if match:
			labels[match.group(1)] = len(buffer)
		else:
			command = re.split(whitespace_re, line.strip())
			
			for argument in command:
				if is_integer(argument):
					buffer.append(int(argument))
				elif pl0_machine.OPCODES.has_key(argument):
					buffer.append(pl0_machine.OPCODES[argument])
				else:
					# A label
					buffer.append(argument)
	
	# This updates any indirect labels
	return list(labels.get(x, x) for x in buffer)

if __name__ == '__main__':
	code = assemble(sys.stdin)
	print `code`
