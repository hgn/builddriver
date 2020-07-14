import os
import sys

import unittest

import builddriver

FILE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestStringMethods(unittest.TestCase):

    def test_return_code_true(self):
        ret = builddriver.execute('whereis python3')
        self.assertTrue(ret.returncode() == 0)

    def test_return_code_false(self):
        ret = builddriver.execute('this_command_does_not_exists_hopefully')
        self.assertTrue(ret.returncode() != 0)


class TestMake(unittest.TestCase):

    def test_warning(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(ret.returncode() == 0)
        self.assertTrue(ret.warnings_no() > 0)
        self.assertTrue(ret.errors_no() == 0)
        self.assertTrue(ret.matched_unknowns_no() == 0)
        self.assertTrue(ret.unmatched_no() > 0)
        # for warning in ret.warnings():
        #    sys.stderr.write('\n')
        #    sys.stderr.write('\n')

    def test_errors(self):
        path = os.path.join(FILE_PATH, 'make-02')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(ret.returncode() != 0)
        self.assertTrue(ret.errors_no() > 0)
        self.assertTrue(ret.matched_unknowns_no() == 0)
        self.assertTrue(ret.unmatched_no() > 0)
        # for warning in ret.errors():
        #    sys.stderr.write('\n')
        #    sys.stderr.write(str(warning))
        #    sys.stderr.write('\n')


class TestTaillog(unittest.TestCase):

    def test_init(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(len(ret.taillog()) > 2)

    def test_all(self):
        # I counted this manually,
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(len(ret.taillog()) > 2)

    def test_limit(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        tail_lines = ret.taillog(limit=2)
        self.assertTrue(len(tail_lines) == 2)

    def test_last_line(self):
        # I know this
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -w -C {path}')
        tail_lines = ret.taillog(limit=2)
        self.assertTrue('Leaving directory' in tail_lines[-1])


class TestCleanup(unittest.TestCase):

    def test_tmp_rm(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        ret.tmp_file_rm()

    def test_disable_precleanup(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}', precleanup=False)
        # this should work as well
        ret.tmp_file_rm()


class TestLogTmp(unittest.TestCase):

    def test_log(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(len(ret.log()) > 0)


class TestBuildDuration(unittest.TestCase):

    def test_duration(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        timedelta = ret.build_duration()
        # simple test, call make should be longer then 0
        # on all platforms
        self.assertTrue(timedelta.microseconds > 1)

    def test_duration_human(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        timedelta = ret.build_duration_human()
        # TODO! self.assertTrue(timedelta != None)


class TestLog(unittest.TestCase):

    def test_log(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(len(ret.log()) > 0)


if __name__ == '__main__':
    unittest.main()
