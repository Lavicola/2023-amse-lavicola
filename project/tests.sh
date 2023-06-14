#!/bin/bash

if [[ $(pwd) == */project ]]; then
    cd ..
else
    echo "Error: Script requires being in /project directory." >&2
    exit 1
fi

if command -v python3 &>/dev/null; then
    (cd .. && cd data && python3 -m unittest pipeline_tests.PipelineTests.test_pipeline_without_arguments)
else
    (cd .. && cd data && python -m unittest pipeline_tests.PipelineTests.test_pipeline_without_arguments)
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
