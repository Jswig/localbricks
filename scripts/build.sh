#!/bin/sh

set -ex

uv sync --group dev
echo "Formatting..."
uv run ruff format
echo "Linting..."
uv run ruff check
echo "Type checking..."
uv run mypy .
echo "Running tests..."
uv run pytest .