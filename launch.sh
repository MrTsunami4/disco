#!/bin/sh -e

git pull --depth=1

source .venv/bin/activate
pip install -r requirements.txt
python bot.py
