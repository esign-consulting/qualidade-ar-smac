#!/bin/sh
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
    CREATE EXTENSION postgis;
    SELECT extname, extversion FROM pg_extension;
    SELECT public.timescaledb_pre_restore();
    \i /docker-entrypoint-initdb.d/postgres.dump
    SELECT public.timescaledb_post_restore();
EOF
