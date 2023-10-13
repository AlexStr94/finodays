#!/bin/bash

alembic upgrade head
python init_mock_data.py
gunicorn main:app --keep-alive 30 --timeout 60 --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
