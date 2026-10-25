.PHONY: dev test lint format audit check

dev:
	python -m pip install -e ".[dev]"
	pre-commit install || true

test:
	python -m pytest

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

audit:
	python -m repodoctor . --fail-under 95

check: lint test audit
