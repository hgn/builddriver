import os
import sys

from unittest import TestCase

import gccoutputparser

ERROR_VALID = 'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]'
WARNING_VALID = 'queue.c:34:6: warning: unused variable ‘foo’ [-Werror=unused-variable]'
WARNING_VALID_PATH_FULL_FOO_ABS = '/home/foo/src/queue.c:34:6: warning: unused variable ‘foo’'
WARNING_VALID_PATH_FULL_FOO_REL = '../foo/src/queue.c:34:6: warning: unused variable ‘foo’'


class TestInit(TestCase):

    def test_is_initiable(self):
        e = gccoutputparser.GccOutputParser()
        del e


class TestSimple(TestCase):

    def test_single_line(self):
        msg = 'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]'
        e = gccoutputparser.GccOutputParser()
        e.feed(msg)

    def test_single_line_parsed_lines(self):
        msg = 'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]'
        e = gccoutputparser.GccOutputParser()
        e.feed(msg)
        assert(e.parsed_lines() == 1)

    def test_multi_line(self):
        msg =  'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]\n'
        msg += 'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]'
        e = gccoutputparser.GccOutputParser()
        e.feed(msg)
        assert(e.parsed_lines() == 2)

    def test_single_line_2(self):
        kwargs = { "trace_unmatched": True }
        e = gccoutputparser.GccOutputParser(**kwargs)
        msg = ' /usr/include/c++/4.9.2/bits/stl_algo.h:2267:error: elements in iterator range [__first, __last) are not partitioned by the value __val. '
        e.feed(msg)


class TestTraceUnmatched(TestCase):

    def test_trace_unmatched(self):
        kwargs = { "trace_unmatched": True }
        e = gccoutputparser.GccOutputParser(**kwargs)
        msg = 'this line is not supported and not valid - thus trace'
        e.feed(msg)
        assert(len(e.unmatched()) == 1)
        assert(e.unmatched()[0] == msg)

    def test_trace_unmatched_empty(self):
        kwargs = { "trace_unmatched": True }
        e = gccoutputparser.GccOutputParser(**kwargs)
        assert(len(e.unmatched()) == 0)

    def test_trace_unmmachted_not_enabled(self):
        e = gccoutputparser.GccOutputParser()
        msg = 'this line is not supported and not valid - thus trace'
        e.feed(msg)
        assert(e.unmatched() == None)

    def test_trace_unmatched_no(self):
        kwargs = { "trace_unmatched": True }
        e = gccoutputparser.GccOutputParser(**kwargs)
        msg = 'this line is not supported and not valid - thus trace'
        e.feed(msg)
        assert(e.unmatched_no() == 1)

    def test_trace_unmatched_no_2(self):
        kwargs = { "trace_unmatched": True }
        e = gccoutputparser.GccOutputParser(**kwargs)
        msg = 'this line is not supported and not valid - thus trace'
        e.feed(msg)
        msg = 'this line is not supported and not valid - thus trace'
        e.feed(msg)
        assert(e.unmatched_no() == 2)

    def test_trace_unmatched_no_disabled(self):
        e = gccoutputparser.GccOutputParser()
        msg = 'this line is not supported and not valid - thus trace'
        e.feed(msg)
        assert(e.unmatched_no() == 1)


class TestNumberAccounting(TestCase):

    def test_zero_warnings(self):
        e = gccoutputparser.GccOutputParser()
        msg = 'this line is not supported and not valid - thus trace'
        e.record(msg)
        assert(e.warnings_no() == 0)
        assert(e.errors_no() == 0)

    def test_error(self):
        e = gccoutputparser.GccOutputParser()
        msg = 'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]'
        e.record(msg)
        assert(e.warnings_no() == 0)
        assert(e.errors_no() == 1)


class TestGenerator(TestCase):

    def test_generator_warning(self):
        e = gccoutputparser.GccOutputParser()
        e.record(WARNING_VALID)
        e.record(WARNING_VALID)
        i = 0
        for warning in e.warnings():
            i += 1
        assert(i == 2)

    def test_generator_error(self):
        e = gccoutputparser.GccOutputParser()
        e.record(ERROR_VALID)
        e.record(ERROR_VALID)
        i = 0
        for erros in e.errors():
            i += 1
        assert(i == 2)
        # no warnings here
        i = 0
        for warning in e.warnings():
            i += 1
        assert(i == 0)

    def test_generator_warning_convert(self):
        e = gccoutputparser.GccOutputParser()
        e.record(WARNING_VALID)
        e.record(WARNING_VALID)
        assert(len(list(e.warnings())) == 2)

    def test_generator_errots_convert(self):
        e = gccoutputparser.GccOutputParser()
        e.record(ERROR_VALID)
        e.record(ERROR_VALID)
        assert(len(list(e.errors())) == 2)


class TestPathFiler(TestCase):

    def test_generator_path_filer_abs(self):
        e = gccoutputparser.GccOutputParser()
        e.record(WARNING_VALID_PATH_FULL_FOO_ABS)
        e.record(WARNING_VALID_PATH_FULL_FOO_REL)
        i = 0
        for warning in e.warnings(path_filter='/home/foo/src'):
            i += 1
        assert(i == 1)

    def test_generator_path_filer_rel(self):
        e = gccoutputparser.GccOutputParser()
        e.record(WARNING_VALID_PATH_FULL_FOO_ABS)
        e.record(WARNING_VALID_PATH_FULL_FOO_REL)
        i = 0
        for warning in e.warnings(path_filter='foo/src'):
            i += 1
        assert(i == 2)

