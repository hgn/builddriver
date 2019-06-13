#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import sys

RE_MAIN = re.compile('^(.*):(\\d+):(\\d+):.*?(warning|error):(.*)$')

class GccOutputParser(object):

    def __init__(self):
        pass

    def feed(self, lines):
        for line in lines.splitlines():
            m = RE_MAIN.match(line)
            if m:
                print(m.group(), file=sys.stderr)



if __name__ == "__main__":
    sys.stderr.write("Please import this file and use provided function\n")
