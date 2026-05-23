#!/bin/sh
set -e

mkdir -p /app/data

for seed_file in /opt/ragbot-seed/*.sqlite; do
    [ -e "$seed_file" ] || continue
    db_name=$(basename "$seed_file")

    if [ ! -f "/app/data/$db_name" ]; then
        echo "Initializing missing database: $db_name"
        cp "$seed_file" "/app/data/$db_name"
    fi
done


exec /app/.venv/bin/python controller.py