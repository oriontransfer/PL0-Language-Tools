PL/0 Language Tools
===================

* Author: Samuel G. D. Williams (<http://www.oriontransfer.co.nz>)
* Copyright (C) 2012 Samuel G. D. Williams.
* Released under the MIT license.

The PL/0 Language Tools serve as an example of how to construct a compiler. The language 'PL/0' was originally introduced in the book "Algorithms + Data Structures = Programs", by Niklaus Wirth in 1975.

This project includes a full stack of tools designed for educational purposes to learn about compilers, interpreters and virtual machines. Each component can be executed independently and is typically between 100-300 lines of code.

It is designed to be clear and concise at the expense of performance. It is easy to extend and modify, e.g. adding new syntax constructs or machine instructions.

For more details including documentation please visit <http://www.oriontransfer.co.nz/learn/pl0-language-tools>.

Installation
------------

Install ply:

	sudo easy_install ply

Then, simply download the files `pl0_*.py` and run them.

Basic Usage
-----------

Here is a full example using the interpreter:

	$ ./pl0_interpreter.py < examples/fibonacci.pl1
	1
	1
	2
	3
	5
	8
	13
	21
	34
	55
	89
	144
	233
	377
	610
	987
	1597
	2584
	4181
	6765
	10946
	-- Stack Frame --
	Constants: {'K': 20}
	Variables: {'count': 21, 'k': 17711, 'm': 17711, 'n': 28657}
	Procedures: {}

If you want to see a abstract syntax tree of your program, use the pl0_graphviz.py command:

	./pl0_graphviz.py < examples/fibonacci.pl1

A sample graph is included in the `examples` directory.

For more advanced usage, including documentation on individual components, please see the [online documentation][2].

[2]: http://www.oriontransfer.co.nz/learn/pl0-language-tools

License
-------

Copyright (c) 2012 Samuel G. D. Williams. <http://www.oriontransfer.co.nz>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
