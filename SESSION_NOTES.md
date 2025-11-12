# WingSight – Session Notes (2025-11-12)

- Current files: `src/wingsight/camera/pi_camera.py`, `scripts/test_camera_capture.py`, `requirements.txt`.
- Camera check (headless): from `/home/hivex/WingSight` run  
  `export PYTHONPATH=/home/hivex/WingSight/src:$PYTHONPATH`  
  `python3 scripts/test_camera_capture.py` → writes `scripts/capture.jpg`.
- System packages in use: `python3-opencv`, `python3-picamera2` (from apt); Python env stays on system `python3`. Only `numpy` is installed via pip if needed.
- Next steps to consider: integrate motion trigger, add bird/no-bird inference hop, log detections locally, and wire telemetry (MQTT/HTTP).


