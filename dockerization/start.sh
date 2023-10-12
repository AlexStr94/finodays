#!/bin/bash

alembic upgrade head
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout-keep-alive 30