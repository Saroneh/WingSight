"""CSV logger for timestamped wildlife detections."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional


class CSVLogger:
    """Simple CSV logger for detection events with timestamps."""

    def __init__(self, log_file: str = "detections.csv") -> None:
        """
        Initialize the CSV logger.

        Args:
            log_file: Path to the CSV log file
        """
        self.log_file = Path(log_file)
        self._ensure_header()

    def _ensure_header(self) -> None:
        """Ensure CSV file has headers if it's new."""
        if not self.log_file.exists():
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "detection", "confidence", "image_path"])

    def log_detection(
        self,
        detection: str,
        confidence: float = 1.0,
        image_path: Optional[str] = None,
    ) -> None:
        """
        Log a detection event to CSV.

        Args:
            detection: Detection result (e.g., "bird", "no_bird")
            confidence: Confidence score (0.0 to 1.0)
            image_path: Optional path to saved image
        """
        timestamp = datetime.now().isoformat()
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, detection, confidence, image_path or ""])

