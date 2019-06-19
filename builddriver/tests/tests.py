import os
import sys

import unittest

import builddriver

dir_path = os.path.dirname(os.path.realpath(__file__))

class TestStringMethods(unittest.TestCase):


    def test_return_code_true(self):
        ret = builddriver.execute('whereis python3')
        assert(ret.returncode() == 0)

    def test_return_code_false(self):
        ret = builddriver.execute('this_command_does_not_exists_hopefully')
        assert(ret.returncode() != 0)

class TestMake(unittest.TestCase):

    def test_warning(self):
        path = os.path.join(dir_path, 'make-01')
        ret = builddriver.execute(f'make -C {path}')
        assert(ret.returncode() == 0)
        assert(ret.warnings_no() > 0)
        assert(ret.errors_no() == 0)
        for warning in ret.warnings():
            sys.stderr.write('\n')
            sys.stderr.write(str(warning))
            sys.stderr.write('\n')

    def test_errors(self):
        path = os.path.join(dir_path, 'make-02')
        ret = builddriver.execute(f'make -C {path}')
        assert(ret.returncode() != 0)
        assert(ret.errors_no() > 0)
        for warning in ret.errors():
            sys.stderr.write('\n')
            sys.stderr.write(str(warning))
            sys.stderr.write('\n')




if __name__ == '__main__':
    unittest.main()
