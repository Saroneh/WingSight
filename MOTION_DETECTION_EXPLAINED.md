# Motion Detection Explained

## Overview
Motion detection identifies when something changes in the camera's view, so you only process frames when there's actual activity (saves CPU/battery on a Pi).

## Three Main Approaches

### 1. **Frame Differencing** (Simplest - Good for WingSight)
**How it works:**
- Compare current frame to the previous frame
- Convert both to grayscale
- Calculate absolute difference pixel-by-pixel
- Count how many pixels changed significantly
- If enough pixels changed → motion detected

**Pros:**
- Very lightweight (fast on Pi)
- No learning phase needed
- Works immediately

**Cons:**
- Sensitive to lighting changes (sunrise/sunset)
- Can trigger on camera shake or wind moving branches

**Best for:** Quick implementation, outdoor wildlife where lighting is relatively stable

---

### 2. **Background Subtraction** (More Robust)
**How it works:**
- Learn a "background model" over ~30 seconds (what the scene looks like when empty)
- Compare each new frame to this learned background
- Pixels that differ significantly = foreground (motion)
- Use algorithms like MOG2 or KNN (built into OpenCV)

**Pros:**
- Handles gradual lighting changes better
- Can ignore repetitive motion (swaying branches)
- More accurate

**Cons:**
- Needs ~30 seconds to "learn" the background
- Slightly more CPU intensive
- Background needs periodic updates

**Best for:** More reliable detection, indoor/controlled environments

---

### 3. **Hardware PIR Sensor** (Physical Motion Sensor)
**How it works:**
- Passive Infrared (PIR) sensor detects heat/movement
- Connected to GPIO pin on Raspberry Pi
- Triggers interrupt when motion detected
- Camera only wakes up when sensor fires

**Pros:**
- Very low power (sensor uses almost nothing)
- Only processes frames when motion detected
- Works in complete darkness
- No false positives from lighting changes

**Cons:**
- Requires hardware wiring
- Can't distinguish what moved (bird vs. person vs. cat)
- Limited range (~5-7 meters typically)

**Best for:** Battery-powered deployments, very low power requirements

---

## Recommended Approach for WingSight

**Start with Frame Differencing** because:
1. ✅ No hardware needed
2. ✅ Works immediately
3. ✅ Lightweight enough for Pi 3B+
4. ✅ Easy to tune (adjust threshold)

**Later upgrade to Background Subtraction** if you get too many false positives from lighting changes.

**Add PIR sensor** if you want ultra-low power operation (battery-powered setup).

---

## How Frame Differencing Works (Step-by-Step)

```
1. Capture Frame 1 → Convert to grayscale → Store as "previous"
2. Capture Frame 2 → Convert to grayscale → Store as "current"
3. Calculate: diff = |current - previous|
4. Count pixels where diff > threshold (e.g., 30 out of 255)
5. If changed_pixels > motion_threshold (e.g., 1% of image) → MOTION!
6. Set "current" as new "previous", repeat
```

**Tuning parameters:**
- `pixel_threshold`: How different must a pixel be? (typically 20-40)
- `motion_threshold`: What % of image must change? (typically 0.5-2%)

---

## Integration with Your Current Code

Instead of capturing every frame:
```
while True:
    frame = camera.capture_frame()
    # Process every frame ← Wastes CPU
```

You'd do:
```
while True:
    frame = camera.capture_frame()
    if motion_detector.has_motion(frame):
        # Only process when motion detected ← Saves CPU!
        detection, confidence = detector(frame)
        logger.log_detection(detection, confidence)
```

