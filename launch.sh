#!/bin/sh -e

git pull --depth=1

uv run bot.py
