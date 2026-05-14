# Common variables
PY_FLAGS := "PYTHONDONTWRITEBYTECODE=1"
SRC      := "src"
TESTS    := "tests"

# Prek: Wire hooks into git automatically
prek-init:
    prek install

# Prek: Run hooks on demand
prek:
    prek run

# Prek: Run hooks on demand against all files
prek-all:
    prek run --all-files

# Install / update dependencies for a given app
init:
    uv sync

# Clean Python cache files
clean:
    find . -type f -name "*.py[co]" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name ".pytest_cache" -delete
    find . -type f \( -name "*.tgz" -o -name "*.tar.gz" \) -delete

# Run tests with coverage
test:
    {{PY_FLAGS}} uv run pytest -v "{{TESTS}}" --cov=research_tools --cov-report=term-missing

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

# Lint, type check, format
ci:
    just lint-fix
    just type-check
    just format

# Spin up a minikube cluster
kube-up:
    minikube start --memory=max --cpus=max
    eval $(minikube docker-env)

# Shutdown minikube
kube-down:
    minikube delete --all --purge

# Spin up a minikube dashboard
kube-dashboard:
    minikube dashboard >/dev/null 2>&1 &

main:
    uv run python -m research_tools.main