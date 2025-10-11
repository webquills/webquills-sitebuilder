# Mindvessel Project Template for Django 5.2

Replace this README file with your own project's info.

## How to use it

To use this repository as a project template for Django, use the following command to
create your Django project, replacing URL and PROJECT_NAME:

    django-admin startproject --template URL -x .git PROJECT_NAME

OR simply create a new repository
[using this repository as a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template),
and rename the `project_name` directory to the name of your project.

After creating your project, set up your development environment:

1. Install [uv](https://docs.astral.sh/uv/):
   ```bash
   # On macOS/Linux:
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Or with pip:
   pip install uv
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r pyproject.toml --extra dev
   ```

3. Copy `example.env` to `.env` and configure your environment variables.

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. (Optional) Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Why to use it

Django's built-in project template is very minimalistic. In practice, every time I start
a new Django project, there are dozens of changes and additions I must make to the
repository to make it a "complete" project, even before writing any custom code. This
template adds those changes to save time.

This template is opinionated. It is not intended to cover all use cases or workflows. It
is optimized for solo projects and small teams, and incorporates the best practices I
have discovered in over a decade of Django development. The structure is designed to
ease long term maintenance, providing configurations for common tasks that otherwise might
require complex commands, extra research, etc.

If you find this template doesn't suit your needs, for a more comprehensive Django
template (with notably different opinions) take a look at the
[Django Cookiecutter](https://github.com/cookiecutter/cookiecutter-django).

### Common Dependencies

Django requires Pillow to use ImageField, and docutils to use Admin Docs, but these are
not installed with a default Django setup, and the default template does not include a
dependency management file.

This template includes a `pyproject.toml` for dependency management, with the following
dependencies:

- **Django 5.2.x** – This template is specifically designed for Django 5.2.
- **Pillow** – For ImageField support.
- **docutils** – For Django Admin Docs support (which is enabled by default in this
  template)
- **django-environ** – Environment-specific settings are pulled from the process
  environment. This prevents having to juggle multiple settings files as in other
  templates, and reduces the risk that you will accidentally leak secrets that might be
  stored in one of those settings files. An `example.env` file is included. Copy this to
  `.env` to quickly setup your local dev environment variables.
- **django-extensions** – This has been promoted from an optional dev dependency to a hard
  dependency. It provides many useful management commands, and the base models also have
  good utility. We use its `validate_templates` command to check template syntax, and
  its `shell_plus` is also useful.
- **django-rich** – Provides enhanced output from the test runner, as well as a base for
  management commands that gives you rich terminal output.
- **granian** – A fast ASGI/WSGI server for production deployment. Replaces gunicorn for
  better performance and modern async support.

### Local Development Enhancements

- **Django Debug Toolbar** is included. It will automatically load and configure itself if
  DEBUG is on. URLs and middleware are added automatically.
- **IPython** is included. Django shell will use it automatically to provide an enhanced
  experience.
- **Ruff** is included for fast linting and code formatting. The included VS Code
  configurations will keep your code tidy as you edit, or you can run `ruff check` and
  `ruff format` manually.
- **pre-commit** configurations are included to automatically run checks before committing.
- **Tox** configurations are included for testing, code checks, and code coverage.
- **Runserver's** console log output is enhanced using `rich.logging.RichHandler`.

### Continuous Integration and Testing

This template includes configurations for continuous integration and release automation
using Github Actions. It implements a testing matrix using
[tox](https://tox.wiki/en/latest/) allowing you to test against multiple versions of
Python (3.10, 3.11, 3.12, 3.13). Out of the box, the test automation checks for common
errors, missing database migrations, and invalid template syntax.

The testing matrix also includes informational tests against pre-release versions of
Django (6.0) and Python (3.14), but these tests are allowed to fail without breaking
the build.

Support for enhanced test output has been added via
[django-rich](https://pypi.org/project/django-rich/).

### Editors

This template includes some extra configuration for users of Visual Studio Code, because
it's a lightweight and free code editor, and it's what I use. If you prefer PyCharm, you
can just ignore or delete the .vscode directory. Both are excellent tools for developing
Django apps. This is purely a matter of personal preference.

I will accept pull requests that add support for other editors, within reason.

### SQLite Optimization

If you use SQLite as your database backend, this template configures optimal settings
for better performance and reliability:

- WAL (Write-Ahead Logging) mode for better concurrency
- IMMEDIATE transaction mode to prevent deadlocks
- Optimized cache and memory-mapped I/O settings

These settings are automatically applied when using the default SQLite configuration.

### Copyright License

Source code in this template is derived from Django's project template. Django does not
include license information in generated projects, but Django itself is licensed under a
[BSD 3-Clause License](https://github.com/django/django/blob/main/LICENSE).

Source code modifications provided as part of this template are licensed under the same
terms as would be applied to the standard output of Django's `startproject` command.

### Final Word

I hope you find this template useful!

You may wish to retain the Dependency Management section below as part of your project's
documentation.

## Dependency Management

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable dependency
management. Dependencies are defined in `pyproject.toml`.

### Adding Dependencies

To add a new dependency:

1. Add it to the `dependencies` list in `pyproject.toml` (for production dependencies)
   or `[project.optional-dependencies.dev]` (for development dependencies).

2. Install the updated dependencies:
   ```bash
   uv pip install -r pyproject.toml --extra dev
   ```

### Updating Dependencies

To update all dependencies to their latest compatible versions:

```bash
uv pip install --upgrade -r pyproject.toml --extra dev
```

To update a specific package:

```bash
uv pip install --upgrade django
```

### Production Deployment

For production, install only the core dependencies:

```bash
uv pip install -r pyproject.toml
```
