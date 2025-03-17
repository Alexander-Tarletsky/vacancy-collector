# Telegram Vacancy Collector

![Code Check Status](https://github.com/Alexander-Tarletsky/vacancy-collector/actions/workflows/dev_branch.yml/badge.svg?branch=development)

I have a `init.sql` file in the root of the project. The file looks like this:
```
CREATE DATABASE test_db;
```
I have a `init.sh` file in the root of the project. The file looks like this:
```
#!/bin/bash
psql -U $POSTGRES_USER -d $POSTGRES_DB -a -f /docker-entrypoint-initdb.d/init.sql
```

Local Testing with Docker Compose
For local testing, you can launch the test database container by passing environment variables directly from the command line. This approach allows you to override settings without relying on a .env file. In your terminal, run:

```
#!/bin/bash
TEST_DB_USER=test_user \
TEST_DB_PASSWORD=your_local_test_password \
TEST_DB_NAME=tvc_test_db \
docker compose -f docker-compose-tests.yml up -d --build --wait
```

This command sets all the necessary environment variables for the test database container.
The --wait flag ensures that the container is fully initialized before running the tests (Docker Compose >=2.0.0).

After you finish testing, you can stop the container with:
```
#!/bin/bash
docker compose -f docker-compose-tests.yml down
```
Note: This local testing setup is intended for development purposes only. For remote CI/CD, such as with GitHub Actions, environment variables are configured via GitHub Secrets and the CI workflow uses the primary docker-compose file without the need for an override.