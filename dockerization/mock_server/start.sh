#!/bin/bash

alembic upgrade head
python init_mock_data.py
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout-keep-alive 20