clean:
	rm -fr dist/ build/ *.egg-info/

docs:
	cd docs && make clean && make html

test:
	PYTHONWARNINGS=default uv run runtests.py

testjs:
	npm run gulp test && \
	jasmine --config=spirit/core/static/spirit/scripts/test/support/jasmine.json

buildjs:
	npm run gulp coffee

buildcss:
	npm run gulp css

sdist: test clean
	uv build --sdist

release: sdist
	twine check dist/* && twine upload dist/*

txpush:
	uv run -- manage.py spiritmakemessages --locale en && \
	uv run manage.py spirittxpush

txpull:
	uv run manage.py spirittxpull && \
	uv run manage.py spiritcompilemessages

tx: txpush txpull

start:
	uv run manage.py runserver

start_tasks_manager:
	uv run manage.py run_huey

.PHONY: clean test sdist release docs txpush txpull tx start start_tasks_manager
