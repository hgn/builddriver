#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import sys

RE_GCC_WITH_COLUMN = re.compile('^(.*):(\\d+):(\\d+):.*?(warning|error):(.*)$')
RE_GCC_WITHOUT_COLUMN = re.compile('^(.*):(\\d+):.*?(warning|error):(.*)$')



class GccOutputParser(object):

    def __init__(self):
        pass

    def _process_gcc_with_column(self, m):
        print(m.group(), file=sys.stderr)

    def _process_gcc_without_column(self, m):
        print(m.group(), file=sys.stderr)


    def feed(self, lines):
        for line in lines.splitlines():
            m = RE_GCC_WITH_COLUMN.match(line)
            if m:
                return self._process_gcc_with_column(m)
            m = RE_GCC_WITHOUT_COLUMN.match(line)
            if m:
                return self._process_gcc_without_column(m)



if __name__ == "__main__":
    sys.stderr.write("Please import this file and use provided function\n")
