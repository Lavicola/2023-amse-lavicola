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
# for action check the exit code
exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "Python Tests executed successfully."
  exit 0
else
  echo "Python Tests failed."
  exit 1
fi
