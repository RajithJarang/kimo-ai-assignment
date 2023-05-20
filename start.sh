#!/usr/bin/env sh
gunicorn -k uvicorn.workers.UvicornWorker --preload --reload --bind 0.0.0.0:8888 -w 1 app.main:app
