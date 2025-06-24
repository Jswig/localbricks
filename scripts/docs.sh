#!/bin/sh
set -ex

repo_root=$(git rev-parse --show-toplevel)

uv sync --group docs
echo "Building documentation..."
sphinx-build -b html "${repo_root}/docs" "${repo_root}/docs/_build/html"
