

install:
	pip3 install -e . --no-deps

test:
	python3 setup.py test

setup:
	python3 setup.py sdist
	python3 setup.py bdist_wheel --universal

upload: setup
	twine upload dist/*

bootstrap:
	python3 -m pip install --user --upgrade setuptools wheel twine

clean:
	git clean -fdx
