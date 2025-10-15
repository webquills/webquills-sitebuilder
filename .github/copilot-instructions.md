This repository is a small Django-based application for building/editing static site sources.

Project snapshot (what matters):
- Core package: `sitebuilder/` — contains the main settings, views, models, and templates.
- Entrypoint: `manage.py` (auto-detects `settings.py`).
- Config: `pyproject.toml` (dependencies + linting rules) and `example.env` for env vars.
- Tests: `tests/` (unit and integration tests). Uses `tox` for isolated testing. Views should be tested with Django TestCase's built-in client.

Quick dev setup (extracted from README.md):
- Use `uv` to create a venv: `uv venv` then `source .venv/bin/activate`.
- Install dependencies: `uv sync`.
- Copy `example.env` → `.env` and set `SECRET_KEY` and other env vars.
- Run migrations: `uv run manage.py migrate`.

Architecture & conventions (important for code changes):
- Add new dependencies with `uv add <package>` and remove with `uv remove <package>`.
- Manage virtual environments with `uv` commands (see `uv --help`).
- Use `pre-commit` for git hooks: `pre-commit install` to set up locally.
- Use `tox` for testing in isolated envs: `tox -e py310` (or other Python versions).
- Django 5.2 project: `sitebuilder/settings.py` holds most runtime configuration.
- Apps: the main app is `sitebuilder`. This app must remain first in the INSTALLED_APPS list to ensure proper loading of templates and static files.
- Auth: Uses `django-allauth` with a custom adapter at `sitebuilder/adapters.py`.
- Templates: There is no top-level templates directory. Project templates are stored in the `sitebuilder/templates/` folder. Formatting follows djlint/ruff config in `pyproject.toml`.
- URLS: All URLs are defined in `sitebuilder/urls.py`. All patterns should be named. Use `reverse('name')` in code and `{% url 'name' %}` in templates.
- Internationalization: Use Django i18n: Mark user-visible strings in templates and Python code (including model and field `verbose_name`) for translation. Locale files live under `sitebuilder/locale/` (eventually).
- Accessibility: Site must conform to WCAG 2.1 AA. Follow best practices for HTML structure, ARIA roles, and keyboard navigation. Ensure all interactive elements are accessible and provide appropriate alt text for images.

Data & storage patterns:
- Default DB: sqlite when `DATABASE_URL` is not provided. DB files live under `var/db/db.sqlite3` by default (see `DATA_DIR` & `DB_DIR` in `settings.py`).
- Uploaded media and static files are placed under `var/www/media` and `var/www/static` by default. Use these paths in tests/fixtures.
- Production deployments are expected to replace local storage (S3, RDS, etc.) via env vars (`DEFAULT_STORAGE`, `DATABASE_URL`, etc.).

Common developer tasks (explicit commands):
- Run dev server: `uv run manage.py runserver` (ensure `.env` exists).
- Open Django shell: use the provided VSCode task `Django Shell` or `uv run manage.py shell`.
- Run tests: `uv run manage.py test <test.module>` for individual tests or `tox run` for the full suite. Tests live under `tests/`.
- Lint/format: `ruff` + `djlint` rules are configured in `pyproject.toml`; prefer running pre-commit hooks (`pre-commit install`) locally.

Code-style & quality gates:
- Follow `pyproject.toml` for ruff/djlint settings.
- Before opening a PR, ensure the full test suite passes (`tox run`) and pre-commit hooks are run.

If you update this file or the repo structure:
- Keep this doc short. Add one-line notices referencing changed files (e.g., "AUTH: moved to sitebuilder/auth.py — update adapter notes").
- Update README.md if setup or architecture changes.
