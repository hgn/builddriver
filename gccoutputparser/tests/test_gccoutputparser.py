import os
import sys

from unittest import TestCase

import gccoutputparser


class TestInit(TestCase):

    def test_is_initiable(self):
        e = gccoutputparser.GccOutputParser()
        del e


class TestSimple(TestCase):

    def test_single_line(self):
        msg = 'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]'
        e = gccoutputparser.GccOutputParser()
        e.feed(msg)

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


