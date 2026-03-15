#!/bin/bash

cd src
redis-server --daemonize yes
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --daemon --pid /tmp/test_gunicorn.pid

cd ..
sleep 2
locust -f tests/locustfile.py --host=http://127.0.0.1:8000 --headless --users 100 --spawn-rate 10 --run-time 20s

kill $(cat /tmp/test_gunicorn.pid)
redis-cli shutdown
