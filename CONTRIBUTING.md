# Contributing to Bifrost

First of all, thank you for considering contributing to Bifrost! We appreciate your time and effort, and we value any contribution you make.

This document provides guidelines and instructions for contributing to the Bifrost Animation Asset Management System.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct. Please be respectful, inclusive, and considerate in all interactions.

## How Can I Contribute?

### Reporting Bugs

1. Ensure the bug was not already reported by searching our issues
2. If you cannot find an existing issue, open a new one
3. Include:
   - A clear title and description
   - Steps to reproduce the issue
   - Expected behavior vs. actual behavior
   - Your operating system and Python version
   - Any relevant screenshots or logs

### Suggesting Features

1. Check if the feature has already been suggested
2. Submit a feature request issue
3. Include:
   - A clear description of the feature
   - The problem it would solve
   - Possible implementation approaches
   - Any relevant examples from other systems

### Submitting Changes

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Run linters: `black . && isort . && flake8 .`
6. Commit your changes: `git commit -m "Add feature X"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Submit a pull request to the `main` branch

## Development Guidelines

### Environment Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`
5. Initialize the workspace: `python scripts/init_workspace.py`

### Coding Standards

- Follow PEP 8 style guidelines
- Use Black for code formatting (line length: 88)
- Use type hints for all function parameters and return values
- Document all modules, classes, and functions using docstrings
- Keep functions small and focused on a single responsibility
- Write tests for new functionality

### Testing

- Write unit tests for all new features or bug fixes
- Ensure tests pass on all supported platforms
- Aim for at least 80% code coverage

### Documentation

- Update documentation for all user-facing changes
- Document new features, APIs, and workflows
- Include examples where appropriate

## Pull Request Process

1. Update the documentation with details of changes
2. Update the README.md with any necessary information
3. The PR should work on all supported platforms
4. Ensure all CI checks pass
5. A maintainer will review your PR and request changes if needed
6. Once approved, a maintainer will merge your PR

## Release Process

1. Bump version numbers where appropriate
2. Update CHANGELOG.md
3. Create a new release on GitHub with release notes
4. Publish the package to PyPI

## Questions?

If you have any questions or need help, feel free to:

- Open an issue with a "question" label
- Contact the project maintainers directly

Thank you for contributing to Bifrost!
