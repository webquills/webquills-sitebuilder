#!/bin/bash
set -e

# This script is executed by the official PostgreSQL Docker image
# when the container is first started. It creates the databases and users
# for Django and Gitea with least-privilege permissions.

echo "Creating databases and users for Django and Gitea..."

# Create Django database and user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create Django user if it doesn't exist
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '${DJANGO_DB_USER}') THEN
            CREATE USER ${DJANGO_DB_USER} WITH PASSWORD '${DJANGO_DB_PASSWORD}';
        END IF;
    END
    \$\$;

    -- Create Django database if it doesn't exist
    SELECT 'CREATE DATABASE ${DJANGO_DB_NAME} OWNER ${DJANGO_DB_USER}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DJANGO_DB_NAME}')\gexec

    -- Grant privileges to Django user
    GRANT ALL PRIVILEGES ON DATABASE ${DJANGO_DB_NAME} TO ${DJANGO_DB_USER};
EOSQL

# Connect to Django database and grant schema privileges
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${DJANGO_DB_NAME}" <<-EOSQL
    -- Grant schema privileges
    GRANT ALL ON SCHEMA public TO ${DJANGO_DB_USER};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DJANGO_DB_USER};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DJANGO_DB_USER};
    
    -- Grant default privileges for future objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DJANGO_DB_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DJANGO_DB_USER};
EOSQL

# Create Gitea database and user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create Gitea user if it doesn't exist
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '${GITEA_DB_USER}') THEN
            CREATE USER ${GITEA_DB_USER} WITH PASSWORD '${GITEA_DB_PASSWORD}';
        END IF;
    END
    \$\$;

    -- Create Gitea database if it doesn't exist
    SELECT 'CREATE DATABASE ${GITEA_DB_NAME} OWNER ${GITEA_DB_USER}'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${GITEA_DB_NAME}')\gexec

    -- Grant privileges to Gitea user
    GRANT ALL PRIVILEGES ON DATABASE ${GITEA_DB_NAME} TO ${GITEA_DB_USER};
EOSQL

# Connect to Gitea database and grant schema privileges
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${GITEA_DB_NAME}" <<-EOSQL
    -- Grant schema privileges
    GRANT ALL ON SCHEMA public TO ${GITEA_DB_USER};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${GITEA_DB_USER};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${GITEA_DB_USER};
    
    -- Grant default privileges for future objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${GITEA_DB_USER};
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${GITEA_DB_USER};
EOSQL

echo "Database initialization complete!"
