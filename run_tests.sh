#!/bin/bash

coverage run --source=./src/auth,./src/links --concurrency=greenlet -m pytest
coverage html
