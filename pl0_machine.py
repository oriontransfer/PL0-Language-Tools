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

import sys

OPCODES = {
    'NOP': 0,
    'HALT': 1,

    'LOAD': 6,
    'SAVE': 7,

    'PUSH': 10,
    'POP': 11,
    'DUP': 12,

    'JMP': 16,
    'CALL': 17,
    'RET': 18,

    'JLT': 20,
    'JLTE': 21,
    'JE': 22,
    'JNE': 23,
    'JGTE': 24,
    'JGT': 25,

    # These instructions are more natural for stack-based machines.
    'CMPLT': 30,
    'CMPLTE': 31,
    'CMPE': 32,
    'CMPNE': 33,
    'CMPGTE': 34,
    'CMPGT': 35,

    'MUL': 43,
    'DIV': 44,
    'ADD': 45,
    'SUB': 46,

    'PRINT': 50,
    'DEBUG': 51
}

NAMES = dict((v,k) for k, v in OPCODES.iteritems())

# Set global name for each opcode
module = sys.modules[__name__]
for name, value in OPCODES.iteritems():
    setattr(module, name, value)

class Machine:
    def __init__(self, sequence):
        self.offset = 0
        self.sequence = sequence
        self.stack = []

    def step(self):
        instruction = NAMES[self.sequence[self.offset]]

        method = getattr(self, "instruction_%s" % instruction.lower())
        method()

        # print `self.offset` + ": Executing " + `instruction` + " stack: " + `self.stack`

        return self.offset >= 0 and self.offset < len(self.sequence)

    def run(self):
        result = True
        while result:
            result = self.step()

    def instruction_nop(self):
        self.offset += 1

    def instruction_halt(self):
        self.offset = -1

    # Basic absolute address load/save unit
    def instruction_load(self):
        self.offset += 1
        address = self.sequence[self.offset]
        self.stack.append(self.sequence[address])
        self.offset += 1

    def instruction_save(self):
        self.offset += 1
        address = self.sequence[self.offset]
        self.sequence[address] = self.stack.pop()
        self.offset += 1

    # Basic stack manipulation
    def instruction_push(self):
        self.offset += 1
        self.stack.append(self.sequence[self.offset])
        self.offset += 1

    def instruction_pop(self):
        self.offset += 1
        self.stack.pop()

    def instruction_dup(self):
        self.offset += 1
        self.stack.append(self.stack[-1])

    def instruction_jmp(self):
        self.offset += 1
        address = self.sequence[self.offset]
        self.offset = address

    def instruction_call(self):
        self.offset += 1
        self.stack.append(self.offset + 1)
        address = self.sequence[self.offset]
        self.offset = address

    def instruction_ret(self):
        address = self.stack.pop()
        self.offset = address

    # Jump based on the result of a subtraction
    def instruction_jlt(self):
        self.offset += 1
        address = self.sequence[self.offset]
        value = self.stack.pop()
        self.offset += 1

        if value > 0:
            self.offset = address

    def instruction_jlte(self):
        self.offset += 1
        address = self.sequence[self.offset]
        value = self.stack.pop()
        self.offset += 1

        if value >= 0:
            self.offset = address

    def instruction_je(self):
        self.offset += 1
        address = self.sequence[self.offset]
        value = self.stack.pop()
        self.offset += 1

        if value == 0:
            self.offset = address

    def instruction_jne(self):
        self.offset += 1
        address = self.sequence[self.offset]
        value = self.stack.pop()
        self.offset += 1

        if value != 0:
            self.offset = address

    def instruction_jgte(self):
        self.offset += 1
        address = self.sequence[self.offset]
        value = self.stack.pop()
        self.offset += 1

        if value <= 0:
            self.offset = address

    def instruction_jgt(self):
        self.offset += 1
        address = self.sequence[self.offset]
        value = self.stack.pop()
        self.offset += 1

        if value < 0:
            self.offset = address

    # Basic comparision support
    def instruction_cmplt(self):
        self.offset += 1
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(int(a < b))

    def instruction_cmplte(self):
        self.offset += 1
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(int(a <= b))

    def instruction_cmpe(self):
        self.offset += 1
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(int(a == b))

    def instruction_cmpne(self):
        self.offset += 1
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(int(a != b))

    def instruction_cmpgt(self):
        self.offset += 1
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(int(a > b))

    def instruction_cmpgte(self):
        self.offset += 1
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(int(a >= b))

    # Basic arithmetic
    def instruction_mul(self):
        self.offset += 1
        self.stack.append(self.stack.pop() * self.stack.pop())

    def instruction_div(self):
        self.offset += 1
        self.stack.append(self.stack.pop() / self.stack.pop())

    def instruction_add(self):
        self.offset += 1
        self.stack.append(self.stack.pop() + self.stack.pop())

    def instruction_sub(self):
        self.offset += 1
        self.stack.append(self.stack.pop() - self.stack.pop())

    def instruction_print(self):
        self.offset += 1
        print self.stack[-1]

    def instruction_debug(self):
        self.offset += 1
        self.debug()

    def debug(self):
        print "-- Machine State --"
        print "Sequence: " + `self.sequence`
        print "Stack: " + `self.stack`
        print "Offset: " + `self.offset`

if __name__ == '__main__':
    buffer = sys.stdin.read()
    code = eval(buffer)
    machine = Machine(code)
    machine.run()
    machine.debug()
