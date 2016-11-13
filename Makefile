clean:
	rm -fr dist/ *.egg-info/

test:
	python runtests.py

sdist: test clean
	python setup.py sdist

release: test clean
	python setup.py sdist upload

.PHONY: clean test sdist release
