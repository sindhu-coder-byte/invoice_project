#!/usr/bin/env bash
# Render build script
# System packages (libpango, libcairo, etc.) are installed by packages.txt BEFORE this runs.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
