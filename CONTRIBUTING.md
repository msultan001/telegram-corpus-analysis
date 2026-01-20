# Contributing

Thanks for contributing! Please follow these steps when opening issues or PRs.

1. Fork the repository and create a feature branch with a descriptive name.
2. Keep changes focused and split large changes into multiple PRs where practical.
3. Write or update tests for new logic and ensure all tests pass locally.
4. Run formatting and linting before committing:

```bash
pip install -r requirements-dev.txt
black .
isort .
flake8 .
pytest -q
```

5. Use clear commit messages (imperative tense) and reference issues when appropriate.
6. Add documentation for any public API changes.

If your change affects the database schema, add a migration SQL file under `scripts/migrations/`.
