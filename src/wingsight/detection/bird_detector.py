"""Bird detection using YOLOv5n for lightweight edge inference."""

from typing import Optional, Tuple

import cv2
import numpy as np


class BirdDetector:
    """
    Bird detector using YOLOv8n/YOLOv5n (nano) models.
    Detects birds in frames using pre-trained COCO model.
    Can use custom fine-tuned models for better Danish bird detection.
    """

    def __init__(self, confidence_threshold: float = 0.25, model_name: str = "yolov8n.pt") -> None:
        """
        Initialize bird detector.

        Args:
            confidence_threshold: Minimum confidence to count as detection (0.0-1.0)
            model_name: YOLO model to use. Default "yolov8n.pt" (better than yolov5n).
                       Can also use "yolov5n.pt" or path to custom fine-tuned model.
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        self._load_model(model_name)

    def _load_model(self, model_name: str = "yolov8n.pt") -> None:
        """
        Load YOLO model (lazy import to avoid errors if not installed).
        
        Args:
            model_name: Model to load. Options:
                - "yolov8n.pt" (recommended - newer, better accuracy)
                - "yolov5n.pt" (older, slightly faster)
                - "path/to/custom.pt" (fine-tuned model)
        """
        try:
            from ultralytics import YOLO

            # Try YOLOv8n first (better bird detection), fallback to YOLOv5n
            try:
                self.model = YOLO(model_name)
                print(f"{model_name} model loaded successfully")
            except Exception:
                # Fallback to YOLOv5n if YOLOv8n fails
                if model_name == "yolov8n.pt":
                    print("YOLOv8n not available, trying YOLOv5n...")
                    self.model = YOLO("yolov5n.pt")
                    print("YOLOv5n model loaded successfully")
                else:
                    raise
            
            print(f"Model device: {self.model.device}")
            print(f"Model classes: {len(self.model.names)} classes available")
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

            # Run inference with lower confidence to see more detections
            results = self.model(frame_bgr, verbose=False, conf=0.1)

            # COCO class 14 is "bird"
            bird_class_id = 14
            max_confidence = 0.0
            all_detections = []  # For debugging

            # Check all detections
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        all_detections.append((class_id, confidence))

                        # Check if it's a bird
                        if class_id == bird_class_id:
                            if confidence > max_confidence:
                                max_confidence = confidence

            # Debug: print what was detected (always show if no bird found)
            if len(all_detections) > 0:
                # Always show detections if no bird was found (for debugging)
                if max_confidence == 0.0:
                    print(f"  [DEBUG] Detected {len(all_detections)} objects (no bird):")
                    for class_id, conf in all_detections[:5]:  # Show first 5
                        class_name = self.model.names[class_id] if hasattr(self.model, 'names') else f"class_{class_id}"
                        print(f"    - {class_name} (ID: {class_id}) confidence: {conf:.2f}")
                # Show detections occasionally even when bird is found
                elif not hasattr(self, '_debug_count'):
                    self._debug_count = 0
                if hasattr(self, '_debug_count') and self._debug_count < 2:
                    print(f"  [DEBUG] Detected {len(all_detections)} objects:")
                    for class_id, conf in all_detections[:5]:
                        class_name = self.model.names[class_id] if hasattr(self.model, 'names') else f"class_{class_id}"
                        print(f"    - {class_name} (ID: {class_id}) confidence: {conf:.2f}")
                    self._debug_count += 1

            # Return result - show max confidence even if below threshold
            if max_confidence >= self.confidence_threshold:
                return "bird", max_confidence
            else:
                # Still return the confidence even if below threshold (for debugging)
                return "no_bird", max_confidence

        except Exception as e:
            print(f"Error in YOLO detection: {e}")
            import traceback
            traceback.print_exc()
            return "no_bird", 0.0

    def _detect_simple(self, frame: np.ndarray) -> Tuple[str, float]:
        """
        Simple fallback detector (placeholder).
        Returns no_bird when YOLOv5 is not available.
        """
        return "no_bird", 0.0

    def detect_all_objects(
        self, frame: np.ndarray, min_confidence: float = 0.5
    ) -> list[tuple[str, float]]:
        """
        Detect all objects in frame (not just birds).
        Useful for smart capture - only save when interesting objects detected.

        Args:
            frame: RGB frame from camera
            min_confidence: Minimum confidence to include detection

        Returns:
            List of (class_name, confidence) tuples for all detected objects
        """
        if frame is None or self.model is None:
            return []

        try:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            results = self.model(frame_bgr, verbose=False, conf=min_confidence)

            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = (
                            self.model.names[class_id]
                            if hasattr(self.model, "names")
                            else f"class_{class_id}"
                        )
                        detections.append((class_name, confidence))

            return detections

        except Exception as e:
            print(f"Error detecting objects: {e}")
            return []

