

install:
	pip3 install --user -e . --no-deps

test:
	python3 -m unittest -v --failfast builddriver/tests/tests.py

lint:
	pylint --disable=too-many-instance-attributes builddriver/builddriver.py

setup: bootstrap
	python3 setup.py sdist
	python3 setup.py bdist_wheel --universal

upload: setup lint test
	twine upload dist/*

bootstrap:
	python3 -m pip install --user --upgrade setuptools wheel twine pylint

really-clean:
	git clean -fdx
