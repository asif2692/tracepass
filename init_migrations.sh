#!/bin/bash
# Generate Flask-Migrate history (run once locally)
set -e
export FLASK_APP=run.py
flask db init || true
flask db migrate -m "initial schema"
flask db upgrade
echo "Migrations ready. Future model changes: flask db migrate -m 'message' && flask db upgrade"
