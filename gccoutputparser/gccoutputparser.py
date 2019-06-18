#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys
import types

from dataclasses import dataclass
from typing import Iterator
from typing import List
from typing import Optional



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

    def __init__(self, **kwargs: str) -> None:
        self._parsed_lines = 0
        self._warnings_no = 0
        self._errors_no = 0
        self._unknown_no = 0
        self._db_warnings = list()
        self._db_errors = list()
        # optional tracing
        self._trace_unmatched = types.SimpleNamespace()
        self._trace_unmatched.enabled = kwargs.get('trace_unmatched', False)
        self._trace_unmatched.db = list()
        self._trace_unmatched.no = 0

    def unmatched(self) -> List[str]:
        """
        Return a list of all unmatched lines where
        the regex did not found any gcc/clang compatible
        lines. This can be used for debugging purpuse.
        Note that because of memory constraints this is
        disabled by default. To enable it

        kwargs = { "trace_unmatched": True }
        e = gccoutputparser.GccOutputParser(**kwargs)
        """
        if not self._trace_unmatched.enabled:
            return None
        return self._trace_unmatched.db

    def unmatched_no(self) -> int:
        return self._trace_unmatched.no

    def parsed_lines(self) -> int:
        return self._parsed_lines

    def record(self, lines: str):
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

    def warnings_no(self) -> int:
        return self._warnings_no

    def errors_no(self) -> int:
        return self._errors_no

    def warnings(self, path_filter: Optional[str] = None) -> Iterator[Entry]:
        '''
        Just an warning generator

        The ordering is the inserted order, no
        internal reording is done
        '''
        for warning in self._db_warnings:
            if path_filter and path_filter not in warning.path:
                continue
            yield warning

    def errors(self, path_filter: Optional[str] = None) -> Iterator[Entry]:
        '''
        Just an error generator

        The ordering is the inserted order, no
        internal reording is done
        '''
        for error in self._db_errors:
            if path_filter and path_filter not in error.path:
                continue
            yield error

    # just an alias, call what you want
    feed = record

    @staticmethod
    def _error_warning_selector(string):
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

    def _process_gcc_with_column(self, regex_match):
        file_ = regex_match.group(1).strip()
        lineno = regex_match.group(2)
        column = regex_match.group(3)
        severity = self._error_warning_selector(regex_match.group(4))
        message = regex_match.group(5)
        entry = Entry(file_, lineno, severity, column, message)
        self._process_new_entry(entry)

    def _process_gcc_without_column(self, regex_match):
        file_ = regex_match.group(1).strip()
        lineno = regex_match.group(2)
        severity = self._error_warning_selector(regex_match.group(3))
        message = regex_match.group(4)
        entry = Entry(file_, lineno, severity, message)
        self._process_new_entry(entry)

    def _process_trace_unmachted(self, line):
        self._trace_unmatched.no += 1
        if not self._trace_unmatched.enabled:
            return
        self._trace_unmatched.db.append(line)



if __name__ == "__main__":
    sys.stderr.write("Please import this file and use provided function\n")
