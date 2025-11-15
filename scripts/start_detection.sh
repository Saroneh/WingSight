#!/bin/bash
# Start WingSight detection script in background
# Run this script to start detection: ./start_detection.sh

cd "$(dirname "$0")/.."
SCRIPT_DIR="$(pwd)/scripts"

# Activate virtual environment if it exists
if [ -d "wgnenv" ]; then
    source wgnenv/bin/activate
fi

# Set Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Start detection script with nohup
nohup python3 "$SCRIPT_DIR/detect_with_motion.py" > "$SCRIPT_DIR/logs/detection.log" 2>&1 &

# Save PID
echo $! > "$SCRIPT_DIR/detection.pid"

echo "WingSight detection started!"
echo "PID: $(cat $SCRIPT_DIR/detection.pid)"
echo "Logs: $SCRIPT_DIR/logs/detection.log"
echo ""
echo "To check status: ./check_status.sh"
echo "To stop: ./stop_detection.sh"

