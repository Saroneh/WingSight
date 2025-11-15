#!/bin/bash
# Check status of WingSight detection

SCRIPT_DIR="$(dirname "$0")"
PID_FILE="$SCRIPT_DIR/detection.pid"
LOG_FILE="$SCRIPT_DIR/logs/detection.log"

echo "=== WingSight Detection Status ==="
echo ""

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Status: RUNNING (PID: $PID)"
    else
        echo "Status: STOPPED (PID file exists but process is dead)"
    fi
else
    # Check if process is running by name
    if pgrep -f "detect_with_motion.py" > /dev/null; then
        echo "Status: RUNNING (but no PID file)"
    else
        echo "Status: STOPPED"
    fi
fi

echo ""
echo "=== Recent Log Output ==="
if [ -f "$LOG_FILE" ]; then
    tail -n 20 "$LOG_FILE"
else
    echo "No log file found"
fi

echo ""
echo "=== Detection Stats ==="
if [ -f "$SCRIPT_DIR/detections.csv" ]; then
    TOTAL=$(wc -l < "$SCRIPT_DIR/detections.csv" | tr -d ' ')
    BIRDS=$(grep -c "bird" "$SCRIPT_DIR/detections.csv" 2>/dev/null || echo "0")
    echo "Total detections: $((TOTAL - 1))"  # Subtract header
    echo "Bird detections: $BIRDS"
else
    echo "No detections.csv found"
fi

if [ -d "$SCRIPT_DIR/captures" ]; then
    IMAGES=$(ls -1 "$SCRIPT_DIR/captures"/*.jpg 2>/dev/null | wc -l)
    echo "Images saved: $IMAGES"
    
    # Disk usage
    SIZE=$(du -sh "$SCRIPT_DIR/captures" 2>/dev/null | cut -f1)
    echo "Captures folder size: $SIZE"
fi

