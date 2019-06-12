

install2:
	pip install -e . --no-deps

install3:
	pip3 install -e . --no-deps

test2:
	python setup.py test

test3:
	python3 setup.py test

test: test2 test3

setup:
	python3 setup.py sdist
	python3 setup.py bdist_wheel --universal

upload: setup
	twine upload dist/*

bootstrap:
	python3 -m pip install --user --upgrade setuptools wheel twine

clean:
	git clean -fdx
