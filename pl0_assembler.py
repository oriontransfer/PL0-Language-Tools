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
