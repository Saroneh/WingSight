"""
Headless-friendly sanity check for the Pi camera integration.
Captures up to 100 frames and saves the first successful capture to disk.
"""

from pathlib import Path

import cv2

from wingsight.camera.pi_camera import PiCamera


def main() -> None:
    output_path = Path(__file__).parent / "capture.jpg"

    camera = PiCamera(resolution=(640, 480), framerate=15)
    saved = False
    try:
        for _ in range(100):
            frame = camera.capture_frame()
            if frame is None:
                print("Failed to capture frame.")
                break

            if not saved:
                cv2.imwrite(str(output_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                print(f"Saved frame to {output_path}")
                saved = True

            camera.sleep_between_frames()
    finally:
        camera.close()


if __name__ == "__main__":
    main()

