"""
Smart motion-triggered detection script.
Only saves images when objects are detected (not just motion).
Includes cooldown to prevent too many images.
"""

import time
from pathlib import Path

import cv2

from wingsight.camera.pi_camera import PiCamera
from wingsight.detection.bird_detector import BirdDetector
from wingsight.detection.motion_detector import MotionDetector
from wingsight.logging.csv_logger import CSVLogger


def main() -> None:
    """Main detection loop with smart capture - only saves when objects detected."""
    # Configuration
    OBJECT_CONFIDENCE_THRESHOLD = 0.5  # Only save if object confidence > 0.5
    COOLDOWN_SECONDS = 10  # Max 1 image per 10 seconds
    MAX_IMAGES_PER_DAY = 100  # Safety limit (optional, can be removed)

    # Setup
    camera = PiCamera(resolution=(640, 480), framerate=15)
    motion_detector = MotionDetector(
        pixel_threshold=30,      # Pixels must differ by 30/255 to count
        motion_threshold=0.01,   # 1% of image must change
        blur_size=5              # Blur to reduce noise
    )
    print("Initializing object detector (YOLOv8n)...")
    detector = BirdDetector(confidence_threshold=0.10)  # Low threshold for detection
    
    # Verify model loaded
    if detector.model is None:
        print("ERROR: Object detector model failed to load!")
        print("Make sure ultralytics is installed: pip install ultralytics")
        return
    
    print("Object detector ready!\n")
    logger = CSVLogger(log_file="detections.csv")
    output_dir = Path(__file__).parent / "captures"
    output_dir.mkdir(exist_ok=True)

    print("Starting smart detection loop.")
    print(f"  - Only saves when objects detected (confidence > {OBJECT_CONFIDENCE_THRESHOLD})")
    print(f"  - Cooldown: {COOLDOWN_SECONDS} seconds between saves")
    print("Press Ctrl+C to stop.\n")

    frame_count = 0
    motion_count = 0
    saved_count = 0
    last_save_time = 0

    try:
        while True:
            frame = camera.capture_frame()
            if frame is None:
                print("Failed to capture frame, skipping...")
                camera.sleep_between_frames()
                continue

            # Check for motion
            has_motion, motion_ratio = motion_detector.has_motion(frame)

            if has_motion:
                motion_count += 1
                
                # Check cooldown
                current_time = time.time()
                time_since_last_save = current_time - last_save_time
                
                if time_since_last_save < COOLDOWN_SECONDS:
                    # Still in cooldown, skip
                    if frame_count % 50 == 0:
                        print(f"Motion detected (cooldown: {COOLDOWN_SECONDS - time_since_last_save:.1f}s remaining)")
                else:
                    # Check for objects in frame
                    objects = detector.detect_all_objects(frame, min_confidence=OBJECT_CONFIDENCE_THRESHOLD)
                    
                    if objects:
                        # Objects detected! Save image
                        saved_count += 1
                        last_save_time = current_time
                        
                        # Create filename with timestamp and detected objects
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        object_names = "_".join([obj[0] for obj in objects[:3]])  # First 3 objects
                        filename = f"{timestamp}_{object_names}.jpg"
                        image_path = output_dir / filename
                        
                        cv2.imwrite(str(image_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                        
                        # Log detection (use first object as primary)
                        primary_obj, primary_conf = objects[0]
                        logger.log_detection(primary_obj, primary_conf, str(image_path))
                        
                        print(f"💾 Saved: {filename}")
                        print(f"   Objects: {', '.join([f'{name} ({conf:.2f})' for name, conf in objects[:5]])}")
                        print()
                    else:
                        # Motion but no objects detected - skip saving
                        if frame_count % 20 == 0:
                            print(f"Motion detected but no objects found (confidence > {OBJECT_CONFIDENCE_THRESHOLD})")
            else:
                # No motion - just skip (saves CPU)
                if frame_count % 100 == 0:
                    print(f"Monitoring... (frames: {frame_count}, motions: {motion_count}, saved: {saved_count})")

            frame_count += 1
            camera.sleep_between_frames()

    except KeyboardInterrupt:
        print(f"\nStopping detection loop...")
        print(f"Total frames: {frame_count}")
        print(f"Motion events: {motion_count}")
        print(f"Images saved: {saved_count}")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        camera.close()
        print(f"Detection log saved to: {logger.log_file}")


if __name__ == "__main__":
    main()

