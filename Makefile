clean:
	rm -fr dist/ build/ *.egg-info/

docs:
	cd docs && make clean && make html

test:
	python -Wd runtests.py

sdist: test clean
	python setup.py sdist

release: test clean
	python setup.py sdist upload

tx:
    python manage.py spiritmakemessages --locale en && \
    python manage.py spirittxpush && \
    python manage.py spirittxpull && \
    python manage.py spiritcompilemessages

.PHONY: clean test sdist release docs
