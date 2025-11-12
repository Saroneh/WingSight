"""
Motion-triggered detection script.
Only processes frames when motion is detected (saves CPU/battery).
"""

from pathlib import Path

import cv2

from wingsight.camera.pi_camera import PiCamera
from wingsight.detection.motion_detector import MotionDetector
from wingsight.logging.csv_logger import CSVLogger


def simple_detector(frame) -> tuple[str, float]:
    """
    Placeholder detector - returns "bird" or "no_bird".
    TODO: Replace with actual YOLOv5n/MobileNet inference.
    """
    return "no_bird", 0.0


def main() -> None:
    """Main detection loop with motion triggering."""
    # Setup
    camera = PiCamera(resolution=(640, 480), framerate=15)
    motion_detector = MotionDetector(
        pixel_threshold=30,      # Pixels must differ by 30/255 to count
        motion_threshold=0.01,   # 1% of image must change
        blur_size=5              # Blur to reduce noise
    )
    logger = CSVLogger(log_file="detections.csv")
    output_dir = Path(__file__).parent / "captures"
    output_dir.mkdir(exist_ok=True)

    print("Starting motion-triggered detection loop.")
    print("Only processing frames when motion is detected.")
    print("Press Ctrl+C to stop.\n")

    frame_count = 0
    motion_count = 0

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
                print(f"Motion detected! (ratio: {motion_ratio:.3f})")

                # Run detection only when motion detected
                detection, confidence = simple_detector(frame)

                # Save image
                timestamp_str = cv2.getTickCount()
                image_path = output_dir / f"motion_{timestamp_str}.jpg"
                cv2.imwrite(str(image_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

                # Log detection
                logger.log_detection(
                    detection, confidence, str(image_path)
                )
                print(f"  → Logged: {detection} (confidence: {confidence:.2f})\n")
            else:
                # No motion - just skip (saves CPU)
                if frame_count % 100 == 0:  # Print status every 100 frames
                    print(f"Monitoring... (frames: {frame_count}, motions: {motion_count})")

            frame_count += 1
            camera.sleep_between_frames()

    except KeyboardInterrupt:
        print(f"\nStopping detection loop...")
        print(f"Total frames: {frame_count}, Motion events: {motion_count}")
    finally:
        camera.close()
        print(f"Detection log saved to: {logger.log_file}")


if __name__ == "__main__":
    main()

