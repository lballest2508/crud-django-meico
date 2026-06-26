PYTHON = ../venv-crud-django-meico/Scripts/python.exe

.PHONY: format lint lint-black lint-isort lint-flake8 \
        lint-mypy lint-bandit lint-pylint test

format:
	$(PYTHON) -m black apps/ config/ \
	    --config .code_quality/pyproject.toml
	$(PYTHON) -m isort apps/ config/ \
	    --settings-file .code_quality/pyproject.toml

lint-black:
	$(PYTHON) -m black apps/ config/ \
	    --config .code_quality/pyproject.toml --check

lint-isort:
	$(PYTHON) -m isort apps/ config/ \
	    --settings-file .code_quality/pyproject.toml --check-only

lint-flake8:
	$(PYTHON) -m flake8 apps/ config/ \
	    --config .code_quality/.flake8

lint-mypy:
	$(PYTHON) -m mypy apps/ \
	    --config-file .code_quality/mypy.ini

lint-bandit:
	$(PYTHON) -m bandit apps/ config/ \
	    -c .code_quality/bandit.yaml -r

lint-pylint:
	$(PYTHON) -m pylint apps/ \
	    --rcfile=.code_quality/.pylintrc

lint: lint-black lint-isort lint-flake8 lint-mypy lint-bandit

test:
	$(PYTHON) manage.py test apps.catalog
