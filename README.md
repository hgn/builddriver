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

### As Python Module

```
import builddriver

result = builddriver.execute('make -C path/to/makfile')
result.returncode()
result.errors_no()
result.warnings_no()
result.taillog()
result.build_duration()
result.build_duration_human()
result.log()
result.tmp_name()
result.tmp_file_rm()
list(result.errors())
list(result.warnings())
```

### As Python Executable

Compiling the Linux Kernel (not a "good" example, because there is usually no
warning in the build, except you increase the warning level somehow):

```sh
$ python3 -m builddriver make -j16 V=2 O=../linux-build
builddriver executing: 'make -j16 V=2 O=../linux-build'
Compilation SUCCEED in 297.833702 seconds
Number of warnings: 0
```

