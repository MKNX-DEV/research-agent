# Common variables
PY_FLAGS := "PYTHONDONTWRITEBYTECODE=1"
SRC      := "src"
TESTS    := "tests"

up:
    docker compose up --build

down:
    docker compose down

logs:
    docker compose logs -f

health:
    curl http://localhost:8000/health

curl query="What is the latest news on batteries? And is there a positive sentiment to these news?":
    curl -X POST http://localhost:8000/research \
        -H "Content-Type: application/json" \
        -d '{"query":"{{query}}"}'

# Clean Python cache files
clean:
    find . -type f -name "*.py[co]" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name ".pytest_cache" -delete
    find . -type f \( -name "*.tgz" -o -name "*.tar.gz" \) -delete

# Run tests with coverage
test app:
    {{PY_FLAGS}} uv run --directory services/{{app}} pytest -v "{{TESTS}}" --cov={{app}} --cov-report=term-missing

# Check formatting
format-check app:
    {{PY_FLAGS}} uv run --directory services/{{app}} ruff format --check --diff {{app}} "{{TESTS}}"

# Apply formatting
format app:
    {{PY_FLAGS}} uv run --directory services/{{app}} ruff format {{app}} "{{TESTS}}"

# Lint
lint app:
    {{PY_FLAGS}} uv run --directory services/{{app}} ruff check {{app}} "{{TESTS}}"

# Lint and auto-fix
lint-fix app:
    {{PY_FLAGS}} uv run --directory services/{{app}} ruff check --fix {{app}} "{{TESTS}}"

# Static type check
type-check app:
    {{PY_FLAGS}} uv run --directory services/{{app}} pyright

run app:
    {{PY_FLAGS}} infisical run -- uv run --directory services/{{app}} python -m {{app}}.main