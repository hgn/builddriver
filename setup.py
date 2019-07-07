from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='builddriver',
      version='0.8.0',
      description='Execute make, cmake, maven and parses gcc/llvm output',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/hgn/builddriver',
      author='Hagen Paul Pfeifer',
      author_email='hagen@jauu.net',
      license='MIT',
      packages=['builddriver'],
      test_suite='tests',
      classifiers=[
	'Development Status :: 4 - Beta',
	'Intended Audience :: Developers',
	'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.7',
        ],
      entry_points={
          'console_scripts': [
              'builddriver = builddriver.__main__:main'
          ]
      },
      zip_safe=False
     )
