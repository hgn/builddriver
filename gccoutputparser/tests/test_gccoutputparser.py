import os
import sys

from unittest import TestCase

import gccoutputparser


class TestGccOutputParser(TestCase):

    def test_is_initiable(self):
        e = gccoutputparser.GccOutputParser()
        del e

    def test_single_line(self):
        msg = 'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]'
        msg = ' /usr/include/c++/4.9.2/bits/stl_algo.h:2267:error: elements in iterator range [__first, __last) are not partitioned by the value __val. '
        e = gccoutputparser.GccOutputParser()
        e.feed(msg)

    def test_single_line_2(self):
        msg = ' /usr/include/c++/4.9.2/bits/stl_algo.h:2267:error: elements in iterator range [__first, __last) are not partitioned by the value __val. '
        e = gccoutputparser.GccOutputParser()
        e.feed(msg)
