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

2. Generate a runner token for Gitea Actions:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))" > runner_token.txt
   ```

3. Start all services:
   ```bash
   docker compose up --build
   ```

4. Access the services:
   - **Django app**: http://localhost:8000/
   - **Gitea**: http://localhost:3000/
   - **Gitea SSH**: `ssh://git@localhost:2222`
   - **PostgreSQL**: `localhost:5432` (databases: `webquills` and `gitea`)
   - **Redis**: `localhost:6379`

5. Set up Gitea (one-time setup):
   ```bash
   ./run setup_gitea
   ```

   This will:
   - Initialize the Gitea database
   - Create an admin user (credentials stored in `var/gitea/`)
   - Generate an access token for Django integration
   - Configure the Django SocialApp for Gitea authentication

6. Run Django management commands:
   ```bash
   ./run manage <command> [args...]
   # Examples:
   ./run manage createsuperuser
   ./run manage shell
   ```

7. Run Gitea CLI commands:
   ```bash
   ./run gitea <command> [args...]
   # Examples:
   ./run gitea admin user list
   ./run gitea admin repo list
   ```

8. Stop all services:
   ```bash
   docker compose down
   ```

The Docker setup includes:
- PostgreSQL with two databases (`webquills` for Django, `gitea` for Gitea)
- Redis for Django cache and job queue
- Gitea for Git repository hosting with Actions support via Act Runner
- Django web application with hot-reload
- Background worker (django-rq) for async tasks
- The image base is `ghcr.io/astral-sh/uv:python3.12-trixie-slim` which includes `uv` tooling and a non-root `appuser`.
- The project is mounted at `/workspace` inside the container (instead of `/app`).
- The compose file declares a `webquills_venv` volume that is mounted into `/workspace/.venv`. This prevents accidental reuse of a host `.venv` (which is platform-specific) and avoids binary mismatches between host and container.

### Gitea Integration

The project includes a full Gitea integration for Git repository management:

- **Gitea Actions**: The setup includes Gitea Act Runner for CI/CD workflows
- **Django Integration**: The `create_socialapp` management command configures django-allauth for Gitea authentication
- **Setup Script**: Use `./run setup_gitea` to automatically configure Gitea with an admin user and API token

Admin credentials and API tokens are stored in the `DATA_DIR/gitea/` directory (default: `var/gitea/`).

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
