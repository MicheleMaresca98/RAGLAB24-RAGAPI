#!/bin/sh
set -eu

for credential in $(find /secrets -iname '*.credentials'); do
  . $credential
  psql -v ON_ERROR_STOP=1 --username="${POSTGRES_USER}" -w \
    -c "CREATE DATABASE ${DB_DATABASE};" \
    -c "CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASSWORD}';
        REVOKE ALL ON DATABASE ${DB_DATABASE} FROM PUBLIC;
        GRANT ALL ON DATABASE ${DB_DATABASE} TO ${DB_USER};"
  psql -v ON_ERROR_STOP=1 --username="${POSTGRES_USER}" -w --dbname="${DB_DATABASE}" \
    -c "GRANT ALL ON SCHEMA PUBLIC TO ${DB_DATABASE};"
done