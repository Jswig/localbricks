#!/bin/sh

set -ex

REPO_ROOT=$(git rev-parse --show-toplevel)

uv sync --group dev
echo "Formatting..."
uv run ruff format "${REPO_ROOT}"
echo "Linting..."
uv run ruff check "${REPO_ROOT}"
echo "Type checking..."
uv run mypy "${REPO_ROOT}"
echo "Running tests..."
uv run pytest "${REPO_ROOT}"