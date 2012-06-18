.PHONY: docs build test

ifndef VTENV_OPTS
VTENV_OPTS = "--no-site-packages"
endif

build:	
	virtualenv $(VTENV_OPTS) .
	bin/python setup.py develop

test: bin/nosetests
	bin/nosetests -s circus

docs: bin/sphinx-build
	SPHINXBUILD=../bin/sphinx-build $(MAKE) -C docs html $^

bin/sphinx-build: bin/python
	bin/pip install sphinx

bin/nosetests: bin/python
	bin/pip install nose
