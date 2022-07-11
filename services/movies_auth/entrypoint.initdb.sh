#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS content;
EOSQL

psql -v ON_ERROR=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE testdb;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname testdb <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS content;
EOSQL
