#!/usr/bin/env bash
set -euo pipefail
python -m pip install --upgrade pip pdm
pdm install --prod
pdm run python manage.py collectstatic --noinput
pdm run python manage.py migrate --noinput
