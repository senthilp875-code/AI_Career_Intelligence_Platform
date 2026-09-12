#!/usr/bin/env bash

set -o errexit

gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT