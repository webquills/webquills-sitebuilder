# WebQuills Site Builder Tests

This directory contains tests for the WebQuills Site Builder application, focusing on authentication flows and core functionality.

## Test Structure

- `test_views.py` - Tests for the home page and profile views
- `test_authentication.py` - Tests for login, logout, signup, and MFA functionality
- `test_adapters.py` - Unit tests for custom django-allauth adapters

## Running Tests

### Run all tests
```bash
python manage.py test tests
```

### Run specific test file
```bash
python manage.py test tests.test_views
python manage.py test tests.test_authentication
python manage.py test tests.test_adapters
```

### Run specific test class
```bash
python manage.py test tests.test_authentication.LoginTests
```

### Run specific test method
```bash
python manage.py test tests.test_authentication.LoginTests.test_login_with_valid_credentials
```

### Run with coverage
```bash
coverage run --source='.' manage.py test tests
coverage report
coverage html  # Generate HTML report
```

### Using tox
```bash
# Run tests across all Python versions
tox

# Run tests for specific Python version
tox -e py312-django52

# Run with coverage
tox -e py312-coverage
```

## Test Coverage

The test suite covers:

### Views
- ✅ Home page loading and template usage
- ✅ Login/logout link display based on authentication state
- ✅ Profile page authentication requirements
- ✅ Profile page content display

### Authentication
- ✅ Login page loading
- ✅ Login with valid credentials
- ✅ Login with invalid credentials
- ✅ Logout functionality and redirects
- ✅ Signup disabled (invitation-only)
- ✅ Email code login option availability
- ✅ GitHub social login option availability
- ✅ MFA activation page accessibility

### Custom Adapters
- ✅ Signup disabled via `is_open_for_signup()`
- ✅ Login redirect to `/profile/`
- ✅ Logout redirect to `/`

## Writing New Tests

When adding new features, please add corresponding tests:

1. Create test methods following the naming convention `test_<what_is_being_tested>`
2. Use descriptive docstrings for each test
3. Follow the existing test structure
4. Ensure tests are independent and can run in any order
5. Clean up test data in `tearDown()` if necessary

## Test Database

Django automatically creates a test database for running tests. It's destroyed after the test run completes.

## Environment Variables

Tests run with:
- `IGNORE_ENV_FILE=true` (when using tox)
- `SECRET_KEY="For testing only!"` (when using tox)
- `DEBUG=True` (Django default for tests)

## CI/CD

Tests are automatically run in CI/CD pipelines. See `.github/workflows/` for configuration.
