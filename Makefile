.PHONY: install test upgrade

install:
	pip install -r test-requirements.txt
	pip install -e .

test:
	pytest

upgrade:
	pip-compile --no-annotate --no-header --output-file requirements.txt requirements.in
	pip-sync requirements.txt
	pip install -r test-requirements.txt
	pip install -e .
