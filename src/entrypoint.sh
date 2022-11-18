#!/bin/bash

# shellcheck disable=SC2164
cd /auth

while ! nc -z "$PG_HOST" "$PG_PORT"; do
      sleep 0.1
done

while ! nc -z "$REDIS_HOST" "$REDIS_PORT"; do
      sleep 0.1
done

export FLASK_APP=wsgi_app
export FLASK_RUN_PORT=8005
python3 -m flask run --with-threads --reload --host=0.0.0.0