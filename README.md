# Telegram Vacancy Collector

![Build Status](https://github.com/Alexander-Tarletsky/vacancy-collector/workflows/CI/badge.svg?branch=master)


```
I have a `init.sql` file in the root of the project. The file looks like this:
```
CREATE DATABASE test_db;
```
I have a `init.sh` file in the root of the project. The file looks like this:
```
#!/bin/bash
psql -U $POSTGRES_USER -d $POSTGRES_DB -a -f /docker-entrypoint-initdb.d/init.sql