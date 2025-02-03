#!/bin/sh

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOF
CREATE EXTENSION postgis;
SELECT extname, extversion FROM pg_extension;
EOF
