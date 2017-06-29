.PHONY: install test upgrade

install:
	pip install -r test-requirements.txt
	pip install -e .

test:
	pytest

upgrade:
	pip-compile --no-annotate --no-header --output-file requirements.txt requirements.in
	pip-compile --no-annotate --no-header --output-file test-requirements.txt test-requirements.in
	echo '-r requirements.txt\n' | cat - test-requirements.txt > \
		test-requirements.temp && mv test-requirements.temp test-requirements.txt
	pip-sync requirements.txt test-requirements.txt
	pip install -e .
