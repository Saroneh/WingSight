"""Simple frame-differencing motion detector."""

import cv2
import numpy as np


class MotionDetector:
    """
    Lightweight motion detector using frame differencing.
    
    Compares consecutive frames to detect movement. Good for edge devices
    like Raspberry Pi where we want to save CPU by only processing frames
    when motion is detected.
    """

    def __init__(
        self,
        pixel_threshold: int = 30,
        motion_threshold: float = 0.01,
        blur_size: int = 5,
    ) -> None:
        """
        Initialize motion detector.

        Args:
            pixel_threshold: How different must a pixel be to count as changed?
                            (0-255, default 30)
            motion_threshold: What fraction of image must change to trigger?
                             (0.0-1.0, default 0.01 = 1%)
            blur_size: Size of blur kernel to reduce noise (odd number, default 5)
        """
        self.pixel_threshold = pixel_threshold
        self.motion_threshold = motion_threshold
        self.blur_size = blur_size
        self.previous_frame: np.ndarray | None = None

    def has_motion(self, frame: np.ndarray) -> tuple[bool, float]:
        """
        Check if motion is detected in the current frame.

        Args:
            frame: RGB frame from camera (numpy array, shape: HxWx3)

        Returns:
            Tuple of (has_motion: bool, motion_ratio: float)
            motion_ratio is the fraction of pixels that changed (0.0-1.0)
        """
        if frame is None:
            return False, 0.0

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Apply blur to reduce noise
        gray = cv2.GaussianBlur(gray, (self.blur_size, self.blur_size), 0)

        # If no previous frame, store this one and return no motion
        if self.previous_frame is None:
            self.previous_frame = gray.copy()
            return False, 0.0

        # Calculate absolute difference
        diff = cv2.absdiff(self.previous_frame, gray)

        # Threshold: pixels that changed significantly
        _, thresh = cv2.threshold(diff, self.pixel_threshold, 255, cv2.THRESH_BINARY)

        # Count changed pixels
        changed_pixels = np.sum(thresh > 0)
        total_pixels = thresh.size
        motion_ratio = changed_pixels / total_pixels

        # Update previous frame
        self.previous_frame = gray.copy()

        # Check if motion threshold exceeded
        has_motion = motion_ratio >= self.motion_threshold

        return has_motion, motion_ratio

    def reset(self) -> None:
        """Reset the detector (forgets previous frame)."""
        self.previous_frame = None

