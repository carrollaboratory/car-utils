# List available recipes
default:
    just --list

install:
    uv sync --extra dev

# Run the test suite
test:
    uv run pytest
