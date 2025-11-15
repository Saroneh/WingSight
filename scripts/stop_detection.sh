#!/bin/bash
# Stop WingSight detection script

SCRIPT_DIR="$(dirname "$0")"
PID_FILE="$SCRIPT_DIR/detection.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "Stopped WingSight detection (PID: $PID)"
        rm "$PID_FILE"
    else
        echo "Process not running (PID file exists but process is dead)"
        rm "$PID_FILE"
    fi
else
    # Try to find and kill by process name
    pkill -f "detect_with_motion.py"
    if [ $? -eq 0 ]; then
        echo "Stopped WingSight detection"
    else
        echo "No detection process found"
    fi
fi

