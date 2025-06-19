.PHONY: help install install-dev test test-cov lint format clean build publish docs

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install runtime dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  publish      - Publish to PyPI"
	@echo "  docs         - Build documentation"
	@echo "  run          - Run the Streamlit app"
	@echo "  pre-commit   - Run pre-commit hooks"

# Installation
install:
	uv pip install -r requirements.txt

install-dev:
	uv pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	.venv/bin/python -m pytest tests/ -v

test-cov:
	.venv/bin/python -m pytest tests/ --cov=src/svg_image_generator --cov-report=html --cov-report=term-missing

test-fast:
	.venv/bin/python -m pytest tests/ -v -m "not slow"

test-integration:
	.venv/bin/python -m pytest tests/ -v -m "integration"

test-unit:
	.venv/bin/python -m pytest tests/ -v -m "unit"

# Code Quality
lint:
	ruff check src/ tests/
	flake8 src/ tests/
	mypy src/
	bandit -r src/

format:
	black src/ tests/
	isort src/ tests/
	ruff check --fix src/ tests/

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Build and Publish
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:
	uv build

publish:
	uv publish

# Documentation
docs:
	mkdocs build

docs-serve:
	mkdocs serve

# Development
run:
	streamlit run src/svg_image_generator/app.py

run-dev:
	streamlit run src/svg_image_generator/app.py --server.port 8502

# Environment setup
setup-dev: install-dev
	pre-commit install
	@echo "Development environment setup complete!"

# Quick checks
check: lint test
	@echo "All checks passed!"

# CI/CD helpers
ci-test:
	.venv/bin/python -m pytest tests/ --cov=src/svg_image_generator --cov-report=xml --cov-report=term-missing --junitxml=test-results.xml

ci-lint:
	ruff check src/ tests/
	flake8 src/ tests/
	mypy src/

# Docker helpers
docker-build:
	docker build -t svg-image-generator .

docker-run:
	docker run -p 8501:8501 svg-image-generator

# Snowflake specific
snowflake-test:
	.venv/bin/python -m pytest tests/ -v -m "snowflake"

ai-test:
	.venv/bin/python -m pytest tests/ -v -m "ai"

# Security
security-check:
	bandit -r src/ -f json -o bandit-report.json
	safety check

# Dependencies
update-deps:
	uv pip install --upgrade -r requirements.txt
	uv pip install --upgrade -r requirements-dev.txt

check-deps:
	uv pip list --outdated
