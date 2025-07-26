# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Build, Format, Lint, Type Check, and Test
```sh
sh scripts/build.sh
```
This runs the complete development workflow:
- `uv sync --group dev` - Install dev dependencies
- `uv run ruff format` - Code formatting
- `uv run ruff check` - Linting 
- `uv run mypy` - Type checking
- `uv run pytest tests` - Run all tests

### Individual Commands
- Format code: `uv run ruff format`
- Lint code: `uv run ruff check`
- Type check: `uv run mypy`
- Run tests: `uv run pytest tests`
- Run specific test: `uv run pytest tests/test_<module>.py`

### Documentation
Build Sphinx documentation:
```sh
sh scripts/docs.sh
```

## Project Architecture

### Core Purpose
`localbricks` provides a unified API for writing code that works identically on both local machines (via Databricks Connect) and Databricks clusters. The library handles environment detection and automatically chooses the appropriate implementation.

### Dependencies and Environment
- Uses `uv` for dependency management
- Requires Java Runtime Environment 11 or 17 for Spark

### Code Style
- Line length: 88 characters (configured in pyproject.toml)
- Uses Ruff for formatting and linting with pydocstyle enforcement
- Type hints required (enforced by mypy)
- Test files exempt from docstring requirements