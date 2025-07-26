#!/bin/bash
set -euo pipefail

echo "Building package..."
uv build

if [ "$PUBLISH_TO_TESTPYPI" = "true" ]; then
  export UV_PUBLISH_TOKEN="$TEST_PYPI_API_TOKEN"
  echo "Publishing to TestPyPI..."
  uv publish --index "https://test.pypi.org"
else
  export UV_PUBLISH_TOKEN="$PYPI_API_TOKEN"
  echo "Publishing to PyPI..."
  uv publish --index "https://upload.pypi.org/legacy/"
fi
