# Running WingSight Headless (Without Mac Connected)

## Quick Start

### Start Detection
```bash
cd /home/hivex/WingSight/scripts
chmod +x *.sh
./start_detection.sh
```

### Check Status
```bash
./check_status.sh
```

### Stop Detection
```bash
./stop_detection.sh
```

### View Logs
```bash
# Watch logs in real-time
tail -f logs/detection.log

# View last 50 lines
tail -n 50 logs/detection.log
```

## Files Created

- `logs/detection.log` - All output from the script
- `detections.csv` - Detection log (timestamp, object, confidence)
- `captures/` - Folder with saved images
- `detection.pid` - Process ID file (for stopping)

## Auto-Start on Boot (Optional)

To make WingSight start automatically when Pi boots:

1. Edit crontab:
```bash
crontab -e
```

2. Add this line (runs on boot):
```
@reboot cd /home/hivex/WingSight/scripts && ./start_detection.sh
```

3. Save and exit

## Monitoring

- **Check if running:** `./check_status.sh`
- **View live logs:** `tail -f logs/detection.log`
- **Check disk space:** `df -h`
- **Count images:** `ls captures/*.jpg | wc -l`

## Troubleshooting

**Script won't start:**
- Check virtual environment: `source ../wgnenv/bin/activate`
- Check Python path: `echo $PYTHONPATH`
- Check logs: `cat logs/detection.log`

**Script stops unexpectedly:**
- Check logs for errors: `tail -50 logs/detection.log`
- Check if out of disk space: `df -h`
- Restart: `./stop_detection.sh && ./start_detection.sh`

