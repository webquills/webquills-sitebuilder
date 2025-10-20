# Gitea API Client

This is an auto-generated Python client for the Gitea API, based on the official Gitea OpenAPI/Swagger specification.

## Generation

The client was generated using [OpenAPI Generator](https://openapi-generator.tech/) from the Gitea API definition:

```bash
docker run --rm -v /tmp:/tmp openapitools/openapi-generator-cli:latest generate \
    -i /tmp/gitea-api-definition.yaml \
    -g python \
    -o /tmp/gitea-client \
    --additional-properties=packageName=gitea_client,projectName=gitea-client
```

## Usage

```python
from gitea_client import ApiClient, Configuration
from gitea_client.api import UserApi

# Configure API client
config = Configuration(
    host="http://localhost:3000/api/v1"
)
config.api_key['TOTPHeader'] = 'YOUR_API_TOKEN'

# Create API client
with ApiClient(config) as api_client:
    # Use the API
    user_api = UserApi(api_client)
    current_user = user_api.user_get_current()
    print(current_user)
```

## Dependencies

- urllib3 >= 2.1.0, < 3.0.0
- python-dateutil >= 2.8.2
- pydantic >= 2
- typing-extensions >= 4.7.1

## Documentation

For detailed API documentation, see the [Gitea API Documentation](https://docs.gitea.com/api/overview/).
