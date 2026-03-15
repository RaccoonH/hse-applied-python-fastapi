#!/bin/bash

coverage run --concurrency=greenlet -m pytest tests
coverage html
