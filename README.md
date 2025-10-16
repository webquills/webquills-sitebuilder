# WebQuills Site Builder

This tool provides a web-based front-end to a static site generator (currently on Hugo).
It gives you a way to create, configure, and edit static site sources in an easy
interface, without having to write raw code or YAML.

## Quick Start with Docker (Recommended)

The easiest way to get started is with Docker Compose, which provides a complete development stack including PostgreSQL, Redis, Gitea, Django, and a background worker.

1. Clone the repository and copy the example environment file:
   ```bash
   cp example.env .env
   ```

2. Start all services:
   ```bash
   docker compose up --build
   ```

3. Access the services:
   - **Django app**: http://localhost:8000/
   - **Gitea**: http://localhost:3000/
   - **Gitea SSH**: `ssh://git@localhost:2222`
   - **PostgreSQL**: `localhost:5432` (databases: `webquills` and `gitea`)
   - **Redis**: `localhost:6379`

4. Run Django management commands:
   ```bash
   ./run manage <command> [args...]
   # Examples:
   ./run manage createsuperuser
   ./run manage shell
   ```

5. Stop all services:
   ```bash
   docker compose down
   ```

The Docker setup includes:
- PostgreSQL with two databases (`webquills` for Django, `gitea` for Gitea)
- Redis for Django cache and job queue
- Gitea for Git repository hosting
- Django web application with hot-reload
- Background worker (django-rq) for async tasks

## Development (Without Docker)

If you prefer to run services locally without Docker:

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
