#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

black task-bot.py
isort task-bot.py
