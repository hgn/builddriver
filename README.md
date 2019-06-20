# Build Driver


Possible integration into build:

```
Building project-foo, this may take a while
Compiling failed for compilation unit 'lib-bar'
Error: ‘stderr’ undeclared (first use in this function) in function qux.c line 23
The complete build log is available at '/tmp/build-392193.log'
```

A simple GCC/LLVM (clang) output parser. It reads lines from compiler and
makefile runs, parse, split them and provides parsed information in a
harmonized format.

It is possible to configure what you want: access to the pased information?
Counters? Affected files?

## Installation

Simple install this module via pip (pip for Python 2 is also supported)

```
pip3 install --user gccoutputparser
```

## Preface

GCC sends warnings and errors to standard error while normal output goes to
standard output.


## Usage

```
import gccoutputparser

e = gccoutputparser.GccOutputParser(working_directory=os.pwd())
e.feed()

stats = e.statistics()

number_warnings = len(e.warnings())

e.warnings(path_filter='path/matching/in')

```

