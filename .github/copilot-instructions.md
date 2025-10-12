This repository is a small Django-based site for building/editing static site sources.
Keep guidance short, actionable, and code-aware. Focus on the files and workflows below.

Project snapshot (what matters):
- Core package: `sitebuilder/` — contains settings, views, adapters and templates.
- Entrypoint: `manage.py` (auto-detects `settings.py`).
- Config: `pyproject.toml` (dependencies + linting rules) and `example.env` for env vars.

Quick dev setup (extracted from README.md):
- Use `uv` to create a venv: `uv venv` then `source .venv/bin/activate`.
- Install dependencies: `uv sync`.
- Copy `example.env` → `.env` and set `SECRET_KEY` and other env vars.
- Run migrations: `uv run manage.py migrate`.

Architecture & conventions (important for code changes):
- Add new dependencies with `uv add <package>` and remove with `uv remove <package>`.
- Django 5.2 project: `sitebuilder/settings.py` holds most runtime configuration. Read it first when changing behaviour (auth, storage, celery, logging).
- Apps: the main app is `sitebuilder` — it intentionally contains views (`views.py`), adapters (`adapters.py`), URL routing (`urls.py`) and templates under `sitebuilder/templates/`.
- Auth: Uses `django-allauth` with a custom adapter at `sitebuilder/adapters.py`. Signups are disabled (invitation-only) via `AccountAdapter.is_open_for_signup`.
- Templates: app templates override Django defaults; use `APP_DIRS=True` and the `sitebuilder/templates/` folder. Formatting follows djlint/ruff config in `pyproject.toml`.
- Internationalization: Use Django i18n: Mark user-visible strings (including model and field `verbose_name`) for translation. Locale files live under `sitebuilder/locale/` (eventually).
- Accessibility: Site must conform to WCAG 2.1 AA. Follow best practices for HTML structure, ARIA roles, and keyboard navigation. Ensure all interactive elements are accessible and provide appropriate alt text for images.

Data & storage patterns:
- Default DB: sqlite when `DATABASE_URL` is not provided. DB files live under `var/db/db.sqlite3` by default (see `DATA_DIR` & `DB_DIR` in `settings.py`).
- Uploaded media and static files are placed under `var/www/media` and `var/www/static` by default. Use these paths in tests/fixtures.
- Production deployments are expected to replace local storage (S3, RDS, etc.) via env vars (`DEFAULT_STORAGE`, `DATABASE_URL`, etc.).

Common developer tasks (explicit commands):
- Run dev server: `uv run manage.py runserver` (ensure `.env` exists).
- Open Django shell: use the provided VSCode task `Django Shell` or `uv run manage.py shell_plus` if `django-extensions` is installed.
- Run tests: `uv run manage.py tests` or `tox` depending on your flow. Tests live under `tests/` and exercise views and adapters.
- Lint/format: `ruff` + `djlint` rules are configured in `pyproject.toml`; prefer running pre-commit hooks (`pre-commit install`) locally.

Patterns & examples to follow (copy when making changes):
- Add new URL routes in `sitebuilder/urls.py`. Note DEBUG-specific behavior (media serving, debug_toolbar insertion).
- Create class-based views in `sitebuilder/views.py` (TemplateView + LoginRequiredMixin used here).
- For auth flows, use `allauth` and the custom adapter `sitebuilder.adapters.AccountAdapter` to centralize redirects and signup policy.
- Tests use Django TestCase helpers: `self.client`, `reverse('home')`, and `RequestFactory()` for adapters. Look at `tests/test_views.py` and `tests/test_adapters.py` for concrete examples.

Code-style & quality gates:
- Follow `pyproject.toml` for ruff/djlint settings. Line length and template rules are project-specific.
- Tests and a passing linter are expected before opening PRs. CI (if present) will rely on these settings.

Integration points & external services:
- Optional: GitHub OAuth configured via `GITHUB_CLIENT_ID`/`GITHUB_SECRET` — see `settings.py` which conditionally populates `SOCIALACCOUNT_PROVIDERS['github']`.
- Celery: tasks default to eager mode (`CELERY_TASK_ALWAYS_EAGER=True`) unless env vars specify otherwise. Broker defaults to local redis URL.

When you don't know where to change behavior:
- Search `sitebuilder/settings.py` for the relevant subsystem (AUTH, CELERY, STORAGE, LOGGING). That file centralizes runtime defaults and environment-driven overrides.
- If the change affects templates, check `sitebuilder/templates/` first.

If you update this file or the repo structure:
- Keep this doc short. Add one-line notices referencing changed files (e.g., "AUTH: moved to sitebuilder/auth.py — update adapter notes").

Questions or missing info? Ask for the intended runtime (local dev vs production) and whether external services (Redis, S3, GitHub OAuth) are available — tests and CI assume local defaults.
