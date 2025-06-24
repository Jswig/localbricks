#!/bin/sh
set -ex

repo_root=$(git rev-parse --show-toplevel)

uv sync --group dev
echo "Formatting..."
uv run ruff format "${repo_root}"
echo "Linting..."
uv run ruff check "${repo_root}"
echo "Type checking..."
uv run mypy "${repo_root}"
echo "Running tests..."
uv run pytest "${repo_root}/tests"
