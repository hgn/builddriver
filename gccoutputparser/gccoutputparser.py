#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import sys

RE_GCC_WITH_COLUMN = re.compile('^(.*):(\\d+):(\\d+):.*?(warning|error):(.*)$')
RE_GCC_WITHOUT_COLUMN = re.compile('^(.*):(\\d+):.*?(warning|error):(.*)$')



class GccOutputParser(object):

    def __init__(self, val2="default value", **kwargs):
        self._trace_unmatched = kwargs.get('trace_unmatched', False)
        self._trace_unmatched_db = list()

    def _process_gcc_with_column(self, m):
        pass

    def _process_gcc_without_column(self, m):
        pass

    def _process_trace_unmachted(self, line):
        if not self._trace_unmatched:
            return
        self._trace_unmatched_db.append(line)

    def unmatched(self):
        if not self._trace_unmatched:
            return None
        return self._trace_unmatched_db


    def feed(self, lines):
        for line in lines.splitlines():
            m = RE_GCC_WITH_COLUMN.match(line)
            if m:
                return self._process_gcc_with_column(m)
            m = RE_GCC_WITHOUT_COLUMN.match(line)
            if m:
                return self._process_gcc_without_column(m)
            # trace unmachted, if enabled
            self._process_trace_unmachted(line)



if __name__ == "__main__":
    sys.stderr.write("Please import this file and use provided function\n")
