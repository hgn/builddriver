#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import types
import subprocess
import tempfile

from dataclasses import dataclass
from typing import Iterator
from typing import List
from typing import Optional

LOG_PREFIX = 'build-'
LOG_SUFFIX = '.log'

class BuildDriverError(Exception): pass
class ArgumentBuildDriverError(BuildDriverError): pass


@dataclass
class WarningErrorEntry:
    '''
    Holds information about ONE gcc warning/error in
    an unified fashion - no matter if gcc/clang or version
    '''
    path: str
    lineno: int
    severity: str
    message: str
    column: int = None



class ExecutionHandle:

    def __init__(self, returncode, tf, taillog_size, record_unmatched):
        self._returncode = returncode
        self._tf = tf
        self._taillog_size = taillog_size
        self._taillog = list()
        self._parsed = False
        kwargs = { "record_unmatched": record_unmatched }
        self._gccoutputparser = GccOutputParser()

    def returncode(self):
        return self._returncode

    def tmp_name(self):
        return self._tf.name

    def _record_taillog(self, line):
        if self._taillog_size <= 0:
            return
        self._taillog.append(line)
        # ok, now truncate the array if exede
        # the user limit (taillog_size), but
        # we will not truncate all the time, just
        # when doubled limited is reached
        if len(self._taillog) > 2 * self._taillog_size:
            truncation = len(self._taillog) - self._taillog_size
            self._taillog = self._taillog[truncation:]

    def _parse(self):
        # on demand parsing function, can be
        # called several times, but only the first
        # time the actual parsing take place
        if self._parsed:
            return
        with open(self._tf.name) as fd:
            for line in fd:
                self._record_taillog(line)
                self._gccoutputparser.record(line)
        self._parsed = True

    def errors(self) -> Iterator[WarningErrorEntry]:
        self._parse()
        return self._gccoutputparser.errors()

    def errors_no(self) -> int:
        self._parse()
        return self._gccoutputparser.errors_no()

    def warnings(self) -> Iterator[WarningErrorEntry]:
        self._parse()
        return self._gccoutputparser.warnings()

    def warnings_no(self) -> int:
        self._parse()
        return self._gccoutputparser.warnings_no()

    def matched_unknowns_no(self) -> int:
        self._parse()
        return self._gccoutputparser.matched_unknowns_no()

    def unmatched_no(self) -> int:
        self._parse()
        return self._gccoutputparser.unmatched_no()

    def unmatched(self) -> int:
        """Returns lines where gcc/llvm warning/error matcher failed

        This normally includes makefile output and other program
        output.

        Note:
            It is required to enable tracing. Tracing holds all
            line in memory. Thus for larger projects it will
            hurt performance.

        Returns:
            This method return None if tracing was not enabled,
            an empty list if every line could be parsed or the
            unparseable lines.
        """
        self._parse()
        return self._gccoutputparser.unmatched()

    def taillog(self, limit: Optional[int] = None):
        self._parse()
        if limit and int(limit) > self._taillog_size:
            msg = 'taillog() limit must be larger as execute taillog_size'
            raise ArgumentBuildDriverError(msg)
        if limit and limit < self._taillog_size:
            truncate_goal = int(limit)
        else:
            truncate_goal = self._taillog_size
        if len(self._taillog) <= truncate_goal:
            return self._taillog
        # bigger, then self._taillog_size, truncate to
        # self._taillog_size
        truncation = len(self._taillog) - truncate_goal
        return self._taillog[truncation:]



def _transport_execution_handle(completed_process, tf, tail_log_size,
                                record_unmatched):
    r = ExecutionHandle(
            completed_process.returncode,
            tf,
            tail_log_size,
            record_unmatched)
    return r

def _redirect_prepare_fds():
    tf = tempfile.NamedTemporaryFile(mode='wt', delete=False,
                                     suffix=LOG_SUFFIX, prefix=LOG_PREFIX)
    return tf


def _cleanup_old_logs():
    # this is an hack to get the system tmp dir, identically
    # how we create it. Delete is false here because of
    # chicken/egg problems
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=LOG_SUFFIX,
                                     prefix=LOG_PREFIX)
    path = os.path.dirname(tf.name)
    pattern = f'{LOG_PREFIX}*{LOG_SUFFIX}'
    for file_ in glob.glob(os.path.join(path, pattern)):
        try:
            os.remove(file_)
        except Exception as err:
            # just ignore for now, leave the file
            pass


def execute(command: str, shell: bool = True, redirect_into_tmp: bool = True,
            taillog_size: int = 256, record_unmatched: bool = False):
    """
    taillog_size: the last n lines captured and keep in memory, can be queried with tail()
    """
    _cleanup_old_logs()
    if not shell:
        # raw syscall, required command array
        command = command.split()
    stderr_fd = sys.stderr
    stdout_fd = sys.stdout
    if redirect_into_tmp:
        tf = _redirect_prepare_fds()
        stderr_fd = tf.file
        stdout_fd = tf.file
    completed = subprocess.run(command, shell=shell, stderr=stderr_fd, stdout=stdout_fd)
    return _transport_execution_handle(completed, tf, taillog_size, record_unmatched)






RE_GCC_WITH_COLUMN = re.compile('^(.*):(\\d+):(\\d+):.*?(warning|error):(.*)$')
RE_GCC_WITHOUT_COLUMN = re.compile('^(.*):(\\d+):.*?(warning|error):(.*)$')


class GccOutputParser:

    def __init__(self, **kwargs: str) -> None:
        self._parsed_lines = 0
        self._warnings_no = 0
        self._errors_no = 0
        self._matched_unknown_no = 0
        self._db_warnings = list()
        self._db_errors = list()
        # optional tracing
        self._unmatched = types.SimpleNamespace()
        self._unmatched.enabled = kwargs.get('record_unmatched', False)
        self._unmatched.db = list()
        self._unmatched.no = 0

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
        if not self._unmatched.enabled:
            return None
        return self._unmatched.db

    def unmatched_no(self) -> int:
        return self._unmatched.no

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

    def matched_unknowns_no(self) -> int:
        return self._matched_unknown_no

    def warnings(self, path_filter: Optional[str] = None) -> Iterator[WarningErrorEntry]:
        '''
        Just an warning generator

        The ordering is the inserted order, no
        internal reording is done
        '''
        for warning in self._db_warnings:
            if path_filter and path_filter not in warning.path:
                continue
            yield warning

    def errors(self, path_filter: Optional[str] = None) -> Iterator[WarningErrorEntry]:
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
        return 'matched-unknown'

    def _account_severity(self, entry):
        if entry.severity == 'warning':
            self._warnings_no += 1
        elif entry.severity == 'error':
            self._errors_no += 1
        else:
            self._matched_unknown_no += 1

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
        message = regex_match.group(5).strip()
        entry = WarningErrorEntry(file_, lineno, severity, message, column)
        self._process_new_entry(entry)

    def _process_gcc_without_column(self, regex_match):
        file_ = regex_match.group(1).strip()
        lineno = regex_match.group(2)
        severity = self._error_warning_selector(regex_match.group(3))
        message = regex_match.group(4).strip()
        entry = WarningErrorEntry(file_, lineno, severity, message)
        self._process_new_entry(entry)

    def _process_trace_unmachted(self, line):
        self._unmatched.no += 1
        if not self._unmatched.enabled:
            return
        self._unmatched.db.append(line)



if __name__ == "__main__":
    sys.stderr.write("Please import this file and use provided function\n")
