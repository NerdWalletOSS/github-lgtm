default: tests lint
tests:
	@. venv/bin/activate; nosetests --with-xunit --exe
coverage:
	@. venv/bin/activate; nosetests --with-coverage --cover-package=lgtm
lint:
	@. venv/bin/activate; frosted -vb --skip venv --recursive .
	@. venv/bin/activate; pep8 --max-line-length=120 --exclude venv .
run:
	@. venv/bin/activate; python -m lgtm.console --integration travis --verbose
help:
	@. venv/bin/activate; python -m lgtm.console --help
version:
	@. venv/bin/activate; python -m lgtm.console --version
dist:
	@python setup.py sdist
upload:
	@python setup.py sdist upload
clean:
	@ find . -name "*.pyc" -exec rm -rf {} \;
	@rm -rf lgtm.egg-info
	@rm -rf dist
	@rm -rf venv
install: venv/bin/activate
venv/bin/activate: requirements.txt
	@test -d venv || virtualenv venv
	@. venv/bin/activate; pip install -r requirements.txt
	@touch venv/bin/activate

.PHONY: default tests run dist install venv/bin/activate
