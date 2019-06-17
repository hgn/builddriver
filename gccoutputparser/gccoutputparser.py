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
    path: str
    lineno: int
    severity: str
    message: str
    column: int = None



class GccOutputParser:

    def __init__(self, **kwargs):
        self._parsed_lines = 0
        self._warnings_no = 0
        self._errors_no = 0
        self._unknown_no = 0
        self._db_warnings = list()
        self._db_errors = list()
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

    def _account_severity(self, entry):
        if entry.severity == 'warning':
            self._warnings_no += 1
        elif entry.severity == 'error':
            self._errors_no += 1
        else:
            self._unknown_no += 1

    def _process_new_entry(self, entry):
        if entry.severity == 'warning':
            self._db_warnings.append(entry)
        if entry.severity == 'error':
            self._db_errors.append(entry)
        self._account_severity(entry)
        #sys.stderr.write('\n')
        #sys.stderr.write(str(entry))
        #sys.stderr.write('\n')

    def _process_gcc_with_column(self, m):
        file_ = m.group(1).strip()
        lineno = m.group(2)
        column = m.group(3)
        severity = self.error_warning_selector(m.group(4))
        message = m.group(5)
        e = Entry(file_, lineno, severity, column, message)
        self._process_new_entry(e)

    def _process_gcc_without_column(self, m):
        file_ = m.group(1).strip()
        lineno = m.group(2)
        severity = self.error_warning_selector(m.group(3))
        message = m.group(4)
        e = Entry(file_, lineno, severity, message)
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

    def warnings_no(self):
        return self._warnings_no

    def errors_no(self):
        return self._errors_no

    def warnings(self, path_filter=None):
        ''' just an warning generator'''
        for warning in self._db_warnings:
            if path_filter and path_filter not in warning.path:
                continue
            yield warning

    def errors(self, path_filter=None):
        ''' just an error generator'''
        for error in self._db_errors:
            if path_filter and path_filter not in warning.path:
                continue
            yield error

    # just an alias, call what you want
    feed = record



if __name__ == "__main__":
    sys.stderr.write("Please import this file and use provided function\n")
