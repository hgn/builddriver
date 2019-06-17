from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='gccoutputparser',
      version='0.1',
      description='Parses gcc/llvm output',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/hgn/gccoutputparser',
      author='Hagen Paul Pfeifer',
      author_email='hagen@jauu.net',
      license='MIT',
      packages=['gccoutputparser'],
      test_suite='nose.collector',
      tests_require=['nose'],
      classifiers=[
	'Development Status :: 4 - Beta',
	'Intended Audience :: Developers',
	'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.7',
        ],
      zip_safe=False
     )
