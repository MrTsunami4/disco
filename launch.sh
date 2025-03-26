#!/bin/sh -e

git pull --depth=1

source .venv/bin/activate
uv pip install -e .
python bot.py
