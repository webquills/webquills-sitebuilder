# Gitea Integration Implementation Summary

This document summarizes the Gitea integration changes made to the webquills-sitebuilder project.

## Changes Implemented

### 1. Docker Compose Updates (compose.yaml)

- **Added Gitea Act Runner service**: 
  - Container: `docker.io/gitea/act_runner:latest`
  - Configured with GITEA_INSTANCE_URL and GITEA_RUNNER_REGISTRATION_TOKEN_FILE
  - Bind-mounted runner_token.txt (read-only)
  - Mounted Docker socket for running workflows
  
- **Updated Gitea service environment variables**:
  - `GITEA__security__INSTALL_LOCK: "true"` - Prevents unauthorized installation
  - `GITEA__service__DISABLE_REGISTRATION: "true"` - Disables public registration
  - `GITEA__database__AUTO_MIGRATION: "true"` - Enables automatic database migrations
  - Added GITEA_RUNNER_REGISTRATION_TOKEN_FILE environment variable
  - Bind-mounted runner_token.txt (read-only)

### 2. Runner Token Generation

- Created `runner_token.txt` with 64 hex characters (32 bytes of entropy)
- Added to `.gitignore` to prevent committing secrets

### 3. Django Management Command

Created `sitebuilder/management/commands/create_socialapp.py`:
- Creates or updates django-allauth SocialApp instances
- Reads secret key from file (not command line) to protect credentials
- Supports multiple providers (github, gitea, etc.)
- Associates SocialApp with Django sites
- Includes comprehensive test coverage in `tests/test_management_commands.py`

### 4. Run Script Functions

Added two new functions to the `run` script:

**gitea function**:
- Executes Gitea CLI commands in the container
- Automatically uses running container or starts new one
- Usage: `./run gitea <command> [args...]`

**setup_gitea function**:
- Complete automated Gitea setup workflow
- Runs database migrations
- Creates admin user with generated password
- Generates admin access token
- Configures Django SocialApp for Gitea authentication
- Stores credentials securely in DATA_DIR/gitea/
- Usage: `./run setup_gitea`

### 5. Environment Variables

Updated `example.env` and `.env`:
- Added `GITEA_ADMIN_USER` - Admin username for Gitea setup
- Added `GITEA_ADMIN_EMAIL` - Admin email for Gitea setup
- Removed deprecated `GITEA_DISABLE_REGISTRATION` (replaced by GITEA__service__DISABLE_REGISTRATION)

### 6. Documentation

Updated `README.md`:
- Added Gitea setup instructions
- Documented runner token generation
- Explained setup_gitea workflow
- Added gitea CLI function documentation
- Noted credential storage locations

Added `docs/gitea-api-definition.yaml`:
- Original OpenAPI specification for reference
- May be used for client generation

## Testing

All changes include appropriate tests:
- Management command tests pass (6 tests)
- Existing Django tests pass (31 total tests)
- Code passes ruff linting checks
- Docker Compose configuration validated

## Security Considerations

1. **Secrets Management**:
   - runner_token.txt is gitignored
   - Admin password stored in DATA_DIR with 600 permissions
   - Admin token stored in DATA_DIR with 600 permissions
   - Secrets read from files, not command-line arguments

2. **Gitea Configuration**:
   - Installation locked to prevent unauthorized changes
   - Public registration disabled
   - Database migrations automated

3. **Access Control**:
   - Admin user required for setup
   - Token-based authentication for API access

## Usage Workflow

1. Start services: `docker compose up --build`
2. Setup Gitea: `./run setup_gitea`
3. Access Gitea at http://localhost:3000/
4. Login with credentials from `var/gitea/admin_password.txt`
5. Use Django integration with automatic authentication

## References

- Gitea Actions Documentation: https://docs.gitea.com/usage/actions/act-runner
- Gitea API Documentation: https://docs.gitea.com/api/overview/
- OpenAPI Generator: https://openapi-generator.tech/
