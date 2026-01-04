# WebQuills Site Builder
GOAL: Create an easily usable, accessible web interface for publishing web sites using Hugo static site generator.

Like Decap CMS, WebQuills Site Builder is a content management system that provides a friendly UI and intuitive workflows for editors, while storing all content in a Git repository at GitHub, GitLab, Gitea, or other similar services using their API.

Unlike Decap CMS, WebQuills Site Builder is a server-side Django application, capable of storing state, including API tokens, repository URLs, and user preferences. It uses minimal JavaScript and no JavaScript frameworks (other than perhaps HTMX if that is needed), opting for a simpler HTML form-based interface that is accessible via keyboard and screen reader. It relies on the Git provider's CI services to perform testing, site build, and deployment.

We will use `django-allauth` to integrate authentication and authorization for backend Git services. We will use the respective API of each service to manipulate the files and repositories, create branches, create and merge pull requests, and trigger workflows. For GitHub interactions, we will use the [PyGitHub](https://pypi.org/project/PyGithub/) library ([docs](https://pygithub.readthedocs.io/en/stable/)).

We eschew both the "fat model" approach (where all logic is in the models) and the "fat view" approach (where all logic is in the views). Instead, we will use a service layer to encapsulate business logic, keeping models and views thin and focused on their respective responsibilities. The sitebuilder directory is both the container for project settings and the home for service layer code. It is itself a Django app and contains the "core" functionality of the project.

## Features and Flows
1. Register a new account via GitHub auth (using a GitHub App and django-allauth).
2. Import site from GitHub repo
	1. Request/Grant write access to a specific repository
	2. Pull site metadata from Hugo config, then display pre-populated form.
	3. Save necessary data to Django models so that sites can be listed and accessed in future. (Design a StaticSite model to hold the data.)
	4. Index metadata for all pages in the site for future use (search, listing, etc).
3. Create new site in GitHub repo
	1. Site creation form
	2. Create new GitHub repo
	3. Populate GitHub repo with Hugo site template
4. List site content
	1. Display tree of content directory showing all pages, page bundles, and Drafts. Pages and bundles have buttons for Edit and Unpublish. Drafts have buttons for Edit, Publish, and Discard.
	2. Allow select for edit.
5. Create a new Draft
   1. User selects "New Draft" button.
   2. Display form to select archetype (if multiple archetypes exist) and enter file name (with validation to ensure no conflicts with existing files).
   3. On form submission, ensure a `_DRAFT` directory exists in the content directory. If not, create it.
   4. Create new markdown file in the `_DRAFT` directory using the selected archetype and file name. Ensure the front matter contains `draft: true`.
   5. Display content edit forms for the new Draft (see Edit Content flow).
6. Edit content (Draft)
	1. User selects "Edit" button next to a Draft in content tree.
	2. Load the selected content file from the repo into a pair of forms. Front matter loads into a metadata panel, while content loads into a content editor panel.
	3. On save, reconstruct the markdown file with front matter from the forms and write the content file to the repo (in `_DRAFT`).
7. Edit content (published)
	1. User selects "Edit" button next to a published page or bundle in content tree.
	2. Copy the page or bundle to the `_DRAFT` directory as a Draft. Ensure the front matter of the new Draft contains `draft: true`.
   3. Load the Draft content file from the repo into a pair of forms. Front matter loads into a metadata panel, while content loads into a content editor panel.
   4. On save, reconstruct the markdown file with front matter from the forms and write the content file to the repo (in `_DRAFT`).
   5. When user publishes the Draft, the Draft file will be moved from `_DRAFT` to the appropriate location in the content directory.
   6. The published version of the page or bundle remains unchanged until the Draft is published.
   7. If the user discards the Draft, the Draft file is moved from `_DRAFT` into a "waste basket" directory and the published version remains unchanged.
   8. A published page or bundle can have only one associated Draft at a time. A user must either publish or discard an existing Draft before creating a new Draft for that page or bundle.
8. Publish content
	1. On list of Drafts, user presses Publish button next to Draft.
	2. Move the page or bundle from the `_DRAFT` directory to the appropriate location in the content directory.
   3. Remove `draft: true` from the front matter.
9.  Discard a Draft
	1. On list of Drafts, user selects the Discard button.
	2. Confirm that the user wants to place this Draft in the waste basket.
	3. Move the Draft file from `_DRAFT` into a "waste basket" directory.
	4. After 90 days of inactivity, pages in the waste basket may be removed from the repository.

## Quick Start Development Environment with Docker (Recommended)

The easiest way to get started is with Docker Compose, which provides a complete development stack.

## Production configuration with Docker
Production deployment including PostgreSQL, Redis, Gitea, Django, and a background worker.

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
- The image base is `ghcr.io/astral-sh/uv:python3.12-trixie-slim` which includes `uv` tooling and a non-root `appuser`.
- The project is mounted at `/workspace` inside the container (instead of `/app`).
- The compose file declares a `webquills_venv` volume that is mounted into `/workspace/.venv`. This prevents accidental reuse of a host `.venv` (which is platform-specific) and avoids binary mismatches between host and container.

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
