.PHONY: test lint format install clean build

# Run all tests
test:
	UV_PROJECT_ENVIRONMENT=.venv uv run pytest tests/ -v

# Run tests with coverage
test-cov:
	uv run pytest tests/ -v --cov=src/fdprof --cov-report=html --cov-report=term

# Run linter
lint:
	uv run ruff check src/ tests/

# Format code
format:
	uv run ruff format src/ tests/

# Fix linting issues
lint-fix:
	uv run ruff check --fix src/ tests/

# Install development dependencies
install:
	uv sync --extra dev --extra test

# Install pre-commit hooks
install-hooks:
	uv run pre-commit install

# Clean build artifacts
clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -f fdprof.jsonl
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build distribution
build:
	uv build

# Run pre-commit on all files
pre-commit:
	uv run pre-commit run --all-files

# Full development setup
dev-setup: install install-hooks
	@echo "Development environment ready!"

# Quick development check
check: lint test
	@echo "All checks passed!"