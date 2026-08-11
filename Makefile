.PHONY: all
all:
	@echo "Run my targets individually!"

.PHONY: lint
lint:
	uv run --dev ruff format --check
	uv run --dev ruff check
	uv run --dev ty check

.PHONY: reformat
reformat:
	uv run --dev ruff check --fix
	uv run --dev ruff format
	uv run --dev ty check --fix
