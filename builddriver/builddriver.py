#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import types
import subprocess
import tempfile
import datetime

from dataclasses import dataclass
from typing import Iterator
from typing import List
from typing import Dict
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

    def __init__(self, returncode, tf, taillog_size, record_unmatched, build_duration):
        self._returncode = returncode
        self._tf = tf
        self._taillog_size = taillog_size
        self._build_duration = build_duration
        self._taillog = list()
        self._parsed = False
        kwargs = {"record_unmatched": record_unmatched}
        self._gccoutputparser = GccOutputParser(**kwargs)

    def returncode(self):
        return self._returncode

    def tmp_name(self):
        return self._tf.name

    def tmp_file_rm(self):
        """Deletes the temporary file, created during build.

        Normally you should call this function to cleanup the
        generated tmp files. You can call this function in an
        exit handler to make sure the function is called in any
        circumstance.

        Note:
            See precleanup for other options to deal with tmp
            files.
        """
        filepath = self._tf.name
        if not os.path.isfile(filepath):
            return
        os.remove(filepath)

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

    def taillog(self, limit: Optional[int] = None) -> List:
        """Return the last n lines of the log
        """
        self._parse()
        if limit and int(limit) > self._taillog_size:
            msg = 'taillog() limit must be larger as execute() taillog_size'
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

    def log(self) -> str:
        """Return the complete log information

        Note:
            The user can split() the lines if required. Often
            it is not required (e.g. to print for user). Thus
            we do not burn the CPU cycles for nothing.

        Returns:
            string object of all output.
        """
        # no self._parse() this is just an shortcut
        # to save processing time here.
        with open(self._tf.name, 'r') as fd:
            return fd.read()

    def build_duration(self):
        """Returns a datetime.timedelta object of the buildprocess

        Note:
            This does not include time to analyse the build output.
            This may also time some time.

        Returns:
            a datetime.timedelta object
        """
        return self._build_duration

    def build_duration_human(self, formatstr: str = '{:0>8}') -> str:
        """Return a human formated duration of the build

        Args:
            formatstr a string how to format the timedelta object,
            default is {:0>8}

        Returns:
            a string looks like:
                '00:00:59' - if it took 59 seconds
                '01:00:00' - if it took exactly one hour
                '1 day, 0:00:01' - if it took one day and one seond
        """
        formatstr.format(str(self._build_duration))


def _transport_execution_handle(completed_process, tf, tail_log_size,
                                record_unmatched, build_duration):
    r = ExecutionHandle(
        completed_process.returncode,
        tf,
        tail_log_size,
        record_unmatched,
        build_duration)
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
        except Exception:
            # just ignore for now, leave the file
            pass


def execute(command: str, shell: bool = True, redirect_into_tmp: bool = True,
            taillog_size: int = 256, record_unmatched: bool = False,
            precleanup: bool = True,
            cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None):
    """Execute an given command, mainly gnu make, cmake or gcc direclty.

    Args:
        precleanup: If true (default) it removes all tmp log files it will
            find on the filesystem (usually within tmp). Set this to False
            if multiple instances of builddriver is executed in parallel.
            If not, you will delete potential files used in the future.
        param2: The second parameter.
        taillog_size: the last n lines captured and keep in memory,
            can be queried with tail()

    Returns:
        True if successful, False otherwise.
    """
    build_time_start = datetime.datetime.now()
    if precleanup:
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
    completed = subprocess.run(command, cwd=cwd, env=env, shell=shell,
                               stderr=stderr_fd, stdout=stdout_fd)
    build_duration = datetime.datetime.now() - build_time_start
    return _transport_execution_handle(completed, tf, taillog_size,
                                       record_unmatched, build_duration)


RE_GCC_WITH_COLUMN = re.compile('^(.*):(\\d+):(\\d+):.*?(warning|error):(.*)$')
RE_GCC_WITHOUT_COLUMN = re.compile('^(.*):(\\d+):.*?(warning|error):(.*)$')

# (.text+0x20): undefined reference to `main'
RE_LD_GENERIC = re.compile('^.*:\s+(?:undefined reference to|could not read symbols).+$')
# /home/me/dev/temp/foo.cpp:7: undefined reference to `clock_gettime'
RE_LD_WITH_FILE_LINE_NO = re.compile('^(.*):(\d+):\s+((?:undefined reference to|could not read symbols).+)$')
# foo.cpp:(.text+0x15): undefined reference to `clock_gettime'
RE_LD_WITH_FILE = re.compile('^(.*):.+:\s+((?:undefined reference to|could not read symbols).+)$')
# (.text+0x20): undefined reference to `main'
RE_LD_WITHOUT_FILE = re.compile('^(.*):\s+((?:undefined reference to|could not read symbols).+)$')


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
            m = RE_LD_GENERIC.match(line)
            if m:
                # some sort of pre-match matched, we
                # will do a deep scan in the function
                self._process_ld_generic(line)
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

    def _process_ld_generic(self, line):
        # function do not group match, because the line can differ
        # thus we do a deep scanning now (ld specific deep scanning).
        m = RE_LD_WITH_FILE_LINE_NO.match(line)
        if m:
            file_ = m.group(1).strip()
            lineno = m.group(2)
            severity = 'error'
            message = m.group(3).strip()
            entry = WarningErrorEntry(file_, lineno, severity, message)
            self._process_new_entry(entry)
            return
        m = RE_LD_WITH_FILE.match(line)
        if m:
            file_ = m.group(1).strip()
            lineno = -1
            severity = 'error'
            message = m.group(2).strip()
            entry = WarningErrorEntry(file_, lineno, severity, message)
            self._process_new_entry(entry)
            return
        m = RE_LD_WITHOUT_FILE.match(line)
        if m:
            file_ = m.group(1)
            lineno = -1
            severity = 'error'
            message = m.group(2).strip()
            entry = WarningErrorEntry(file_, lineno, severity, message)
            self._process_new_entry(entry)
            return
        # trace unmachted, if enabled
        self._process_trace_unmachted(line)

    def _process_trace_unmachted(self, line):
        self._unmatched.no += 1
        if not self._unmatched.enabled:
            return
        self._unmatched.db.append(line)



if __name__ == "__main__":
    sys.stderr.write("Please import this file and use provided function\n")
    sys.exit(1)
