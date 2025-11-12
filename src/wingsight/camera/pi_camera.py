"""
Camera abstraction reused from the rover project's streaming module.
Provides a lightweight, dependency-friendly wrapper to obtain frames from the
Pi Camera (via picamera2) or an OpenCV-compatible USB camera fallback.
"""

from __future__ import annotations

import logging
import time
from typing import Optional, Tuple

import cv2
import numpy as np


logger = logging.getLogger(__name__)


class PiCamera:
    """Unified interface for PiCamera2 and OpenCV-compatible cameras."""

    def __init__(self, resolution: Tuple[int, int] = (640, 480), framerate: int = 30) -> None:
        """
        Args:
            resolution: Frame resolution (width, height).
            framerate: Desired frames per second.
        """
        self.resolution = resolution
        self.framerate = framerate
        self._camera = None
        self.camera_type: Optional[str] = None  # 'picamera2' or 'opencv'
        self._setup_camera()

    def _setup_camera(self) -> None:
        """Attempt to initialise the Pi Camera first, then fall back to OpenCV."""
        try:
            import sys

            sys.path.append("/usr/lib/python3/dist-packages")
            from picamera2 import Picamera2

            camera = Picamera2()
            config = camera.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"},
                controls={
                    "FrameDurationLimits": (
                        1_000_000 // self.framerate,
                        1_000_000 // self.framerate,
                    )
                },
            )
            camera.configure(config)
            camera.start()
            self._camera = camera
            self.camera_type = "picamera2"
            logger.info(
                "PiCamera2 initialised at %s resolution, %s fps",
                self.resolution,
                self.framerate,
            )
            return
        except ImportError:
            logger.info("picamera2 not available; falling back to OpenCV.")
        except Exception as exc:
            logger.warning("PiCamera2 initialisation failed: %s", exc)

        self._setup_opencv_fallback()

    def _setup_opencv_fallback(self) -> None:
        """Fallback initialisation for systems without PiCamera2."""
        camera = None
        try:
            for index in range(4):
                camera = cv2.VideoCapture(index)
                if camera.isOpened():
                    break
            if not camera or not camera.isOpened():
                raise RuntimeError("No OpenCV camera available.")

            camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            camera.set(cv2.CAP_PROP_FPS, self.framerate)

            ret, frame = camera.read()
            if not ret or frame is None:
                raise RuntimeError("OpenCV camera opened but failed to capture a frame.")

            self._camera = camera
            self.camera_type = "opencv"
            logger.info("OpenCV camera fallback initialised.")
        except Exception as exc:
            logger.error("Failed to initialise OpenCV camera: %s", exc)
            if camera:
                camera.release()
            self._camera = None
            self.camera_type = None

    def capture_frame(self) -> Optional[np.ndarray]:
        """Return a single RGB frame or None if capture fails."""
        if self._camera is None or self.camera_type is None:
            return None

        try:
            if self.camera_type == "picamera2":
                frame = self._camera.capture_array()
                if frame is None:
                    return None
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame

            if self.camera_type == "opencv":
                ret, frame = self._camera.read()
                if not ret or frame is None:
                    return None
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as exc:
            logger.error("Error capturing frame: %s", exc)
            return None

        return None

    def sleep_between_frames(self) -> None:
        """Sleep to respect requested framerate."""
        if self.framerate > 0:
            time.sleep(1.0 / self.framerate)

    def close(self) -> None:
        """Release camera resources."""
        if self._camera is None:
            return

        try:
            if hasattr(self._camera, "close"):
                self._camera.close()
            else:
                self._camera.release()
        finally:
            self._camera = None
            logger.info("Camera resources released.")


__all__ = ["PiCamera"]


