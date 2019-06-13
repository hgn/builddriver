import os
import sys

from unittest import TestCase

import gccoutputparser


class TestGccOutputParser(TestCase):

    def test_is_initiable(self):
        e = gccoutputparser.GccOutputParser()

    def test_single_line(self):
        msg = 'queue.c:34:6: error: unused variable ‘foo’ [-Werror=unused-variable]'
        e = gccoutputparser.GccOutputParser()
        e.feed(msg)
