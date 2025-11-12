"""
Simple detection and logging script.
Captures frames periodically and logs detections (placeholder for AI model).
"""

from pathlib import Path

import cv2

from wingsight.camera.pi_camera import PiCamera
from wingsight.logging.csv_logger import CSVLogger


def simple_detector(frame) -> tuple[str, float]:
    """
    Placeholder detector - returns "bird" or "no_bird".
    TODO: Replace with actual YOLOv5n/MobileNet inference.

    Args:
        frame: Camera frame (numpy array)

    Returns:
        Tuple of (detection_label, confidence)
    """
    # For now, just return "no_bird" as placeholder
    # Later: run YOLOv5n inference here
    return "no_bird", 0.0


def main() -> None:
    """Main detection loop."""
    # Setup
    camera = PiCamera(resolution=(640, 480), framerate=15)
    logger = CSVLogger(log_file="detections.csv")
    output_dir = Path(__file__).parent / "captures"
    output_dir.mkdir(exist_ok=True)

    print("Starting detection loop. Press Ctrl+C to stop.")
    frame_count = 0

    try:
        while True:
            frame = camera.capture_frame()
            if frame is None:
                print("Failed to capture frame, skipping...")
                camera.sleep_between_frames()
                continue

            # Run detection (placeholder for now)
            detection, confidence = simple_detector(frame)

            # Save image if detection is interesting (for now, save every 10th frame)
            image_path = None
            if frame_count % 10 == 0:
                timestamp_str = cv2.getTickCount()  # Simple unique name
                image_path = output_dir / f"frame_{timestamp_str}.jpg"
                cv2.imwrite(str(image_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                image_path = str(image_path)

            # Log detection
            logger.log_detection(detection, confidence, image_path)
            print(f"Logged: {detection} (confidence: {confidence:.2f})")

            frame_count += 1
            camera.sleep_between_frames()

    except KeyboardInterrupt:
        print("\nStopping detection loop...")
    finally:
        camera.close()
        print(f"Detection log saved to: {logger.log_file}")


if __name__ == "__main__":
    main()

