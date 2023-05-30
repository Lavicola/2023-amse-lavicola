#!/bin/bash

if [[ $(pwd) == */project ]]; then
    cd ..
else
    echo "Error: Script requires being in /project directory." >&2
    exit 1
fi

if command -v python3 &>/dev/null; then
    python3 data/pipeline_tests.py
else
    python data/pipeline_tests.py
fi