#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import sys
from dataclasses import dataclass


RE_GCC_WITH_COLUMN = re.compile('^(.*):(\\d+):(\\d+):.*?(warning|error):(.*)$')
RE_GCC_WITHOUT_COLUMN = re.compile('^(.*):(\\d+):.*?(warning|error):(.*)$')

@dataclass
class Entry:
    '''
    Holds information about ONE gcc warning/error in
    an unified fashion - no matter if gcc/clang or version
    '''
    file: str
    lineno: int
    severity: str
    column: int = None



class GccOutputParser:

    def __init__(self, val2="default value", **kwargs):
        self._parsed_lines = 0
        self._db = list()
        # optional tracing
        self._trace_unmatched = kwargs.get('trace_unmatched', False)
        self._trace_unmatched_db = list()
        self._trace_unmatched_no = 0

    @staticmethod
    def error_warning_selector(string):
        if 'error' in string:
            return 'error'
        if 'warning' in string:
            return 'warning'
        return 'unknown'

    def _process_new_entry(self, entry):
        self._db.append(entry)
        sys.stderr.write('\n')
        sys.stderr.write(str(entry))
        sys.stderr.write('\n')

    def _process_gcc_with_column(self, m):
        file_ = m.group(1)
        lineno = m.group(2)
        column = m.group(3)
        severity = self.error_warning_selector(m.group(4))
        e = Entry(file_, lineno, severity, column)
        self._process_new_entry(e)

    def _process_gcc_without_column(self, m):
        file_ = m.group(1)
        lineno = m.group(2)
        severity = self.error_warning_selector(m.group(3))
        e = Entry(file_, lineno, severity)
        self._process_new_entry(e)

    def _process_trace_unmachted(self, line):
        self._trace_unmatched_no += 1
        if not self._trace_unmatched:
            return
        self._trace_unmatched_db.append(line)

    def unmatched(self):
        if not self._trace_unmatched:
            return None
        return self._trace_unmatched_db

    def unmatched_no(self):
        return self._trace_unmatched_no

    def parsed_lines(self):
        return self._parsed_lines

    def record(self, lines):
        for line in lines.splitlines():
            line = line.rstrip()
            self._parsed_lines += 1
            m = RE_GCC_WITH_COLUMN.match(line)
            if m:
                self._process_gcc_with_column(m)
                continue
            m = RE_GCC_WITHOUT_COLUMN.match(line)
            if m:
                self._process_gcc_without_column(m)
                continue
            # trace unmachted, if enabled
            self._process_trace_unmachted(line)

    # just an alias, call what you want
    feed = record



if __name__ == "__main__":
    sys.stderr.write("Please import this file and use provided function\n")
