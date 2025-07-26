#!/bin/sh
set -ex

echo "Building package..."
uv build

echo "Publishing to PyPI..."
uv publish
