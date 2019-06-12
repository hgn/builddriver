# gccoutputparser

## Installation

Simple install this module via pip (pip for Python 2 is also supported)

```
pip3 install --user gccoutputparser
```


## Usage

```
import gccoutputparser

e = gccoutputparser.GccOutputParser(working_directory=os.pwd())
e.feed()

stats = e.statistics()

number_warnings = len(e.warnings())

e.warnings(path_filter='path/matching/in')

```

