#!/bin/bash

if command -v python3 &>/dev/null; then
    python3 data/PipeLineTests.py
else
    python data/PipeLineTests.py
read -rp "Press Enter to exit..."
read -p "Press Enter to exit..."

fi
