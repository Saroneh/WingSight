"""Bird detection using YOLOv5n for lightweight edge inference."""

from typing import Optional, Tuple

import cv2
import numpy as np


class BirdDetector:
    """
    Bird detector using YOLOv5n (nano) model.
    Detects birds in frames using pre-trained COCO model.
    """

    def __init__(self, confidence_threshold: float = 0.25) -> None:
        """
        Initialize bird detector.

        Args:
            confidence_threshold: Minimum confidence to count as detection (0.0-1.0)
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load YOLOv5n model (lazy import to avoid errors if not installed)."""
        try:
            from ultralytics import YOLO

            # Load YOLOv5n (nano - smallest, fastest model)
            self.model = YOLO("yolov5n.pt")
            print("YOLOv5n model loaded successfully")
        except ImportError:
            print(
                "Warning: ultralytics not installed. Install with: pip install ultralytics"
            )
            print("Falling back to simple color-based detection...")
            self.model = None
        except Exception as e:
            print(f"Error loading YOLOv5n: {e}")
            print("Falling back to simple color-based detection...")
            self.model = None

    def detect(self, frame: np.ndarray) -> Tuple[str, float]:
        """
        Detect birds in frame.

        Args:
            frame: RGB frame from camera (numpy array, shape: HxWx3)

        Returns:
            Tuple of (detection_label, confidence)
            - "bird" if bird detected, "no_bird" otherwise
            - confidence score (0.0-1.0)
        """
        if frame is None:
            return "no_bird", 0.0

        # Use YOLOv5 if available
        if self.model is not None:
            return self._detect_yolo(frame)

        # Fallback: simple detection (always returns no_bird for now)
        return self._detect_simple(frame)

    def _detect_yolo(self, frame: np.ndarray) -> Tuple[str, float]:
        """Detect using YOLOv5n model."""
        try:
            # YOLO expects BGR, but we have RGB - convert
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Run inference
            results = self.model(frame_bgr, verbose=False)

            # COCO class 14 is "bird"
            bird_class_id = 14
            max_confidence = 0.0

            # Check all detections
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])

                        # Check if it's a bird
                        if class_id == bird_class_id:
                            if confidence > max_confidence:
                                max_confidence = confidence

            # Return result
            if max_confidence >= self.confidence_threshold:
                return "bird", max_confidence
            else:
                return "no_bird", max_confidence

        except Exception as e:
            print(f"Error in YOLO detection: {e}")
            return "no_bird", 0.0

    def _detect_simple(self, frame: np.ndarray) -> Tuple[str, float]:
        """
        Simple fallback detector (placeholder).
        Returns no_bird when YOLOv5 is not available.
        """
        return "no_bird", 0.0

