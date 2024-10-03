#!/bin/sh

set -eu

for credential in $(find /secrets -iname '*.credentials'); do
  . $credential
  mysql --user="${MYSQL_ROOT_USER}" --password="${MYSQL_ROOT_PASSWORD}" -e "
    CREATE DATABASE IF NOT EXISTS ${DB_DATABASE};
    CREATE USER IF NOT EXISTS '${DB_USER}' IDENTIFIED BY '${DB_PASSWORD}';
    GRANT ALL PRIVILEGES ON ${DB_DATABASE}.* TO '${DB_USER}';"
done
