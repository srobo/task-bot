#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

echo "> Running formatter..."
black task-bot.py --check

echo "> Running linter..."
flake8 task-bot.py

echo "> Running isort..."
isort -rc -c task-bot.py

echo "> Running type checker..."
mypy task-bot.py
