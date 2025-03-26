#!/bin/sh -e

git pull --depth=1

source .venv/bin/activate
uv run bot.py
