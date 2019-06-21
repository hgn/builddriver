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
        #for warning in ret.warnings():
        #    sys.stderr.write('\n')
        #    sys.stderr.write(str(warning))
        #    sys.stderr.write('\n')

    def test_errors(self):
        path = os.path.join(FILE_PATH, 'make-02')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(ret.returncode() != 0)
        self.assertTrue(ret.errors_no() > 0)
        #for warning in ret.errors():
        #    sys.stderr.write('\n')
        #    sys.stderr.write(str(warning))
        #    sys.stderr.write('\n')


class TestTaillog(unittest.TestCase):

    def test_init(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(len(ret.taillog()) > 0)

    def test_all(self):
        # I counted this manually, 
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        self.assertTrue(len(ret.taillog()) == 25)

    def test_limit(self):
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        tail_lines = ret.taillog(limit=2)
        self.assertTrue(len(tail_lines) == 2)

    def test_last_line(self):
        # I know this
        path = os.path.join(FILE_PATH, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        tail_lines = ret.taillog(limit=2)
        self.assertTrue('Leaving directory' in tail_lines[-1])




if __name__ == '__main__':
    unittest.main()
