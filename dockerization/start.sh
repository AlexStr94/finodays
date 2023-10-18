#!/bin/bash

alembic upgrade head
gunicorn main:app --keep-alive 30 --timeout 60 --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000