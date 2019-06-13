# gccoutputparser

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

