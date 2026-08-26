---
name: konsierge-project-setup
description: Prepare Konsierge Ruby and Rails repositories for local development or tests using mise, Bundler, Git submodules, and Docker Compose services such as PostgreSQL, Redis, and Elasticsearch. Use when onboarding a Konsierge project, installing its Ruby version and gems, initializing contracts, discovering and starting local infrastructure dependencies, reporting required environment variables, repairing an empty test database, or troubleshooting db:prepare, missing psql, Spring database caching, and service connection issues.
---

# Konsierge Project Setup

Prepare the repository without changing application behavior or destroying an existing database.

## Inspect the repository

1. Read `AGENTS.md`, `README.md`, `mise.toml`, `.ruby-version`, `.gitmodules`, `Gemfile`, `Gemfile.lock`, `config/database.yml`, environment examples, and the existing Compose file (`compose.yml` or legacy `docker-compose.yml`) when present.
2. Run `git status --short --branch` and preserve existing changes.
3. Prefer repository commands over generic commands.
4. Search application configuration, initializers, jobs, clients, and gems for PostgreSQL, Redis, Elasticsearch/OpenSearch, RabbitMQ, Kafka, MinIO/S3, Mailpit, and other required local services.
5. Derive versions, Compose service names, ports, credentials, and environment variable names from repository files. Do not silently invent values.

## Install Ruby with mise

From the repository root:

```bash
mise trust
mise install
mise exec -- ruby --version
mise exec -- bundle --version
```

If the repository has no mise configuration but has `.ruby-version`, create `mise.toml` only when the user authorizes a repository change:

```toml
[tools]
ruby = "<version from .ruby-version>"
```

Never substitute a different Ruby version merely because installation fails. Report missing build packages or unavailable versions explicitly.

## Install gems

Use the mise-selected Ruby:

```bash
mise exec -- bundle check
mise exec -- bundle install
```

Do not run `bundle update` during setup. Preserve `Gemfile.lock`. Use private gem credentials already configured in Bundler or the environment; never print or persist secret values.

## Initialize contract submodules

When `.gitmodules` defines a contracts submodule and the repository provides `bin/contracts-update`, inspect the submodule before running the updater:

```bash
git submodule status contracts
```

A leading `-` means the submodule is not initialized. Initialize it from the repository root, then run the project command:

```bash
git submodule update --init contracts
mise exec -- bin/contracts-update
```

Do not assume an HTTPS authentication error from `bin/contracts-update` requires a token. Some updater implementations change into `contracts` and run `git fetch`; if `contracts` is an empty, uninitialized submodule directory, Git can walk up to the parent repository and fetch the parent's HTTPS remote instead. Confirm with `git submodule status`, `.gitmodules`, and `git -C contracts remote -v`. After initialization, the submodule uses its configured remote, which may already authenticate through SSH. Never place a GitLab token in the repository or `.env` to work around an uninitialized submodule.

## Start PostgreSQL with Compose

For a new Compose file, use the modern canonical name `compose.yml`. If the repository already uses `docker-compose.yml`, preserve that filename unless the user requests a rename.

Inspect the Compose file first, then start only required database services:

```bash
docker compose up -d postgres_development postgres_test
docker compose ps
```

Wait for each healthcheck to become healthy before preparing databases. Do not use `docker compose down --volumes` unless the user explicitly authorizes deletion of local database data.

Use this `compose.yml` as a starting point when the repository has no database services. Replace the image version, ports, and database names with project values:

```yaml
services:
  postgres_development:
    image: postgres:17.5
    ports:
      - "127.0.0.1:5433:5432"
    environment:
      POSTGRES_DB: app_development
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app_development"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_development_data:/var/lib/postgresql/data

  postgres_test:
    image: postgres:17.5
    ports:
      - "127.0.0.1:5434:5432"
    environment:
      POSTGRES_DB: app_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d app_test"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - postgres_test_data:/var/lib/postgresql/data

volumes:
  postgres_development_data:
  postgres_test_data:
```

Keep development and test on separate ports and volumes. Bind ports to `127.0.0.1`, add healthchecks, and avoid embedding production credentials. Re-read the repository's selected Compose file and `config/database.yml` before every setup because project values may differ from this example.

## Add other required services

Add every locally required dependency discovered in the repository to the same Compose file unless the project intentionally uses a shared or remote service. Do not add Redis, Elasticsearch, or another service merely because it is common; require evidence from gems, configuration, code, or documentation.

Use service-specific healthchecks and persistent volumes where state is useful. Example additions:

```yaml
services:
  redis:
    image: redis:7.4-alpine
    ports:
      - "127.0.0.1:6380:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.17.0
    ports:
      - "127.0.0.1:9201:9200"
    environment:
      discovery.type: single-node
      xpack.security.enabled: "false"
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
    healthcheck:
      test: ["CMD-SHELL", "curl --fail http://localhost:9200/_cluster/health || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 10
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

volumes:
  elasticsearch_data:
```

Merge these entries into the existing top-level `services` and `volumes` mappings; do not create duplicate YAML keys. Match image versions to project compatibility. For Elasticsearch, confirm whether security must remain enabled and never copy production credentials into Compose.

After editing Compose, run `docker compose config` before starting services, then run `docker compose up -d <required-services>` and wait for healthy status.

## Prepare databases

When the PostgreSQL client is installed locally, prefer Rails tasks:

```bash
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/app_development \
  mise exec -- bin/rails db:prepare

RAILS_ENV=test \
TEST_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5434/app_test \
  mise exec -- bin/rails db:prepare
```

For repositories using `structure.sql`, Rails requires `psql` on `PATH`. Install the matching PostgreSQL client package when possible. If only the Compose container has `psql`, load the structure through that container. Recreate only an explicitly identified disposable development or test database, never production or staging.

Use `rtk proxy` for stdin passthrough when repository instructions require RTK:

```bash
rtk proxy docker exec -i <postgres-container> \
  psql --username=<user> --dbname=<database> --set ON_ERROR_STOP=1 --quiet --no-psqlrc \
  < db/structure.sql
```

After a manual structure load, ensure `ar_internal_metadata` contains the correct environment and current `schema_sha1`; otherwise `maintain_test_schema!` may purge and reload the database. Prefer Rails' schema-loading task when local `psql` is available because Rails sets these flags automatically.

## Run Rails and tests

Pass the same connection URL on every command:

```bash
DATABASE_URL=<development-url> mise exec -- bin/rails server
TEST_DATABASE_URL=<test-url> mise exec -- bin/rspec
```

If Spring previously booted with another database configuration:

```bash
mise exec -- bin/spring stop
DISABLE_SPRING=1 TEST_DATABASE_URL=<test-url> mise exec -- bin/rspec <spec-path>
```

Start with one focused spec. Run the full repository verification command only after focused checks pass.

## Verify setup

Confirm all applicable checks:

```bash
mise exec -- ruby --version
mise exec -- bundle check
docker compose ps
DISABLE_SPRING=1 TEST_DATABASE_URL=<test-url> mise exec -- bin/rspec <spec-path>
```

## Report required environment variables

Collect variable names from `.env.example`, credentials/config wrappers, initializers, `ENV.fetch`, `ENV[]`, Compose ports, and service client configuration. At the end, show the user every variable they must add or confirm for local development and tests.

Output variables as a copy-ready `.env` code block, not a table. Put status and scope in comments immediately above each variable when needed:

```dotenv
# Required for development
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/app_development

# Required for tests
TEST_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5434/app_test

# Optional; required only when Redis-backed features run locally
REDIS_URL=redis://127.0.0.1:6380/0

# Required secret; obtain from the team password manager
EXTERNAL_API_TOKEN=<required-secret>
```

Use exact variable names expected by the repository. Include safe local credentials when they are explicitly defined by repository-local Compose configuration so the block works when copied. For real secrets, tokens, keys, production credentials, and private endpoints, use clear placeholders such as `<required-secret>`; never reveal or invent values. Distinguish required, optional, test-only, and already-configured variables with short comments. If a required secret has no safe local default, state where it must come from.

Report Ruby version, gem installation result, Compose services and health, required environment variables, database URLs without secrets, tests run, and any blocked checks. Do not commit setup changes unless the user requests a commit.
