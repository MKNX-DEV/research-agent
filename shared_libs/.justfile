# Common variables
PY_FLAGS := "PYTHONDONTWRITEBYTECODE=1"
SRC      := "shared_libs"
TESTS    := "tests"

# Clean Python cache files
clean:
    find . -type f -name "*.py[co]" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name ".pytest_cache" -delete
    find . -type f \( -name "*.tgz" -o -name "*.tar.gz" \) -delete

# Run tests with coverage
test:
    {{PY_FLAGS}} uv run pytest -v "{{TESTS}}" --cov="{{SRC}}" --cov-report=term-missing

# Check formatting
format-check:
    {{PY_FLAGS}} uv run ruff format --check --diff "{{SRC}}" "{{TESTS}}"

# Apply formatting
format:
    {{PY_FLAGS}} uv run ruff format "{{SRC}}" "{{TESTS}}"

# Lint
lint:
    {{PY_FLAGS}} uv run ruff check "{{SRC}}" "{{TESTS}}"

# Lint and auto-fix
lint-fix:
    {{PY_FLAGS}} uv run ruff check --fix "{{SRC}}" "{{TESTS}}"

# Static type check
type-check:
    {{PY_FLAGS}} uv run pyright