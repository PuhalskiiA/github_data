#!/bin/sh

p="/app/.venv/bin/python"

cd /app/src
if [ "$1" = "save" ]; then
    $p save_data.py
elif [ "$1" = "analyze" ]; then
    $p analyze_data.py
else
    echo "Usage: run {save|analyze}"
    exit 1
fi
